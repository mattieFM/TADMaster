from celery.decorators import task
from celery.utils.log import get_task_logger
import subprocess
from celery import Task
import os
from .models import Data
from django.core import mail
from .inform_using_mail import send_mail_to
from .hasher import GetHashofDirs
from celery.exceptions import SoftTimeLimitExceeded

logger = get_task_logger("tasks")
logger.info("tasks logging working")

#timeout of 30 min
timeout = (30 * 60)


def on_failure(pk):
        #var declaration
        data = Data.objects.get(pk=pk)
        job_id = data.job_id
        
        #log the failure
        log = open ("/var/www/html/TADMaster/Site/manyTAD/jobs.log", "a")
        log.write("Task Failure:")
        log.write(str(job_id))
        log.write("\n")
        log.close()
        
        #update database
        data.status = "job_failure"
        data.save()
        
        #send email to user about failure
        if data.email != '':
            #very basic validation
            if('@' in data.email):
                subject = 'TADMaster: Your Job \"' + str(data.title) + '\" has Failed or Timedout [No Reply]'
                message = "Your TADMaster job has failed.\n"
                message += 'Feel free to resubmit your job at http://biomlearn.uccs.edu/TADMaster\n'
                message += 'If a job fails repeatedly it might be due to size of files resulting in a timeout from the job taking to long to run on our servers.\n'
                message += 'In this case feel free to clone the easy to use dockerised version at our github: https://github.com/OluwadareLab/TADMaster\n'
                message += 'Thank you for using TADMaster. \n'
                message += 'Oluwadare Lab \n\n'
                message += '------------------\n'
                message += 'The TADMaster Team'
                receiver = data.email
                send_mail_to(subject,message,receiver)
    



@task(name="data_processing", soft_time_limit=timeout)
def data_processing(pk):
    """sends an email when feedback form is filled successfully"""
    try:
        logger.info("Started Processing")
        data = data = Data.objects.get(pk=pk)
        job = data.job_id
        if data.status != "Complete":
            subprocess.run(["taskset", "-c", "0-149", "bash","../test_new.sh", str(job)])
            path = os.path.join('/var/www/html/TADMaster/Site/storage/data/', "job_%s" % str(data.job_id))
            hash = GetHashofDirs(path)
            print(hash)
            log = open("/var/www/html/TADMaster/Site/manyTAD/jobs.log", "a")
            log.write("Data Processing on (Regular Tad Master):")
            log.write(hash)
            log.write("\n")
            log.close()
            Data.objects.filter(pk=pk).update(status="Complete")
            if data.email != '':
                #very basic validation as this should be handeled in the form
                if('@' in data.email):
                    subject = 'TADMaster: Your Job \"' + str(data.title) + '\" is Complete [No Reply]'
                    message = "Your TADMaster job completed.\n"
                    message += 'The results can be found at http://biomlearn.uccs.edu/TADMaster/visualize/'+ str(data.pk) +'/ \n\n'
                    message += 'Thank you for using TADMaster. \n'
                    message += 'Oluwadare Lab \n\n'
                    message += '------------------\n'
                    message += 'The TADMaster Team'
                    receiver = data.email
                    send_mail_to(subject,message,receiver)
    except SoftTimeLimitExceeded:
        on_failure(pk)
    return True

@task(name="upload_bed_task", soft_time_limit=timeout)
def upload_bed_task(pk):
    """sends an email when feedback form is filled successfully"""
    try:
        logger.info("Started Processing")
        data = data = Data.objects.get(pk=pk)
        job = data.job_id
        log = open("/var/www/html/TADMaster/Site/manyTAD/jobs.log", "a")
        log.write("uplaod_bed_task on (Tad Master Plus):")
        log.write(str(job))
        log.write("\n")
        log.close()
        if data.status != "Complete":
            out = subprocess.run(["bash","../bed.sh", str(job)])
            print(out)
            path = os.path.join('/var/www/html/TADMaster/Site/storage/data', "job_%s" % str(data.job_id))
            Data.objects.filter(pk=pk).update(status="Complete")
            if data.email != '':
                #very basic validation as this should be handeled in the form
                if('@' in data.email):
                    subject = 'TADMaster: Your Job \"' + str(data.title) + '\" is Complete [No Reply]'
                    message = "Your TADMaster job completed.\n"
                    message += 'The results can be found at http://biomlearn.uccs.edu/TADMaster/visualize/'+ str(data.pk) +'/ \n\n'
                    message += 'Thank you for using TADMaster. \n'
                    message += 'Oluwadare Lab \n\n'
                    message += '------------------\n'
                    message += 'The TADMaster Team'
                    receiver = data.email
                    send_mail_to(subject,message,receiver)
    except SoftTimeLimitExceeded:
        on_failure(pk)
    return True


