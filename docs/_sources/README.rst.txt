#################################
Ubuntu 20.04 on Asus C302CA Notes
#################################

Github `source code`_ and `documentation`_.

.. contents::
        :depth: 3
        :local:


What 
====

The Asus Chromebook Flip C302CA was kind of a great deal a long while ago when it was new, but as a programmer I had a love hate relationship with it. The form factor, long battery life, table / laptop etc is just fantastic. Nothing like blowing 4 hours on battery and still having half to go. And the thing is small, with a decent keyboard so you can tablet or laptop to your hearts content.

The hate came with chrome os. There was promise of linux apps that every other platform after the c302ca got years before I gave up on waiting and got this working with linux. Unfortunately I had to do it a second time for an upgrade and some stuff changed and I didn't take notes, so... This time I took notes.

The little device is now my current favorite device ever.  All aspects of it are working including suspend, resume, audio, rotation, touch, disabling the keyboard and touch pad in tablet mode, and automatically bringing up an on screen keyboard when in table mode and you bring focus to a text input. All of this on ubuntu 20.4 LTS so I shouldn't have to do this again for a good long while.

Google has since finally allegedly brought linux apps to the skylake/cave devices within chromeos, but why bother. I can't say I miss it, but it's not chomeos, it is me. I would rather build the sandbox than play in it, and it's a much more useful tool to build sandboxes if you void the warranty and put some linux on it.

Much of this was written after the fact so there might be some errors of memory.


Process
=======

Void the warranty
^^^^^^^^^^^^^^^^^
This requires removing the `write protect screw`_ and flashing to a `third party`_ BIOS to allow install native linux. That process is covered elsewhere. 

.. warning:: The above steps can brick a device, and will stop you from going back to chromeos without some additional drama.

(Mostly) Install Ubuntu Desktop 20.04
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

I had a heck of a time getting this to install with an intact bootloader. Milage may vary, but you can complete it without a boot loader from the live disk then just fix it so it boots. These instructions are from memory so they might not work either.

1. Boot into the live CD and get on the internet.
2. Temporarily ix screen rotation. Turn the screen upside down, click the drop down at the top (now bottom) right and lock screen rotation.
3. Optional: setup your paritions to install to in the live cd. I don't think you need to put boot as a primary partition, but it does make fixing boot issues easier.

   .. code-block:: shell

        # I created something like the following with something like the following.
        # NAME          MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
        # mmcblk0       179:8    0 58.2G  0 disk 
        # ├─mmcblk0p1   179:9    0  128M  0 part /boot/efi
        # ├─mmcblk0p2   179:10   0    1G  0 part /boot
        # └─mmcblk0p3   179:11   0 57.1G  0 part 
        #   ├─vg0-slash 253:0    0   14G  0 lvm  /
        #   ├─vg0-home  253:1    0   14G  0 lvm  /home
        #   └─vg0-swap  253:2    0    4G  0 lvm  [SWAP]
        sudo bash -il
        sfdisk<<-'END'
                label: gpt
                label-id: 138A1911-51AC-4B00-BA5A-8E4F1A09FBFD
                device: /dev/mmcblk0
                unit: sectors
                first-lba: 34
                last-lba: 122142686
                
                /dev/mmcblk0p1 : start=        4096, size=      262144, type=C12A7328-F81F-11D2-BA4B-00A0C93EC93B, uuid=833E3796-0282-4F67-B0A4-B937D758EF8B, name="UEFI System"
                /dev/mmcblk0p2 : start=      268288, size=     2097152, type=0FC63DAF-8483-4772-8E79-3D69D8477DE4, uuid=14459C81-CC21-4516-9C07-45AA6E0C3296, name="boot", attrs="LegacyBIOSBootable"
                /dev/mmcblk0p3 : start=     2365440, size=   119775232, type=E6D6D379-F507-44C2-A23C-238F2A3DF928, uuid=9AA487E3-1C14-47DB-B03C-075EAABE6AD5, name="pv1
        END
        apt-get update
        sudo apt-get install lvm2
        vgcreate vg0 /dev/mmcblk0p3
        vgchange -a y vg0
        lvcreate -n swap -L 4G vg0
        lvcreate -n slash -L 14G vg0
        lvcreate -n home -L 14G vg0
        mkfs.ext4 -L slash /dev/mapper/vg0-slash
        mkfs.ext4 -L home /dev/mapper/vg0-home
        mkswap -L swap0 /dev/mapper/vg0-swap
        mkfs.ext4 -L boot /dev/mmcblk0p2

