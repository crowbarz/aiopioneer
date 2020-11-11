.PHONY: sdist
sdist:
	-rm dist/*
	python setup.py sdist bdist_wheel

dist: sdist
	python -m twine upload dist/*
