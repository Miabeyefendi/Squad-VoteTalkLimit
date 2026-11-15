import os
HERE = os.path.dirname(os.path.abspath(__file__))
import unreal

OUT = os.path.join(HERE, "vote_dump.txt")
lines = []


def doc(o, n=900):
    try:
        return (o.__doc__ or "").strip().replace("\r", "")[:n]
    except Exception as e:
        return "ERR %s" % e


for name in ("SQVotingState", "SQVoiceChannel", "SQGameRuleSet", "SQVotingComponent", "SQPlayerState"):
    obj = getattr(unreal, name, None)
    lines.append("##### %s %s" % (name, "MISSING" if obj is None else ""))
    if obj is None:
        continue
    lines.append(doc(obj, 500))
    keys = [k for k in obj.__dict__.keys() if not k.startswith("_")]
    for k in sorted(keys):
        if name in ("SQGameRuleSet", "SQVotingComponent", "SQPlayerState") and not any(
                t in k for t in ("vote", "voting", "match", "second", "end", "login", "controller", "online", "player_name", "owner")):
            continue
        lines.append("--- %s.%s" % (name, k))
        try:
            lines.append(doc(getattr(obj, k), 500))
        except Exception as e:
            lines.append("ERR %s" % e)

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")
