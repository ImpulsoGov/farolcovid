IMAGE_TAG=impulsogov/simulacovid

UNAME := $(shell uname)
ifeq ($(UNAME), Linux)
SHELL := /bin/bash
else
SHELL := /bin/sh
endif

# Python
create-env:
	virtualenv venv
	wget https://github.com/ImpulsoGov/streamlit/raw/develop/builds/streamlit-0.60.0-py2.py3-none-any.whl \
	source venv/bin/activate; \
			pip3 install --upgrade -r requirements.txt; \
			pip3 install streamlit-0.60.0-py2.py3-none-any.whl;\
			python3 -m ipykernel install --user --name=venv

create-env-analysis:
	virtualenv venvanalysis
	wget https://github.com/ImpulsoGov/streamlit/raw/develop/builds/streamlit-0.60.0-py2.py3-none-any.whl \
	source venvanalysis/bin/activate; \
			pip3 install --upgrade -r requirements-analysis.txt; \
			pip3 install streamlit-0.60.0-py2.py3-none-any.whl;\
			python3 -m ipykernel install --user --name=venvanalysis

update-env:
	source venv/bin/activate; \
			pip3 install --upgrade -r requirements.txt;

serve:
	source venv/bin/activate; cd src; export IS_LOCAL=FALSE; streamlit run farolcovid.py

serve-local:
	source venv/bin/activate; cd src; export IS_LOCAL=TRUE; streamlit run farolcovid.py

# Docker
docker-build:
	docker build -t $(IMAGE_TAG) .

docker-run:
	docker run -d --restart=unless-stopped -p 80:8501 $(IMAGE_TAG)

docker-build-run: docker-build docker-run

docker-shell:
	docker run --rm -it \
		--entrypoint "/bin/bash" \
		$(IMAGE_TAG)

docker-heroku-test: docker-build
	docker run -it --rm \
		-e PORT=8080 \
		-p 8080:8080 \
		$(IMAGE_TAG)
