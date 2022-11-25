import re
from docutils import core
from pathlib import Path
import json
from followthemoney.types import registry

def rst_to_html(source):
    parts = core.publish_parts(source=source, writer_name='html')
    return parts['fragment']

if __name__ == "__main__":
  out_dir = Path(__file__, '../../src').resolve()
  out_file = Path(out_dir, 'types.json').resolve()

  print(out_dir)
  print(out_file)

  out_dir.mkdir(parents=True, exist_ok=True)
  descriptions = {}

  for prop_type in registry.types:
    docstring = prop_type.__doc__
    docstring = re.sub(r'^[ \t]+', '', docstring, flags=re.MULTILINE)
    descriptions[prop_type.name] = rst_to_html(docstring)

  out_file.write_text(json.dumps(descriptions))
