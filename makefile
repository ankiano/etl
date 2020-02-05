.PHONY: clean-pyc clean-build doc clean

help:
	@echo "clean - remove all build, test and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "doc - generate Sphinx HTML documentation, including API docs"
	@echo "dist - package"
	@echo "install - install the package to the active Python's site-packages"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr test/csv
	rm -fr test/xls
	find . -name '*.log' -exec rm -f {} +

lint:
	flake8 sparkle

dist: clean
	git describe --tags | sed -e "s/v\(.*\)-\(.*\)-\(.*\)/\1.dev\2+\3/g" > etl/VERSION
	python3 setup.py sdist
	python3 setup.py bdist_wheel

upload:
	twine upload dist/* --config-file /etc/pypirc --repository repository_name

install: clean
	python3 setup.py install
