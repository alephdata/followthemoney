# -*- coding: utf-8 -*-
import unittest
from datetime import datetime

from followthemoney.types import dates


class DatesTest(unittest.TestCase):

    def test_validate(self):
        self.assertTrue(dates.validate('2017-04-04T10:30:29'))
        self.assertTrue(dates.validate('2017-04-04T10:30:29Z'))
        self.assertTrue(dates.validate('2017-04-04T10:30:29+01'))
        self.assertTrue(dates.validate('2017-04-04T10:30:29+0200'))
        self.assertTrue(dates.validate('2017-04-04T10:30:29+03:00'))
        self.assertTrue(dates.validate('2017-04-04T10:30:29-04:00'))
        self.assertTrue(dates.validate(datetime.utcnow().isoformat()))
        self.assertFalse(dates.validate('01-02-2003'))
        self.assertFalse(dates.validate('Thursday 21 March 2017'))

    def test_is_partial_date(self):
        self.assertTrue(dates.validate('2017-04-04 10:30:29'))
        self.assertTrue(dates.validate('2017-04-04 10:30'))
        self.assertTrue(dates.validate('2017-04-04 10'))
        self.assertTrue(dates.validate('2017-04-04'))
        self.assertTrue(dates.validate('2017-4-4'))
        self.assertTrue(dates.validate('2017-4'))
        self.assertTrue(dates.validate('2017'))
        self.assertFalse(dates.validate('0017'))
        self.assertFalse(dates.validate(None))
        self.assertFalse(dates.validate(5))
        self.assertFalse(dates.validate('2017-20-01'))

    def test_chop_dates(self):
        self.assertEquals(dates.clean('2017-00-00'), '2017')
        self.assertEquals(dates.clean('2017-00-00T00:00:00'), '2017')
        self.assertEquals(dates.clean('2017-00-00T12:03:49'), '2017')
        self.assertEquals(dates.clean('2017-01-01T00:00:00'), '2017-01-01')

    def test_patch_dates(self):
        self.assertEquals(dates.clean('2017-1-3'), '2017-01-03')
        self.assertEquals(dates.clean('2017-3'), '2017-03')
        self.assertEquals(dates.clean('2017-0'), '2017')
        self.assertEquals(dates.clean('2017-5-2T00:00:00'), '2017-05-02')
        self.assertEquals(dates.clean('2017-5-2T10:00:00'), '2017-05-02T10:00:00')  # noqa

    def test_convert_datetime(self):
        dt = datetime.utcnow()
        iso, _ = dt.isoformat().split('.', 1)
        self.assertEquals(dates.clean(dt), iso)
        self.assertTrue(dates.validate(iso))

        dt = datetime.utcnow().date()
        iso = dt.isoformat()
        self.assertEquals(dates.clean(dt), iso)

    def test_parse_date(self):
        self.assertEquals(dates.clean(None), None)
        self.assertEquals(dates.clean(''), None)
        self.assertEquals(dates.clean('2017-04-04'), '2017-04-04')
        self.assertEquals(dates.clean('2017-4-4'), '2017-04-04')

        self.assertEquals(dates.clean('23-AUG-2001'), '2001-08-23')
        self.assertEquals(dates.clean('09-jun-1993'), '1993-06-09')

        # TODO: make this yield an imprecise date somehow?
        self.assertEquals(dates.clean('4/2017', format="%m/%Y"), '2017-04-01')
        self.assertEquals(dates.clean('4/2xx017', format="%m/%Y"), None)

    def test_guess_date(self):
        self.assertEquals(dates.clean('12.4.2017'), '2017-04-12')

    def test_fuzzy_date_parser_failure(self):
        self.assertEquals(dates.fuzzy_date_parser('nothing'), None)

    def test_fuzzy_date_parser_success_english(self):
        result = dates.fuzzy_date_parser('15 march, 1987')
        self.assertIsInstance(result, datetime)
        self.assertEqual(result.strftime('%x'), '03/15/87')

    def test_fuzzy_date_parser_success_german(self):
        result = dates.fuzzy_date_parser(u'15. März 1987')
        self.assertIsInstance(result, datetime)
        self.assertEqual(result.strftime('%x'), '03/15/87')

    def test_fuzzy_date_parser_success_spanish(self):
        result = dates.fuzzy_date_parser(u'15 Marzo 1987')
        self.assertIsInstance(result, datetime)
        self.assertEqual(result.strftime('%x'), '03/15/87')
