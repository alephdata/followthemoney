import sys
import logging
import balkhash

from followthemoney import model
from followthemoney.types import registry

fmt = "%(name)s [%(levelname)s] %(message)s"
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format=fmt)
registry.text.total_size = 1 * 1024 * 1024

dataset = balkhash.init("memtest", backend="LEVELDB")
text = open("LICENSE", "r").read()
bulk = dataset.bulk()
for i in range(1000000):
    entity = model.make_entity("PlainText")
    entity.id = "banana"
    entity.add("indexText", "%s - %s" % (text, i))
    bulk.put(entity, fragment=str(i))
    print(i)
bulk.flush()


for entity in dataset.iterate():
    print(entity)
