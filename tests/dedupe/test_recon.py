import io
from unittest import TestCase

from followthemoney.dedupe import Recon


class ReconTestCase(TestCase):

    def test_recon_serialize(self):
        recon = Recon('foo', 'bar', Recon.MATCH)
        text = recon.to_json()
        assert 'foo' in text, text
        assert 'bar' in text, text
        other = recon.from_json(text)
        assert other.subject == recon.subject
        assert other.canonical == recon.canonical
        assert other.canonical != recon.subject
        assert other.judgement == recon.judgement

        sio = io.StringIO(text)
        items = list(Recon.from_file(sio))
        assert len(items) == 1
