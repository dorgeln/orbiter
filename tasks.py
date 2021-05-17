from invoke import task
import jinja2
import yaml
import json
import git
import os.path
import sys
from pathlib import Path
import collections

templates = jinja2.Environment(loader=jinja2.FileSystemLoader("builder"))


def flatten(l):
    """flatten nested list

    Args:
        l: list

    Returns:
        flatten list
    """
    result = []
    for el in l:
        if isinstance(l, collections.Iterable) and not isinstance(el, str):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result

@task()
def clean(c):
    """Clean generated files

    Args:
        c: context
    """
    c.run("rm -f pyproject.toml package*.json README.md build-*",warn=True)
    c.run("rm -rf  build dockerfiles",warn=True)


@task()
def docker_clean(c):
    """Clean dangling docker images
    Args:
        c: context
    """
    c.run('docker rmi $(docker images -f "dangling=true" -q)',warn=True)

def mkdir(c,b):
    """Make directory
    Args:
        b: build context
    """
    c.run('mkdir -p {path}'.format(path=get_path(b)))
  

def get_path(b):
    """Get path for image build
    Args:
        b: build context
    Returns:
        path
    """
    return os.path.join(*b._keypath)

def get_dockerfile_path(b):
    """Get path for final dockerfile
    Args:
        b: build context
    Returns:
        path
    """
    return 'dockerfiles/{build}/{stage}'.format(build=get_build(b),stage='-'.join(b._keypath[2:]))

def get_build(b):
    """Get build name
    Args:
        b: build context
   Returns:
        build name
    """
    return(b._keypath[1])
templates.filters['build'] = get_build

def get_stage(b):
    """Get stage name
    Args:
        b: build context
   Returns:
        stage name
    """
    return(b._keypath[-1])
templates.filters['stage'] = get_stage

def get_user(b):
    """Get user name
    Args:
        b: build context
    """
    return(b._root.user)
templates.filters['user'] = get_user

def get_uid(b):
    """Get UID
    Args:
        b: build context
   Returns:
        uid
    """
    return(b._root.uid)
templates.filters['uid'] = get_uid

def get_gid(b):
    """Get GID
    Args:
        b: build context
   Returns:
        gid
    """
    return(b._root.gid)
templates.filters['gid'] = get_gid

def get_repo(b):
     """Get Docker repo name
    Args:
        b: build context
   Returns:
        repo name
    """
     return(b._root.docker.repo)
templates.filters['repo'] = get_repo

def get_version(b):
    """Get version
    Args:
        b: build context
    Returns:
        version
     """
    return(b._root.version)
templates.filters['version'] = get_version

def get_python_version(b):
    """Get python version
    Args:
        b: build context
    Returns:
        python version
    """
    return(b._root.python.version)
templates.filters['python_version'] = get_python_version

def get_maintainer(b):
    """Get maintainer
    Args:
        b: build context
    Returns:
        maintainer
    """
    return(b._root.maintainer)
templates.filters['maintainer'] = get_maintainer

def get_image(b):
    """Get image
    Args:
        b: build context
    Returns:
        image
    """
    return(b.image)
templates.filters['image'] = get_image

def get_conda(b):
    """Get conda specs
    Args:
        b: build context
    Returns:
        conda specs
    """
    return(dict(b.conda))
templates.filters['conda'] = get_conda

def get_imagename(b):
    """Get image name
    Args:
        b: build context
    Returns:
        image name
    """
    return '-'.join(b._keypath[1:])+'-'+get_version(b)
templates.filters['imagename'] = get_imagename

def get_builder(b):
    """Get image builder
    Args:
        b: build context
    Returns:
        builder
    """
    return(b.builder)
templates.filters['builder'] = get_builder

def get_postbuild(b):
    """Get postbuild commands
    Args:
        b: build context
    Returns:
        command string
    """
    return(' && '.join(flatten(b.postbuild)))
templates.filters['postbuild'] = get_postbuild



def gen_apk(c,b):
    """Generate alpine.pkg file
    Args:
        c: context
        b: build context
    """
    pkgs = ' '.join([pkg for pkg in flatten(b.apk)])
    with open('{path}/alpine.pkg'.format(path=get_path(b)),'w') as file:
        file.write(pkgs+'\n')

def gen_conda(c,b):
    """Generate conda.yml file
    Args:
        c: context
        b: build context
    """
    with open(r'{path}/conda.yml'.format(path=get_path(b)), 'w') as file:
        yaml.dump(get_conda(b), file, sort_keys=True, canonical=False, explicit_start=True)


def gen_npm(c,b):
    """Generate package.json file
    Args:
        c: context
        b: build context
    """
    pkgs = ' '.join([pkg for pkg in flatten(b.npm)])
    file='{path}/package.json'.format(path=get_path(b))

    c.run("npm install - -package-lock-only {pkgs}".format(pkgs=pkgs))
    c.run("cp package.json {file}".format(file=file))


