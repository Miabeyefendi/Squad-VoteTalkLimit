"""BP_VoteTalkLimit v2: per player token bucket during the end-of-match vote (UE5 T3D clipboard text).

One state: member variable Bucket (Map<int, real>), key = player id.
  s >= 0 : not muted, s seconds of talk budget left (0..T)
  s <  0 : muted, refills at rate r = T/(T+M) until it reaches 0, then unmuted with budget TH = r*M
Settings from CustomOptions.cfg (defaults in the graph): VTL_Enabled true, VTL_TalkSeconds 4.0, VTL_MuteSeconds 10.0
The gate is open while the end-of-match vote runs (SQVotingState). When it closes, everybody is unmuted and the map emptied.
"""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import t3d_lib as L
from t3d_lib import *

OUT = os.path.join(HERE, "rpc_graph2.t3d")
CLS = "/Script/CoreUObject.Class'%s'"
SQ_PC = CLS % "/Script/Squad.SQPlayerController"
SQ_PS_C = CLS % "/Script/Squad.SQPlayerState"
SQ_GS = CLS % "/Script/Squad.SQGameState"
SQ_VS = CLS % "/Script/Squad.SQVotingState"
ENG_GS = CLS % "/Script/Engine.GameState"
ACTOR = CLS % "/Script/Engine.Actor"
MATH = CLS % "/Script/Engine.KismetMathLibrary"
MATH_O = "/Script/Engine.Default__KismetMathLibrary"
MAPLIB = CLS % "/Script/Engine.BlueprintMapLibrary"
MAPLIB_O = "/Script/Engine.Default__BlueprintMapLibrary"
RULESET = CLS % "/Script/Squad.SQGameRuleSet"
VOICE_ENUM = "/Script/CoreUObject.Enum'/Script/SquadVoice.ESQVoiceChannel'"
SQLIB_O = "/Script/Squad.Default__SQBlueprintLibrary"
FOREACH_META = [
    'MacroGraphReference=(MacroGraph="/Script/Engine.EdGraph\'/Engine/EditorBlueprintResources/StandardMacros.StandardMacros:ForEachLoop\'",'
    'GraphBlueprint="/Script/Engine.Blueprint\'/Engine/EditorBlueprintResources/StandardMacros.StandardMacros\'",'
    'GraphGuid=99DBFD5540A796041F72A5A9DA655026)',
    'ResolvedWildcardType=(PinCategory="object",PinSubCategoryObject="%s",bIsUObjectWrapper=True)' % PSB]

_x = [0]


def X(step=330):
    _x[0] += step
    return _x[0]


# ---------- small builders ----------
def R(n, name, out=False, default=None, ref=False, const=False):
    return n.pin(name, "real", out=out, default=default, subcat="double", ref=ref, const=const)


def math(fn, x, y, a=None, b=None, ret="real"):
    n = call(MATH, fn, x, y, pure=True, static_obj=MATH_O)
    R(n, "A", default=a)
    R(n, "B", default=b)
    if ret == "real":
        R(n, "ReturnValue", out=True)
    else:
        n.pin("ReturnValue", "bool", out=True, default="false")
    return n


def boolop(fn, x, y):
    n = call(MATH, fn, x, y, pure=True, static_obj=MATH_O)
    n.pin("A", "bool", default="false")
    n.pin("B", "bool", default="false")
    n.pin("ReturnValue", "bool", out=True, default="false")
    return n


def select_float(x, y, a=None, b=None):
    n = call(MATH, "SelectFloat", x, y, pure=True, static_obj=MATH_O)
    R(n, "A", default=a)
    R(n, "B", default=b)
    n.pin("bPickA", "bool", default="true")
    R(n, "ReturnValue", out=True)
    return n


def branch(x, y):
    n = Node("K2Node_IfThenElse", [], x, y)
    n.pin("execute", "exec")
    n.pin("Condition", "bool", default="false")
    n.pin("then", "exec", out=True)
    n.pin("else", "exec", out=True)
    return n


def event(member, x, y, parent=RULESET):
    ev = Node("K2Node_Event", ['EventReference=(MemberParent="%s",MemberName="%s")' % (parent, member),
                               "bOverrideFunction=True"], x, y)
    ev.pin("then", "exec", out=True)
    return ev


