import os, shutil, uuid, hashlib, random, sys
from django.db import models
from django.core.files.base import ContentFile


def get_upload_path(instance, filename):
	return os.path.join('/storage/store/TADMaster/data', "job_%s" % str(instance.job_id), filename)

class Data(models.Model):
	#REQUIRED
	title = models.CharField(max_length=100)
	chromosome = models.IntegerField()
	description = models.CharField(max_length=255, blank=True)
	email = models.CharField(max_length=100, blank=True)
	document = models.FileField(upload_to=get_upload_path)
	resolution = models.IntegerField(default=0)
	uploaded_at = models.DateTimeField(auto_now_add=True)
	job_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
	status = models.CharField(max_length=25, default='Pending')
	#Data Input
	data_input_type = models.CharField(max_length=10, default='square')
	#NORMALIZATION
	norm_ice = models.BooleanField(default=False)
	norm_kr = models.BooleanField(default=False)
	norm_scn = models.BooleanField(default=False)
	norm_vc = models.BooleanField(default=False)
	norm_mcfs = models.BooleanField(default=False)
	#TADCALLERS
	clustertad = models.BooleanField(default=False)

	catch = models.BooleanField(default=False)

	arrowhead = models.BooleanField(default=False)
	arrowhead_genomeID = models.CharField(max_length=10, default='hg19')

	topdom = models.BooleanField(default=False)
	topdom_window = models.CharField(max_length=10, default='5')

	armatus = models.BooleanField(default=False)
	armatus_gamma = models.CharField(max_length=10, default='0.2')
	
	di = models.BooleanField(default=False)
	di_length = models.CharField(max_length=10, default='10')

	spectral = models.BooleanField(default=False)
	chdf = models.BooleanField(default=False)
	gmap = models.BooleanField(default=False)
	ic_finder = models.BooleanField(default=False)
	chromo_r = models.BooleanField(default=False)
	hic_seg = models.BooleanField(default=False)
	insulation = models.BooleanField(default=False)
	hic_explorer = models.BooleanField(default=False)

	insulation= models.BooleanField(default=False)
	insulation_window = models.IntegerField(default=0)

	spectralTAD = models.BooleanField(default=False)

	has_ran = models.BooleanField(default=False)



	def __str__(self):
		return self.title

#overloading the delete function to delete file in directory
	def delete(self, *args, **kwargs):
		path = os.path.join('/storage/store/TADMaster/data/', "job_%s" % str(self.job_id))
		self.document.delete()
		super().delete(*args, **kwargs)
		if os.path.exists(path):
			shutil.rmtree(path)


#needs refactoring eventually
	def make_config(self):
		path = os.path.join('/storage/store/TADMaster/data', "job_%s" % str(self.job_id), "TADMaster.config")
		f = open(path, "w")
		f.write("#Required\n\n")
		f.write("input_matrix=%s \n" % str(self.document))
		f.write('title="%s" \n' % str(self.title))
		f.write('description="%s" \n' % str(self.description))
		f.write("chr=%s \n" % str(self.chromosome))
		f.write("resolution=%s \n" % str(self.resolution))
		f.write("job_id=%s \n" % str(self.job_id))
		f.write("email=%s \n\n\n" % str(self.email))
		f.write("data_input_type=%s \n\n" % str(self.data_input_type))
		
		f.write("#Normalization\n\n\n")
		f.write("norm_chromor=False\n\n")
		f.write("species=hg19\n\n")
		f.write("norm_ice=%s \n\n" % str(self.norm_ice))
		f.write("norm_kr=%s \n\n" % str(self.norm_kr))
		f.write("norm_scn=%s \n\n" % str(self.norm_scn))
		f.write("norm_vc=%s \n\n" % str(self.norm_vc))
		f.write("norm_mcfs=%s \n\n\n" % str(self.norm_mcfs))
		
		f.write("#TAD Callers\n\n\n")
		f.write("clustertad=%s \n\n" % str(self.clustertad))
		f.write("catch=%s \n\n" % str(self.catch))

		f.write("arrowhead=%s \n\n" % str(self.arrowhead))
		f.write("arrowhead_genomeID=%s \n\n" % str(self.arrowhead_genomeID))

		f.write("topdom=%s \n" % str(self.topdom))
		f.write("topdom_window=%s \n\n" % str(self.topdom_window))
		
		f.write("armatus=%s \n" % str(self.armatus))
		f.write("armatus_gamma=%s \n\n" % str(self.armatus_gamma))
		
		f.write("di=%s \n" % str(self.di))
		f.write("di_length=%s \n\n" % str(self.di_length))
		
		f.write("spectral=%s \n\n" % str(self.spectralTAD))
		f.write("chdf=%s \n\n" % str(self.chdf))
		f.write("gmap=%s \n\n" % str(self.gmap))
		f.write("ic_finder=%s \n\n" % str(self.ic_finder))
		f.write("chromo_r=%s \n\n" % str(self.chromo_r))
		f.write("hic_seg=%s \n\n" % str(self.hic_seg))
		f.write("insulation=%s \n\n" % str(self.insulation))
		f.write("insulation_window=%s \n\n" % str(self.insulation_window))
		f.write("hic_explorer=%s \n\n\n" % str(self.hic_explorer))
		f.close()