4. Check out properties on the "Install ..." app on the desktop to find the sudo / command they use to start the installer.
5. Add '--help' to the quoted invocation of the installer to find the "install without bootloader" flag.
6. Open a terminal and start the installer with a minus bootload flag.
7. Install selecting the paritions you just setup for /boot / swap /home and UEFI.
8. next next finish wait continue instead of rebooting.
9. Capture some info on your filesystem layout in case you need it. *lsblk -f /dev/mmcblk0* captured in a picture with your phone should do.
10. Do a *df*. I forget if target is still mounted at this point. If it isn't, you can mount it with something like.

    .. code-block:: shell

       mount /dev/mapper/vg0-slash /somepath
       mount /dev/mmcblk0p2 /somepath/boot
       mount /dev/mmcblk0p1 /somepath/efi
       chroot /somepath
       mount -t udevtmpfs udev /dev
       mount -t devpts devpts /dev/pts
       mount -t proc proc /proc
       mount -t sysfs sysfs /sys

11. Try to install a bootloader. Is it just me, or do you also resent `RMS`_ for putting out man pages refering you to info pages because he's obsessed with emacs?

    .. code-block:: shell

        # Edit /etc/default/grub and set the folowing vars
        GRUB_CMDLINE_LINE="acpi_osi=Linux tpm_tis.interupts=0 tpm_tis.force=0"
        GRUB_CMDLINE_LINUX_DEFAULT="i915.enable_guc=2 i915.modeset=1 intel_ide.max_cstate=7 i915.fastboot=1 vt.handoff=7 i915.alpha_support=1 i915.fastboot=1 splash"
        # then run the following as root.
        env GRUB_DISABLE_OS_PROBER="true" grub-mkconfig -o /boot/grub/grub.cfg
        grub-install --verbose --target=x86_64-efi

12. If you can boot, I remembered. If not, try boot from file in the bootmanager or the grub prompt. a grub prompt boot would be something like the following. Then try to fix whatever I remembered incorrectly.

    .. code-block:: shell

       linux (hd0,gpt2)/vmlinuz root=/dev/mapper/vg0-slash tmp_tis.interupts=0 tpm_tis.force=0
       initrd (hd0,gpt2)/initrd.img
       boot

About that screen rotation
^^^^^^^^^^^^^^^^^^^^^^^^^^

If your screen is upside down again, do step 2 above to temporarily fix it then disable iio-sensor-proxy.service.

.. code-block:: shell

   systemctl disable iio-sensor-proxy.service
   systemctl stop iio-sensor-proxy.service
   systemctl mask iio-sensor-proxy.service

So that iio sensor service connects various industrial sensors on the iio bus throughout the device. Among them are two accelerometers, one each in the base and lid, a gyro, and an ambient light sensor. What iio-sensor-proxy does is offer a multithreaded service to find out what sensors exist, and gather data from them over the dbus. It almost works so well you could kick yourself.  For starters, it only deals with the one accelerator in the lid that is mounted upside down and the ambient light sensor. Gnome-shell than has some compiled in goodies to automatically turn on the rotate screen lock / unlock menu item and keep adjusting brightness in response to the ambient light sensor. It appears that this was recently cutover to iio-sensor-proxy and some of the gsettings to disable the plugin simply don't do anything currently, but shutting of iio-sensor-proxy works like a charm. If you log out and log back in again, the options for screen rotate will be gone. For now, you are better off without it. Even though it would spastically and aggressively rotate a screen, and the directionality of it can be fixed it won't do most of what we need, and it also won't stop playing with the screen brightness which drove me nuts.

Replacing iio-sensor-proxy for a tablet.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

What it doesn't do?

1. Adjust the track pad or touch orientation when it flips the screen around so suddenly everything is backwards directionally.
2. Disable the keyboard in tent or tablet mode.
3. Present a visual keyboard when there is a text input in tablet or tent mode and the physical keyboard is disabled.

As it turns out, this is a mathy problem. For starters, there is no lid angle sensor. And the gyro is mostly useless and power hungry and all you get out of an accelerometer is some strange numbers for xyz coordinates representing force and along what axis, but even that is a little wonky since the number wrap around on themselves in several spots as the sensor positions change. Long story short, these can be used to decipher velocity along an axis of the sensor which, when at a stand still, can tell you the position of the sensor in space accross three rotational axis given the constant of gravity! AHA you say! So if my sensor falls through a vacuum at terminal velocity, the accelerometer will be all zeros! And that is neat, but how do know if it is in tent or tablet mode or the other weird on where it's like tent, but the keyboard is upside down acting as a display holder?

For that, you need both accelerometers. Now, with `gravity riding everything`_, you have two set of three axis positioning data that can be compared to establish positional planes in three dimensional space that must intersect eachother or be parallel.

Yes, that is a lot of math. It turns out that you don't actually need to do that though largely because the hinge creates one fixed relationship around which the others pivot. Yay, down to two dimensions. Also, you don't have to really do the math, just compare the readings.

