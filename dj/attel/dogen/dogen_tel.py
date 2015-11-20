import collections

from attel.dogen import dogen_gen


class Sensor(object):
  """Sensor."""
  def __init__(self, descr):
    """Initialize Sensor.

    Args:
      descr: dict, Sensor description.
    """
    self.descr = descr
    runner = dogen_gen.ChannelRunner()

    self.dogen = runner.AddChannel(descr['gen'], self._Callback)
    self.relships = {}

  def connectByRel(self, relship, target):
    """Connect sensor by relship.

    Args:
      relship: str, Relship.
      target: str, Target Id.
    """
    self.relships[relship] = target

  def _Callback(self, point):
    for relship, target in self.relships.iteritems():
      outPoint = point.copy()
      outPoint['relship'] = relship
      self.Propagate(target, outPoint)


class Entity(object):
  """Entity with traces."""
  def __init__(self, entityDescr):
    """"""