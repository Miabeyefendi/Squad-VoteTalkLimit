import os
HERE = os.path.dirname(os.path.abspath(__file__))
import unreal, re

OUT = os.path.join(HERE, "msg_dump.txt")
lines = []
pat = re.compile(r"message|warn|notif|toast|popup|admin_|server_message|client_|print|hud_text|show_text|announce", re.I)


def doc(o, n=500):
    try:
        return (o.__doc__ or "").strip().replace("\r", "")[:n]
    except Exception as e:
        return "ERR %s" % e


for name in ("SQPlayerController", "PlayerController", "SQBlueprintLibrary", "SQPlayerState", "SQGameRuleSet", "SQGameMode"):
    obj = getattr(unreal, name, None)
    lines.append("##### %s %s" % (name, "MISSING" if obj is None else ""))
    if obj is None:
        continue
    for k in sorted(k for k in obj.__dict__.keys() if not k.startswith("_") and pat.search(k)):
        lines.append("--- %s.%s" % (name, k))
        try:
            lines.append(doc(getattr(obj, k)))
        except Exception as e:
            lines.append("ERR %s" % e)

lines.append("##### BlueprintEditorLibrary")
bel = getattr(unreal, "BlueprintEditorLibrary", None)
lines.append("MISSING" if bel is None else ", ".join(sorted(k for k in dir(bel) if not k.startswith("_"))))
lines.append("##### KismetEditorUtilities-ish")
for n in ("KismetEditorUtilities", "BlueprintFunctionNodeSpawner", "EditorBlueprintLibrary", "BlueprintVariableLibrary"):
    lines.append("%s: %s" % (n, "yes" if hasattr(unreal, n) else "no"))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
