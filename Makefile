DEST=~/install/lib64/python2.7/site-packages/

install: pyLabCalc.py
	mkdir -p $(DEST)
	install $< $(DEST)

