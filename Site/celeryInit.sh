#!/bin/bash
cd /var/www/html/TADMaster/Site
source ./virtual-site/bin/activate
celery -A djangoproject worker -l info >> ./celery.log &
