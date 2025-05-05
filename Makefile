SHELL := /bin/bash
VERSION := $(shell cd aiopioneer ; python3 - <<< "import const ; print(const.VERSION)" )

.PHONY: sdist
default: usage

usage:
	@echo "usage: make [ dist | main ]"

sdist:
	@echo Creating sdist for version $(VERSION)
	-rm dist/*
	python3 -m build

dist: sdist
	python3 -m twine upload dist/*

main:
	@echo Merging dev to main for version $(VERSION)
	git checkout main
	git merge --ff-only dev
	git push
	git checkout dev

local:
	@echo Pushing dev and main to local for version $(VERSION)
	git push local dev
	git push local main

release-log:
	git --no-pager log main..HEAD --oneline --no-merges --format="%H%n%B%n---"
