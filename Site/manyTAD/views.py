from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.forms.models import model_to_dict
from django.conf import settings
from .forms import DataForm, NormForm, CallerForm, UploadFileForm, ExistingForm, UploadBedForm, UploadZipForm
from .models import Data
import subprocess
from os import path
import os
import sys
from manyTAD.tasks import data_processing, upload_bed_task
from plotly.offline import plot
from plotly.graph_objs import Scatter
import plotly.express as px
import time
import importlib
import shutil
from manyTAD.dash_apps import *
from importlib import reload
import zipfile
from .hasher import GetHashofDirs
from django.http import JsonResponse
from django.core import mail
from .inform_using_mail import send_mail_to


protected_visualizations = [389, 392, 393, 421, 395, 396, 397, 413, 414, 415, 379, 374, 371, 370, 367, 366, 365, 359, 412, 358, 352, 357, 387, 479, 505, 522]

def home(request):
	return render(request, 'manyTAD/home.html')

def help(request):
	return render(request, 'manyTAD/help.html')

def privacy_policy(request):
	return render(request, 'manyTAD/privacy_policy.html')


def data_list(request):
	datas = Data.objects.all()
	return render(request, 'manyTAD/list.html',{
		'datas': datas
		})

def examples(request):
	return render(request, 'manyTAD/example.html')

def delete_data(request, pk):
	if request.method == 'POST':
		data = Data.objects.get(pk=pk)
		data.delete()
	return redirect('data_list')	

def upload_data(request):
	context = {}
	context["error"] = "none"
	if request.method == 'POST':
		form = DataForm(request.POST, request.FILES)
		if form.is_valid() and request.POST.get('data_input_type') is not None:
			if request.POST.get('data_input_type') == 'hic':
				if request.POST.get('resolution') not in ['2500000', '1000000', '500000', '250000', '100000', '50000', '25000', '10000', '5000']:
					context["error"] = "resolution error"
			if context["error"] == "none":
				data = form.save()
				data.data_input_type = request.POST.get('data_input_type')
				data.save()
				return HttpResponseRedirect('%s/norms' % (data.pk))
		elif request.POST.get('data_input_type') is None:
			context["error"] = "input type error"	
	else:
		form = DataForm()
		print("FORM FAIL")
	context["form"] = form	
	return render(request, 'manyTAD/new_input.html', context)


def upload_norm(request, pk):
	context = {}
	data = Data.objects.get(pk=pk)
	if data.status == "Complete":
		return redirect('visualize', pk=pk)
	if data.has_ran == True:
		return redirect('processing', pk=pk)
	if request.method == 'POST':
		form = NormForm(request.POST, instance=data)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('upload_caller' ,args=(data.pk,)))
	else:
		form = NormForm()
	context["form"] = form
	context["input_type"] = data.data_input_type	
	return render(request, 'manyTAD/norm.html', context)
 

def upload_caller(request, pk):
	context = {}
	data = Data.objects.get(pk=pk)
	if data.status == "Complete":
		return redirect('visualize', pk=pk)
	if data.has_ran == True:
		return redirect('processing', pk=pk)
	context["error"] = "none"
	if request.method == 'POST':
		num_selected = 0
		for key in request.POST:
			print(request.POST[key])
			if request.POST[key] == 'on':
				num_selected += 1
		form = CallerForm(request.POST, instance=data)
		if form.is_valid() and num_selected > 1:
			form.save()			
			return redirect('comfirmation', pk=pk)
		elif num_selected <= 1:
			context["error"] = "insufficient parameters"

	else:
		form = CallerForm()
	context["form"] = form
	context["input_type"] = data.data_input_type
	norm = []
	if data.norm_ice: norm.append('ICE')
	if data.norm_kr : norm.append('KR')
	if data.norm_scn : norm.append('SCN')
	if data.norm_vc: norm.append('VC')
	if data.norm_mcfs: norm.append('MCFS')
	context['normalizations'] = norm
	return render(request, 'manyTAD/caller.html', context)

