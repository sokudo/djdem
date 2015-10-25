import collections
import functools
import pprint
import time

from attel.dogen import dogen_gen


CHANNEL_CONFIG = {
    'name': 'chA',
    'start': {'start': 2000, 'stop': 12000, 'step': 2000},
    'duration': {'start': 20000, 'stop': 30000, 'step': 2000},
    'step': 1000,
    'count': 5,
    'fields': [
        {'name': 'time_ms',
         'fun': dogen_gen.GetCurrentTimeMs},
        {'name': 'yval',
         'fun': functools.partial(
             dogen_gen.GenerateNextInRange,
             {'start': 100, 'step': 10})},
        {'name': 'yv2',
         'fun': functools.partial(
             dogen_gen.GenerateRandomInRange,
             {'start': 100, 'stop': 400})},
    ]}

CHANNEL_CONFIGS = [CHANNEL_CONFIG]


def Run(channelConfigList, outHandler, realTime=False):
  """Runs channels.

  Args:
    channelConfigList: list<channel configuration>.
    outHandler: callable, Called with produced channel messages.
    realTime: bool, Emulate real time run.
  """
  runner = dogen_gen.ChannelRunner(channelConfigList, outHandler)
  time_ms = 0
  while not runner.IsEmpty():
    dogen_gen.SetCurrentTimeMs(time_ms)
    runner.RunTill(time_ms)
    if realTime:
      time.sleep(1)
    time_ms += 1000


class DataCollector(object):
  """Collects channel data by channel id."""

  def __init__(self):
    # Channel id to list of data entities map.
    self.channel_map = collections.defaultdict(list)

  def Add(self, entity):
    self.channel_map[entity['chId']].append(entity)

  def GetAll(self):
    return self.channel_map

  def GetChannelData(self, chId, start_ms=None, stop_ms=None):
    """Get collected channel data.

    Args:
      chId: int, Channel id.
      start_ms: int, Start of a time interval (inclusive).
      stop_ms: int, End of a time interval (non-inclusive).
    Returns:
      list<dict>, A list of a entities within a time interval.
    """
    channelEntities = self.channel_map.get(chId)
    if not channelEntities:
      return channelEntities
    if start_ms is not None:
      channelEntities = (x for x in channelEntities if x['time_ms'] >= start_ms)
    if stop_ms is not None:
      channelEntities = (x for x in channelEntities if x['time_ms'] < stop_ms)
    return list(channelEntities)

  def Clear(self, limit_ms=None):
    """Clears all entities or outdated entities only.

    Args:
      limit_ms: int, A limit. Entities earlier than limit are dropped.
    """
    if limit_ms is None:
      self.channel_map = collections.defaultdict(list)
      return
    for chId, entities in self.channel_map.iteritems():
      self.channel_map[chId] = [x for x in entities if x['time_ms'] < limit_ms]


if __name__ == '__main__':
  Run(CHANNEL_CONFIGS, pprint.pprint)