That is just what `src/modewatcher.py`_ will do for you minus all of the dbus complexity. I originally wrote it for 19.10 xubuntu and the only thing I needed to change was change disp from "eDP1" to "eDP-1". 

Installing modewatcher with onboard (on screen keyboard)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some basic notes.

The rotation is lazy. Instead of almost the next position and rapidly changing, it waits until it gets serveral consistent polls confirming the new position before changing, then it blocks another rapid change for a few polls. I hate it when my Tesla breaks for pedestrians and I lose my place in the LA times as the screen jumps to inappropriate orientations and back again. \*kidding\* You can make it more aggressive by messing with some of the vars that aren't device identifiers or sensor paths.

It will only switch to portate modes when the hinge is folded completely over because that is the only time it makes sense (to me).

Some of the vars are xinput ids or xrandr display identifiers which you can confirm with `xinput --list` or `xrandr --listmonitors`. That may differ.

.. warning::

    Do this as your non-priv user. Commands will call sudo where escalation is needed.

1. Files to install.

   .. code-block:: shell

      sudo apt-get update
      sudo apt-get install git onboard gnome-teaks mousetweak x11-xserver-utils xinput
      cd ~
      git clone https://github.com/devendor/c302ca
      test -d ~/bin || mkdir ~/bin
      cp ~/c302ca/src/modewatcher.py ~/bin/
      chmod +x ~/bin/modewatcher.py
      test -d ~/.local/share/applications/ || mkdir -p ~/.local/share/applications/
      sed -i "s#/home/rferguson#${HOME}#" ~/ca/src/devendor-modewatcher.desktop
      desktop-file-install  --dir=${HOME}/.local/share/applications/ ~/c302ca/src/devendor-modewatcher.desktop
      cat<<'END'>>~/.pam_environment
      ACCESSIBILITY_ENABLED=1
      GNOME_ACCESSIBILITY=1
      QT_ACCESSIBILITY=1
      END

2. In gnomes settings > Universal Access set **Always show universal access menu = True**
3. In Onboard Preferences. Note modewatcher will hide and pause autoshow via dbus in normal mode. The builting on-screen keyboard lacks features so I use onboard in a user session.
   **General > Show when unlocking screen = False**
   **Auto Show > General > Auto-show when editing text = True**
   **Auto Show > General > Hide when typeing on a physical keyboard = False**
   **Auto Show > Convertable Devices > all False**
   **Auto Show > External Keyboard > all False**
4. From the gnome tweaks menu. Add "Onboard" and "devendor modewatcher" to startup applications.
5. Fix for chrome if you have it installed. Similar should work for chome other based browsers. See notes in chrome://accessibility.

   .. code-block:: shell
   
      # Chrome requires a startup flag to enable accessibility persistence.
      test -f /usr/share/applications/google-chrome.desktop &&
      sed 's#/google-chrome-stable#/google-chrome-stable --force-renderer-accessibility#g'</usr/share/applications/google-chrome.desktop >~/google-chrome.desktop &&
      desktop-file-install --dir=${HOME}/.local/share/applications/google-chrome.desktop ~/google-chrome.desktop &&
      rm ~/google-chrome.desktop


Fixing Sound
^^^^^^^^^^^^

You may have noticed that sound doesn't work. This was somewhat easier to fix in 19.10 before some alsa sound changes that moved SOF into the default for intel sound drivers. The trouble is that this is some weird intelish sound hardware working in coordination with some other sound chips that I can't get to work with the sof open firmware or kernels built to include it. So custom kernel time.

.. warning:: Installing an unsigned kernel from the internet is easier, but not a good security choice. You should probably skip to building a kernel instead of using mine.

**The Lazy (insecure) way**

.. code-block:: shell

   cd ~
   apt install ./c302ca/debs/linux-headers-5.10.3_5.10.3-1_amd64.deb ./c302ca/debs/linux-image-5.10.3_5.10.3-1_amd64.deb ./c302ca/debs/linux-libc-dev_5.10.3-1_amd64.deb

skip to step 8

**The right way**

.. warning:: As non priv user please.

1. Go to kernel.org_ and download the latest source release or whatever release you fancy.
2. Verify you checksum.
3. Install build dependencies. I think this is enough? It will fail and complain if I missed something.

   .. code-block:: shell

      sudo apt install libc6-dev ncurses-dev gcc make binutils elfutils flex bison devscripts libssl-dev python-pytest

4. unpack, configure, build.

   .. code-block:: shell

      tar -Jxvf ~/Downloads/linux-x.y.z.tar.xz
      cd linux-x.y.z
      cp ~/c302ca/src/kernel-config .config
      make help # in case you are curious.
      make oldconfig
      make testconfig
      make -j2 bindeb-pkg 

