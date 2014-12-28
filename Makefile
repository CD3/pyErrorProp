DEST=~/install/lib64/python2.7/site-packages/

install: pyLabCalc.py
	install -d $(DEST)
	install $< $(DEST)
	install pyErrorProp/pyErrorProp.py $(DEST)

