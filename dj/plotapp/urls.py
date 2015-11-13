
from django.conf.urls import patterns, url

from plotapp import views

urlpatterns = [
    url(r'^start/$', views.plotter.StartPlotter),
    url(r'^table/$', views.plotter.PrintTable),
    url(r'^s/$', views.plotter.DrawPlots),
    url(r'^m/$', views.plotter.DrawMultiPlot),
    url(r'^$', views.plotter.DrawPlot),
]
