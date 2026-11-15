"""Blueprint text for BP_VoteTalkLimit, stage 1 probe (UE5 T3D clipboard format).

Three event chains in one paste:
  On End Match            : every player's controller gets Set Mute All Players(true), then Is All Players Muted is logged
  Match Is Waiting To Start: Set Mute All Players(false) for everyone, logged
  Event Tick              : while the match has ended, log every player whose Recent Voice Channel is not None
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.insert(0, HERE)
import t3d_lib as L
from t3d_lib import *

OUT = os.path.join(HERE, "vote_graph.t3d")
SQ_PC = "/Script/CoreUObject.Class'/Script/Squad.SQPlayerController'"
SQ_GS = "/Script/CoreUObject.Class'/Script/Squad.SQGameState'"
ENG_GS = "/Script/CoreUObject.Class'/Script/Engine.GameState'"
ACTOR = "/Script/CoreUObject.Class'/Script/Engine.Actor'"
MATH = "/Script/CoreUObject.Class'/Script/Engine.KismetMathLibrary'"
VOICE_ENUM = "/Script/CoreUObject.Enum'/Script/SquadVoice.ESQVoiceChannel'"
RULESET = "/Script/CoreUObject.Class'/Script/Squad.SQGameRuleSet'"
FOREACH_META = [
    'MacroGraphReference=(MacroGraph="/Script/Engine.EdGraph\'/Engine/EditorBlueprintResources/StandardMacros.StandardMacros:ForEachLoop\'",'
    'GraphBlueprint="/Script/Engine.Blueprint\'/Engine/EditorBlueprintResources/StandardMacros.StandardMacros\'",'
    'GraphGuid=99DBFD5540A796041F72A5A9DA655026)',
    'ResolvedWildcardType=(PinCategory="object",PinSubCategoryObject="%s",bIsUObjectWrapper=True)' % PSB]


def event(member, x, y, parent=RULESET):
    ev = Node("K2Node_Event", ['EventReference=(MemberParent="%s",MemberName="%s")' % (parent, member),
                               "bOverrideFunction=True"], x, y)
    ev.pin("then", "exec", out=True)
    return ev


def get_game_state(x, y):
    gs = call(GPS, "GetGameState", x, y, pure=True, static_obj="/Script/Engine.Default__GameplayStatics")
    gs.pin("WorldContextObject", "object", subobj=OBJ, const=True, hidden=True)
    gs.pin("ReturnValue", "object", out=True, subobj=GSB)
    return gs


def cast_to(cls, label, x, y):
    c = Node("K2Node_DynamicCast", ['TargetType="%s"' % cls], x, y)
    c.pin("execute", "exec")
    c.pin("then", "exec", out=True)
    c.pin("CastFailed", "exec", out=True)
    c.pin("Object", "wildcard", subobj=OBJ)
    c.pin("As" + label, "object", out=True, subobj=cls)
    c.pin("bSuccess", "bool", out=True, hidden=True)
    return c


def player_loop(exec_pin, x, y):
    """For Each player state, cast its owner to SQPlayerController. Returns (loop, controller cast, player state pin)."""
    gs = get_game_state(x, y + 250)
    pa = Node("K2Node_VariableGet", ['VariableReference=(MemberParent="%s",MemberName="PlayerArray")' % GSB,
                                     "SelfContextInfo=NotSelfContext"], x, y + 400)
    pa.pin("PlayerArray", "object", out=True, subobj=PSB, container="Array", wrapper=True,
           friendly='NSLOCTEXT("UObjectDisplayNames", "GameStateBase:PlayerArray", "Player Array")')
    pa.pin("self", "object", subobj=GSB, friendly=TARGET)
    link(gs["ReturnValue"], pa["self"])
    loop = Node("K2Node_MacroInstance", FOREACH_META, x + 330, y)
    loop.pin("Exec", "exec")
    loop.pin("Array", "object", subobj=PSB, container="Array", wrapper=True)
    loop.pin("LoopBody", "exec", out=True)
    loop.pin("Array Element", "object", out=True, subobj=PSB, wrapper=True)
    loop.pin("Array Index", "int", out=True)
    loop.pin("Completed", "exec", out=True)
    link(exec_pin, loop["Exec"])
    link(pa["PlayerArray"], loop["Array"])
    owner = call(ACTOR, "GetOwner", x + 330, y + 250, pure=True)
    owner.pin("ReturnValue", "object", out=True, subobj=ACTOR)
    link(loop["Array Element"], owner["self"])
    cc = cast_to(SQ_PC, "SQPlayer Controller", x + 660, y)
    link(loop["LoopBody"], cc["execute"])
    link(owner["ReturnValue"], cc["Object"])
    return loop, cc, loop["Array Element"]


def player_name(ps_pin, x, y):
    n = call(PSB, "GetPlayerName", x, y, pure=True)
    n.pin("ReturnValue", "string", out=True)
    link(ps_pin, n["self"])
    return n["ReturnValue"]


def bool_str(x, y):
    n = call(STR_LIB, "Conv_BoolToString", x, y, pure=True, static_obj="/Script/Engine.Default__KismetStringLibrary")
    n.pin("InBool", "bool", default="false")
    n.pin("ReturnValue", "string", out=True)
    return n


def mute_chain(member_event, ev_x, ev_y, mute, text):
    ev = event(member_event, ev_x, ev_y)
    head = log_error(ev_x + 330, ev_y, "VoteTalkLimit %s" % text)
    link(ev["then"], head["execute"])
    loop, cc, ps = player_loop(head["then"], ev_x + 660, ev_y)
    setm = call(SQ_PC, "SetMuteAllPlayers", ev_x + 1650, ev_y)
    setm.pin("bMute", "bool")
    link(cc["then"], setm["execute"])
    link(cc["AsSQPlayer Controller"], setm["self"])
    ism = call(SQ_PC, "IsAllPlayersMuted", ev_x + 1650, ev_y + 200, pure=True)
    ism.pin("ReturnValue", "bool", out=True, default="false")
    link(cc["AsSQPlayer Controller"], ism["self"])
    bs = bool_str(ev_x + 1980, ev_y + 200)
    link(ism["ReturnValue"], bs["InBool"])
    nm = player_name(ps, ev_x + 1650, ev_y + 400)
    c1 = concat(ev_x + 1980, ev_y + 400, a_default="VoteTalkLimit %s name=" % text.split(":")[0])
    link(nm, c1["B"])
    c2 = concat(ev_x + 2310, ev_y + 400, b_default=" muteAll=")
    link(c1["ReturnValue"], c2["A"])
    c3 = concat(ev_x + 2640, ev_y + 400)
    link(c2["ReturnValue"], c3["A"])
    link(bs["ReturnValue"], c3["B"])
    out = log_error(ev_x + 2970, ev_y)
    link(setm["then"], out["execute"])
    link(c3["ReturnValue"], out["Contents"])


mute_chain("OnEndMatch", 0, 0, True, "end of match: muting everyone (probe)")
mute_chain("MatchIsWaitingToStart", 0, 1100, False, "new match: unmuting everyone")

# ---- Event Tick: log players who are talking after the match ended ----
tk = event("ReceiveTick", 0, 2300, parent=ACTOR)
gs = get_game_state(330, 2300)
cg = cast_to(SQ_GS, "SQGame State", 660, 2300)
link(tk["then"], cg["execute"])
link(gs["ReturnValue"], cg["Object"])
ended = call(ENG_GS, "HasMatchEnded", 990, 2450, pure=True)
ended.pin("ReturnValue", "bool", out=True, default="false")
link(cg["AsSQGame State"], ended["self"])
br = Node("K2Node_IfThenElse", [], 990, 2300)
br.pin("execute", "exec")
br.pin("Condition", "bool", default="false")
br.pin("then", "exec", out=True)
br.pin("else", "exec", out=True)
link(cg["then"], br["execute"])
link(ended["ReturnValue"], br["Condition"])

loop, cc, ps = player_loop(br["then"], 1320, 2300)
rv = Node("K2Node_VariableGet", ['VariableReference=(MemberParent="%s",MemberName="RecentVoiceChannel")' % SQ_PC,
                                 "SelfContextInfo=NotSelfContext"], 2310, 2300)
rv.pin("RecentVoiceChannel", "byte", out=True, subobj=VOICE_ENUM)
rv.pin("self", "object", subobj=SQ_PC, friendly=TARGET)
link(cc["AsSQPlayer Controller"], rv["self"])
lit = Node("K2Node_EnumLiteral", ['Enum="%s"' % VOICE_ENUM], 2310, 2450)
lit.pin("Enum", "byte", subobj=VOICE_ENUM, default="None")
lit.pin("ReturnValue", "byte", out=True, subobj=VOICE_ENUM)
ne = call(MATH, "NotEqual_ByteByte", 2640, 2300, pure=True, static_obj="/Script/Engine.Default__KismetMathLibrary")
ne.pin("A", "byte", default="0")
ne.pin("B", "byte", default="0")
ne.pin("ReturnValue", "bool", out=True, default="false")
link(rv["RecentVoiceChannel"], ne["A"])
link(lit["ReturnValue"], ne["B"])
br2 = Node("K2Node_IfThenElse", [], 2970, 2300)
br2.pin("execute", "exec")
br2.pin("Condition", "bool", default="false")
br2.pin("then", "exec", out=True)
br2.pin("else", "exec", out=True)
link(cc["then"], br2["execute"])
link(ne["ReturnValue"], br2["Condition"])
nm = player_name(ps, 2310, 2650)
chs = call(STR_LIB, "Conv_ByteToString", 2310, 2800, pure=True, static_obj="/Script/Engine.Default__KismetStringLibrary")
chs.pin("InByte", "byte", default="0")
chs.pin("ReturnValue", "string", out=True)
link(rv["RecentVoiceChannel"], chs["InByte"])
c1 = concat(2640, 2650, a_default="VoteTalkLimit talking name=")
link(nm, c1["B"])
c2 = concat(2970, 2650, b_default=" channel=")
link(c1["ReturnValue"], c2["A"])
c3 = concat(3300, 2650)
link(c2["ReturnValue"], c3["A"])
link(chs["ReturnValue"], c3["B"])
out = log_error(3300, 2300)
link(br2["then"], out["execute"])
link(c3["ReturnValue"], out["Contents"])

with open(OUT, "w", encoding="utf-8", newline="") as f:
    f.write("\r\n".join(n.text() for n in L.NODES) + "\r\n")
print("nodes", len(L.NODES))