def gen_pip(c,b):
    """Generate requirements.txt file
    Args:
        c: context
        b: build context
    """
    pkgs = ' '.join([pkg for pkg in flatten(b.pip)])
    file='{path}/requirements.txt'.format(path=get_path(b))

    if not os.path.exists('pyproject.toml'):
        c.run("poetry init -n --python '{python_required}'".format(python_required=c.python.required))

    c.run("poetry config virtualenvs.path .env")
    c.run("poetry config cache-dir .cache")
    c.run("poetry config virtualenvs.in-project true")
    c.run("poetry add -v --lock {pkgs}".format(pkgs=pkgs))
    c.run("poetry export --without-hashes -f requirements.txt -o {file}".format(file=file))


def gen_builder(c,b):
    """Generate Dockerfile to build image
    Args:
        c: context
        b: build context
    """
    dockerfile = templates.get_template(get_builder(b))
    with open('{path}/Dockerfile'.format(path=get_path(b)),'w') as file:
        file.write(dockerfile.render(b=b))

def gen_dockerfile(c,b):
    """Generate Dockerfile to run image
    Args:
        c: context
        b: build context
    """   
    dockerfile = templates.get_template('dockerfile')
    path=get_dockerfile_path(b)
    if not 'build' in path and not 'core' in path:
        c.run('mkdir -p {path}'.format(path=path))
        with open('{path}/Dockerfile'.format(path=path),'w') as file:
            file.write(dockerfile.render(b=b))


def builder(c,b):
    """Image builder
    Args:
        c: context
        b: build context
    """ 
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
    gen_dockerfile(c,b) 


def docker_build(c,b):
    """Build image with docker
    Args:
        c: context
        b: build context
    """ 
    c.run("docker buildx build --progress plain --load -t {repo}:{imagename} {path} | tee build-{imagename}.log".format(
        repo=get_repo(b),  
        imagename=get_imagename(b),
        path=get_path(b)
        ))


@task()
def images(c):
    """Show images""" 
    c.run("docker images")

@task()
def readme(c):
    """Update README
    Args:
        c: context
    """ 
    invoke_list=json.loads(c.run("inv -l --list-format=json",hide=True).stdout)

    readme = templates.get_template("README.md")
    with open("README.md","w") as file:
        with open("invoke.yaml","r") as invoke_yaml:
            file.write(readme.render(invoke_list=invoke_list,invoke_yaml=invoke_yaml.read()))


@task(clean,readme,help={'build': 'build','image':'image'})
def build(c,build=None,image=None):
    """Build image(s)""" 
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

def help_option(c):
    print("Please choose one of the following options:")
    for build in c.build:
            for image in c.build[build]:
                print ("-b",get_build(c.build[build]),'-i',image)
    sys.exit()  



@task(help={'image': 'image','version':'version'})
def bash(c,build=None,image=None,repo=None,version=None):
    """Bash into image"""

    if not build or not image:
        help_option(c)

    if not repo:
        repo=c.docker.repo

    if not version:
        version=c.version

    c.run("docker run -it {repo}:{build}-{image}-{version} bash".format(
        repo=repo,
        build=build,
        image=image,
        version=version        
        ), pty=True)


@task(help={'image': 'image','version':'version'})
def run(c,build=None,image=None,repo=None,version=None,mount=None):
    """Run image"""

    if not build or not image:
        help_option(c)

    if not repo:
        repo=c.docker.repo

    if not version:
        version=c.version

    if not mount:
        mount=c.docker.mount

    mount_path=Path(mount).resolve()

    b=c.build[build][image]

    if not mount:
        c.run("docker run -p 8888:8888  {repo}:{build}-{image}-{version}".format(

            repo=repo,
            build=build,
            image=image,
            version=version        
            ), pty=True)
    else:
        c.run("docker run --volume {mount_path}:/home/{user}/{mount} -p 8888:8888  {repo}:{build}-{image}-{version}".format(
            user=get_user(b),
            repo=repo,
            build=build,
            image=image,
            version=version,
            mount_path=mount_path,
            mount=mount  
            ), pty=True)


@task()
def r2d(c,build=None,image=None):
    """Run image with repo2docker"""

    if not build:
        sys.exit("Please set build with -b")    

    if not image:
        sys.exit("Please set image with -i")    

    b=c.build[build][image]

    path=get_dockerfile_path(b)
    c.run("docker rmi r2d",warn=True)
    c.run("jupyter-repo2docker --debug -P --image-name r2d {path}".format(path=path), pty=True)


@task(build)
def docker_push(c):
    """Push images to docker hub"""

    c.run("docker image push -a {repo}".format(
        repo=c.docker.repo))


@task(readme)
def docker_pushrm(c):
    """Push README to docker hub"""

    c.run("docker pushrm {repo}".format(repo=c.docker.repo))


@task()
def docker_rmi(c):
    """Remove all docker images"""
    c.run("docker rmi -f $(docker images -a -q)",warn=True)

@task()
def docker_prune(c):
    """Prune all docker images"""
    c.run("docker system prune -a")
