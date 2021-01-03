#!/bin/bash

if [ -f README.rst ]; then
	sphinx-build -C  -D "extensions=sphinx.ext.githubpages" -D "html_sidebars.**=" -D html_show_sphinx=0  -D master_doc=README -D html_theme=haiku ./ ./docs/
else
	echo "This must run from dir with README.rst"
fi

