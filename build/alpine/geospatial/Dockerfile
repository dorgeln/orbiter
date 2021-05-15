#syntax=docker/dockerfile:1.2

FROM dorgeln/microbe:alpine-geospatial-build-0.0.20 as build
FROM dorgeln/microbe:alpine-core-0.0.20


USER root
COPY alpine.pkg alpine.pkg
RUN --mount=type=cache,id=apk-cache,target=/etc/apk/cache \
    PKG=`cat alpine.pkg` && echo "Installing ${PKG}" && apk add ${PKG}






COPY --chown= --from=build /env  /env

WORKDIR ${HOME}
USER jovyan

CMD ["jupyter", "lab", "--ip", "0.0.0.0","--no-browser","--NotebookApp.token=''","--NotebookApp.password=''"]
EXPOSE 8888