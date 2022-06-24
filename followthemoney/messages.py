import yaml
from typing import Any, Dict, Generator, List, TextIO, Tuple, Union

Message = Tuple[Any, Any, List[str], List[str]]


def extract_object(
    data: Dict[str, Any], path: List[str]
) -> Generator[Message, None, None]:
    for key, value in data.items():
        subpath = path + [key]
        if isinstance(value, str):
            if key in ["label", "reverse", "description", "plural"]:
                comment = ".".join(subpath)
                yield (None, None, [value], [comment])
        if isinstance(value, dict):
            for res in extract_object(value, subpath):
                yield res


def extract_yaml(
    fileobj: TextIO, keywords: Any, comment_tags: Any, options: Any
) -> Generator[Message, None, None]:
    data = yaml.safe_load(fileobj)
    return extract_object(data, [])
