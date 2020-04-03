
create-env:
	virtualenv venv
	source venv/bin/activate; \
			pip3 install --upgrade -r requirements.txt; \
			python -m ipykernel install --user --name=venv

update-env:
	source venv/bin/activate; \
			pip3 install --upgrade -r requirements.txt;

serve:
	source venv/bin/activate; cd src; streamlit run app.py