def cast_to(cls, label, x, y):
    c = Node("K2Node_DynamicCast", ['TargetType="%s"' % cls], x, y)
    c.pin("execute", "exec")
    c.pin("then", "exec", out=True)
    c.pin("CastFailed", "exec", out=True)
    c.pin("Object", "wildcard", subobj=OBJ)
    c.pin("As" + label, "object", out=True, subobj=cls)
    c.pin("bSuccess", "bool", out=True, hidden=True)
    return c


def custom_setting(kind, name, default, x, y):
    fn = {"bool": "GetCustomServerSettingAsBool", "float": "GetCustomServerSettingAsFloat"}[kind]
    n = call(SQ_LIB, fn, x, y, pure=True, static_obj=SQLIB_O)
    n.pin("PropertyName", "string", default=name)
    if kind == "bool":
        n.pin("DefaultValue", "bool", default=default)
        n.pin("ReturnValue", "bool", out=True, default="false")
    else:
        R(n, "DefaultValue", default=default)
        R(n, "ReturnValue", out=True)
    return n


def bucket_get(x, y):
    n = Node("K2Node_VariableGet", ['VariableReference=(MemberName="Bucket",bSelfContext=True)'], x, y)
    n.pin("Bucket", "int", out=True, container="Map", valtype=("real", "double"))
    return n


def map_target(n):
    return n.pin("TargetMap", "int", container="Map", valtype=("real", "double"), ref=True, const=True)


def map_find(x, y):
    n = call(MAPLIB, "Map_Find", x, y, static_obj=MAPLIB_O)
    map_target(n)
    n.pin("Key", "int", default="0")
    R(n, "Value", out=True)
    n.pin("ReturnValue", "bool", out=True, default="false")
    return n


def map_add(x, y):
    n = call(MAPLIB, "Map_Add", x, y, static_obj=MAPLIB_O)
    map_target(n)
    n.pin("Key", "int", default="0")
    R(n, "Value")
    return n


def map_remove(x, y):
    n = call(MAPLIB, "Map_Remove", x, y, static_obj=MAPLIB_O)
    map_target(n)
    n.pin("Key", "int", default="0")
    n.pin("ReturnValue", "bool", out=True, default="false")
    return n


def notify(text, x, y):
    n = call(RULESET, "NotifyPlayer", x, y)
    n.pin("Player", "object", subobj=SQ_PC)
    n.pin("Message", "string", default=text)
    return n


def get_owner(ps_pin, x, y):
    o = call(ACTOR, "GetOwner", x, y, pure=True)
    o.pin("ReturnValue", "object", out=True, subobj=ACTOR)
    link(ps_pin, o["self"])
    return o["ReturnValue"]


def foreach_players(exec_pin, array_pin, x, y):
    loop = Node("K2Node_MacroInstance", FOREACH_META, x, y)
    loop.pin("Exec", "exec")
    loop.pin("Array", "object", subobj=PSB, container="Array", wrapper=True)
    loop.pin("LoopBody", "exec", out=True)
    loop.pin("Array Element", "object", out=True, subobj=PSB, wrapper=True)
    loop.pin("Array Index", "int", out=True)
    loop.pin("Completed", "exec", out=True)
    link(exec_pin, loop["Exec"])
    link(array_pin, loop["Array"])
    return loop


TOGGLE_RANGES = []
HELPER_O = "/VoteTalkLimit/BP_VTLClientHelper.BP_VTLClientHelper_C"
HELPER_CLS = "/Script/Engine.BlueprintGeneratedClass'/VoteTalkLimit/BP_VTLClientHelper.BP_VTLClientHelper_C'"
ACTOR_CLS = CLS % "/Script/Engine.Actor"
TRANSFORM = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Transform'"
GPS_O = "/Script/Engine.Default__GameplayStatics"


def resume_nothing(exec_pin):
    """client-rpc: the helper actor ends itself after the mute time, nothing to do on resume."""
    TOGGLE_RANGES.append((len(L.NODES), len(L.NODES)))
    return exec_pin


