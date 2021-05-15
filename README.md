# microbe
Jupyter Lab micro image

# Tasks

Microbe includes the following [Invoke](http://www.pyinvoke.org/) tasks to help with generating and publishing images.

| Task | Help |
| --- | --- |
| bash | Bash into image |
| build | Build image(s) |
| clean | Clean generated files |
| clean-docker | Clean dangling docker images |
| docker-push | Push images to docker hub |
| docker-pushrm | Push README to docker hub |
| images | Show images |
| prune | Prune all local docker images |
| push | Push images to docker hub |
| r2d | Run Dockerfile with repo2docker |
| readme | Update README |
| run | Run image |
| test | None |


# Configuration 

All microbe configuration is done in invoke.yaml. 

```
version: 0.0.20
maintainer: Andreas Trawoeger <atrawog@dorgeln.org>
user: jovyan
uid: 1000
gid: 100


docker:
  user: dorgeln
  repo: microbe

python:
  version: 3.8.8
  required: ">=3.8,<3.9"

build:
  micromamba:
    core:
      image: frolvlad/alpine-glibc
      builder: micromamba_core

      apk:
        - bash 
        - tar
        - bzip2 
        - curl 
        - sudo
        - git

    base:
      image: core   
      builder: micromamba_deploy

      build:
        image: core 
        builder: micromamba_builder
        conda:
          name: base
          channels:
            - conda-forge
          dependencies:
            - python=3.8 
            - numpy
            - pandas
            - jupyterlab
            - jupyter-server-proxy
            - jupyterlab-spellchecker
            - jupyterlab-git
            - altair
            - altair_saver
            - nbgitpuller
            - matplotlib
            - cython
            - bash_kernel

    full:
      image: core   
      builder: micromamba_deploy

      build:
        image: base-build 
        builder: micromamba_builder
        conda:
          name: base
          channels:
            - conda-forge
          dependencies:
            - intake
            - intake-stac
            - sat-search
            - fiona 
            - shapely
            - pyproj
            - rtree
            - geopandas
            - rasterio
            - geopy
            - xarray
            - dvc
            - jupyter-book
            - h5py
            - netcdf4
            - cysgp4
            - asciinema
            - Pillow


  alpine:
    core:
      image: alpine:20210212
      builder: pip_core
      apk:
        - sudo 
        - bash 
        - curl 
        - git
        - git-lfs
        - ttf-liberation
        - nodejs
        - npm
        - gettext
        - openblas
        - openblas-ilp64
        - lapack
        - openssl
        - tar
        - zlib
        - ncurses
        - bzip2
        - xz
        - cairo
        - pango
        - openjpeg
        - tiff
        - freetype
        - pixman
        - zeromq 

    base:
      image: core   
      builder: pip_deploy
      apk:
        - neofetch
        - libffi
        - libzmq
        - sqlite-libs
        - libffi
        - librsvg
        - giflib
        - libpng libxml2
        - libnsl
        - libxslt
        - libtirpc
        - libjpeg-turbo
        - libwebp
        - libimagequant 

      build:
        image: core 
        builder: pip_builder
        apk: 
          - build-base
          - alpine-sdk
          - g++
          - expat-dev
          - openssl-dev
          - zlib-dev
          - ncurses-dev
          - bzip2-dev
          - xz-dev
          - sqlite-dev
          - libffi-dev
          - linux-headers
          - readline-dev
          - pixman-dev
          - cairo-dev
          - pango-dev
          - openjpeg-dev
          - librsvg-dev
          - giflib-dev
          - libpng-dev
          - openblas-dev
          - lapack-dev
          - gfortran
          - libxml2-dev
          - zeromq-dev
          - gnupg
          - expat-dev
          - gdbm-dev
          - libnsl-dev
          - libtirpc-dev
          - pax-utils
          - util-linux-dev
          - xz-dev
          - zlib-dev
          - libjpeg-turbo-dev
          - tiff-dev
          - libwebp-dev
          - libimagequant-dev
          - lcms2-dev
          - cargo
          - libxml2-dev
          - libxslt-dev
          - boost-dev 
        npm:
          - vega-lite
          - vega-cli
          - canvas
          - configurable-http-proxy
        pip:
          - numpy
          - pandas
          - jupyterlab
          - altair
          - altair_saver
          - nbgitpuller
          - jupyter-server-proxy
          - jupyterlab-spellchecker
          - matplotlib
          - jupyterlab-git
          - cython

    full:
      image: core 
      builder: pip_deploy

      apk: 
        - neofetch
        - libffi
        - libzmq
        - sqlite-libs
        - libffi
        - librsvg
        - giflib
        - libpng
        - libxml2
        - libnsl
        - libxslt
        - libtirpc
        - libjpeg-turbo
        - libwebp
        - libimagequant
        - geos
        - gdal
        - gdal-tools
        - proj
        - proj-util
        - libgit2


      build:
        image: base-build 
        builder: pip_builder
        apk: 
          - geos-dev
          - proj-dev
          - hdf5-dev
          - netcdf-dev
          - gdal-dev gdal-tools
          - proj-dev
          - proj-util
          - geos-dev
          - libgit2-dev

        pip: 
          - intake
          - intake-stac
          - sat-search
          - fiona shapely
          - pyproj
          - rtree
          - geopandas
          - rasterio
          - geopy
          - xarray
          - dvc
          - jupyter-book
          - h5py
          - netcdf4
          - cysgp4
          - asciinema
          - lolcat
          - ttygif
          - Pillow
          - nbdev



debug: true
run:
  echo: true


```