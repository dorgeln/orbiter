FROM dorgeln/orbiter:alpine-geospatial-0.0.21
ARG NB_USER=jovyan
ARG NB_UID=1000 
COPY . ${HOME}
USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}