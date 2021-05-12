from invoke import task
import jinja2
import yaml
import json
import git

templates = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))

def gittest(c):
    g = git.Repo().git
    print(str(g.branch("--show-current")))


@task()
def microm_build_core(c):
    "Build core image"

    c.run("mkdir -p microm/core")

    with open("microm/core/alpine.pkg", "w") as output:
        output.write(c.microm.alpine.pkg+'\n')
        dockerfile = templates.get_template("Dockerfile_core_microm.j2")

    with open("microm/core/Dockerfile","w") as file:
        file.write(dockerfile.render(maintainer=c.maintainer,nb_user=c.nb.user,nb_uid=c.nb.uid,nb_gid=c.nb.gid))

    c.run("docker buildx build -t {docker_user}/{docker_repo}:core-microm-{version} microm/core | tee build-microm-core.log".format(
        version=c.version, docker_user=c.docker.user, docker_repo=c.docker.repo))


@task(microm_build_core)
def microm_build_builder(c):
    "Build builder image"

    c.run("mkdir -p microm/builder")

    specs={}
    specs['name']="base"
    specs['channels']=c.microm.base.channels
    specs['dependencies']=c.microm.base.dependencies

    with open(r'microm/builder/base.yml', 'w') as file:
        yaml.dump(specs, file, sort_keys=True, canonical=False, explicit_start=True)

    dockerfile = templates.get_template("Dockerfile_builder_microm.j2")
    with open(r'microm/builder/Dockerfile','w') as file:
        file.write(dockerfile.render(maintainer=c.maintainer,version=c.version,docker_user=c.docker.user,docker_repo=c.docker.repo,nb_uid=c.nb.uid,nb_gid=c.nb.gid))

    c.run("docker buildx build -t {docker_user}/{docker_repo}:builder-microm-{version} microm/builder | tee build-microm-stage.log".format(
        version=c.version, docker_user=c.docker.user, docker_repo=c.docker.repo))


@task(microm_build_builder)
def microm_build_base(c):
    "Build base image"

    c.run("mkdir -p microm/base") 
    dockerfile = templates.get_template("Dockerfile_base_microm.j2")
    with open("microm/base/Dockerfile","w") as file:
        file.write(dockerfile.render(maintainer=c.maintainer,version=c.version,docker_user=c.docker.user,docker_repo=c.docker.repo,nb_user=c.nb.user,nb_uid=c.nb.uid,nb_gid=c.nb.gid))
   
    c.run("docker buildx build  -t {docker_user}/{docker_repo}:base-microm-{version} microm/base | tee build-microm-base.log".format(
        version=c.version, docker_user=c.docker.user, docker_repo=c.docker.repo))
   
@task(microm_build_base)
def build(c):
    "Build all images"
    print("Building images")

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


@task(build)
def docker_push(c):
    "Push images to docker hub"
    c.run("docker image push -a {docker_user}/{docker_repo}".format(
        docker_user=c.docker.user, docker_repo=c.docker.repo))

@task()
def docker_pushrm(c):
    "Push README to docker hub"

    c.run("docker pushrm {docker_user}/{docker_repo}".format(docker_user=c.docker.user, docker_repo=c.docker.repo))

@task(docker_push,docker_pushrm)
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
    c.run("rm -f README.md base/* core/* stage/*")

@task()
def readme(c):
    "Update README"

    invoke_list=json.loads(c.run("inv -l --list-format=json",hide=True).stdout)

    readme = templates.get_template("README.j2")
    with open("README.md","w") as file:
        with open("invoke.yaml","r") as invoke_yaml:
            file.write(readme.render(invoke_list=invoke_list,invoke_yaml=invoke_yaml.read()))
