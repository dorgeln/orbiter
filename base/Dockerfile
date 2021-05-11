#syntax=docker/dockerfile:1.2

FROM dorgeln/microbe:stage-0.0.20 as stage

RUN find /env -name "*.pyc" -exec rm -f {} \; && \
    find /env -name "*.pyx" -exec rm -f {} \; && \
    find /env -name '*.a' -exec rm -f {} \; && \
    find /env -name '__pycache__' -type d -exec rm -rf '{}' '+'


FROM dorgeln/microbe:core-0.0.20 as core

LABEL maintainer="Andreas Trawoeger <atrawog@dorgeln.org>"

COPY --chown=${NB_USER} --from=stage /env  ${ENV_ROOT}

WORKDIR ${HOME}
CMD ["jupyter", "lab", "--ip", "0.0.0.0","--no-browser","--NotebookApp.token=''","--NotebookApp.password=''"]
EXPOSE 8888