clean:
	rm -rf dist build _build __pycache__ *.egg-info

format:
	pipenv run isort setup.py src tests
	pipenv run black --line-length=120 setup.py src tests

lint:
	pipenv run flake8 setup.py src tests
	pipenv run mypy src
	pipenv run pylint --rcfile=.pylintrc setup.py src tests

.PHONY: notebook
notebook:
	cd notebooks && PYTHONPATH=../ jupyter notebook

unit-tests:
	pipenv run pytest -v -m "not integration" -k "not parse_market_state and not open_orders_account"

int-tests:
	bash scripts/run_int_tests.sh

# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = docsrc
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: docs
docs:
	@make html
	@cp -a _build/html/ docs
