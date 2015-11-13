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
          google.load('visualization', '1', {'packages':['corechart']});

          // Set a callback to run when the Google Visualization API is loaded.
          google.setOnLoadCallback(drawAllCharts);
  """

  DRAW = """
            // Set chart options
            var options = {title: %r};

            // Instantiate and draw our chart, passing in some options.
            var chart = new google.visualization.LineChart(
                document.getElementById(%r));
            chart.draw(data, options);
  """

  MID = """
        </script>
      </head>

      <body>
  """

  # Div holds the chart.
  DIV = """
        <p></p>
        <div id="%s"></div>
  """

  FOOTER = """
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
    """Generates JS for Google Charts DataTable object."""

    jslist = ['            // Create the data table (chId %s).' % chId,
              '            var data = new google.visualization.DataTable();']
    entities = self.dataCollector.GetChannelData(
        chId, start_ms=start_ms, stop_ms=stop_ms)
    column_names = {key for x in entities for key in x}
    column_names -= {'time_ms', 'chId'}
    header = ['time_ms']
    header.extend(sorted(column_names))
    column_names = header
    for name in column_names:
      kind = 'number'
      jslist.append('            data.addColumn(%r, %r);' % (kind, name))
      rows = []
      for entity in entities:
        row = [entity.get(cn, '') for cn in column_names]
        rows.append(row)
    rows_repr = ', '.join('%r' % row for row in rows)
    jslist.append('            data.addRows([%s])' % rows_repr)
    return '\n'.join(jslist), len(column_names)

  def _GenChart(self, chId):
    jslist = [
        self.HEADER,
        '        function drawAllCharts() {',
        self._GenDataTable(chId)[chId],
        self.DRAW % ('Chart', 'chart_div'),
        '        }',
        self.MID,
        self.DIV % 'chart_div',
        self.FOOTER]
    return '\n'.join(jslist)

  def _GenChartFun(self, chIds, name, title=None, chart_div=None):
    title = title or 'Chart'
    chart_div = chart_div or 'chart_div'
    jslist = [
        '          function %s() {' % name,
        '            var datas = [];']
    jsdata_ncols = [self._GenDataTable(chId) for chId in chIds]
    for jsdata, ncols in jsdata_ncols:
        jslist.extend([
            jsdata,
            '            datas.push(data);',
        ])
    jslist.append('            data = datas[0];')
    i = -1
    for jsdata, ncols in jsdata_ncols:
      i += 1
      if i == 0:
        max_ncols = ncols
        continue
      jslist.append('            data = google.visualization.data.join('
                    "data, datas[%d], 'full', [[0, 0]], %r, %r);" % (
          i, range(1, max_ncols), range(1, ncols)))
      max_ncols = max(max_ncols, ncols)
    jslist.extend([
        self.DRAW % (title, chart_div),
        '          }'])
    return '\n'.join(jslist)

  def _GenMultiChart(self, chIds):
    jslist = [self.HEADER]
    jslist.append(self._GenChartFun(chIds, 'drawAllCharts'))
    jslist.extend([
        self.MID,
        self.DIV % 'chart_div',
        self.FOOTER])
    return '\n'.join(jslist)

  def _GenMultiCharts(self, chDescList):
    """
    Args:
      chDescList: list<{chIds: [], title: , div: }>, Chart descriptors.

    Returns:
      str, Generated Javascript.
    """
    jslist = [self.HEADER]
    for i, chDesc in enumerate(chDescList):
      jslist.append(self._GenChartFun(
          chDesc['chIds'],
          'drawChart%d' % i,
          chDesc.get('title', 'Chart%d' % i),
          chDesc.get('div', 'chart_div%d' % i)))
    jslist.append('          function drawAllCharts() {')
    jslist.extend(['            drawChart%d();' % i
                   for i in xrange(len(chDescList))])
    jslist.extend([
        '          }',
        self.MID])
    for i, chDesc in enumerate(chDescList):
      jslist.append(self.DIV % chDesc.get('div', 'chart_div%d' % i))
    jslist.append(self.FOOTER)
    return '\n'.join(jslist)

  def DrawPlot(self, request):
    """Draws a plot for a single channel."""
    return HttpResponse(self._GenChart(0))

  def DrawMultiPlot(self, request):
    """Draws a plot for several channels."""
    return HttpResponse(self._GenMultiChart([0, 1]))

  def DrawPlots(self, request):
    """Draws multiple plots with multiple charts each."""
    return HttpResponse(self._GenMultiCharts([
      {'chIds': [0, 1]},
      {'chIds': [0, 1], 'title': 'ch01', 'div': 'ch_div1'},
      {'chIds': [1]},
      {'chIds': [1], 'title': 'ch1', 'div': 'ch_div3'},
    ]))


plotter = Plotter()