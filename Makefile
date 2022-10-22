default: test

test: env
	.env/bin/pytest

.PHONY: doc
doc: env
	.env/bin/python setup.py build_sphinx -a -E


env: .env/.up-to-date


.env/.up-to-date: setup.cfg Makefile requirements.txt
	virtualenv .env
	.env/bin/pip install -e '.[testing,doc]'
	touch $@

