
all: clean test dists release

test:
	pip install -q nose coverage responses
	nosetests --with-coverage --cover-package=followthemoney --cover-erase

dist:
	python setup.py sdist bdist_wheel

release: clean dist
	twine upload dist/*

# initalize a new language:
# pybabel init -i followthemoney/i18n/messages.pot -d followthemoney/i18n -l de
translate:
	pip install --upgrade transifex-client
	pybabel extract -F babel.cfg -o followthemoney/i18n/messages.pot followthemoney
	tx push --source
	pybabel compile -d followthemoney/i18n
	tx pull --all

clean:
	rm -rf dist build .eggs
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +

namespace:
	python ns/ontology.py https://w3id.org/ftm# docs/ns