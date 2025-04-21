from followthemoney.types import registry

ibans = registry.iban


def test_parse():
    assert ibans.clean("GB29 NWBK 6016 1331 9268 19") == "GB29NWBK60161331926819"


def test_rdf():
    rdf = ibans.rdf("GB29NWBK60161331926819")
    assert "iban:GB29NWBK60161331926819" in rdf
    nid = ibans.node_id("gb29NWBK60161331926819")
    assert nid is not None
    assert "iban:GB" in nid


def test_domain_validity():
    assert ibans.validate("GB29 NWBK 6016 1331 9268 19") is True
    assert ibans.validate("GB29NWBK60161331926819") is True
    assert ibans.validate("GB28 NWBK 6016 1331 9268 19") is False
    assert ibans.validate("GB29NWBKN0161331926819") is False
    assert ibans.validate("") is False
    assert ibans.validate("AL35202111090000000001234567") is True
    assert ibans.validate("AD1400080001001234567890") is True
    assert ibans.validate("AT483200000012345864") is True
    assert ibans.validate("AZ96AZEJ00000000001234567890") is True
    assert ibans.validate("BH02CITI00001077181611") is True
    # assert ibans.validate('BY86AKBB10100000002966000000') is True
    assert ibans.validate("BE71096123456769") is True
    assert ibans.validate("BA275680000123456789") is True
    assert ibans.validate("BR1500000000000010932840814P2") is True
    assert ibans.validate("BG18RZBB91550123456789") is True
    # assert ibans.validate('CR37012600000123456789') is True
    assert ibans.validate("HR1723600001101234565") is True
    assert ibans.validate("CY21002001950000357001234567") is True
    assert ibans.validate("CZ5508000000001234567899") is True
    assert ibans.validate("DK9520000123456789") is True
    assert ibans.validate("DO22ACAU00000000000123456789") is True
    # assert ibans.validate('SV43ACAT00000000000000123123') is True
    assert ibans.validate("EE471000001020145685") is True
    assert ibans.validate("FO9264600123456789") is True
    assert ibans.validate("FI1410093000123458") is True
    assert ibans.validate("FR7630006000011234567890189") is True
    assert ibans.validate("GE60NB0000000123456789") is True
    assert ibans.validate("DE91100000000123456789") is True
    assert ibans.validate("GI04BARC000001234567890") is True
    assert ibans.validate("GR9608100010000001234567890") is True
    assert ibans.validate("GL8964710123456789") is True
    assert ibans.validate("GT20AGRO00000000001234567890") is True
    assert ibans.validate("HU93116000060000000012345676") is True
    assert ibans.validate("IS030001121234561234567890") is True
    # assert ibans.validate('IQ20CBIQ861800101010500') is True
    assert ibans.validate("IE64IRCE92050112345678") is True
    assert ibans.validate("IL170108000000012612345") is True
    assert ibans.validate("IT60X0542811101000000123456") is True
    assert ibans.validate("JO71CBJO0000000000001234567890") is True
    assert ibans.validate("KZ563190000012344567") is True
    assert ibans.validate("XK051212012345678906") is True
    assert ibans.validate("KW81CBKU0000000000001234560101") is True
    assert ibans.validate("LV97HABA0012345678910") is True
    assert ibans.validate("LB92000700000000123123456123") is True
    assert ibans.validate("LI7408806123456789012") is True
    assert ibans.validate("LT601010012345678901") is True
    assert ibans.validate("LU120010001234567891") is True
    assert ibans.validate("MK07200002785123453") is True
    assert ibans.validate("MT31MALT01100000000000000000123") is True
    assert ibans.validate("MR1300020001010000123456753") is True
    assert ibans.validate("MU43BOMM0101123456789101000MUR") is True
    assert ibans.validate("MD21EX000000000001234567") is True
    assert ibans.validate("MC5810096180790123456789085") is True
    assert ibans.validate("ME25505000012345678951") is True
    assert ibans.validate("NL02ABNA0123456789") is True
    assert ibans.validate("NO8330001234567") is True
    assert ibans.validate("PK36SCBL0000001123456702") is True
    assert ibans.validate("PS92PALS000000000400123456702") is True
    assert ibans.validate("PL10105000997603123456789123") is True
    assert ibans.validate("PT50002700000001234567833") is True
    assert ibans.validate("QA54QNBA000000000000693123456") is True
    assert ibans.validate("RO09BCYP0000001234567890") is True
    assert ibans.validate("LC14BOSL123456789012345678901234") is True
    assert ibans.validate("SM76P0854009812123456789123") is True
    assert ibans.validate("ST23000200000289355710148") is True
    assert ibans.validate("SA4420000001234567891234") is True
    assert ibans.validate("RS35105008123123123173") is True
    assert ibans.validate("SC52BAHL01031234567890123456USD") is True
    assert ibans.validate("SK8975000000000012345671") is True
    assert ibans.validate("SI56192001234567892") is True
    assert ibans.validate("ES7921000813610123456789") is True
    assert ibans.validate("SE1412345678901234567890") is True
    assert ibans.validate("CH5604835012345678009") is True
    assert ibans.validate("TL380080012345678910157") is True
    assert ibans.validate("TN4401000067123456789123") is True
    assert ibans.validate("TR320010009999901234567890") is True
    assert ibans.validate("UA903052992990004149123456789") is True
    assert ibans.validate("AE460090000000123456789") is True
    assert ibans.validate("GB98MIDL07009312345678") is True
    assert ibans.validate("VG21PACG0000000123456789") is True


def test_specificity():
    assert ibans.specificity("VG21PACG0000000123456789") == 1


def test_country():
    iban = "AE460090000000123456789"
    assert ibans.country_hint(iban) == "ae"


def test_compare():
    iban = "AE460090000000123456789"
    comp = ibans.compare_safe(iban, iban)
    assert comp == 1
    comp = ibans.compare_safe(iban, iban + "X")
    assert comp == 0
    comp = ibans.compare_safe(iban, None)
    assert comp == 0