def comfirmation(request, pk):
	data = Data.objects.get(pk=pk)
	if data.status == "Complete":
		return redirect('visualize', pk=pk)
	if data.has_ran == True:
		return redirect('processing', pk=pk)
	context = model_to_dict(data)
	if request.is_ajax():
		job_path = os.path.join('/storage/store/TADMaster/data', "job_%s" % str(data.job_id))
		form = UploadFileForm(request.POST, request.FILES)
		print(request.FILES)
		if form.is_valid():
			path = os.path.join('/storage/store/TADMaster/data', "job_%s" % str(data.job_id))
			save_path = os.path.join(path, request.FILES['document'].name)
			os.mkdir(path)
			with open(save_path, 'wb+') as destination:
				for chunk in request.FILES['document'].chunks():
					destination.write(chunk)
			data.document = save_path
			data.status = "TADMasterPlus_Pending"
			data.save()
			return JsonResponse({
				'success': 'True',
				'url': reverse('processing', args=[data.pk]),
			})
		else:
			return JsonResponse({
				'success': 'False',
			})

	else:
		form = UploadFileForm()
		norm = []
		caller = []
		if data.norm_ice: norm.append('ICE')
		if data.norm_kr : norm.append('KR')
		if data.norm_scn : norm.append('SCN')
		if data.norm_vc: norm.append('VC')
		if data.norm_mcfs: norm.append('MCFS')
		context['normalizations'] = norm
		if data.clustertad: caller.append('ClusterTAD')
		if data.catch: caller.append('Catch')
		if data.arrowhead: caller.append('Arrowhead')
		if data.topdom: caller.append('TopDom')
		if data.armatus: caller.append('Armatus')
		if data.di: caller.append('DI')
		if data.spectralTAD: caller.append('SpectralTAD')
		if data.chdf: caller.append('CHDF')
		if data.gmap: caller.append('GMAP')
		if data.ic_finder: caller.append('IC_Finder')
		if data.chromo_r: caller.append('Crhomo_R')
		if data.hic_seg: caller.append('HIC_Seg')
		if data.insulation: caller.append('Insulation')
		if data.hic_explorer: caller.append('HIC_Explorer')
		context['callers'] = caller
	context["form"] = form
	return render(request, 'manyTAD/comfirmation.html', context)


def upload_existing(request):
	context = {}
	context["error"] = "none"
	if request.is_ajax():
		form = ExistingForm(request.POST, request.FILES)
		if form.is_valid() and request.POST.get('data_input_type') is not None:
			if request.POST.get('data_input_type') == 'hic':
				if request.POST.get('resolution') not in ['2500000', '1000000', '500000', '250000', '100000', '50000', '25000', '10000', '5000']:
					context["error"] = "resolution error"
			if context["error"] == "none":
				data = form.save()
				data.data_input_type = request.POST.get('data_input_type')
				data.save()
				return JsonResponse({
					'success': 'True',
					'url': reverse('upload_bed', args=[data.pk]),
				})
		elif request.POST.get('data_input_type') is None:
			context["error"] = "input type error"
			return JsonResponse({
				'success': False,
			})
		else:
			return JsonResponse({
				'success': False,
			})
	else:
		form = ExistingForm()
		print("FORM FAIL")
	context["form"] = form	
	return render(request, 'manyTAD/input_existing.html', context)

def handle_uploaded_bed(f, title, path):
	with open(path +'/'+ title + '.bed', 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)

def upload_bed(request, pk):
	data = Data.objects.get(pk=pk)
	if data.has_ran == True:
		return redirect('processing', pk=pk)
	if request.method == 'POST':
		form = UploadBedForm(request.POST, request.FILES)
		if form.is_valid():
			print(data.document)
			job_path = os.path.join('/storage/store/TADMaster/data', "job_%s" % str(data.job_id))
			output_path = os.path.join(job_path, "output")
			norm_path = os.path.join(job_path, "normalizations")
			os.mkdir(output_path)
			os.mkdir(norm_path)
			final_out_path = os.path.join(output_path, str(data.document)[71:])
			os.mkdir(final_out_path)
			handle_uploaded_bed(request.FILES['bed_file_1'], request.POST.get('bed_title_1'), final_out_path)
			handle_uploaded_bed(request.FILES['bed_file_2'], request.POST.get('bed_title_2'), final_out_path)
			data.status = "TADMaster_Pending"
			data.save()
			return redirect('processing', pk=pk)
	else:
		form = UploadBedForm()
	return render(request, 'manyTAD/upload_bed.html', {'form': form})

