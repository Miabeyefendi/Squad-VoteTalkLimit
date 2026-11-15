"""Prefix every level-2 heading with its section emoji (the translation checker keys on it) and fix anchors."""
import io, os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
README = ["\U0001F6A7", "\u2728", "\U0001F500", "\U0001F4E6", "\U0001F680", "\u2699\uFE0F", "\U0001F9E0", "\u2753", "\U0001F91D", "\U0001F6E1\uFE0F", "\U0001F4DC", "\U0001F4EC"]
TUTORIAL = ["\U0001F4D1", "\U0001F52D", "\U0001FA9C", "\u2699\uFE0F", "\U0001F9EA", "\U0001F527", "\u2753", "\U0001F4D5"]


def slug(text):
    t = re.sub(r"[^\w\s-]", "", text.strip().lower(), flags=re.U)
    return t.replace(" ", "-")


for name in os.listdir(ROOT):
    m = re.match(r"(README|TUTORIAL)(_[A-Z]{2})?\.md$", name)
    if not m:
        continue
    emojis = README if m.group(1) == "README" else TUTORIAL
    path = os.path.join(ROOT, name)
    text = io.open(path, encoding="utf-8").read()
    heads = re.findall(r"^## (.+?)\s*$", text, re.M)
    assert len(heads) == len(emojis), (name, len(heads), heads)
    mapping = {}
    for h, e in zip(heads, emojis):
        mapping[slug(h)] = "-" + slug(h)
    it = iter(emojis)
    text = re.sub(r"^## (.+?)\s*$", lambda mo: "## %s %s" % (next(it), mo.group(1)), text, flags=re.M)
    for old, new in mapping.items():
        text = text.replace("](#%s)" % old, "](#%s)" % new)
    io.open(path, "w", encoding="utf-8", newline="").write(text)
    print(name, "ok")