def mute_speaker(exec_pin, pc_pin, x, y):
    """Spawn BP_VTLClientHelper owned by the speaker's controller; it lives MuteSeconds (SetLifeSpan)."""
    i0 = len(L.NODES)
    sp = Node("K2Node_SpawnActorFromClass", ["AdvancedPinDisplay=Shown"], x, y)
    sp.pin("execute", "exec")
    sp.pin("then", "exec", out=True)
    sp.pin("Class", "class", subobj=ACTOR_CLS, defobj=HELPER_O)
    sp.pin("ReturnValue", "object", out=True, subobj=HELPER_CLS)
    sp.pin("SpawnTransform", "struct", subobj=TRANSFORM)
    sp.pin("CollisionHandlingOverride", "byte",
           subobj="/Script/CoreUObject.Enum'/Script/Engine.ESpawnActorCollisionHandlingMethod'", default="AlwaysSpawn")
    sp.pin("Owner", "object", subobj=ACTOR_CLS)
    link(exec_pin, sp["execute"])
    link(pc_pin, sp["Owner"])
    mt = call(MATH, "MakeTransform", x, y + 330, pure=True, static_obj=MATH_O)
    mt.pin("Location", "struct", subobj="/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Vector'", default="0.0,0.0,0.0")
    mt.pin("Rotation", "struct", subobj="/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Rotator'", default="0.0,0.0,0.0")
    mt.pin("Scale", "struct", subobj="/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Vector'", default="1.0,1.0,1.0")
    mt.pin("ReturnValue", "struct", out=True, subobj=TRANSFORM)
    link(mt["ReturnValue"], sp["SpawnTransform"])
    life = call(ACTOR, "SetLifeSpan", x + 420, y)
    R(life, "InLifespan", default="10.0")
    link(sp["then"], life["execute"])
    link(sp["ReturnValue"], life["self"])
    link(set_m["ReturnValue"], life["InLifespan"])
    TOGGLE_RANGES.append((i0, len(L.NODES)))
    return life["then"]


def destroy_helpers(exec_pin, x, y):
    """Destroy every BP_VTLClientHelper (the vote is over). Returns the Completed exec pin."""
    i0 = len(L.NODES)
    ga = call(GPS, "GetAllActorsOfClass", x, y, static_obj=GPS_O)
    ga.pin("WorldContextObject", "object", subobj=OBJ, const=True, hidden=True)
    ga.pin("ActorClass", "class", subobj=ACTOR_CLS, defobj=HELPER_O)
    ga.pin("OutActors", "object", out=True, subobj=ACTOR_CLS, container="Array")
    link(exec_pin, ga["execute"])
    loop = Node("K2Node_MacroInstance", FOREACH_META[:1] + [
        'ResolvedWildcardType=(PinCategory="object",PinSubCategoryObject="%s")' % ACTOR_CLS], x + 420, y)
    loop.pin("Exec", "exec")
    loop.pin("Array", "object", subobj=ACTOR_CLS, container="Array")
    loop.pin("LoopBody", "exec", out=True)
    loop.pin("Array Element", "object", out=True, subobj=ACTOR_CLS)
    loop.pin("Array Index", "int", out=True)
    loop.pin("Completed", "exec", out=True)
    link(ga["then"], loop["Exec"])
    link(ga["OutActors"], loop["Array"])
    ds = call(ACTOR, "K2_DestroyActor", x + 840, y)
    link(loop["LoopBody"], ds["execute"])
    link(loop["Array Element"], ds["self"])
    TOGGLE_RANGES.append((i0, len(L.NODES)))
    return loop["Completed"]


# ---------- shared pure values ----------
gs = call(GPS, "GetGameState", 0, 900, pure=True, static_obj="/Script/Engine.Default__GameplayStatics")
gs.pin("WorldContextObject", "object", subobj=OBJ, const=True, hidden=True)
gs.pin("ReturnValue", "object", out=True, subobj=GSB)
pa = Node("K2Node_VariableGet", ['VariableReference=(MemberParent="%s",MemberName="PlayerArray")' % GSB,
                                 "SelfContextInfo=NotSelfContext"], 330, 900)
pa.pin("PlayerArray", "object", out=True, subobj=PSB, container="Array", wrapper=True,
       friendly='NSLOCTEXT("UObjectDisplayNames", "GameStateBase:PlayerArray", "Player Array")')
pa.pin("self", "object", subobj=GSB, friendly=TARGET)
link(gs["ReturnValue"], pa["self"])
PLAYERS = pa["PlayerArray"]

