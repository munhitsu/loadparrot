from fabric.api import run, task, env

env.hosts = ["localhost"]

@task
def start():
    run('uname -a')