def handle_uploaded_zip(f, title, path):
	with open(path + '/' + title, 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)

def upload_previous_job(request):
	context = {}
	context["error"] = "none"
	if request.is_ajax():
		form = UploadZipForm(request.POST, request.FILES)
		if form.is_valid():
			data = Data(title='Previous Job', chromosome=1)
			data.save()
			path = '/storage/store/TADMaster/data'
			temp_path = "temp_%s" % str(data.job_id)
			handle_uploaded_zip(request.FILES['file'], request.FILES['file'].name, path)
			zip_name = str(request.FILES['file'])
			os.chdir('/storage/store/TADMaster/data')
			if zipfile.is_zipfile(zip_name):
				os.system("unzip " + zip_name + " -d " + temp_path)
				dir_name = zip_name[:-4]
				hash = GetHashofDirs(path + '/' + temp_path + '/' + dir_name)
				print(str(hash))
				valid_hash = False
				with open('/var/www/html/TADMaster/Site/manyTAD/jobs.log', 'r') as fh:
					lines = fh.readlines()
					for line in lines:
						if str(hash) == line.strip():
							valid_hash = True
				if valid_hash:
					new_dir_path = "/storage/store/TADMaster/data/" + 'job_' + str(data.job_id)
					os.system("mv "+ path + '/' + temp_path + '/' + dir_name  + " " + new_dir_path)
					with open(new_dir_path + '/TADMaster.config', 'r') as fh:
						lines = fh.readlines()
						for line in lines:
							if line[:6] == 'title=':
								data.title = str(line[6:])
							if line[:12] == 'description=':
								data.description = str(line[12:])
							if line[:4] == 'chr=':
								data.chromosome = int(line[4:])
							if line[:11] == 'resolution=':
								data.resolution = int(line[11:])
					data.has_ran = True
					data.status = "Reuploaded"
					data.save()
					#os.rename(dir_name, 'job_' + str(data.job_id))
					os.system("rm -rf " + temp_path)
					os.system("rm -rf " + zip_name)
					return JsonResponse({
						'success': 'True',
						'url': reverse('visualize', args=[data.pk]),
					})

				else:
					#os.system("rm -rf " + dir_name)
					os.system("rm -rf " + temp_path)
					os.system("rm -rf " + zip_name)
					context["error"] = "upload error"
					return JsonResponse({
						'success': 'False',
					})

			else:
				os.system("rm -rf " + zip_name)
				context["error"] = "not a zip error"
				return JsonResponse({
					'success': 'False',
				})


	else:
		form = UploadZipForm()
	context["form"] = form	
	return render(request, 'manyTAD/input_zip.html', context)


def processing(request, pk):
	context = {}
	context["pk"] = str(pk)
	data = Data.objects.get(pk=pk)
	if data.has_ran != True:
		data.has_ran = True
		data.save()
		if data.status == "TADMasterPlus_Pending":
			data.make_config()
			data_processing.delay(pk)
		if data.status == "TADMaster_Pending":
			data.make_config()
			upload_bed_task.delay(pk)
		if data.email != '':
			subject = 'TADMaster: Your Job \"' + str(data.title) + '\" Was Accepted [No Reply]'
			message = "Your TADMaster job has been accepted and added to the queue of pending jobs.\n"
			message += "TADMaster aims to provide a quality experience to its users. Thus, jobs are processed in a first come first serve manner.\n"
			message += 'We will process your job as soon as possible. Please use http://biomlearn.uccs.edu/TADMaster/queue/'+ str(data.pk) +'/ to see your place in the queue. \n'
			message += "We will notify you when your job has completed.\n\n"
			message += 'Thank you for using TADMaster. \n'
			message += 'Oluwadare Lab \n\n'
			message += '------------------\n'
			message += 'The TADMaster Team'
			receiver = data.email
			send_mail_to(subject,message,receiver)

	return render(request, 'manyTAD/processing.html', context)



