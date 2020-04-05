IMAGE_TAG=impulsogov/simulacovid

# Python
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

# Docker
docker-build:
	docker build -t $(IMAGE_TAG) .

docker-run:
	docker run --rm -p 8501:8501 $(IMAGE_TAG)

docker-build-run: docker-build docker-run

docker-shell:
	docker run --rm -it \
		--entrypoint "/bin/bash" \
		$(IMAGE_TAG)
