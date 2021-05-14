from invoke import task
import jinja2
import yaml
import json
import git
import os.path


#templates = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
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

def gittest(c):
    g = git.Repo().git
    print(str(g.branch("--show-current")))


def gen_npm(c,variant,image,path):

    pkg=c[variant][image].npm
    file='{path}/package.json'.format(path=path,variant=variant,image=image)

    c.run("npm install - -package-lock-only {pkg}".format(pkg=pkg))
    c.run("cp package.json {file}".format(file=file))

def gen_pip(c,variant,image,path):

    pkg=c[variant][image].python
    file='{path}/requirementb.txt'.format(path=path,variant=variant,image=image)

    if not os.path.exists('pyproject.toml'):
        c.run("poetry init -n --python '{python_required}'".format(python_required=c.python.required))

    c.run("poetry config virtualenvb.path .env")
    c.run("poetry config cache-dir .cache")
    c.run("poetry config virtualenvb.in-project true")

    c.run("poetry add -v --lock {pkg}".format(pkg=pkg))
    c.run("poetry export --without-hashes -f requirementb.txt -o {file}".format(file=file))


def get_path(b):
    return os.path.join(*b._keypath)

def mkdir(c,b):

    c.run('mkdir -p {path}'.format(path=get_path(b)))

    # print(path(stage))

    #path = 'stages/{variant}/{image}'.format(variant=variant,image=image)
    #c.run('mkdir -p {path}'.format(path=path))
    #return path       

        
def get_build(b):
    return(b._keypath[1])
templates.filters['build'] = get_build

def get_stage(b):
    return(b._keypath[-1])
templates.filters['stage'] = get_stage

def get_user(b):
    return(b._root.docker.user)
templates.filters['user'] = get_user

def get_repo(b):
    return(b._root.docker.repo)
templates.filters['repo'] = get_repo

def get_version(b):
    return(b._root.version)
templates.filters['version'] = get_version

def get_maintainer(b):
    return(b._root.maintainer)
templates.filters['maintainer'] = get_maintainer

def get_uid(b):
    return(b._root.nb.uid)
templates.filters['uid'] = get_uid

def get_gid(b):
    return(b._root.nb.gid)
templates.filters['gid'] = get_gid

def get_image(b):
    return(b.image)
templates.filters['image'] = get_image

def get_conda(b):
    return(dict(b.conda))
templates.filters['conda'] = get_conda

def get_imagename(b):
    return '-'.join(b._keypath[1:])+'-'+get_version(b)
templates.filters['imagename'] = get_imagename



def gen_apk(c,b):

    pkgs = ' '.join([pkg for pkg in b.apk])
    with open('{path}/alpine.pkg'.format(path=get_path(b)),'w') as file:
        file.write(pkgs+'\n')

def gen_conda(c,b):

    with open(r'{path}/conda.yml'.format(path=get_path(b)), 'w') as file:
        yaml.dump(get_conda(b), file, sort_keys=True, canonical=False, explicit_start=True)



def docker_build(c,b):

    c.run("docker buildx build --progress plain -t {user}/{repo}:{imagename} {path} | tee build-{imagename}.log".format(

        user=get_user(b),
        repo=get_repo(b),  
        imagename=get_imagename(b),
        path=get_path(b)
        ))

def gen_builder(c,b):

    builder=b.builder

    print("Using Builder",builder)

    dockerfile = templates.get_template(builder)
    with open('{path}/Dockerfile'.format(path=get_path(b)),'w') as file:
        file.write(dockerfile.render(b=b))


def builder(c,b):

    print ("Building Images")

    if 'build' in b:
        builder(c,b.build)

    mkdir(c,b)
     
    if 'builder' in b:
        gen_builder(c,b)
    
    if 'apk' in b:
        gen_apk(c,b)

    if 'conda' in b:
        gen_conda(c,b)

    if 'npm' in b:
        gen_npm(c,b)

    if 'pip' in b:
        gen_pip(c,b)

    docker_build(c,b) 


@task()
def build(c):
    "Build all images"

    print("Building images")

    b=c.build['micromamba']['core']
    builder(c,b)

    b=c.build['micromamba']['base']
    builder(c,b)

@task()
def images(c):
    "Show images"

    c.run("docker images")


@task(help={'image': 'Image','version':'Version'})
def bash(c,image='base',version=None):
    "Bash into image"

    if not version:
        version=c.version

    c.run("docker run -it {docker_user}/{docker_repo}:{image}-{version} bash".format(
         docker_user=c.docker.user, docker_repo=c.docker.repo,image=image,version=version),pty=True)


@task(help={'image': 'Image','version':'Version'})
def run(c,image='base',version=None):
    "Run image"

    if not version:
        version=c.version
    c.run("docker run -p 8888:8888 {docker_user}/{docker_repo}:{image}-{version}".format(   
        docker_user=c.docker.user, docker_repo=c.docker.repo,image=image,version=version,), pty=True)


@task()
def r2d(c):
    "Run Dockerfile with repo2docker"

    c.run("docker rmi r2d-microbe",warn=True)
    c.run("jupyter-repo2docker --debug -P --image-name r2d-microbe .".format(
        version=c.version, docker_user=c.docker.user, docker_repo=c.docker.repo), pty=True)


@task()
def readme(c):
    "Update README"

    invoke_list=json.loads(c.run("inv -l --list-format=json",hide=True).stdout)

    readme = templates.get_template("README.j2")
    with open("README.md","w") as file:
        with open("invoke.yaml","r") as invoke_yaml:
            file.write(readme.render(invoke_list=invoke_list,invoke_yaml=invoke_yaml.read()))

@task()
def docker_push(c):
    "Push images to docker hub"

    c.run("docker image push -a {docker_user}/{docker_repo}".format(
        docker_user=c.docker.user, docker_repo=c.docker.repo))


@task(readme)
def docker_pushrm(c):
    "Push README to docker hub"

    c.run("docker pushrm {docker_user}/{docker_repo}".format(docker_user=c.docker.user, docker_repo=c.docker.repo))


@task(readme,docker_push,docker_pushrm)
def push(c):
    "Push changes to git repo and docker hub"

    print("Pushing changes")


@task()
def prune(c):
    "Prune all local docker images"
    c.run("docker system prune -a")


@task()
def test(c):
    #print(dir(c.build.conda))
    #print(c.build.conda.core._keypath[-1])
    #print(c.build.conda.core._root.version)
    #print(c.build.conda._config)
    #print(c.build.micromamba.base.build._keypath)
    #print(c.build.micromamba.base.build._keypath[1])
    #print(c.build.micromamba.base.build._keypath[1:])

    print(get_imagename(c.build.micromamba.base.build))