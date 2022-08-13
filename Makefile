.PHONY: all build


all: test lint demos

test: build
	@pytest --cov=rubato --cov-report term-missing tests -s

test-rub: build
	@pytest -m "rub" --cov=rubato --cov-report term-missing tests -s

test-sdl: build
	@pytest -m "sdl or rub" --cov=rubato --cov-report term-missing tests -s

test-no-rub: build
	@pytest -m "not rub" --cov=rubato --cov-report term-missing tests

test-no-sdl: build
	@pytest -m "not sdl and not rub" --cov=rubato --cov-report term-missing tests -s

test-indiv: build
	@pytest tests -k "$(test)"

lint:
	@echo "Linting Code"
	@pylint rubato

demos:
	@cd demo && ./_run_all.sh

SPHINXBUILD   ?= sphinx
SOURCEDIR     = source
BUILDDIR      = ./build/html
LIVEBUILDDIR  = ./build/_html
BUILDER          = dirhtml

docs-save: docs-clear delete-build
	@cd docs && python -m $(SPHINXBUILD) -W --keep-going -T -q -b $(BUILDER) "$(SOURCEDIR)" "$(BUILDDIR)"
	@cd docs && touch build/html/_modules/robots.txt

docs-test: docs-clear delete-build
	@cd docs && python -m $(SPHINXBUILD) -b $(BUILDER) "$(SOURCEDIR)" "$(LIVEBUILDDIR)"

docs-live: docs-clear delete-bin
	@bash -c "trap 'make build;echo ctrl+c to exit' SIGINT; (cd docs && sphinx-autobuild "$(SOURCEDIR)" "$(LIVEBUILDDIR)" -b $(BUILDER) $(O) --watch ../rubato)"

docs-clear:
	@cd docs && rm -rf build

build:
	@python setup.py build_ext --inplace

watch:
	@bash ./watchBuild.sh

setup:
	@git submodule update --init --recursive
	@pip install --editable .[dev]
	@pre-commit install -f
	@pre-commit run --all-files
	@python setup.py build_ext --inplace

delete-bin:
	@cd rubato && find . -name "*.pyd" -type f -delete
	@cd rubato && find . -name "*.so" -type f -delete

delete-c:
	@cd rubato && find . -name "*.c" -o -name "*.cpp" -not -name "PixelEditor.cpp" -type f -delete
	@cd rubato && find . -name "*.c" -type f -delete

delete-build: delete-bin delete-c
	@rm -rf build


pypi-build:
	@rm -rf dist
	@python -m build

pypi-publish-wheels:
	@rm -rf dist
	@pip install build twine
	@python -m build
	@python -m twine upload dist/*.whl
