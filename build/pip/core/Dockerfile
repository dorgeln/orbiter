#syntax=docker/dockerfile:1.2

FROM alpine:20210212

ENV VERSION=0.0.20
ENV PYTHON_VERSION=3.8.8
ENV DOCKER_USER=dorgeln
ENV DOCKER_REPO=microbe
ENV NB_USER=dorgeln
ENV NB_UID=1000
ENV NB_GID=100

LABEL maintainer="Andreas Trawoeger <atrawog@dorgeln.org>"

COPY alpine.pkg alpine.pkg
RUN PKG=`cat alpine.pkg` && echo "Installing ${PKG}" &&  apk add --no-cache ${PKG}
RUN echo '%wheel ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/wheel && chmod 0440 /etc/sudoers.d/wheel

RUN adduser --disabled-password  -u ${NB_UID} -G users ${NB_USER} && \
    addgroup -g ${NB_UID}  ${NB_USER} && \
    adduser ${NB_USER} ${NB_USER} && \
    adduser ${NB_USER} wheel

ENV ENV_ROOT="/env" 
ENV BUILD_ROOT="/build"
ENV PYENV_ROOT=${ENV_ROOT}/pyenv \
    NPM_DIR=${ENV_ROOT}/npm 
ENV PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${NPM_DIR}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

RUN sed -i "s/^export PATH=/#export PATH=L/g" /etc/profile


ENV PYTHONUNBUFFERED=true \
    PYTHONDONTWRITEBYTECODE=true \
    TMPDIR=${BUILD_ROOT}/tmp \
    PIP_CACHE_DIR=${BUILD_ROOT}/cache \
    PIP_DOWNLOAD_CACHE=${BUILD_ROOT}/download \
    PIP_DISABLE_PIP_VERSION_CHECK=true \
    PIP_DEFAULT_TIMEOUT=300 \
    NODE_PATH=${NPM_DIR}/node_modules \
    NPM_CONFIG_GLOBALCONFIG=${NPM_DIR}/npmrc \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8 \
    SHELL=/bin/bash \
    NB_USER=${NB_USER} \
    NB_UID=${NB_UID} \
    NB_GID=${NB_GID} \
    JUPYTER_ENABLE_LAB=yes \
    PYTHON_VERSION=${PYTHON_VERSION} \
    DOCKER_USER=${DOCKER_USER} \
    DOCKER_REPO=${DOCKER_REPO} \
    VERSION=${VERSION} \
    USER=${NB_USER} \
    HOME=/home/${NB_USER} \
    REPO_DIR=/home/${NB_USER} \
    XDG_CACHE_HOME=/home/${NB_USER}/.cache \
    MAKE_OPTS="-j8" \
    CONFIGURE_OPTS="--enable-shared --enable-optimizations --with-computed-gotos" \
    NPY_USE_BLAS_ILP64=1 \
    MAX_CONCURRENCY=8

RUN mkdir -p ${ENV_ROOT} ${NPM_DIR} ${TMPDIR} ${PIP_CACHE_DIR} ${PIP_DOWNLOAD_CACHE} && chown -R ${NB_USER}.${NB_GID} ${ENV_ROOT} ${BUILD_ROOT}

WORKDIR ${HOME}

USER ${NB_USER}

RUN ln -s ${NODE_PATH}  ${HOME}/node_modules
RUN curl https://pyenv.run | bash

CMD ["jupyter", "lab", "--ip", "0.0.0.0","--no-browser","--NotebookApp.token=''","--NotebookApp.password=''"]
EXPOSE 8888
