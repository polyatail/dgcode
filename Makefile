lint:
	flake8 audioserver/ tests/
	black -l 100 --check audioserver/ tests/
	pydocstyle --convention=numpy --add-ignore=D100,D101,D102,D103,D104,D105,D202 audioserver/ tests/
format:
	black -l 100 audioserver/ tests/
test:
	py.test -v -W ignore::DeprecationWarning tests/
update_deps:
	pip-compile --generate-hashes
