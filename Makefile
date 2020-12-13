.PHONY: sdist
sdist:
	-rm dist/*
	python setup.py sdist

dist: sdist
	python -m twine upload dist/*
