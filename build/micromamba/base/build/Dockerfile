#syntax=docker/dockerfile:1.2

FROM dorgeln/microbe:micromamba-core-0.0.20

LABEL maintainer="Andreas Trawoeger <atrawog@dorgeln.org>"

COPY conda.yml conda.yml

RUN --mount=type=cache,id=mamba-pkgs,target=/env/mamba/pkgs,uid=1000,gid=100 \
    ${MAMBA_EXE} install -y -n base -f conda.yml



