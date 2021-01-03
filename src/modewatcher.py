#!/usr/bin/python3

import json
import subprocess
import time
import syslog
import signal


iio_path = "/sys/bus/iio/devices/iio:device%s/in_accel_%s_raw"
tablet_threshold=300
interval=.7
last_mode=""
stable_reads=0
stable_threshold=3
orientation_factor=2
orientation_threshold=300
current_mode=".unlock_normal"
v_keyboard="3"
v_pointer="2"
keyboard="11"
touchscreen="9"
touchpad="10"
disp="eDP-1"
running=True


syslog.openlog("modewatcher",syslog.LOG_PID,syslog.LOG_USER)

def do_exit(signal,frame):
    globals()['running']=False

signal.signal(signal.SIGHUP, do_exit)
signal.signal(signal.SIGINT, do_exit)
signal.signal(signal.SIGTERM, do_exit)

def get_accel(fp):
    fp.seek(0,0);
    return int(fp.readline().rstrip("\n"))

def set_mode(mode,orientation):
    lock_str,orient = orientation.split("_")
    subprocess.run(["/usr/bin/xrandr", "--output", disp, "--rotate", orient])
    subprocess.run(["/usr/bin/xinput", "--map-to-output", touchscreen, disp])
    if lock_str == "unlock":
        subprocess.run(["/usr/bin/xinput", "reattach", keyboard, v_keyboard])
        subprocess.run(["/usr/bin/xinput", "reattach", touchpad, v_pointer])
        time.sleep(4)
        subprocess.run(['/usr/bin/dbus-send','--type=method_call', '--dest=org.onboard.Onboard',
                        '/org/onboard/Onboard/Keyboard', 'org.freedesktop.DBus.Properties.Set',
                        'string:org.onboard.Onboard.Keyboard', 'string:AutoShowPaused', 'variant:boolean:true'])

    else:
        subprocess.run(["/usr/bin/xinput", "float", keyboard])
        subprocess.run(["/usr/bin/xinput", "float", touchpad])
        time.sleep(2)
        subprocess.run(['/usr/bin/dbus-send','--type=method_call', '--dest=org.onboard.Onboard',
                        '/org/onboard/Onboard/Keyboard', 'org.freedesktop.DBus.Properties.Set',
                        'string:org.onboard.Onboard.Keyboard', 'string:AutoShowPaused', 'variant:boolean:false'])


with open(iio_path % (1, 'x')) as LIDX, open(iio_path % (2, 'x')) as BASEX, \
     open(iio_path % (1, 'y')) as LIDY, open(iio_path % (2, 'y')) as BASEY, \
     open(iio_path % (1, 'z')) as LIDZ, open(iio_path % (2, 'z')) as BASEZ:
    syslog.syslog(syslog.LOG_INFO,"Starting modewatcher")
    while running:
        accel = { "lx": get_accel(LIDX),
                   "bx": get_accel(BASEX),
                   "ly": get_accel(LIDY),
                   "by": get_accel(BASEY),
                   "lz": get_accel(LIDZ),
                   "bz": get_accel(BASEZ),
                   }
        if (accel['ly'] > 0) and (accel['bz'] > 0):
            accel['mode'] = "laptop"
            accel["orientation"] = "unlock_normal"
        elif abs(accel['lz'] + accel['bz']) < tablet_threshold:
            accel['mode'] = "tablet"
            if (abs(accel['lx']) > abs(orientation_factor*accel['ly']) and
                abs(accel['lx']) > orientation_threshold
            ):
                accel['orientation'] = "lock_right" if (accel['lx']>0) else "lock_left"
            elif (abs(accel['ly']) > abs(orientation_factor*accel['lx']) and
                  abs(accel['ly']) > orientation_threshold
            ):
                accel['orientation'] = "lock_normal" if (accel['ly']>0) else "lock_inverted"
            else:
                accel['orientation'] = current_mode.split(".")[1]
        elif accel['ly'] > 0:
            accel['mode'] = "kiosk"
            accel["orientation"] = "lock_normal"
        else:
            accel['mode'] = "tent"
            accel['orientation'] = "lock_inverted"
        full_mode = "%(mode)s.%(orientation)s" % accel
        if full_mode == last_mode:
            stable_reads+=1
        else:
            stable_reads=0
            last_mode=full_mode
        if (stable_reads > stable_threshold) and (current_mode != last_mode):
            syslog.syslog(syslog.LOG_INFO, "Mode change %(mode)s.%(orientation)s" % accel)
            syslog.syslog(syslog.LOG_DEBUG, json.dumps(accel))
            current_mode=full_mode
            set_mode(accel["mode"], accel["orientation"])
            time.sleep(interval*4)
        time.sleep(interval)


syslog.syslog(syslog.LOG_INFO, "Signal received. Exiting")
syslog.closelog()
