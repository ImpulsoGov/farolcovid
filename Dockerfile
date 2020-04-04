FROM ubuntu:18.04

ENV USER_HOME=/app \
    USER_NAME=parsoid \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

WORKDIR ${USER_HOME}

ADD ./requirements.txt ${USER_HOME}/

RUN set -x \
    # Install OS libs
    && apt-get update \
    && apt-get install -y virtualenv python3 \
    # Add user
    && useradd -M -u 1000 -s /bin/sh ${USER_NAME} \
    # Create virtualenv
    && virtualenv -p python3 venv \
    # Install Python libs
	&& . venv/bin/activate \
    && pip install --upgrade -r requirements.txt \
    && python -m ipykernel install --user --name=venv

ADD . ${USER_HOME}

RUN set -x \
    # Set permissions
    && chmod +x setup.sh entrypoint.sh

EXPOSE 8501

ENTRYPOINT ["./entrypoint.sh"]
