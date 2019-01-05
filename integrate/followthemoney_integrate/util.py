from normality import normalize


def text_parts(text):
    text = normalize(text, latinize=True)
    if text is None:
        return set()
    return set(text.split(' '))


def index_text(proxy):
    texts = set()
    for name in proxy.names:
        texts.update(text_parts(name))
    return ' '.join(texts)