5. Get a pot of coffee. Processors keep getting faster, but the kernel keeps getting more modules and I was too lazy to do much pruning from the distro kitchen sink kernel.
6. When it is done, if it worked.

   .. code-block:: shell

     cd ..
     sudo apt install linux-image-x.y.z_x.y.z-1_amd64.deb linux-headers-x.y.z_x.y.z-1_amd64.deb linux-libc-dev-x.y.z_x.y.z-1_amd64.deb
     mv linux*.deb ~/c302ca/debs/
     cp linux-x-y-z/.config ~/c302ca/debs/kernel-config
     rm -rf linux-x-y-z ~/Downloads/linux-x.y.z.tar.xz

7. If that was your first time, congratulations. Next time get out of the chair while it compiles because you will never get those moments back.
8. Point intel-hda-snd at old firmware.

   .. code-block:: shell
   
      cd /lib/firmware/intel
      sudo ln -sf dsp_fw_release_v969.bin dsp_fw_release.bin

9. Place the topology file where the driver currently looks for it. Formerly used dfw_sst.bin. loglevel=7 boot flag should show where it is trying to find a device topology to drive the card. Note that this is built from src/skl_n88l25_m98357a-tplg. See comments in the file.

   .. code-block:: shell
   
      cd ~
      sudo cp ./c302ca/fs/lib/firmware/skl_n88l25_m98357a-tplg.bin /lib/firmware/

10. Add the alsa use case manager configuration.

   .. code-block:: shell

      cd ~
      sudo cp -r ./c302ca/fs/usr/share/ucm2/sklnau8825max /usr/share/alsa/ucm2/
      sudo chown -R +r /usr/share/alsa/ucm2/sklnau8825max

11. Add some acpi event listeners for headphone / speaker switching.

   .. code-block:: shell

      cd ~
      sudo cp ./c302ca/fs/etc/acpi/events/* /etc/acpi/events/
      sudo chmod +r /etc/acpi/events/{plugheadphone,plugheadset,unplugheadphone}

12. Reboot and check.

    .. code-block:: shell

        rferguson@cave:~$ cat /proc/asound/cards 
         0 [sklnau8825max  ]: sklnau8825max - sklnau8825max
                      Google-Cave-1.0
        rferguson@cave:~$ pactl list cards 
        Card #0
                Name: alsa_card.platform-skl_n88l25_m98357a
                Driver: module-alsa-card.c
                Owner Module: 24
                Properties:
                        alsa.card = "0"
                        alsa.card_name = "sklnau8825max"
                        alsa.long_card_name = "Google-Cave-1.0"
                        alsa.driver_name = "snd_skl_nau88l25_max98357a"
                        device.bus_path = "platform-skl_n88l25_m98357a"
                        sysfs.path = "/devices/platform/skl_n88l25_m98357a/sound/card0"
                        device.form_factor = "internal"
                        device.string = "0"
                        device.description = "Built-in Audio"
                        module-udev-detect.discovered = "1"
                        device.icon_name = "audio-card"
                Profiles:
                        Headphone: Headphone (sinks: 1, sources: 1, priority: 1, available: yes)
                        Speaker: Speaker (sinks: 1, sources: 1, priority: 1, available: yes)
                        off: Off (sinks: 0, sources: 0, priority: 0, available: yes)
                Active Profile: Speaker
                Ports:
                        [Out] InternalMic: Internal Mic (priority: 100, latency offset: 0 usec)
                                Part of profile(s): Headphone, Speaker
                        [Out] Headphone: Headphone (priority: 100, latency offset: 0 usec)
                                Part of profile(s): Headphone
                        [In] InternalMic: Internal Mic (priority: 2, latency offset: 0 usec)
                                Part of profile(s): Headphone, Speaker
                        [Out] Speaker: Speaker (priority: 100, latency offset: 0 usec)
                                Part of profile(s): Speaker
                        [In] Speaker: Speaker (priority: 100, latency offset: 0 usec)
                                Part of profile(s): Speaker

13. Plug in some headphone and retry **pactl list cards** hopefulling noting a change in the Active Profile.
14. Try to use it.


Call Out
========

Please do let me know if you get sound working under SOF or get the little speaker icon to switch to a headphone icon when you switch outputs.



.. _third party: https://mrchromebox.tech
.. _write protect screw: https://google.com/search?q=write+protect+screw+c302ca
.. _RMS: https://www.google.com/search?q=Richard+Stallman&tbm=isch
.. _gravity riding everything: https://www.youtube.com/watch?v=U6XhVj5GF0I
.. _src/modewatcher.py: https://github.com/devendor/c302ca/blob/main/src/modewatcher.py
.. _kernel.org: https://kernel.org
.. _source code: https://github.com/devendor/c302ca
.. _documentation: https://devendor.github.io/c302ca/
