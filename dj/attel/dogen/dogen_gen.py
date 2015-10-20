"""Data generation.

  channel_set descr = {
      name: str,
      start: InRange or Number,
      duration: InRange or Number,
      step: InRange or Number,
      count: int,
      fields: [Field, ]}

  InRange is {
      start: Number,
      stop: Number,
      opt step: Number,
      opt random: Bool}

  Field is {
      name: str,
      fun: callable or Value,
      opt init: Value}

"""

import random
import Queue


_CurrentTimeMs = 0


def GetCurrentTimeMs(prev=None):
  return _CurrentTimeMs


def SetCurrentTimeMs(time_ms):
  global _CurrentTimeMs
  _CurrentTimeMs = time_ms


def _NextInRange(inrangeOrNum, prev):
  if not isinstance(inrangeOrNum, dict):
    return inrangeOrNum
  inrange = inrangeOrNum
  if inrange.get('random'):
    return GenerateRandomInRange(inrange)
  return GenerateNextInRange(inrange, prev)


def GetMaxInRange(inrangeOrNum):
  if not isinstance(inrangeOrNum, dict):
    return inrangeOrNum
  return inrangeOrNum.get('stop')


def CreateChannels(chIdBase, descr):
  """Creates data generation channels.

  Args:
    chIdBase: int, A channel id base value.
    descr: dict, A channel_set.
  Yields:
    list<dict>, channels.
  """
  for field_descr in descr['fields']:
    if 'init' not in field_descr and 'fun' not in field_descr:
      raise AttributeError('no init and fun in %s', descr['name'])

  start, duration = None, None
  for channel_index in xrange(descr.get('count', 1)):
    name = '%s_%i' % (descr['name'], channel_index)
    start = _NextInRange(descr['start'], start)
    duration = _NextInRange(descr['duration'], duration)
    channel = {
        'name': name,
        'chId': chIdBase + channel_index,
        'start': start,
        'stop': start + duration,
        'step': _NextInRange(descr.get('step', 1), None),
        'fields': descr['fields'],
    }
    yield channel


def GetNextTimeMs(channel):
  if 'prevPoint' not in channel:
    return channel['start']
  time_ms = channel['prevPoint']['time_ms'] + channel['step']
  return time_ms if time_ms < channel['stop'] else None


class ChannelRunner(object):
  def __init__(self, descrSeq, sender):
    self.channelQueue = Queue.PriorityQueue()
    self.sender = sender
    chIdBase = 0
    for descr in descrSeq:
      for channel in CreateChannels(chIdBase, descr):
        chIdBase += 1
        next_ms = GetNextTimeMs(channel)
        if next_ms is not None:
          self.channelQueue.put((next_ms, channel))

  def IsEmpty(self):
    return self.channelQueue.empty()

  def RunTill(self, limit_ms):
    try:
      while True:
        time_ms, channel = self.channelQueue.get_nowait()
        if time_ms > limit_ms:
          self.channelQueue.put((time_ms, channel))
          return
        point = GenerateChannelData(channel)
        channel['prevPoint'] = point
        self.sender(point)
        next_ms = GetNextTimeMs(channel)
        if next_ms is not None:
          self.channelQueue.put((next_ms, channel))
    except Queue.Empty:
      pass


def GenerateChannelData(channel):
  point = GenerateDataPoint(channel, channel.get('prevPoint'))
  point['time_ms'] = GetCurrentTimeMs()
  point['chId'] = channel['chId']
  return point


def GenerateDataPoint(channel, prev=None):
  """Generates a data point given a metadata descriptor and a previous value.

  Args:
    channel: dict, A channel.
    prev: dict, A previous value.
  """
  result = {}
  for field_descr in channel['fields']:
    name = field_descr['name']
    if not prev and 'init' in field_descr:
      result[name] = field_descr['init']
      continue
    prev_value = prev.get(name) if prev else None
    result[name] = field_descr.get('fun', lambda prev: prev)(prev=prev_value)
  return result


def GenerateRandomInRange(range, prev=None):
  """Generates random value in range.

  Args:
    range: dict, A range descriptor:
      {start: Value, stop: Value, opt step: Value}
    prev: unused.
  Returns:
    int or float, Random value.
  """
  start, stop = range['start'], range['stop']
  if type(start) == float or type(stop) == float:
    return random.uniform(start, stop)
  if 'step' in range:
    return random.randrange(start, stop, range['step'])
  return random.randint(start, stop)


def GenerateNextInRange(range, prev=None):
  """Generates next value in range.

  Args:
    range: dict, A range descriptor:
      {start: Value, stop: Value, opt step: Value}
    prev: int or float or None, A previous value or None.
  Returns:
    int or float, Random value.
  """
  start = range['start']
  if prev is None:
    return start
  stop = range.get('stop')
  step = range.get('step', 1)
  if stop is None:
    return prev + step
  if type(start) == float or type(stop) == float:
    return start + (float(prev) - start + step) % (stop - start)
  return start + (prev - start + step) % (stop - start)


def GenerateRandomChoice(choices, prev=None):
  """Generates a random choice from a sequence.

  Args:
    choices: sequence.
  Returns:
    A value.
  """
  return random.choice(choices)


def GenerateNextChoice(choices, prev=None):
  """Generates the next choice from a sequence (round robin).

  Args:
    choices: sequence.
  Returns:
    A value.
  """
  if prev is None:
    return GenerateRandomChoice(choices, prev)
  return choices[(choices.index(prev) + 1) % len(choices)]
