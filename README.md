# Orbiter - Jupyter image builder framework

## Quick start

You can try all the images build by Orbiter by picking a Dockerfile from [dockerfile](https://github.com/dorgeln/orbiter/tree/main/dockerfiles) directory and add it to your repository and launch it on [binder](https://mybinder.org).
If you want to have a quick look at how Orbiter builds images go to the [build](https://github.com/dorgeln/orbiter/tree/main/build) dircatory and have a look at the generated Dockerfiles for building the Orbiter images.


## Builders

Orbiter currently includes two different builder templates **micromamba** and **alpine**. Micromamba uses conda-forge as package repository and builds really fast. The alpine builder uses pip and compiles most packages from source which increases build time by a lot, but results in significantly smaller image sizes. Both builders use a build cache and image build time increase dramatically over time.


## Images

The Orbiter default configuration includes definitions for two different image **base** and **geospatial**. Base includes Jupyter Lab and the usual suspects like numpy, pandas,altair, matplotlib, nbgitpuller and jupyter-book. Geospatial includes a lot of additional geospatial related libaries. The geospatial image hasn't seen much testing (yet) and is primarily used to stress test the Orbiter building toolchain.


## Dependencies

Orbiter needs the following dependencies installed locally on your system

* [Docker](https://www.docker.com/)
* [PyInvoke](http://www.pyinvoke.org/)
* [Jinja](https://jinja.palletsprojects.com/en/3.0.x/)
* [Poetry](https://python-poetry.org/) (for pip dependency resolution)
* [npm](https://www.npmjs.com/) (for nodejs dependency resolution)
* [docker-pushrm](https://github.com/christian-korneck/docker-pushrm) (only needed for *inv docker-pushrm*).
* [repo2docker](https://repo2docker.readthedocs.io/) (only needed for *inv r2d*).


## Tasks

Orbiter includes the following [Invoke](http://www.pyinvoke.org/) tasks to automate building and publishing images.

| Task | Help |
| --- | --- |
| inv bash | Bash into image |
| inv build | Build image(s) |
| inv clean | Clean generated files |
| inv docker-clean | Clean dangling docker images |
| inv docker-prune | Prune all docker images |
| inv docker-push | Push images to docker hub |
| inv docker-pushrm | Push README to docker hub |
| inv docker-rmi | Remove all docker images |
| inv images | Show images |
| inv r2d | Run image with repo2docker |
| inv readme | Update README |
| inv run | Run image |


Additional help for the specific task options is available using *inv --help TASKNAME*.


## Configuration 

All orbiter build settings are configured in *invoke.yaml*. 

### Global section

```
# Version and maintainer
version: 0.1.0 
maintainer: Andreas Trawoeger <atrawog@dorgeln.org>

# Notebook user for image
user: jovyan
uid: 1000
gid: 100

# Docker settings
docker:
  repo: dorgeln/orbiter
  mount: book # Local directory used for run task bind mount

# Python settings
# Only used for pip builder
python:
  version: 3.8.8
  required: ">=3.8,<3.9"
```

### Anchors

Definitions can be reused between different build configurations by using Yaml anchors.

```
apk: &alpine_core
  - bash 
  - tar
  - bzip2 
  - curl 
  - sudo
  - git
```

### Build section

Build definitions are recursive and it's possible to configure a single additional build definition for every build.

**Single stage build example**

```
build:
  micromamba:
    core:
      image: frolvlad/alpine-glibc
      builder: micromamba_core

      apk: 
        - *alpine_core
```

This example builds a *micromaba-core* image based on 'frolvlad/alpine-glibc' using the *micromamba_core* builder and the apk package list defined in &alpine_core anchor.

**Multi stage build example**

```
build:
  micromamba:
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
            - jupyter-book
        postbuild:
          - jupyter serverextension enable --sys-prefix nbgitpuller
          - jupyter serverextension enable --sys-prefix jupyter_server_proxy
          - jupyter lab clean  -y
```

This example first builds a *micromamba-base-build* image based on the already build *micromaba-core* image using the *micromamba_builder* with the defined conda specs and then executes the commands defined in the postbuild section.

Once building the *micromamba-base-build* is done. The *micromamba_deploy* builder builds a new image based on *micromaba-core* and copies the build packages from *micromamba-base-build* to the final *micromamba-base* image.

**Multi stage build with stacked builds**

```
build:
  alpine:
    core:
      image: alpine:20210212
      builder: pip_core
      apk:
        - *alpine_core 
    base:
      image: core   
      builder: pip_deploy

      build:
        image: core 
        builder: pip_builder
        apk: 
          - build-base
          - alpine-sdk
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
    geospatial:
      image: core
      builder: pip_deploy

      apk: 
        - geos
        - gdal

      build:
        image: base-build 
        builder: pip_builder
        apk: 
          - geos-dev
          - proj-dev

        pip: 
          - pyproj
```

This configuration builds five images in total. First *alpine-core* is build using the *pip_core* builder. Then the *alpine-base* is generated by the *pip_deploy* builder using the packages build by *alpine-base-build* and the *pip_builder* builder.

Once the *alpine-base* images are finished. *alpine-geospatial* is build by the *pip_deploy* builder using the packages build by *alpine-geospatial-build*. 
With  *alpine-geospatial-build* extending the *alpine-base-build* image using the same *pip_builder* builder template with additional package definitions to the once already build by *alpine-base-build* .
