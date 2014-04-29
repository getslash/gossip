default: test

test: env
	.env/bin/py.test tests

env: .env/.up-to-date


.env/.up-to-date: setup.py
	virtualenv .env
	.env/bin/pip install -e .
	.env/bin/pip install -r test_requirements.txt
	touch $@

