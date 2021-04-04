STATIC_DIRS="entropy_encoders"
export PYTHONPATH=.
test: clean
	pytest 
	for dir in $(STATIC_DIRS); do \
		find $$dir -name '*py' | xargs mypy ; \
	done

clean: 
	find . -name '__pycache__' -type d | xargs rm -rf 
	find . -name '.*_cache' -type d | xargs rm -rf 
	find . -name '.hypothesis' -type d | xargs rm -rf 
