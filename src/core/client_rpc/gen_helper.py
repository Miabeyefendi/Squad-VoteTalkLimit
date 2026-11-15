"""BP_VTLClientHelper graph (UE5 T3D clipboard text).

The actor is spawned by the server with the speaker's PlayerController as owner and is replicated to that owner only.
On the owning client: BeginPlay toggles the local voice channel (muted), EndPlay toggles it back.
The server destroys it (or its lifespan ends), so the mute can never outlive the vote or the player.
"""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import t3d_lib as L
from t3d_lib import *

L.BP = "/VoteTalkLimit/BP_VTLClientHelper.BP_VTLClientHelper:EventGraph"
OUT = os.path.join(HERE, "helper_graph.t3d")
CLS = "/Script/CoreUObject.Class'%s'"
ACTOR = CLS % "/Script/Engine.Actor"
SQ_PC = CLS % "/Script/Squad.SQPlayerController"
CTRL = CLS % "/Script/Engine.Controller"
VOICE_ENUM = "/Script/CoreUObject.Enum'/Script/SquadVoice.ESQVoiceChannel'"
END_ENUM = "/Script/CoreUObject.Enum'/Script/Engine.EEndPlayReason'"
CHANNEL = "LOCAL"


def event(member, x, y):
    ev = Node("K2Node_Event", ['EventReference=(MemberParent="%s",MemberName="%s")' % (ACTOR, member),
                               "bOverrideFunction=True"], x, y)
    ev.pin("then", "exec", out=True)
    return ev


def chain(ev, y):
    own = call(ACTOR, "GetOwner", 400, y + 200, pure=True)
    own.pin("ReturnValue", "object", out=True, subobj=ACTOR)
    c = Node("K2Node_DynamicCast", ['TargetType="%s"' % SQ_PC], 400, y)
    c.pin("execute", "exec")
    c.pin("then", "exec", out=True)
    c.pin("CastFailed", "exec", out=True)
    c.pin("Object", "wildcard", subobj=OBJ)
    c.pin("AsSQPlayer Controller", "object", out=True, subobj=SQ_PC)
    c.pin("bSuccess", "bool", out=True, hidden=True)
    link(ev["then"], c["execute"])
    link(own["ReturnValue"], c["Object"])
    loc = call(CTRL, "IsLocalController", 780, y + 200, pure=True)
    loc.pin("ReturnValue", "bool", out=True, default="false")
    link(c["AsSQPlayer Controller"], loc["self"])
    br = Node("K2Node_IfThenElse", [], 1000, y)
    br.pin("execute", "exec")
    br.pin("Condition", "bool", default="false")
    br.pin("then", "exec", out=True)
    br.pin("else", "exec", out=True)
    link(c["then"], br["execute"])
    link(loc["ReturnValue"], br["Condition"])
    tg = call(SQ_PC, "BlueprintToggleVoice", 1300, y)
    tg.pin("VoiceChannel", "byte", subobj=VOICE_ENUM, default=CHANNEL)
    link(br["then"], tg["execute"])
    link(c["AsSQPlayer Controller"], tg["self"])


bp = event("ReceiveBeginPlay", 0, 0)
chain(bp, 0)
ep = event("ReceiveEndPlay", 0, 600)
ep.pin("EndPlayReason", "byte", out=True, subobj=END_ENUM)
chain(ep, 600)

with open(OUT, "w", encoding="utf-8", newline="") as f:
    f.write("\r\n".join(n.text() for n in L.NODES) + "\r\n")
print("nodes", len(L.NODES))
