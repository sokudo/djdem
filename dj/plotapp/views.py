from django.shortcuts import render

from attel.dogen import dogen_data

# Create your views here.
from django.http import HttpResponse


class Plotter(object):

  HEADER = """
      <html>
      <head>
        <!--Load the AJAX API-->
        <script type="text/javascript" src="https://www.google.com/jsapi"></script>
        <script type="text/javascript">

          // Load the Visualization API and the package.
          google.load('visualization', '1.1', {'packages':['line']});

          // Set a callback to run when the Google Visualization API is loaded.
          google.setOnLoadCallback(drawChart);
  """

  FOOTER = """
        </script>
      </head>

      <body>
        <!--Div that will hold the  chart-->
        <div id="chart_div" style="width: 900px; height: 500px"></div>
      </body>
      </html>
  """

  def __init__(self):
    self.StartPlotter()

  def StartPlotter(self, request=None):
    self.dataCollector = dogen_data.DataCollector()
    self.runner = dogen_data.Run(
        dogen_data.CHANNEL_CONFIGS, self.dataCollector.Add, realTime=False)
    return HttpResponse('Ok')

  def PrintTable(self, request):
    data_map = self.dataCollector.GetAll()
    column_names = sorted({
        key for entities in data_map.itervalues()
        for x in entities
        for key in x .keys()})
    response = []
    response.append('<table style="width:100%">')
    response.append('  <tr>')
    for column_name in column_names:
      response.append('    <td>%s</td>' % column_name)
    response.append('  </tr>')
    for entities in data_map.itervalues():
      for entity in entities:
        response.append('  <tr>')
        for column_name in column_names:
          response.append('    <td>%s</td>' % entity.get(column_name, ''))
        response.append('  </tr>')
    response.append('</table>')
    return HttpResponse('\n'.join(response))

  def _GenDataTable(self, chId, start_ms=None, stop_ms=None):
    """Generates JS for Google Chartsd DataTable object."""

    js = """
            // Create the data table.
            var data = new google.visualization.DataTable();
    """
    entities = self.dataCollector.GetChannelData(
        chId, start_ms=start_ms, stop_ms=stop_ms)
    column_names = {key for x in entities for key in x}
    column_names -= {'time_ms', 'chId'}
    header = ['time_ms']
    header.extend(sorted(column_names))
    column_names = header
    for name in column_names:
      kind = 'number'
      js += "            data.addColumn(%r, %r);\n" % (kind, name)
    rows = []
    for entity in entities:
      row = [entity.get(cn, '') for cn in column_names]
      rows.append(row)
    rows_repr = ', '.join('%r' % row for row in rows)
    js += "            data.addRows([%s]);\n" % rows_repr
    return js, len(column_names)

  def DrawPlot(self, request):
    """Draws a plot for a single channel."""
    js = self.HEADER
    js += """        function drawChart() {
    """
    js0, _ = self._GenDataTable(0)
    js += js0
    js += """
            // Set chart options
            var options = {title: 'Chart'};

            // Instantiate and draw our chart, passing in some options.
            var chart = new google.charts.Line(
                document.getElementById('chart_div'));
            chart.draw(data, options);
          }
    """
    js += self.FOOTER

    return HttpResponse(js)


  def DrawPlots(self, request):
    """Draws a plot for 2 channels."""
    js = self.HEADER
    js += """        function drawChart() {
    """
    js0, ncols0 = self._GenDataTable(0)
    js += js0
    js += '        data0 = data;\n'
    js1, ncols1 = self._GenDataTable(1)
    js += js1
    js += """
            data = google.visualization.data.join(data0, data,
                'full', [[0, 0]], %r, %r);
    """ % (range(1, ncols0), range(1, ncols1))
    js += """
            // Set chart options
            var options = {title: 'Chart'};

            // Instantiate and draw our chart, passing in some options.
            var chart = new google.charts.Line(
                document.getElementById('chart_div'));
            chart.draw(data, options);
          }
    """
    js += self.FOOTER

    return HttpResponse(js)

plotter = Plotter()