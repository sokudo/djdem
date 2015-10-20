from django.shortcuts import render

from attel.dogen import dogen_data

# Create your views here.
from django.http import HttpResponse


class Plotter(object):

  def __init__(self):
    self.StartPlotter()

  def StartPlotter(self, request=None):
    self.dataCollector = dogen_data.DataCollector()
    self.runner = dogen_data.Run(
        dogen_data.CHANNEL_CONFIGS, self.dataCollector.Add, realTime=False)
    return HttpResponse('Ok')

  def DrawPlot(self, request):
    data_map = self.dataCollector.GetAll()
    row_names = sorted({
        key for entities in data_map.itervalues()
        for x in entities
        for key in x .keys()})
    response = []
    response.append('<table style="width:100%">')
    response.append('  <tr>')
    for row_name in row_names:
      response.append('    <td>%s</td>' % row_name)
    response.append('  </tr>')
    for entities in data_map.itervalues():
      for entity in entities:
        response.append('  <tr>')
        for row_name in row_names:
          response.append('    <td>%s</td>' % entity.get(row_name, ''))
        response.append('  </tr>')
    response.append('</table>')
    return HttpResponse('\n'.join(response))


plotter = Plotter()