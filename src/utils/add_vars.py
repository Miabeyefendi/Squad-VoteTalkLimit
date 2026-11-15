import os
HERE = os.path.dirname(os.path.abspath(__file__))
import unreal

LOG = os.path.join(HERE, "add_vars.log")
out = []
try:
    bel = unreal.BlueprintEditorLibrary
    bp = unreal.EditorAssetLibrary.load_asset("/VoteTalkLimit/BP_VoteTalkLimit")
    out.append("bp: %s" % bp)
    t_int = bel.get_basic_type_by_name("int")
    t_real = bel.get_basic_type_by_name("real")
    ok = bel.add_member_variable(bp, "Bucket", bel.get_map_type(t_int, t_real))
    out.append("Bucket map<int,real>: %s" % ok)
    unreal.EditorAssetLibrary.save_loaded_asset(bp)
    out.append("saved")
except Exception as e:
    out.append("ERROR %s" % e)
with open(LOG, "w", encoding="utf-8") as f:
    f.write("\n".join(out))
