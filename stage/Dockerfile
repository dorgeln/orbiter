#syntax=docker/dockerfile:1.2

FROM dorgeln/microbe:core-0.0.20 as core

LABEL maintainer="Andreas Trawoeger <atrawog@dorgeln.org>"

COPY base.yml base.yml

RUN --mount=type=cache,id=mamba-pkgs,target=/env/mamba/pkgs,uid=1000,gid=100 \
    --mount=type=cache,id=mamba-meta,target=/env/mamba/conda-meta,uid=1000,gid=100 \
    ${MAMBA_EXE} install -y -n base -f base.yml
