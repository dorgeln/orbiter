#syntax=docker/dockerfile:1.2

FROM dorgeln/microbe:pip-base-build-0.0.20 as build
FROM dorgeln/microbe:pip-core-0.0.20

COPY --chown=${NB_USER} --from=build ${ENV_ROOT} ${ENV_ROOT}
COPY alpine.pkg alpine.pkg
RUN PKG=`cat alpine.pkg` && echo "Installing ${PKG}" &&  sudo apk add --no-cache ${PKG}
COPY --chown=${NB_USER} requirements.txt requirements.txt
RUN pip install -r requirements.txt