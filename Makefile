default: test

test: env
	.env/bin/nosetests -x -w tests --nologcapture -s

env: .env/.up-to-date


.env/.up-to-date: setup.py
	virtualenv .env
	.env/bin/pip install -e .
	.env/bin/pip install nose
	touch $@