def visualize(request, pk):
	context = {}
	data = Data.objects.get(pk=pk)
	package = "manyTAD.dash_apps"
	context['dash_context'] = {'target_id': {'value': str(data.pk)}}
	if pk not in protected_visualizations:
		try:
			return render(request, "manyTAD/visualize.html", context)
		except Exception as e:
			print(e)
			return redirect('setting_up', pk=pk)
	else:
		return redirect('visualize_example', pk=pk)	

def visualize_example(request, pk):
	context = {}
	data = Data.objects.get(pk=pk)
	package = "manyTAD.dash_apps"
	context['dash_context'] = {'target_id': {'value': str(data.pk)}}
	try:
		return render(request, "manyTAD/visualize_example.html", context)
	except Exception as e:
		print(e)
		return redirect('setting_up', pk=pk)

def heatmap(request, pk):
	context = {}
	data = Data.objects.get(pk=pk)
	package = "manyTAD.dash_apps"
	context['dash_context'] = {'target_id': {'value': str(data.pk)}}
	try:
		return render(request, "manyTAD/heatmap.html", context)
	except Exception as e:
		print(e)
		return redirect('setting_up', pk=pk)


def setting_up(request, pk):
	if request.method == 'POST':
		return redirect('visualize', pk=pk)
	else:
		context = {}
		context["pk"] = str(pk)
		return render(request, 'manyTAD/setting_up.html', context)


def download(request, pk):
	data = Data.objects.get(pk=pk)
	path = os.path.join('/storage/store/TADMaster/data', "job_%s" % str(data.job_id))
	zip_path = os.path.join(path, "job_%s" % str(data.job_id)+".zip")
	shutil.make_archive(path, 'zip', '/storage/store/TADMaster/data', "job_%s" % str(data.job_id))
	shutil.move("/storage/store/TADMaster/data/job_%s" % str(data.job_id)+".zip", path)
	if os.path.exists(zip_path):
		with open(zip_path, 'rb') as fh:
			response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
			response['Content-Disposition'] = 'inline; filename=' + os.path.basename(zip_path)
		os.remove(zip_path)
		add_hash = True
		hash = GetHashofDirs(path)
		with open('/var/www/html/TADMaster/Site/manyTAD/jobs.log', 'r') as fh:
			lines = fh.readlines()
			for line in lines:
				if str(hash) == line:
					add_hash = False
		if add_hash:
			log = open("/var/www/html/TADMaster/Site/manyTAD/jobs.log", "a")
			log.write(hash)
			log.write("\n")
			log.close()
		return response
	raise Http404

def queue(request, pk):
	context = {}
	data = Data.objects.get(pk=pk)
	last = Data.objects.filter(status="Complete").order_by('-id')[0]
# Load job if competed
	if pk <= last.pk and data.status == "Complete":
		package = "manyTAD.dash_apps"
		context['dash_context'] = {'target_id': {'value': str(data.pk)}}
		if pk not in protected_visualizations:
			try:
				return render(request, "manyTAD/visualize.html", context)
			except Exception as e:
				print(e)
				return redirect('setting_up', pk=pk)
		else:
			return redirect('visualize_example', pk=pk)

# Return to home if job was not submitted
	elif data.status == "Pending":
		return render(request, 'manyTAD/home.html')

# Calculate true position in queue	
	else:	
		position = 0
		for i in range(last.pk, pk):
			try: 
				check_data = Data.objects.get(pk=i)
				if check_data.status == 'TADMasterPlus_Pending' or check_data.status == 'TADMaster_Pending':
					position += 1
			except Exception as e:
				print(e)
		if position == 0:
			context['position'] = "Your job is currently being processed"
			return render(request, "manyTAD/queue.html", context)
		elif position == 1:
			context['position'] = "There is " + str(position) + " job ahead of you in the queue"
			return render(request, "manyTAD/queue.html", context)
		elif position > 1:
			context['position'] = "There are " + str(position) + " jobs ahead of you in the queue"
			return render(request, "manyTAD/queue.html", context)
