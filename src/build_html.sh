#!/bin/bash

if [ -f README.rst ]; then
	sphinx-build -C   \
		-D html_show_sphinx=0  -D master_doc=README -D html_theme=haiku -D "html_title=Asus c302ca + Ubuntu 20.04" \
		-D html_use_index=0 -D html_style=haikuish.css -D html_static_path=src/_static -D html_show_copyright=0 ./ ./docs/
	cd docs && ln -sf README.html index.html
else
	echo "This must run from dir with README.rst"
fi

