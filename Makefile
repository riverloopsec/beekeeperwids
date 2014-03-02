install:
	sudo python setup.py install
	
clean:
	sudo python setup.py clean
	sudo rm -rf dist/ *.egg-info
	find . -iname *~ -delete

