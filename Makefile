.PHONY: dist
dist:
	python setup.py sdist bdist_wheel
	python -m twine upload dist/*
	rm dist/*