set_t = custom_setting("float", "VTL_TalkSeconds", "4.0", 0, 1100)
set_m = custom_setting("float", "VTL_MuteSeconds", "10.0", 0, 1300)
sum_tm = math("Add_DoubleDouble", 330, 1100)
link(set_t["ReturnValue"], sum_tm["A"])
link(set_m["ReturnValue"], sum_tm["B"])
rate = math("Divide_DoubleDouble", 660, 1100)
link(set_t["ReturnValue"], rate["A"])
link(sum_tm["ReturnValue"], rate["B"])
th = math("Multiply_DoubleDouble", 990, 1100)
link(rate["ReturnValue"], th["A"])
link(set_m["ReturnValue"], th["B"])
neg_th = math("Subtract_DoubleDouble", 1320, 1100, a="0.0")
link(th["ReturnValue"], neg_th["B"])

# ---------- Event Tick ----------
tk = event("ReceiveTick", 0, 0, parent=ACTOR)
tk.pin("DeltaSeconds", "real", out=True, subcat="double")
DT = tk["DeltaSeconds"]

en = custom_setting("bool", "VTL_Enabled", "true", 330, 0)
gsc = call(GPS, "GetGameState", 330, 150, pure=True, static_obj="/Script/Engine.Default__GameplayStatics")
gsc.pin("WorldContextObject", "object", subobj=OBJ, const=True, hidden=True)
gsc.pin("ReturnValue", "object", out=True, subobj=GSB)
cg = cast_to(SQ_GS, "SQGame State", 660, 0)
link(tk["then"], cg["execute"])
link(gsc["ReturnValue"], cg["Object"])
vs = Node("K2Node_VariableGet", ['VariableReference=(MemberParent="%s",MemberName="VotingState")' % SQ_GS,
                                 "SelfContextInfo=NotSelfContext"], 990, 150)
vs.pin("VotingState", "object", out=True, subobj=SQ_VS)
vs.pin("self", "object", subobj=SQ_GS, friendly=TARGET)
link(cg["AsSQGame State"], vs["self"])
any_vote = call(SQ_VS, "HasAnyVoteInProgress", 1320, 150, pure=True)
any_vote.pin("ReturnValue", "bool", out=True, default="false")
link(vs["VotingState"], any_vote["self"])
end_vote = Node("K2Node_VariableGet", ['VariableReference=(MemberParent="%s",MemberName="bEndMapVoteInProgress")' % SQ_VS,
                                       "SelfContextInfo=NotSelfContext"], 1320, 300)
end_vote.pin("bEndMapVoteInProgress", "bool", out=True, default="false")
end_vote.pin("self", "object", subobj=SQ_VS, friendly=TARGET)
link(vs["VotingState"], end_vote["self"])
vote_or = boolop("BooleanOR", 1650, 150)
link(any_vote["ReturnValue"], vote_or["A"])
link(end_vote["bEndMapVoteInProgress"], vote_or["B"])
gate = boolop("BooleanAND", 1980, 150)
link(en["ReturnValue"], gate["A"])
link(vote_or["ReturnValue"], gate["B"])
gbr = branch(2310, 0)
link(cg["then"], gbr["execute"])
link(gate["ReturnValue"], gbr["Condition"])

# ================= gate ON: token bucket per player =================
BX, BY = 2640, 0
loop = foreach_players(gbr["then"], PLAYERS, BX, BY)
psq = cast_to(SQ_PS_C, "SQPlayer State", BX + 330, BY)
link(loop["LoopBody"], psq["execute"])
link(loop["Array Element"], psq["Object"])
owner = get_owner(loop["Array Element"], BX + 330, BY + 250)
pc = cast_to(SQ_PC, "SQPlayer Controller", BX + 660, BY)
link(psq["then"], pc["execute"])
link(owner, pc["Object"])
pid = call(PSB, "GetPlayerId", BX + 660, BY + 250, pure=True)
pid.pin("ReturnValue", "int", out=True, default="0")
link(loop["Array Element"], pid["self"])

bk1 = bucket_get(BX + 660, BY + 400)
find = map_find(BX + 990, BY)
link(pc["then"], find["execute"])
link(bk1["Bucket"], find["TargetMap"])
link(pid["ReturnValue"], find["Key"])

found_br = branch(BX + 1320, BY)
link(find["then"], found_br["execute"])
link(find["ReturnValue"], found_br["Condition"])
n_new = notify("Voice limit: your talk time is limited while the map vote is running.", BX + 1650, BY + 200)
link(pc["AsSQPlayer Controller"], n_new["Player"])
link(found_br["else"], n_new["execute"])

