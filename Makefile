PYTHON = python3
CONFIG = config.txt

install:
	$(PYTHON) -m pip install -e .

run:
	$(PYTHON) a_maze_ing.py $(CONFIG)

gui:
	$(PYTHON) gui.py $(CONFIG)

debug:
	$(PYTHON) -m pdb a_maze_ing.py $(CONFIG)

clean:
	rm -rf __pycache__ .mypy_cache *.pyc *.whl dist build *.egg-info

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

.PHONY: install run gui debug clean lint lint-strict