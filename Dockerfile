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
    && apt-get purge --auto-remove nodejs npm\
    && apt-get install -y virtualenv python3 curl\
    #Plotly dependencies
    && apt-get install -y ghostscript build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info libgconf2-4\
    && apt-get install -y wget npm nodejs\
    #&& npm install -g electron@6.1.4 orca
    && apt-get install -y --no-install-recommends \
    wget \
    xvfb \
    xauth \
    libgtk2.0-0 \
    libxtst6 \
    libxss1 \
    libgconf-2-4 \
    libnss3 \
    libasound2 && \
    mkdir -p /opt/orca && \
    cd /opt/orca && \
    wget https://github.com/plotly/orca/releases/download/v1.2.1/orca-1.2.1-x86_64.AppImage && \
    chmod +x orca-1.2.1-x86_64.AppImage && \
    ./orca-1.2.1-x86_64.AppImage --appimage-extract && \
    rm orca-1.2.1-x86_64.AppImage && \
    printf '#!/bin/bash \nxvfb-run --auto-servernum --server-args "-screen 0 640x480x24" /opt/orca/squashfs-root/app/orca "$@"' > /usr/bin/orca && \
    chmod +x /usr/bin/orca \
    # Add user
    && useradd -M -u 1000 -s /bin/sh -d ${USER_HOME} ${USER_NAME} \
    && mkdir -p ${USER_HOME} \
    && chown -R 1000:1000 ${USER_HOME}
RUN set -x\
    && apt-get update\
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --fix-missing xorg openbox
# Download orca AppImage, extract it, and make it executable under xvfb
RUN apt-get install --yes xvfb xauth
RUN wget https://github.com/plotly/orca/releases/download/v1.1.1/orca-1.1.1-x86_64.AppImage -P /home
RUN chmod 777 /home/orca-1.1.1-x86_64.AppImage 

# To avoid the need for FUSE, extract the AppImage into a directory (name squashfs-root by default)
RUN cd /home && /home/orca-1.1.1-x86_64.AppImage --appimage-extract
RUN printf '#!/bin/bash \nxvfb-run --auto-servernum --server-args "-screen 0 640x480x24" /home/squashfs-root/app/orca "$@"' > /usr/bin/orca
RUN chmod 777 /usr/bin/orca
RUN chmod -R 777 /home/squashfs-root/
USER ${USER_NAME}

RUN set -x \
    # Create virtualenv
    && virtualenv -p python3 venv \
    #Downloads the hacked streamlit
    && wget https://github.com/ImpulsoGov/streamlit/raw/develop/builds/streamlit-0.60.0-py2.py3-none-any.whl \
    # Install Python libs
    && . venv/bin/activate \
    && pip install --default-timeout=100 future \
    && pip install --upgrade -r requirements.txt \
    # Install streamlit
    && pip install --no-cache-dir streamlit-0.60.0-py2.py3-none-any.whl\
    && python -m ipykernel install --user --name=venv

ADD . ${USER_HOME}

USER root

RUN set -x \
    # Set permissions
    && chmod +x setup.sh entrypoint.sh

USER ${USER_NAME}

EXPOSE ${STREAMLIT_SERVER_PORT}

CMD ["./entrypoint.sh"]
