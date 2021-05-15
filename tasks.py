from invoke import task
import jinja2
import yaml
import json
import git
import os.path
import sys

templates = jinja2.Environment(loader=jinja2.FileSystemLoader("builder"))


@task()
def clean(c):
    "Clean generated files"

    c.run("rm -f pyproject.toml package*.json Dockerfile README.md build-*",warn=True)
    c.run("rm -rf  build",warn=True)


@task()
def clean_docker(c):
    "Clean dangling docker images"

    c.run('docker rmi $(docker images -f "dangling=true" -q)',warn=True)


def get_path(b):
    return os.path.join(*b._keypath)

def mkdir(c,b):

    c.run('mkdir -p {path}'.format(path=get_path(b)))
        
def get_build(b):
    return(b._keypath[1])
templates.filters['build'] = get_build

def get_stage(b):
    return(b._keypath[-1])
templates.filters['stage'] = get_stage

def get_user(b):
    return(b._root.user)
templates.filters['user'] = get_user

def get_uid(b):
    return(b._root.uid)
templates.filters['uid'] = get_uid

def get_gid(b):
    return(b._root.gid)
templates.filters['gid'] = get_gid

def get_docker_user(b):
    return(b._root.docker.user)
templates.filters['docker_user'] = get_docker_user

def get_docker_repo(b):
    return(b._root.docker.repo)
templates.filters['docker_repo'] = get_docker_repo

def get_version(b):
    return(b._root.version)
templates.filters['version'] = get_version

def get_python_version(b):
    return(b._root.python.version)
templates.filters['python_version'] = get_python_version

def get_maintainer(b):
    return(b._root.maintainer)
templates.filters['maintainer'] = get_maintainer

def get_image(b):
    return(b.image)
templates.filters['image'] = get_image

def get_conda(b):
    return(dict(b.conda))
templates.filters['conda'] = get_conda

def get_imagename(b):
    return '-'.join(b._keypath[1:])+'-'+get_version(b)
templates.filters['imagename'] = get_imagename

def get_builder(b):
    return(b.builder)
templates.filters['builder)'] = get_builder


def docker_build(c,b):

    c.run("docker buildx build --progress plain --load -t {user}/{repo}:{imagename} {path} | tee build-{imagename}.log".format(
        user=get_docker_user(b),
        repo=get_docker_repo(b),  
        imagename=get_imagename(b),
        path=get_path(b)
        ))

def gen_apk(c,b):

    pkgs = ' '.join([pkg for pkg in b.apk])
    with open('{path}/alpine.pkg'.format(path=get_path(b)),'w') as file:
        file.write(pkgs+'\n')

def gen_conda(c,b):

    with open(r'{path}/conda.yml'.format(path=get_path(b)), 'w') as file:
        yaml.dump(get_conda(b), file, sort_keys=True, canonical=False, explicit_start=True)


def gen_npm(c,b):

    pkgs = ' '.join([pkg for pkg in b.npm])
    file='{path}/package.json'.format(path=get_path(b))

    c.run("npm install - -package-lock-only {pkgs}".format(pkgs=pkgs))
    c.run("cp package.json {file}".format(file=file))


def gen_pip(c,b):

    pkgs = ' '.join([pkg for pkg in b.pip])
    file='{path}/requirements.txt'.format(path=get_path(b))

    if not os.path.exists('pyproject.toml'):
        c.run("poetry init -n --python '{python_required}'".format(python_required=c.python.required))

    c.run("poetry config virtualenvs.path .env")
    c.run("poetry config cache-dir .cache")
    c.run("poetry config virtualenvs.in-project true")

    c.run("poetry add -v --lock {pkgs}".format(pkgs=pkgs))
    c.run("poetry export --without-hashes -f requirements.txt -o {file}".format(file=file))


def gen_builder(c,b):
    dockerfile = templates.get_template(get_builder(b))
    with open('{path}/Dockerfile'.format(path=get_path(b)),'w') as file:
        file.write(dockerfile.render(b=b))


def builder(c,b):

    print("Building",get_imagename(b))

    if 'build' in b:
        builder(c,b.build)

    mkdir(c,b)
     
    if 'builder' in b:
        gen_builder(c,b)
    else:
        sys.exit("ERROR: No builder defined for {path}".format(path=get_path(b)))    
    
    if 'apk' in b:
        gen_apk(c,b)

    if 'npm' in b:
        gen_npm(c,b)

    if 'conda' in b:
        gen_conda(c,b)

    if 'pip' in b:
        gen_pip(c,b)

    docker_build(c,b) 


@task()
def images(c):
    "Show images"

    c.run("docker images")

@task()
def readme(c):
    "Update README"

    invoke_list=json.loads(c.run("inv -l --list-format=json",hide=True).stdout)

    readme = templates.get_template("README")
    with open("README.md","w") as file:
        with open("invoke.yaml","r") as invoke_yaml:
            file.write(readme.render(invoke_list=invoke_list,invoke_yaml=invoke_yaml.read()))

@task(clean,readme)
def build(c,build=None,image=None):
    "Build image(s)"

    if not build:
        build=c.build
    else:
        build=[build]

    for b in build:
        if not image:
            for i in c.build[b]:
                builder(c,c.build[b][i])
        else:
            builder(c,c.build[b][image])

@task(help={'image': 'Image','version':'Version'})
def bash(c,build=None,image=None,user=None,repo=None,version=None):
    "Bash into image"

    if not build:
        sys.exit("Please set build with -b")    

    if not image:
        sys.exit("Please set image with -i")    

    if not user:
        user=c.docker.user

    if not repo:
        repo=c.docker.repo

    if not version:
        version=c.version

    c.run("docker run -it {user}/{repo}:{build}-{image}-{version} bash".format(
        user=user,
        repo=repo,
        build=build,
        image=image,
        version=version        
        ), pty=True)


@task(help={'image': 'Image','version':'Version'})
def run(c,build=None,image=None,user=None,repo=None,version=None):
    "Run image"

    if not build:
        sys.exit("Please set build with -b")    

    if not image:
        sys.exit("Please set image with -i")    

    if not user:
        user=c.docker.user

    if not repo:
        repo=c.docker.repo

    if not version:
        version=c.version

    c.run("docker run -p 8888:8888  {user}/{repo}:{build}-{image}-{version}".format(
        user=user,
        repo=repo,
        build=build,
        image=image,
        version=version        
        ), pty=True)


@task()
def r2d(c):
    "Run image with repo2docker"

    c.run("docker rmi r2d-microbe",warn=True)
    c.run("jupyter-repo2docker --debug -P --image-name r2d-microbe .".format(
        version=c.version, docker_user=c.docker.user, docker_repo=c.docker.repo), pty=True)


@task(build)
def docker_push(c):
    "Push images to docker hub"

    c.run("docker image push -a {docker_user}/{docker_repo}".format(
        docker_user=c.docker.user, docker_repo=c.docker.repo))


@task(readme)
def docker_pushrm(c):
    "Push README to docker hub"

    c.run("docker pushrm {docker_user}/{docker_repo}".format(docker_user=c.docker.user, docker_repo=c.docker.repo))


@task(build,readme,docker_push,docker_pushrm)
def push(c):
    "Push images to docker hub"

    print("Pushing Images")


@task()
def prune(c):
    "Prune all local docker images"
    c.run("docker system prune -a")


def gittest(c):
    g = git.Repo().git
    print(str(g.branch("--show-current")))

@task()
def test(c):
    print(get_imagename(c.build.micromamba.base.build))