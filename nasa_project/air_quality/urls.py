from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('download/', views.trigger_download, name='download'),
    path('plot/', views.trigger_plot, name='plot'),
    path('excel/', views.trigger_excel, name='excel'),
    path('status/', views.status, name='status'),
]