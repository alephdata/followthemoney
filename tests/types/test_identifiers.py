from followthemoney.types import registry
from followthemoney import model

identifiers = registry.identifier


def iban_valid(text: str) -> bool:
    return registry.identifier.validate(text, format="iban")


def test_parse():
    assert identifiers.clean("88/9") == "88/9"


def test_domain_validity():
    assert identifiers.validate("foo@pudo.org")


def test_compare():
    assert identifiers.compare("AS9818700", "9818700") > 0
    assert identifiers.compare_safe(None, "9818700") == 0
    assert identifiers.compare_sets(["AS9818700"], ["9818700"]) > 0
    assert identifiers.compare_sets(["9818700"], ["AS9818700"]) > 0
    iban = "AE460090000000123456789"
    assert identifiers.compare_safe(iban, iban) == 1


def test_iban_parse():
    val = "GB29 NWBK 6016 1331 9268 19"
    assert identifiers.clean(val) == val
    assert identifiers.clean(val, format="iban") == "GB29NWBK60161331926819"


def test_imo_format():
    assert identifiers.clean_text("IMO1234567") == "IMO1234567"
    assert identifiers.caption("IMO1234567", format="imo") == "IMO1234567"

    vessel = model.get("Vessel")
    prop = vessel.get("imoNumber")
    assert prop.caption("IMO 1234567") == "IMO1234567"


def test_specificity():
    assert identifiers.specificity("VG21PACG0000000123456789") == 1
    assert identifiers.specificity("123") < 1
    assert identifiers.specificity("") == 0


def test_invalid_identifiers():
    assert identifiers.validate("not-an-email")
    assert identifiers.validate("123")
    assert not identifiers.validate("")


def test_iban_validation():
    assert iban_valid("GB29 NWBK 6016 1331 9268 19")
    assert iban_valid("GB29NWBK60161331926819")
    assert not iban_valid("GB28 NWBK 6016 1331 9268 19")
    assert not iban_valid("GB29NWBKN0161331926819")
    assert not iban_valid("")
    assert iban_valid("AL35202111090000000001234567")
    assert iban_valid("AD1400080001001234567890")
    assert iban_valid("AT483200000012345864")
    assert iban_valid("AZ96AZEJ00000000001234567890")
    assert iban_valid("BH02CITI00001077181611")
    # assert iban_valid('BY86AKBB10100000002966000000')
    assert iban_valid("BE71096123456769")
    assert iban_valid("BA275680000123456789")
    assert iban_valid("BR1500000000000010932840814P2")
    assert iban_valid("BG18RZBB91550123456789")
    # assert iban_valid('CR37012600000123456789')
    assert iban_valid("HR1723600001101234565")
    assert iban_valid("CY21002001950000357001234567")
    assert iban_valid("CZ5508000000001234567899")
    assert iban_valid("DK9520000123456789")
    assert iban_valid("DO22ACAU00000000000123456789")
    # assert iban_valid('SV43ACAT00000000000000123123')
    assert iban_valid("EE471000001020145685")
    assert iban_valid("FO9264600123456789")
    assert iban_valid("FI1410093000123458")
    assert iban_valid("FR7630006000011234567890189")
    assert iban_valid("GE60NB0000000123456789")
    assert iban_valid("DE91100000000123456789")
    assert iban_valid("GI04BARC000001234567890")
    assert iban_valid("GR9608100010000001234567890")
    assert iban_valid("GL8964710123456789")
    assert iban_valid("GT20AGRO00000000001234567890")
    assert iban_valid("HU93116000060000000012345676")
    assert iban_valid("IS030001121234561234567890")
    # assert iban_valid('IQ20CBIQ861800101010500')
    assert iban_valid("IE64IRCE92050112345678")
    assert iban_valid("IL170108000000012612345")
    assert iban_valid("IT60X0542811101000000123456")
    assert iban_valid("JO71CBJO0000000000001234567890")
    assert iban_valid("KZ563190000012344567")
    assert iban_valid("XK051212012345678906")
    assert iban_valid("KW81CBKU0000000000001234560101")
    assert iban_valid("LV97HABA0012345678910")
    assert iban_valid("LB92000700000000123123456123")
    assert iban_valid("LI7408806123456789012")
    assert iban_valid("LT601010012345678901")
    assert iban_valid("LU120010001234567891")
    assert iban_valid("MK07200002785123453")
    assert iban_valid("MT31MALT01100000000000000000123")
    assert iban_valid("MR1300020001010000123456753")
    assert iban_valid("MU43BOMM0101123456789101000MUR")
    assert iban_valid("MD21EX000000000001234567")
    assert iban_valid("MC5810096180790123456789085")
    assert iban_valid("ME25505000012345678951")
    assert iban_valid("NL02ABNA0123456789")
    assert iban_valid("NO8330001234567")
    assert iban_valid("PK36SCBL0000001123456702")
    assert iban_valid("PS92PALS000000000400123456702")
    assert iban_valid("PL10105000997603123456789123")
    assert iban_valid("PT50002700000001234567833")
    assert iban_valid("QA54QNBA000000000000693123456")
    assert iban_valid("RO09BCYP0000001234567890")
    assert iban_valid("LC14BOSL123456789012345678901234")
    assert iban_valid("SM76P0854009812123456789123")
    assert iban_valid("ST23000200000289355710148")
    assert iban_valid("SA4420000001234567891234")
    assert iban_valid("RS35105008123123123173")
    assert iban_valid("SC52BAHL01031234567890123456USD")
    assert iban_valid("SK8975000000000012345671")
    assert iban_valid("SI56192001234567892")
    assert iban_valid("ES7921000813610123456789")
    assert iban_valid("SE1412345678901234567890")
    assert iban_valid("CH5604835012345678009")
    assert iban_valid("TL380080012345678910157")
    assert iban_valid("TN4401000067123456789123")
    assert iban_valid("TR320010009999901234567890")
    assert iban_valid("UA903052992990004149123456789")
    assert iban_valid("AE460090000000123456789")
    assert iban_valid("GB98MIDL07009312345678")
    assert iban_valid("VG21PACG0000000123456789")
