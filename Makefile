default: test

.PHONY: doc
doc: env
	.venv/bin/python setup.py build_sphinx -a -E

test: env
	uv run --extra testing pytest tests

env:
	uv venv
	uv pip install -e ".[testing]"
