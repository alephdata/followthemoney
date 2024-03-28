import unittest

from followthemoney.types import registry

identifiers = registry.identifier

def iban_valid(text: str) -> bool:
    return registry.identifier.validate(text, format='iban')


class IdentifiersTest(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(identifiers.clean("88/9"), "88/9")

    def test_domain_validity(self):
        self.assertTrue(identifiers.validate("foo@pudo.org"))

    def test_compare(self):
        comp = identifiers.compare("AS9818700", "9818700")
        assert comp > 0, comp
        comp = identifiers.compare_safe(None, "9818700")
        assert comp == 0, comp
        comp = identifiers.compare_sets(["AS9818700"], ["9818700"])
        assert comp > 0, comp
        comp = identifiers.compare_sets(["9818700"], ["AS9818700"])
        assert comp > 0, comp
        iban = "AE460090000000123456789"
        comp = identifiers.compare_safe(iban, iban)
        assert comp == 1, comp
        
    def test_iban_parse(self):
        val = "GB29 NWBK 6016 1331 9268 19"
        self.assertEqual(identifiers.clean(val), val)
        self.assertEqual(
            identifiers.clean(val, format='iban'),
            "GB29NWBK60161331926819"
        )

    def test_specificity(self):
        self.assertEqual(identifiers.specificity("VG21PACG0000000123456789"), 1)

    def test_iban_validation(self):
        self.assertTrue(iban_valid("GB29 NWBK 6016 1331 9268 19"))
        self.assertTrue(iban_valid("GB29NWBK60161331926819"))
        self.assertFalse(iban_valid("GB28 NWBK 6016 1331 9268 19"))
        self.assertFalse(iban_valid("GB29NWBKN0161331926819"))
        self.assertFalse(iban_valid(""))
        self.assertTrue(iban_valid("AL35202111090000000001234567"))
        self.assertTrue(iban_valid("AD1400080001001234567890"))
        self.assertTrue(iban_valid("AT483200000012345864"))
        self.assertTrue(iban_valid("AZ96AZEJ00000000001234567890"))
        self.assertTrue(iban_valid("BH02CITI00001077181611"))
        # self.assertTrue(iban_valid('BY86AKBB10100000002966000000'))
        self.assertTrue(iban_valid("BE71096123456769"))
        self.assertTrue(iban_valid("BA275680000123456789"))
        self.assertTrue(iban_valid("BR1500000000000010932840814P2"))
        self.assertTrue(iban_valid("BG18RZBB91550123456789"))
        # self.assertTrue(iban_valid('CR37012600000123456789'))
        self.assertTrue(iban_valid("HR1723600001101234565"))
        self.assertTrue(iban_valid("CY21002001950000357001234567"))
        self.assertTrue(iban_valid("CZ5508000000001234567899"))
        self.assertTrue(iban_valid("DK9520000123456789"))
        self.assertTrue(iban_valid("DO22ACAU00000000000123456789"))
        # self.assertTrue(iban_valid('SV43ACAT00000000000000123123'))
        self.assertTrue(iban_valid("EE471000001020145685"))
        self.assertTrue(iban_valid("FO9264600123456789"))
        self.assertTrue(iban_valid("FI1410093000123458"))
        self.assertTrue(iban_valid("FR7630006000011234567890189"))
        self.assertTrue(iban_valid("GE60NB0000000123456789"))
        self.assertTrue(iban_valid("DE91100000000123456789"))
        self.assertTrue(iban_valid("GI04BARC000001234567890"))
        self.assertTrue(iban_valid("GR9608100010000001234567890"))
        self.assertTrue(iban_valid("GL8964710123456789"))
        self.assertTrue(iban_valid("GT20AGRO00000000001234567890"))
        self.assertTrue(iban_valid("HU93116000060000000012345676"))
        self.assertTrue(iban_valid("IS030001121234561234567890"))
        # self.assertTrue(iban_valid('IQ20CBIQ861800101010500'))
        self.assertTrue(iban_valid("IE64IRCE92050112345678"))
        self.assertTrue(iban_valid("IL170108000000012612345"))
        self.assertTrue(iban_valid("IT60X0542811101000000123456"))
        self.assertTrue(iban_valid("JO71CBJO0000000000001234567890"))
        self.assertTrue(iban_valid("KZ563190000012344567"))
        self.assertTrue(iban_valid("XK051212012345678906"))
        self.assertTrue(iban_valid("KW81CBKU0000000000001234560101"))
        self.assertTrue(iban_valid("LV97HABA0012345678910"))
        self.assertTrue(iban_valid("LB92000700000000123123456123"))
        self.assertTrue(iban_valid("LI7408806123456789012"))
        self.assertTrue(iban_valid("LT601010012345678901"))
        self.assertTrue(iban_valid("LU120010001234567891"))
        self.assertTrue(iban_valid("MK07200002785123453"))
        self.assertTrue(iban_valid("MT31MALT01100000000000000000123"))
        self.assertTrue(iban_valid("MR1300020001010000123456753"))
        self.assertTrue(iban_valid("MU43BOMM0101123456789101000MUR"))
        self.assertTrue(iban_valid("MD21EX000000000001234567"))
        self.assertTrue(iban_valid("MC5810096180790123456789085"))
        self.assertTrue(iban_valid("ME25505000012345678951"))
        self.assertTrue(iban_valid("NL02ABNA0123456789"))
        self.assertTrue(iban_valid("NO8330001234567"))
        self.assertTrue(iban_valid("PK36SCBL0000001123456702"))
        self.assertTrue(iban_valid("PS92PALS000000000400123456702"))
        self.assertTrue(iban_valid("PL10105000997603123456789123"))
        self.assertTrue(iban_valid("PT50002700000001234567833"))
        self.assertTrue(iban_valid("QA54QNBA000000000000693123456"))
        self.assertTrue(iban_valid("RO09BCYP0000001234567890"))
        self.assertTrue(iban_valid("LC14BOSL123456789012345678901234"))
        self.assertTrue(iban_valid("SM76P0854009812123456789123"))
        self.assertTrue(iban_valid("ST23000200000289355710148"))
        self.assertTrue(iban_valid("SA4420000001234567891234"))
        self.assertTrue(iban_valid("RS35105008123123123173"))
        self.assertTrue(iban_valid("SC52BAHL01031234567890123456USD"))
        self.assertTrue(iban_valid("SK8975000000000012345671"))
        self.assertTrue(iban_valid("SI56192001234567892"))
        self.assertTrue(iban_valid("ES7921000813610123456789"))
        self.assertTrue(iban_valid("SE1412345678901234567890"))
        self.assertTrue(iban_valid("CH5604835012345678009"))
        self.assertTrue(iban_valid("TL380080012345678910157"))
        self.assertTrue(iban_valid("TN4401000067123456789123"))
        self.assertTrue(iban_valid("TR320010009999901234567890"))
        self.assertTrue(iban_valid("UA903052992990004149123456789"))
        self.assertTrue(iban_valid("AE460090000000123456789"))
        self.assertTrue(iban_valid("GB98MIDL07009312345678"))
        self.assertTrue(iban_valid("VG21PACG0000000123456789"))
