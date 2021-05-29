FROM dorgeln/orbiter:micromamba-geospatial-0.1.1
ARG NB_USER=jovyan
ARG NB_UID=1000 
COPY . ${HOME}
USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}