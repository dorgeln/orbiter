# microbe
Jupyter Lab micro image

# Tasks

Microbe includes the following [Invoke](http://www.pyinvoke.org/) tasks to help with generating and publishing images.

| Task | Help |
| --- | --- |
| bash | Bash into image |
| build | Build all images |
| build-microm | Build microm images |
| clean | Clean dangling docker images and generated files |
| docker-push | Push images to docker hub |
| docker-pushrm | Push README to docker hub |
| images | Show images |
| prune | Prune all local docker images |
| push | Push changes to git repo and docker hub |
| r2d | Run Dockerfile with repo2docker |
| readme | Update README |
| run | Run image |


# Configuration 

All microbe configuration is done in invoke.yaml. 

```
version: 0.0.20
maintainer: Andreas Trawoeger <atrawog@dorgeln.org>

docker:
  user: dorgeln
  repo: microbe


nb:
  user: jovyan
  uid: 1000
  gid: 100

microm:
  name: base
  alpine:
    from: frolvlad/alpine-glibc
    pkg: bash tar bzip2 curl sudo git

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


debug: true
run:
  echo: true


```

