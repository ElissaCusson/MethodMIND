install_local:
	pip install -e .
database_local:
	python MethodMINDpackage/train/create_db.py
run_website_local:
	streamlit run MethodMINDpackage/deployment/website.py
