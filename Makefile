# ========================
# User-definable variables
# ========================

PYTHON ?= python3
CHECK_BRANCH ?= true
CHECK_DIRTY ?= true
GIT_REMOTE ?= origin
GIT ?= git
SED ?= sed
VENV_DIST_TEST_DIR ?= venv-dist-test

# ==========
# Parameters
# ==========

PROJECT := youpy
REVISION := $(shell git rev-parse HEAD)
DIST_DIR := dist
BUILD_DIR := build
DOC_DIR := doc
RELNOTES_DIR := $(DOC_DIR)/RelNotes
VERSION_FILE := VERSION
VERSION := $(shell cat ${VERSION_FILE})
ifndef VERSION
  $(error not version set ; create the $(VERSION_FILE) file)
endif
TAG = v$(VERSION)
SDIST_PKG_FILE := $(DIST_DIR)/$(PROJECT)-$(VERSION).zip
BDIST_WHEEL_PKG_FILE := $(DIST_DIR)/$(PROJECT)-$(VERSION)-py3-none-any.whl
MANIFEST_FILE := MANIFEST.in
VERSION_PY_FILE := youpy/version.py

# ==========
# Dist rules
# ==========

.DEFAULT_GOAL := dist

include sources.mk


$(MANIFEST_FILE): $(SOURCES) $(GENERATED_SOURCES)
	rm -f $@
	for i in $(SOURCES); do echo "include $$i" >> $@; done

.PHONY: check_branch
check_branch:
	if $(CHECK_BRANCH); then [[ "$$(git branch --show-current)" =~ ^(master)$$ ]]; fi

.PHONY: check_dirty
check_dirty:
	if $(CHECK_DIRTY); then test -z "$$(git status --porcelain)"; fi

$(VERSION_PY_FILE): $(VERSION_PY_FILE).in $(VERSION_FILE) check_dirty check_branch
	$(SED) -e "s/@VERSION@/$(VERSION)/;s/@REVISION@/$(REVISION)/" < $< > $@

PKG_SOURCES := $(VERSION_PY_FILE) $(MANIFEST_FILE)

$(SDIST_PKG_FILE): $(PKG_SOURCES)
	$(PYTHON) setup.py sdist --formats zip
.PHONY: sdist
sdist: $(SDIST_PKG_FILE)

$(BDIST_WHEEL_PKG_FILE): $(PKG_SOURCES)
	$(PYTHON) setup.py bdist_wheel
.PHONY: bdist_wheel
bdist_wheel: $(BDIST_WHEEL_PKG_FILE)

.PHONY: dist
dist: sdist bdist_wheel

.PHONY: test-dist
test-dist: bdist_wheel
	rm -rf "$(VENV_DIST_TEST_DIR)"
	$(PYTHON) -m virtualenv $(VENV_DIST_TEST_DIR)
	(cd "$(VENV_DIST_TEST_DIR)" &&\
	 source bin/activate &&\
	 python -m pip install ../$(BDIST_WHEEL_PKG_FILE) &&\
	 python -m youpy --version &&\
	 python -m youpy.examples.SimpleBasketBall &&\
	 deactivate)
	rm -rf "$(VENV_DIST_TEST_DIR)"

# ==================
# Tag and push rules
# ==================

.PHONY: tag
tag:
	$(GIT) tag -a -F $(RELNOTES_DIR)/$(VERSION).txt $(TAG) HEAD

.PHONY: push-commits
push-commits:
	$(GIT) push origin
.PHONY: push-tags
push-tag: tag
	$(GIT) push origin $(TAG)
.PHONY: push
push: push-commits push-tag

# =============
# Publish rules
# =============

PKG_FILES := $(BDIST_WHEEL_PKG_FILE) $(SDIST_PKG_FILE)

.PHONY: publish
publish: $(PKG_FILES) push
	twine upload -r pypi $(PKG_FILES)

.PHONY: publish-test
publish-test: $(PKG_FILES) push
	twine upload -r pypitest $(PKG_FILES)

# ===========
# clean rules
# ===========

.PHONY: clean
clean:
	rm -rf "$(DIST_DIR)" "$(BUILD_DIR)" $(MANIFEST_FILE) $(VERSION_PY_FILE)

.PHONY: clean-tag
clean-tag:
	$(GIT) tag -d "$(TAG)" || true

.PHONY: clean-version
clean-version:
	rm -f $(VERSION_FILE) $(VERSION_PY_FILE)

.PHONY: clean-all
clean-all: clean clean-tag clean-VERSION

# ==========
# Test rules
# ==========

.PHONY: test
test:
	$(PYTHON) -m unittest discover -s youpy.test

# Delete output file on error.
.DELETE_ON_ERROR:
