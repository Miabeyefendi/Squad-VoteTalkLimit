import os
HERE = os.path.dirname(os.path.abspath(__file__))
import unreal

LOG = os.path.join(HERE, "create_bp.log")
out = []
try:
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.SQGameRuleSet)
    bp = tools.create_asset("BP_VoteTalkLimit", "/VoteTalkLimit", unreal.Blueprint, factory)
    out.append("created: %s" % bp)
    if bp:
        unreal.EditorAssetLibrary.save_loaded_asset(bp)
        unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets([bp])
        out.append("opened")
except Exception as e:
    out.append("ERROR %s" % e)
with open(LOG, "w", encoding="utf-8") as f:
    f.write("\n".join(out))
