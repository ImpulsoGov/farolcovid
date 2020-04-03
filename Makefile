
create-env:
	virtualenv venv
	source venv/bin/activate; pip3 install --upgrade -r requirements.txt