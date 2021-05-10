from invoke import task
import jinja2

templates = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))


@task()
def build_core(c):
    with open("core/alpine.pkg", "w") as output:
        output.write(c.alpine.pkg+'\n')

        dockerfile = templates.get_template("Dockerfile_core.j2")

    with open("core/Dockerfile","w") as df:
        df.write(dockerfile.render(nb_user=c.nb.user,nb_uid=c.nb.uid,nb_gid=c.nb.gid))

    c.run("docker buildx build -t {docker_user}/{docker_repo}:core-{version} core | tee build-core.log".format(
        version=c.version, docker_user=c.docker.user, docker_repo=c.docker.repo))
    
@task()
def build_stage(c):
    dockerfile = templates.get_template("Dockerfile_stage.j2")
    with open("stage/Dockerfile","w") as df:
        df.write(dockerfile.render(version=c.version,docker_user=c.docker.user,docker_repo=c.docker.repo))

    c.run("docker buildx build -t {docker_user}/{docker_repo}:stage-{version} stage | tee build-stage.log".format(
        version=c.version, docker_user=c.docker.user, docker_repo=c.docker.repo))


@task()
def build_base(c):
   
    dockerfile = templates.get_template("Dockerfile_base.j2")
    with open("base/Dockerfile","w") as df:
        df.write(dockerfile.render(version=c.version,docker_user=c.docker.user,docker_repo=c.docker.repo,nb_user=c.nb.user,nb_uid=c.nb.uid,nb_gid=c.nb.gid))
   
    c.run("docker buildx build  -t {docker_user}/{docker_repo}:{version}  -t {docker_user}/{docker_repo}:base -t {docker_user}/{docker_repo}:base-{version} base | tee build-stage.log".format(
        version=c.version, docker_user=c.docker.user, docker_repo=c.docker.repo))
   
    dockerfile = templates.get_template("Dockerfile.j2")
    with open("Dockerfile","w") as df:
        df.write(dockerfile.render(version=c.version,docker_user=c.docker.user,docker_repo=c.docker.repo))


@task(build_core,build_stage,build_base)
def build(c):
    print("Building images")


@task(build)
def bash(c):
    c.run("docker run -it {docker_user}/{docker_repo}:latest bash".format(
        version=c.version, docker_user=c.docker.user, docker_repo=c.docker.repo),pty=True)


@task(build)
def run(c):
    c.run("docker run -p 8888:8888 {docker_user}/{docker_repo}:latest".format(   
        version=c.version, docker_user=c.docker.user, docker_repo=c.docker.repo), pty=True)


@task(build)
def r2d(c):
    c.run("docker rmi r2d-microbe",warn=True)
    c.run("jupyter-repo2docker --debug -P --image-name r2d-microbe .".format(
        version=c.version, docker_user=c.docker.user, docker_repo=c.docker.repo), pty=True)


@task(build)
def push(c):
    c.run("docker image push -a {docker_user}/{docker_repo}".format(
        docker_user=c.docker.user, docker_repo=c.docker.repo))

@task()
def prune(c):
    c.run("docker system prune -a")
    # c.run("docker buildx prune")