# s = found ? Value : T
s_sel = select_float(BX + 1320, BY + 400)
link(find["Value"], s_sel["A"])
link(set_t["ReturnValue"], s_sel["B"])
link(find["ReturnValue"], s_sel["bPickA"])
S = s_sel["ReturnValue"]

# talking = RecentVoiceChannel != None ; consume = talking ? dt : 0
rv = Node("K2Node_VariableGet", ['VariableReference=(MemberParent="%s",MemberName="RecentVoiceChannel")' % SQ_PC,
                                 "SelfContextInfo=NotSelfContext"], BX + 1650, BY + 600)
rv.pin("RecentVoiceChannel", "byte", out=True, subobj=VOICE_ENUM)
rv.pin("self", "object", subobj=SQ_PC, friendly=TARGET)
link(pc["AsSQPlayer Controller"], rv["self"])
lit = Node("K2Node_EnumLiteral", ['Enum="%s"' % VOICE_ENUM], BX + 1650, BY + 750)
lit.pin("Enum", "byte", subobj=VOICE_ENUM, default="None")
lit.pin("ReturnValue", "byte", out=True, subobj=VOICE_ENUM)
talking = call(MATH, "NotEqual_ByteByte", BX + 1980, BY + 600, pure=True, static_obj=MATH_O)
talking.pin("A", "byte", default="0")
talking.pin("B", "byte", default="0")
talking.pin("ReturnValue", "bool", out=True, default="false")
link(rv["RecentVoiceChannel"], talking["A"])
link(lit["ReturnValue"], talking["B"])
consume = select_float(BX + 2310, BY + 600, b="0.0")
link(DT, consume["A"])
link(talking["ReturnValue"], consume["bPickA"])

refill = math("Multiply_DoubleDouble", BX + 1980, BY + 400)
link(rate["ReturnValue"], refill["A"])
link(DT, refill["B"])

is_muted = math("Less_DoubleDouble", BX + 2310, BY + 400, b="0.0", ret="bool")
link(S, is_muted["A"])
mbr = branch(BX + 2640, BY)
link(found_br["then"], mbr["execute"])
link(n_new["then"], mbr["execute"])
link(is_muted["ReturnValue"], mbr["Condition"])

# ---- muted path: s2m = s + refill ; resume when s2m >= 0 ----
s2m = math("Add_DoubleDouble", BX + 2970, BY + 400)
link(S, s2m["A"])
link(refill["ReturnValue"], s2m["B"])
resume = math("GreaterEqual_DoubleDouble", BX + 3300, BY + 400, b="0.0", ret="bool")
link(s2m["ReturnValue"], resume["A"])
rbr = branch(BX + 2970, BY)
link(mbr["then"], rbr["execute"])
link(resume["ReturnValue"], rbr["Condition"])
un_done = resume_nothing(rbr["then"])
n_un = notify("Voice limit: you can talk again.", BX + 4950, BY - 700)
link(pc["AsSQPlayer Controller"], n_un["Player"])
link(un_done, n_un["execute"])
add_th = map_add(BX + 5280, BY - 700)
bk2 = bucket_get(BX + 4950, BY - 500)
link(bk2["Bucket"], add_th["TargetMap"])
link(pid["ReturnValue"], add_th["Key"])
link(th["ReturnValue"], add_th["Value"])
link(n_un["then"], add_th["execute"])
add_s2m = map_add(BX + 3300, BY)
bk3 = bucket_get(BX + 3300, BY + 200)
link(bk3["Bucket"], add_s2m["TargetMap"])
link(pid["ReturnValue"], add_s2m["Key"])
link(s2m["ReturnValue"], add_s2m["Value"])
link(rbr["else"], add_s2m["execute"])

