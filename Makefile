build:
	# Replace live-config.py check
	sed -i "s/live_config = locate('live-config.config')/live_config = {}/g" ./jesse/jesse/__init__.py
	docker build -t screoff/jesse:0.21.3 jesse
	docker build -t screoff/live_jesse:0.21.3 jesse_live

.PHONY: build
