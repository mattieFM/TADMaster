from django.urls import path, include
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('help/', views.help, name='help'),
    path('list/', views.data_list, name='data_list'),
    path('examples/', views.examples, name='examples'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('upload/', views.upload_data, name='upload_data'),
    path('input/', views.input, name='input'),
    path('upload_existing/', views.upload_existing, name='upload_existing'),
    path('upload_existing/<int:pk>/bed/', views.upload_bed, name='upload_bed'),
    path('upload_previous_job/', views.upload_previous_job, name='upload_previous_job'),
    path('upload/<int:pk>/callers/', views.upload_caller, name='upload_caller'),
    path('upload/<int:pk>/norms/', views.upload_norm, name='upload_norm'),
    path('list/<int:pk>/delete', views.delete_data, name='delete_data'),
    path('list/<int:pk>/fail', views.fail_data, name='fail_data'),
    path('visualize/<int:pk>/', views.visualize, name='visualize'),
    path('visualize_example/<int:pk>/', views.visualize_example, name='visualize_example'),
    path('heatmap/<int:pk>/', views.heatmap, name='heatmap'),
    path('comfirmation/<int:pk>/', views.comfirmation, name='comfirmation'),
    path('setting_up/<int:pk>/', views.setting_up, name='setting_up'),
    path('processing/<int:pk>/', views.processing, name='processing'),
    path('download/<int:pk>/', views.download, name='download'),
    path('queue/<int:pk>/', views.queue, name='queue'),
]