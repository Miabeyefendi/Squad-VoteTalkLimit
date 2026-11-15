import os
HERE = os.path.dirname(os.path.abspath(__file__))
import unreal

OUT = os.path.join(HERE, "times_dump.txt")
lines = []


def dump_obj(label, obj):
    lines.append("##### %s" % label)
    if obj is None:
        lines.append("MISSING")
        return
    try:
        cls = obj.get_class()
        lines.append("class: %s" % cls.get_name())
    except Exception as e:
        lines.append("ERR class %s" % e)
    names = [k for k in dir(obj) if not k.startswith("_")]
    for k in sorted(names):
        if not any(t in k for t in ("vote", "time", "duration", "reroll", "regenerat", "voting", "second", "delay", "cooldown")):
            continue
        try:
            v = obj.get_editor_property(k)
            lines.append("%s = %s" % (k, v))
        except Exception as e:
            lines.append("%s : (not readable: %s)" % (k, str(e)[:80]))


for cls_name in ("SQDataSettings", "SQGameMode", "SQGameState", "SQVotingState", "SQVotingComponent", "SQGameSession", "SQLayerVoteConfig"):
    cls = getattr(unreal, cls_name, None)
    if cls is None:
        lines.append("##### %s MISSING" % cls_name)
        continue
    try:
        dump_obj(cls_name + " (CDO)", unreal.get_default_object(cls))
    except Exception as e:
        lines.append("##### %s ERR %s" % (cls_name, e))

# struct types used by the vote configs, if python knows them
for n in ("SQVoteConfig", "SQLayerVoteConfig", "SQFactionVoteConfig", "SQCommanderVoteConfig", "SQVoteSessionConfig"):
    c = getattr(unreal, n, None)
    lines.append("##### struct %s: %s" % (n, "yes" if c else "no"))
    if c:
        try:
            s = c()
            for k in sorted(k for k in dir(s) if not k.startswith("_")):
                try:
                    lines.append("   %s = %s" % (k, s.get_editor_property(k)))
                except Exception:
                    pass
        except Exception as e:
            lines.append("   ERR %s" % e)

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")
