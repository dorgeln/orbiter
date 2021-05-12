from invoke import task
import jinja2
import yaml
import json
import git

templates = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))

def gittest(c):
    g = git.Repo().git
    print(str(g.branch("--show-current")))

def create_dir(c,variant,image):

    c.run('mkdir -p {variant}/{image}'.format(variant=variant,image=image))

def create_dockerfile(c,variant,image):

    dockerfile = templates.get_template("Dockerfile_{image}_{variant}.j2".format(variant=variant,image=image))
    with open('{variant}/{image}/Dockerfile'.format(variant=variant,image=image),'w') as file:
        file.write(dockerfile.render(variant=variant,image=image,version=c.version,maintainer=c.maintainer,docker_user=c.docker.user,docker_repo=c.docker.repo,nb_user=c.nb.user,nb_uid=c.nb.uid,nb_gid=c.nb.gid))

def create_alpine(c,variant,image):

    with open('{variant}/{image}/alpine.pkg'.format(variant=variant,image=image),'w') as file:
        file.write(c[variant].alpine.pkg+'\n')

def create_specs(c,variant,image):

    name=c[variant].name
    channels=c[variant].channels
    dependencies=c[variant].dependencies

    specs={}
    specs['name']=name
    specs['channels']=channels
    specs['dependencies']=dependencies

    with open(r'{variant}/{image}/{name}.yml'.format(variant=variant,image=image,name=name), 'w') as file:
        yaml.dump(specs, file, sort_keys=True, canonical=False, explicit_start=True)

def docker_build(c,variant,image):

    c.run("docker buildx build -t {docker_user}/{docker_repo}:{image}-{variant}-{version} {variant}/{image} | tee build-{variant}-{image}.log".format(
        version=c.version, docker_user=c.docker.user, docker_repo=c.docker.repo,variant=variant,image=image))


def builder(c,variant,image):

    create_dir(c,variant=variant,image=image)  
    create_dockerfile(c,variant=variant,image=image)
    create_alpine(c,variant=variant,image=image)
    if variant=='microm' and image=='builder':
        create_specs(c,variant=variant,image=image)
    docker_build(c,variant=variant,image=image)


@task()
def build_microm(c):
    "Build microm images"

    builder(c,variant='microm',image='core')
    builder(c,variant='microm',image='builder')
    builder(c,variant='microm',image='base')


@task()
def build(c):
    "Build all images"

    print("Building images")
    build_microm(c)

    dockerfile = templates.get_template("Dockerfile.j2")
    with open("Dockerfile","w") as file:
        file.write(dockerfile.render(maintainer=c.maintainer,version=c.version,docker_user=c.docker.user,docker_repo=c.docker.repo))


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

@task(build)
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
def clean(c):
    "Clean dangling docker images and generated files"

    c.run('docker rmi $(docker images -f "dangling=true" -q)',warn=True)
    c.run("rm -f Dockerfile README.md build-* microm/core/* microm/builder/* microm/base/*")
    c.run("rmdir microm/core microm/builder microm/base microm")

