import unreal, os

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "create_helper.log")
out = []
try:
    for n in dir(unreal.SQVoiceChannel):
        if n.isupper():
            v = getattr(unreal.SQVoiceChannel, n)
            out.append("enum %s -> %r" % (n, v))
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    bp = unreal.EditorAssetLibrary.load_asset("/VoteTalkLimit/BP_VTLClientHelper")
    if not bp:
        bp = tools.create_asset("BP_VTLClientHelper", "/VoteTalkLimit", unreal.Blueprint, factory)
    out.append("bp: %s" % bp)
    cdo = unreal.get_default_object(bp.generated_class()) if hasattr(unreal, "get_default_object") else None
    if cdo is None:
        cdo = bp.generated_class().get_default_object()
    for k, v in (("replicates", True), ("only_relevant_to_owner", True), ("replicate_movement", False),
                 ("net_load_on_client", True), ("initial_life_span", 0.0)):
        try:
            cdo.set_editor_property(k, v)
            out.append("set %s=%s" % (k, v))
        except Exception as e:
            out.append("FAIL %s: %s" % (k, e))
    unreal.EditorAssetLibrary.save_loaded_asset(bp)
    out.append("saved")
except Exception as e:
    out.append("ERROR %s" % e)
with open(LOG, "w", encoding="utf-8") as f:
    f.write("\n".join(out))
unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")
