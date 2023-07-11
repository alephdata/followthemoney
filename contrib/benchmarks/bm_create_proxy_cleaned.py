import os
from platform import python_version
from timeit import timeit

from followthemoney import model
from followthemoney.proxy import EntityProxy

ITERATIONS = 1_000_000

ENTITY = {
    "id": "test",
    "schema": "Person",
    "properties": {
        "name": ["Ralph Tester", "Ralph Tester", "Ralf Tester"],
        "birthDate": ["1972-05-01"],
        "idNumber": ["9177171", "8e839023"],
        "website": ["https://ralphtester.me"],
        "phone": ["+12025557612", "+12025557612", "+12025557612"],
        "email": ["info@ralphtester.me", "info@ralphtester.org", "info@ralphtester.com"],
        "topics": ["role.spy"],
    },
}


def create_proxy(data):
    proxy = EntityProxy.from_dict(model, data, cleaned=True)
    data = proxy.to_dict()
    return data


def benchmark():
    for _ in range(ITERATIONS):
        create_proxy(ENTITY)


if __name__ == "__main__":
    commit = os.environ.get("GIT_COMMIT", "None")
    version = python_version()
    time = timeit(benchmark, number=10)
    print(f"{commit},{version},{time}")
