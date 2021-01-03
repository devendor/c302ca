#!/bin/bash

if [ -f README.rst ]; then
	sphinx-build -C  -D "extensions=sphinx.ext.githubpages" -D "html_sidebars.**=" \
		-D html_show_sphinx=0  -D master_doc=README -D html_theme=haiku -D "html_title=Asus c302ca + Ubuntu 20.04" \
		-D html_use_index=0 ./ ./docs/
	cd docs && ln -sf README.html index.html
else
	echo "This must run from dir with README.rst"
fi

