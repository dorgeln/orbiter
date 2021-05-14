#syntax=docker/dockerfile:1.2

FROM dorgeln/microbe:pip-core-0.0.20
LABEL maintainer="Andreas Trawoeger <atrawog@dorgeln.org>"


COPY alpine.pkg alpine.pkg
RUN PKG=`cat alpine.pkg` && echo "Installing ${PKG}" &&  sudo apk add --no-cache ${PKG}

RUN echo "Installing Python-${PYTHON_VERSION}" && pyenv install ${PYTHON_VERSION} && pyenv global ${PYTHON_VERSION}
RUN pip install -U  pip -U setuptools -U wheel -U cython-setuptools

WORKDIR ${NPM_DIR}
COPY --chown=${NB_USER} package.json  ${NPM_DIR}/package.json
RUN npm install --prefix ${NPM_DIR} && npm cache clean --force

WORKDIR ${PYENV_ROOT}
COPY --chown=${NB_USER} requirements.txt requirements.txt
RUN --mount=type=cache,id=pip-cache,target=/build/cache,uid=1000,gid=100 \
    --mount=type=cache,id=pip-tmp,target=/build/tmp,uid=1000,gid=100 \  
    pip install -r requirements.txt

# RUN jupyter serverextension enable --sys-prefix nbgitpuller  && jupyter serverextension enable --sys-prefix jupyter_server_proxy && python -m sshkernel install --sys-prefix && python -m bash_kernel.install --sys-prefix  && jupyter serverextension enable --sys-prefix sshkernel && jupyter lab clean  -y && npm cache clean --force

WORKDIR ${HOME}