SHELL := /bin/bash
VERSION := $(shell cd aiopioneer ; python3 - <<< "import const ; print(const.VERSION)" )

.PHONY: sdist
default: usage

usage:
	@echo "usage: make [ dist | main ]"

sdist:
	@echo Creating sdist for version $(VERSION)
	-rm dist/*
	python setup.py sdist

dist: sdist
	python -m twine upload dist/*

main:
	@echo Pushing dev to main for version $(VERSION)
	git checkout main
	git merge --ff-only dev
	git push
	git checkout dev
