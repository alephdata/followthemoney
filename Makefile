
all: clean test dists release

test:
	pip install -q nose coverage responses
	nosetests --with-coverage --cover-package=followthemoney --cover-erase

dist:
	python setup.py sdist bdist_wheel

release: clean dist
	twine upload dist/*

clean:
	rm -rf dist build .eggs
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
