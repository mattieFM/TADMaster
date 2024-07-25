#this script will launch all parts of the server
#that is to say:
#launch redis-server
#launch celery workers
#launch the django server


#! /bin/bash

#enter into virtual env for python
#no longer need virtual env due to docker
#source /var/www/html/TADMaster/Site/virtual-site/bin/activate

#init log files
echo "Start of Redis log" > redis.log
echo "Start of Celery log" > celery.log
redis-server >> redis.log &
celery -A djangoproject worker -l debug >> celery.log &
python3 ./manage.py runserver 0.0.0.0:8000