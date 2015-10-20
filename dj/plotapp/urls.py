
from django.conf.urls import patterns, url

from plotapp import views

urlpatterns = [
    url(r'^start/$', views.plotter.StartPlotter),
    url(r'^$', views.plotter.DrawPlot)
]
