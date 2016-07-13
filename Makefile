default: test

test: env
	.env/bin/py.test

.PHONY: doc
doc: env
	.env/bin/python setup.py build_sphinx -a -E


env: .env/.up-to-date


.env/.up-to-date: setup.py Makefile test_requirements.txt doc_requirements.txt
	virtualenv .env
	.env/bin/pip install -e .
	.env/bin/pip install -r test_requirements.txt
	.env/bin/pip install -r doc_requirements.txt
	touch $@

