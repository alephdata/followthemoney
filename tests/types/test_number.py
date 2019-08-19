import unittest

from followthemoney.types import registry

numbers = registry.number


class NumberTest(unittest.TestCase):

    def test_cast_num(self):
        self.assertEqual(numbers._cast_num('1,00,000'), 100000.0)
        self.assertEqual(numbers._cast_num(' -999.0'), -999.0)
        self.assertEqual(numbers._cast_num('- 1,00,000.234'), -100000.234)
        self.assertEqual(numbers._cast_num('99'), 99.0)
