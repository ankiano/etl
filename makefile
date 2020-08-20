help:
	@echo "clean - remove all build, test and Python artifacts"
	@echo "dist - build package"
	@echo "install - install the package to the active Python's site-packages"

clean:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	rm -fr test/csv
	rm -fr test/xls
	find . -name '*.log' -exec rm -f {} +

dist: clean
	git describe --tags | sed -e "s/v\(.*\)-\(.*\)-\(.*\)/\1.dev\2+\3/g" > etl/VERSION
	python3 setup.py sdist
	python3 setup.py bdist_wheel

install: clean
	python3 setup.py install
