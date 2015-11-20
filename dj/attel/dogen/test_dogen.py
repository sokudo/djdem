"""Tests data generation."""

import collections
import unittest
import pprint

from attel.dogen import dogen_gen


class GenerateTestCase(unittest.TestCase):

  def testGenerateNextChoice(self):
    self.assertIn(dogen_gen.GenerateNextChoice((1, 2, 3)), (1, 2, 3))
    self.assertEqual(2, dogen_gen.GenerateNextChoice((1, 2, 3), 1))
    self.assertEqual(1, dogen_gen.GenerateNextChoice((1, 2, 3), 3))
    self.assertRaises(ValueError, dogen_gen.GenerateNextChoice, (1, 2, 3), 4)

  def testGenerateNextInRange(self):
    irange = {'start': 2, 'stop': 5}
    self.assertEqual(2, dogen_gen.GenerateNextInRange(irange, None))
    self.assertEqual(3, dogen_gen.GenerateNextInRange(irange, 2))
    self.assertEqual(2, dogen_gen.GenerateNextInRange(irange, 4))

    frange = {'start': 2.0, 'stop': 5, 'step': 1.5}
    self.assertAlmostEqual(2.0, dogen_gen.GenerateNextInRange(frange, None))
    self.assertAlmostEqual(3.5, dogen_gen.GenerateNextInRange(frange, 2.0))
    self.assertAlmostEqual(2.0, dogen_gen.GenerateNextInRange(frange, 3.5))


class ChannelRunnerTestCase(unittest.TestCase):

  CHANNEL_DATA = [
      {'name': 'chName',
       'start': 10000,
       'duration': 20000,
       'step': 1000,
       'fields': [
           {'name': 'kind',
            'init': 'chKind'},
           {'name': 'val',
            'init': 1,
            'fun': lambda prev: prev + 1}]
      },
      {'name': 'chName',
       'start': 15000,
       'duration': 10000,
       'step': 500,
       'fields': [
           {'name': 'kind',
            'init': 'kind1'},
           {'name': 'fval',
            'init': 1.0,
            'fun': lambda prev: prev + 2.0}]
      }]

  def setUp(self):
    self.output = collections.defaultdict(list)

  def OutHandler(self, ent):
    self.output[ent['chId']].append(ent)

  def testOneChannel(self):
    runner = dogen_gen.ChannelRunner()
    runner.AddChannel(self.CHANNEL_DATA[0], self.OutHandler)
    ii = 1
    for time_ms in xrange(10000, 30000, 1000):
      dogen_gen.SetCurrentTimeMs(time_ms)
      runner.RunTill(time_ms)

      ent = self.output[0][-1]
      expected = {
          'time_ms': dogen_gen.GetCurrentTimeMs(),
          'kind': 'chKind',
          'chId': 0,
          'val': ii}
      self.assertEqual(expected, ent)
      ii += 1

  def testChannels(self):

    runner = dogen_gen.ChannelRunner(self.OutHandler)
    for d in self.CHANNEL_DATA:
      runner.AddChannel(d)
    for time_ms in xrange(0, 31000, 500):
      dogen_gen.SetCurrentTimeMs(time_ms)
      runner.RunTill(time_ms)

    ii = 1
    expected = collections.defaultdict(list)
    for time_ms in xrange(10000, 30000, 1000):
      expected[0].append({
          'time_ms': time_ms,
          'kind': 'chKind',
          'chId': 0,
          'val': ii})
      ii += 1
    fval = 1.0
    for time_ms in xrange(15000, 25000, 500):
      expected[1].append({
          'time_ms': time_ms,
          'kind': 'kind1',
          'chId': 1,
          'fval': fval})
      fval += 2.0

    self.assertEqual(expected, self.output)

if __name__ == '__main__':
  unittest.main()
