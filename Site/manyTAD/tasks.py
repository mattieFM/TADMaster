from celery.decorators import task
from celery.utils.log import get_task_logger
import subprocess
import os
from .models import Data
from django.core import mail
from .inform_using_mail import send_mail_to
from .hasher import GetHashofDirs

logger = get_task_logger(__name__)


@task(name="data_processing")
def data_processing(pk):
	"""sends an email when feedback form is filled successfully"""
	logger.info("Started Processing")
	data = data = Data.objects.get(pk=pk)
	job = data.job_id
	if data.status != "Complete":

		subprocess.run(["taskset", "-c", "0-149", "bash","../test_new.sh", str(job)])
		path = os.path.join('/storage/store/TADMaster/data', "job_%s" % str(data.job_id))
		hash = GetHashofDirs(path)
		print(hash)
		log = open("/var/www/html/TADMaster/Site/manyTAD/jobs.log", "a")
		log.write(hash)
		log.write("\n")
		log.close()
		Data.objects.filter(pk=pk).update(status="Complete")
		if data.email != '':
			subject = 'TADMaster: Your Job \"' + str(data.title) + '\" is Complete [No Reply]'
			message = "Your TADMaster job completed.\n"
			message += 'The results can be found at http://biomlearn.uccs.edu/TADMaster/visualize/'+ str(data.pk) +'/ \n\n'
			message += 'Thank you for using TADMaster. \n'
			message += 'Oluwadare Lab \n\n'
			message += '------------------\n'
			message += 'The TADMaster Team'
			receiver = data.email
			send_mail_to(subject,message,receiver)
	return 

@task(name="upload_bed_task")
def upload_bed_task(pk):
	"""sends an email when feedback form is filled successfully"""
	logger.info("Started Processing")
	data = data = Data.objects.get(pk=pk)
	job = data.job_id
	if data.status != "Complete":
		subprocess.run(["bash","../bed.sh", str(job)])
		path = os.path.join('/var/www/html/TADMaster/Site/data', "job_%s" % str(data.job_id))
		Data.objects.filter(pk=pk).update(status="Complete")
		if data.email != '':
			subject = 'TADMaster: Your Job \"' + str(data.title) + '\" is Complete [No Reply]'
			message = "Your TADMaster job completed.\n"
			message += 'The results can be found at http://biomlearn.uccs.edu/TADMaster/visualize/'+ str(data.pk) +'/ \n\n'
			message += 'Thank you for using TADMaster. \n'
			message += 'Oluwadare Lab \n\n'
			message += '------------------\n'
			message += 'The TADMaster Team'
			receiver = data.email
			send_mail_to(subject,message,receiver)
	return 

