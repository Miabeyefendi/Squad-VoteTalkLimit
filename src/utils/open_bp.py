import unreal
# usage in editor console: py <this file>; opens the helper and the ruleset blueprints
subsys = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
for path in ("/VoteTalkLimit/BP_VTLClientHelper", "/VoteTalkLimit/BP_VoteTalkLimit"):
    subsys.open_editor_for_assets([unreal.EditorAssetLibrary.load_asset(path)])
