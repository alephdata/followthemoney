import six
import yaml


def extract_object(data, path):
    for key, value in data.items():
        subpath = path + [key]
        if isinstance(value, six.string_types):
            if key in ['label', 'reverse', 'description', 'plural']:
                comment = '.'.join(subpath)
                yield (None, None, [value], [comment])
        if isinstance(value, dict):
            for res in extract_object(value, subpath):
                yield res


def extract_yaml(fileobj, keywords, comment_tags, options):
    data = yaml.safe_load(fileobj)
    return extract_object(data, [])