# ---- unmuted path: s2u = min(T, s + refill - consume) ----
plus = math("Add_DoubleDouble", BX + 2970, BY + 700)
link(S, plus["A"])
link(refill["ReturnValue"], plus["B"])
minus = math("Subtract_DoubleDouble", BX + 3300, BY + 700)
link(plus["ReturnValue"], minus["A"])
link(consume["ReturnValue"], minus["B"])
s2u = math("FMin", BX + 3630, BY + 700)
link(set_t["ReturnValue"], s2u["A"])
link(minus["ReturnValue"], s2u["B"])
empty = math("LessEqual_DoubleDouble", BX + 3960, BY + 700, b="0.0", ret="bool")
link(s2u["ReturnValue"], empty["A"])
ebr = branch(BX + 3300, BY + 1000)
link(mbr["else"], ebr["execute"])
link(empty["ReturnValue"], ebr["Condition"])
mu_done = mute_speaker(ebr["then"], pc["AsSQPlayer Controller"], BX + 3300, BY + 1300)
n_mu = notify("Voice limit reached: you are muted for a short while.", BX + 4950, BY + 1300)
link(pc["AsSQPlayer Controller"], n_mu["Player"])
link(mu_done, n_mu["execute"])
add_neg = map_add(BX + 5280, BY + 1300)
bk4 = bucket_get(BX + 4950, BY + 1500)
link(bk4["Bucket"], add_neg["TargetMap"])
link(pid["ReturnValue"], add_neg["Key"])
link(neg_th["ReturnValue"], add_neg["Value"])
link(n_mu["then"], add_neg["execute"])

low_a = math("GreaterEqual_DoubleDouble", BX + 4290, BY + 700, b="1.0", ret="bool")
link(S, low_a["A"])
low_b = math("Less_DoubleDouble", BX + 4620, BY + 700, b="1.0", ret="bool")
link(s2u["ReturnValue"], low_b["A"])
low_and = boolop("BooleanAND", BX + 4950, BY + 700)
link(low_a["ReturnValue"], low_and["A"])
link(low_b["ReturnValue"], low_and["B"])
lbr = branch(BX + 3630, BY + 1000)
link(ebr["else"], lbr["execute"])
link(low_and["ReturnValue"], lbr["Condition"])
n_low = notify("Voice limit: talk time almost up.", BX + 3960, BY + 1000)
link(pc["AsSQPlayer Controller"], n_low["Player"])
link(lbr["then"], n_low["execute"])
add_s2u = map_add(BX + 4290, BY + 1000)
bk5 = bucket_get(BX + 3960, BY + 1200)
link(bk5["Bucket"], add_s2u["TargetMap"])
link(pid["ReturnValue"], add_s2u["Key"])
link(s2u["ReturnValue"], add_s2u["Value"])
link(n_low["then"], add_s2u["execute"])
link(lbr["else"], add_s2u["execute"])

# ================= gate OFF: unmute whoever is muted and forget everybody =================
FX, FY = 2640, 3200
floop = foreach_players(gbr["else"], PLAYERS, FX, FY)
fpsq = cast_to(SQ_PS_C, "SQPlayer State", FX + 330, FY)
link(floop["LoopBody"], fpsq["execute"])
link(floop["Array Element"], fpsq["Object"])
fpid = call(PSB, "GetPlayerId", FX + 330, FY + 250, pure=True)
fpid.pin("ReturnValue", "int", out=True, default="0")
link(floop["Array Element"], fpid["self"])
fbk = bucket_get(FX + 660, FY + 300)
ffind = map_find(FX + 660, FY)
link(fpsq["then"], ffind["execute"])
link(fbk["Bucket"], ffind["TargetMap"])
link(fpid["ReturnValue"], ffind["Key"])
fbr = branch(FX + 990, FY)
link(ffind["then"], fbr["execute"])
link(ffind["ReturnValue"], fbr["Condition"])
fneg = math("Less_DoubleDouble", FX + 990, FY + 300, b="0.0", ret="bool")
link(ffind["Value"], fneg["A"])
fmb = branch(FX + 1320, FY)
link(fbr["then"], fmb["execute"])
link(fneg["ReturnValue"], fmb["Condition"])
f_done = destroy_helpers(fmb["then"], FX + 1650, FY - 700)
frem = map_remove(FX + 3300, FY)
fbk2 = bucket_get(FX + 3000, FY + 200)
link(fbk2["Bucket"], frem["TargetMap"])
link(fpid["ReturnValue"], frem["Key"])
link(f_done, frem["execute"])
link(fmb["else"], frem["execute"])

with open(OUT, "w", encoding="utf-8", newline="") as f:
    f.write("\r\n".join(n.text() for n in L.NODES) + "\r\n")
print("nodes", len(L.NODES))
