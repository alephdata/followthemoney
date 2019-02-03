import unittest

from followthemoney.types import registry

ibans = registry.iban


class IbansTest(unittest.TestCase):

    def test_parse(self):
        self.assertEqual(ibans.clean('GB29 NWBK 6016 1331 9268 19'),
                         'GB29NWBK60161331926819')

    def test_rdf(self):
        rdf = ibans.rdf('GB29NWBK60161331926819')
        assert 'iban:GB29NWBK60161331926819' in rdf

    def test_domain_validity(self):
        self.assertTrue(ibans.validate('GB29 NWBK 6016 1331 9268 19'))
        self.assertTrue(ibans.validate('GB29NWBK60161331926819'))
        self.assertFalse(ibans.validate('GB28 NWBK 6016 1331 9268 19'))
        self.assertFalse(ibans.validate('GB29NWBKN0161331926819'))
        self.assertFalse(ibans.validate(None))
        self.assertTrue(ibans.validate('AL35202111090000000001234567'))
        self.assertTrue(ibans.validate('AD1400080001001234567890'))
        self.assertTrue(ibans.validate('AT483200000012345864'))
        self.assertTrue(ibans.validate('AZ96AZEJ00000000001234567890'))
        self.assertTrue(ibans.validate('BH02CITI00001077181611'))
        # self.assertTrue(ibans.validate('BY86AKBB10100000002966000000'))
        self.assertTrue(ibans.validate('BE71096123456769'))
        self.assertTrue(ibans.validate('BA275680000123456789'))
        self.assertTrue(ibans.validate('BR1500000000000010932840814P2'))
        self.assertTrue(ibans.validate('BG18RZBB91550123456789'))
        # self.assertTrue(ibans.validate('CR37012600000123456789'))
        self.assertTrue(ibans.validate('HR1723600001101234565'))
        self.assertTrue(ibans.validate('CY21002001950000357001234567'))
        self.assertTrue(ibans.validate('CZ5508000000001234567899'))
        self.assertTrue(ibans.validate('DK9520000123456789'))
        self.assertTrue(ibans.validate('DO22ACAU00000000000123456789'))
        # self.assertTrue(ibans.validate('SV43ACAT00000000000000123123'))
        self.assertTrue(ibans.validate('EE471000001020145685'))
        self.assertTrue(ibans.validate('FO9264600123456789'))
        self.assertTrue(ibans.validate('FI1410093000123458'))
        self.assertTrue(ibans.validate('FR7630006000011234567890189'))
        self.assertTrue(ibans.validate('GE60NB0000000123456789'))
        self.assertTrue(ibans.validate('DE91100000000123456789'))
        self.assertTrue(ibans.validate('GI04BARC000001234567890'))
        self.assertTrue(ibans.validate('GR9608100010000001234567890'))
        self.assertTrue(ibans.validate('GL8964710123456789'))
        self.assertTrue(ibans.validate('GT20AGRO00000000001234567890'))
        self.assertTrue(ibans.validate('HU93116000060000000012345676'))
        self.assertTrue(ibans.validate('IS030001121234561234567890'))
        # self.assertTrue(ibans.validate('IQ20CBIQ861800101010500'))
        self.assertTrue(ibans.validate('IE64IRCE92050112345678'))
        self.assertTrue(ibans.validate('IL170108000000012612345'))
        self.assertTrue(ibans.validate('IT60X0542811101000000123456'))
        self.assertTrue(ibans.validate('JO71CBJO0000000000001234567890'))
        self.assertTrue(ibans.validate('KZ563190000012344567'))
        self.assertTrue(ibans.validate('XK051212012345678906'))
        self.assertTrue(ibans.validate('KW81CBKU0000000000001234560101'))
        self.assertTrue(ibans.validate('LV97HABA0012345678910'))
        self.assertTrue(ibans.validate('LB92000700000000123123456123'))
        self.assertTrue(ibans.validate('LI7408806123456789012'))
        self.assertTrue(ibans.validate('LT601010012345678901'))
        self.assertTrue(ibans.validate('LU120010001234567891'))
        self.assertTrue(ibans.validate('MK07200002785123453'))
        self.assertTrue(ibans.validate('MT31MALT01100000000000000000123'))
        self.assertTrue(ibans.validate('MR1300020001010000123456753'))
        self.assertTrue(ibans.validate('MU43BOMM0101123456789101000MUR'))
        self.assertTrue(ibans.validate('MD21EX000000000001234567'))
        self.assertTrue(ibans.validate('MC5810096180790123456789085'))
        self.assertTrue(ibans.validate('ME25505000012345678951'))
        self.assertTrue(ibans.validate('NL02ABNA0123456789'))
        self.assertTrue(ibans.validate('NO8330001234567'))
        self.assertTrue(ibans.validate('PK36SCBL0000001123456702'))
        self.assertTrue(ibans.validate('PS92PALS000000000400123456702'))
        self.assertTrue(ibans.validate('PL10105000997603123456789123'))
        self.assertTrue(ibans.validate('PT50002700000001234567833'))
        self.assertTrue(ibans.validate('QA54QNBA000000000000693123456'))
        self.assertTrue(ibans.validate('RO09BCYP0000001234567890'))
        self.assertTrue(ibans.validate('LC14BOSL123456789012345678901234'))
        self.assertTrue(ibans.validate('SM76P0854009812123456789123'))
        self.assertTrue(ibans.validate('ST23000200000289355710148'))
        self.assertTrue(ibans.validate('SA4420000001234567891234'))
        self.assertTrue(ibans.validate('RS35105008123123123173'))
        self.assertTrue(ibans.validate('SC52BAHL01031234567890123456USD'))
        self.assertTrue(ibans.validate('SK8975000000000012345671'))
        self.assertTrue(ibans.validate('SI56192001234567892'))
        self.assertTrue(ibans.validate('ES7921000813610123456789'))
        self.assertTrue(ibans.validate('SE1412345678901234567890'))
        self.assertTrue(ibans.validate('CH5604835012345678009'))
        self.assertTrue(ibans.validate('TL380080012345678910157'))
        self.assertTrue(ibans.validate('TN4401000067123456789123'))
        self.assertTrue(ibans.validate('TR320010009999901234567890'))
        self.assertTrue(ibans.validate('UA903052992990004149123456789'))
        self.assertTrue(ibans.validate('AE460090000000123456789'))
        self.assertTrue(ibans.validate('GB98MIDL07009312345678'))
        self.assertTrue(ibans.validate('VG21PACG0000000123456789'))

    def test_specificity(self):
        self.assertEqual(ibans.specificity('VG21PACG0000000123456789'), 1)

    def test_country(self):
        iban = 'AE460090000000123456789'
        assert 'ae' == ibans.country_hint(iban)
        assert ibans.country_hint('') is None

    def test_compare(self):
        iban = 'AE460090000000123456789'
        comp = ibans.compare_safe(iban, iban)
        assert comp == 1, comp
        comp = ibans.compare_safe(iban, iban + 'X')
        assert comp == 0, comp
        comp = ibans.compare_safe(iban, None)
        assert comp == 0, comp
