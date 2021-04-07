FROM ubuntu:18.04

ENV USER_NAME=ubuntu \
    USER_HOME=/home/ubuntu \
    # Set clock and location
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    # Special Streamlit variables
    STREAMLIT_GLOBAL_DEVELOPMENT_MODE=False \
    STREAMLIT_GLOBAL_LOG_LEVEL=warning \
    STREAMLIT_GLOBAL_METRICS=True \
    STREAMLIT_BROWSER_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8501 \
    INLOCO_CITIES_ROUTE="" \ 
    INLOCO_STATES_ROUTE="" \ 
    AMPLITUDE_KEY=""

WORKDIR ${USER_HOME}

ADD ./requirements.txt ${USER_HOME}/
RUN set -x \
    # Install OS libs
    && apt-get update \
    && apt-get install -y virtualenv python3 curl \
    && apt-get install -y wget\
    # Add user
    && useradd -M -u 1000 -s /bin/sh -d ${USER_HOME} ${USER_NAME} \
    && mkdir -p ${USER_HOME} \
    && chown -R 1000:1000 ${USER_HOME}
USER ${USER_NAME}
RUN set -x \
    # Create virtualenv
    && virtualenv -p python3 venv \
    #Downloads the hacked streamlit
    && wget https://github.com/ImpulsoGov/streamlitlastversion/raw/main/builds/streamlit-0.70.0-py2.py3-none-any.whl \
    # Install Python libs
    && . venv/bin/activate \
    && pip install --default-timeout=100 future \
    && pip install --upgrade -r requirements.txt \
    # Install streamlit
    && pip install --no-cache-dir streamlit-0.70.0-py2.py3-none-any.whl\
    && python -m ipykernel install --user --name=venv
ADD . ${USER_HOME}
USER root
RUN set -x \
    # Set permissions
    && chmod +x setup.sh entrypoint.sh
USER ${USER_NAME}
EXPOSE ${STREAMLIT_SERVER_PORT}
CMD ["./entrypoint.sh"]