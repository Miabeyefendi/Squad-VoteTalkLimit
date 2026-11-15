import os
HERE = os.path.dirname(os.path.abspath(__file__))
import unreal, re

OUT = os.path.join(HERE, "voice_dump.txt")
lines = []
cls_pat = re.compile(r"voice|mute|voip|talk|speak|microphone|\bmic\b|radio|proximity", re.I)
mem_pat = re.compile(r"voice|mute|voip|talk|speak|microphone|(^|_)mic(_|$)|radio|proximity|vote|voting", re.I)

def doc(o, n=1400):
    try:
        return (o.__doc__ or "").strip().replace("\r", "")[:n]
    except Exception as e:
        return "ERR %s" % e

# 1. every class whose own name looks voice related, with all members
names = sorted(dir(unreal))
for name in names:
    obj = getattr(unreal, name, None)
    if not isinstance(obj, type):
        continue
    if cls_pat.search(name):
        lines.append("##### CLASS %s (bases: %s)" % (name, ",".join(b.__name__ for b in obj.__bases__)))
        lines.append(doc(obj, 600))
        try:
            keys = [k for k in obj.__dict__.keys() if not k.startswith("_")]
        except Exception:
            keys = []
        for k in sorted(keys):
            lines.append("--- %s.%s" % (name, k))
            try:
                lines.append(doc(getattr(obj, k)))
            except Exception as e:
                lines.append("ERR %s" % e)

# 2. members of SQ / Squad classes that look voice or vote related
lines.append("\n\n########## MEMBERS OF SQ* CLASSES ##########")
for name in names:
    obj = getattr(unreal, name, None)
    if not isinstance(obj, type):
        continue
    if not (name.startswith("SQ") or name.startswith("Squad")):
        continue
    if cls_pat.search(name):
        continue
    try:
        keys = [k for k in obj.__dict__.keys() if not k.startswith("_") and mem_pat.search(k)]
    except Exception:
        continue
    if not keys:
        continue
    lines.append("##### %s (bases: %s)" % (name, ",".join(b.__name__ for b in obj.__bases__)))
    for k in sorted(keys):
        lines.append("--- %s.%s" % (name, k))
        try:
            lines.append(doc(getattr(obj, k), 700))
        except Exception as e:
            lines.append("ERR %s" % e)

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")
