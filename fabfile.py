from functools import wraps
from fabric.api import *
from fabric.contrib.files import exists
from path import path as ppath

env['blobber_target_defs'] = {
    'staging': {
        'user': 'blobber',
        'host_string': 'blobber@10.134.48.49',
        'blobber_repo':     '/var/local/blobber',
        'blobber_sandbox':  '/var/local/blobber/sandbox',
    },
}

env['blobber_default_target'] = 'staging'


def choose_target(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        name = kwargs.pop('target', None)
        if name is None and 'blobber_target' not in env:
            name = env['blobber_default_target']

        if name is None:
            target_env = {}
        else:
            target_env = env['blobber_target_defs'][name]
            target_env['blobber_target'] = name

        with settings(**target_env):
            return func(*args, **kwargs)

    return wrapper


@task
@choose_target
def ssh():
    open_shell("cd '%(blobber_repo)s' && "
               "source '%(blobber_sandbox)s'/bin/activate"
               % env)

@task
@choose_target
def install():
    if not exists("%(blobber_repo)s/.git" % env):
        run("git init '%(blobber_repo)s'" % env)

    local("git push -f '%(host_string)s:%(blobber_repo)s' HEAD:incoming" % env)
    with cd(env['blobber_repo']):
        run("git reset incoming --hard")

    if not exists(env['blobber_sandbox']):
        run("virtualenv --no-site-packages --python=/tools/python27/bin/python2.7 '%(blobber_sandbox)s'" % env)
        run("echo '*' > '%(blobber_sandbox)s/.gitignore'" % env)

    with cd(env['blobber_repo']):
        run("%(blobber_sandbox)s/bin/python %(blobber_repo)s/setup.py develop" % env)
