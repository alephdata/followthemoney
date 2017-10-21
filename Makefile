
all: clean test dists release

test:
	nosetests --with-coverage --cover-package=followthemoney --cover-erase

dists:
	python setup.py sdist bdist_wheel

release: dists
	twine upload dist/*

clean:
	rm -rf dist build .eggs
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
