README.md: README.md.t
	expand-macros.py README.md.t README.md

install:
	python setup.py install
