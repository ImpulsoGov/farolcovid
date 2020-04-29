IMAGE_TAG=impulsogov/simulacovid

# Python
create-env:
	virtualenv venv
	source venv/bin/activate; \
			pip3 install --upgrade -r requirements.txt; \
			python -m ipykernel install --user --name=venv

create-env-analysis:
	virtualenv venvanalysis
	source venvanalysis/bin/activate; \
			pip3 install --upgrade -r requirements-analysis.txt; \
			python -m ipykernel install --user --name=venvanalysis

update-env:
	source venv/bin/activate; \
			pip3 install --upgrade -r requirements.txt;

serve:
	source venv/bin/activate; cd src; export IS_LOCAL=FALSE; streamlit run app.py

serve-local:
	source venv/bin/activate; cd src; export IS_LOCAL=TRUE; streamlit run app.py

# Docker
docker-build:
	docker build -t $(IMAGE_TAG) .

docker-run:
	docker run -it --rm -p 8501:8501 $(IMAGE_TAG)

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
