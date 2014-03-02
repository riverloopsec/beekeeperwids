install:
	sudo python setup.py --quiet install
	
clean:
	sudo python setup.py clean
	sudo rm -rf build/ dist/ *.egg-info
	find . -iname *~ -delete

