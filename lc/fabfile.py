from fabric.api import local, settings, abort, run, cd, env, put, hosts
env.use_ssh_config = True
env.user = 'ubuntu'
import sys
from time import sleep

@hosts('ec2-67-202-12-238.compute-1.amazonaws.com')
def test():
    local('tar cvf archive.tar lc webapp static apache manage.py')
    local('gzip archive.tar')
    run('rm -rf /home/ubuntu/lc ; mkdir -p /home/ubuntu/lc')
    put('archive.tar.gz', '/home/ubuntu/lc')
    with cd('/home/ubuntu/lc'):
       run('tar zxvf archive.tar.gz')
    local('rm -f archive.tar.gz')
    with cd('/var/www/static'):
        run('sudo rm -rf * && sudo cp -r /home/ubuntu/lc/static/* . ')
    with cd('/var/www/lc.com'):
        run('sudo rm -rf * && sudo cp -r /home/ubuntu/lc/* . && python manage.py syncdb && sudo service apache2 restart')
