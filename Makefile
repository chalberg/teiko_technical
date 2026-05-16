.PHONY: setup pipeline dashboard

setup:
	pip install -r requirements.txt

pipeline:
	mkdir -p exports
	python load_data.py
	python pipeline.py

dashboard:
	streamlit run dashboard.py
