#syntax=docker/dockerfile:1.2

FROM frolvlad/alpine-glibc
ARG NB_USER=jovyan
ARG NB_UID=1000
ARG NB_GID=100

LABEL maintainer="Andreas Trawöger <atrawog@dorgeln.org>"

COPY alpine.pkg alpine.pkg
RUN PKG=`cat alpine.pkg` && echo "Installing ${PKG}" &&  apk add --no-cache ${PKG}

RUN adduser --disabled-password  -u ${NB_UID} -G users ${NB_USER} && \
    addgroup -g ${NB_UID}  ${NB_USER} && \
    adduser ${NB_USER} ${NB_USER} && \
    adduser ${NB_USER} wheel

RUN echo '%wheel ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/wheel && chmod 0440 /etc/sudoers.d/wheel
RUN sed -i "s/^export PATH=/#export PATH=L/g" /etc/profile && rm /etc/profile.d/locale.sh

ENV ENV_ROOT="/env"
ENV LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8 \
    SHELL=/bin/bash \
    NB_USER=${NB_USER} \
    NB_UID=${NB_UID} \
    NB_GID=${NB_GID} \
    JUPYTER_ENABLE_LAB=yes \
    USER=${NB_USER} \
    HOME=/home/${NB_USER} \
    MAMBA_EXE=${ENV_ROOT}/bin/micromamba \
    MAMBA_ROOT_PREFIX=${ENV_ROOT}/mamba
ENV PATH=${MAMBA_ROOT_PREFIX}/bin:${ENV_ROOT}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

RUN mkdir -p ${ENV_ROOT}  && chown ${NB_USER}.${NB_GID} -R ${ENV_ROOT} 

USER ${NB_USER}
WORKDIR ${ENV_ROOT}

RUN curl -L https://micromamba.snakepit.net/api/micromamba/linux-64/0.11.3 | tar -xj -C /env bin/micromamba

RUN ${MAMBA_EXE} create -p ${MAMBA_ROOT_PREFIX}
