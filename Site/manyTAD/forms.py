from django import forms

from .models import Data

class DataForm(forms.ModelForm):
	class Meta:
		model = Data
		fields = ('title', 'chromosome', 'description', 'email', 'resolution')
		labels = {'resolution': 'Resolution (basepairs)'}

class NormForm(forms.ModelForm):
	class Meta:
		model = Data
		fields = ('norm_ice', 'norm_kr', 'norm_scn', 'norm_vc', 'norm_mcfs')


class CallerForm(forms.ModelForm):
	class Meta:
		model = Data
		fields = ('clustertad', 'catch', 'arrowhead', 'arrowhead_genomeID', 'topdom', 'topdom_window',
					'armatus', 'armatus_gamma', 'di', 'di_length', 'spectral', 'chdf', 'gmap', 
					'ic_finder', 'chromo_r', 'hic_seg', 'insulation', 'insulation_window', 'hic_explorer', 'spectralTAD')		


class UploadFileForm(forms.ModelForm):
	class Meta:
		model = Data
		fields = ('document',)

class ExistingForm(forms.ModelForm):
	class Meta:
		model = Data
		fields = ( 'title',  'description', 'chromosome', 'email', 'resolution', 'document')
		labels = {'resolution': 'Resolution (basepairs)', 'document': 'Contact Matrix*'}

class ExistingFormNoMatrix(forms.ModelForm):
	class Meta:
		model = Data
		fields = ( 'title',  'description', 'chromosome', 'email', 'resolution')
		labels = {'resolution': 'Resolution (basepairs)'}


class UploadBedForm(forms.Form):
    bed_title_1 = forms.CharField(max_length=50)
    bed_file_1 = forms.FileField()
    bed_title_2 = forms.CharField(max_length=50)
    bed_file_2 = forms.FileField()


class UploadZipForm(forms.Form):
    file = forms.FileField()

