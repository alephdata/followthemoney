
test:
	echo "nah"

upload: clean
	python setup.py sdist bdist_wheel
	twine upload dist/*

clean:
	rm -rf dist build
