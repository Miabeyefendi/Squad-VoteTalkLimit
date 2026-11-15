import os
HERE = os.path.dirname(os.path.abspath(__file__))
import unreal

OUT = os.path.join(HERE, "bel_doc.txt")
lines = []
bel = unreal.BlueprintEditorLibrary
for n in ("add_member_variable", "get_map_type", "get_set_type", "get_basic_type_by_name", "get_array_type",
          "compile_blueprint", "find_event_graph", "add_function_graph", "get_object_reference_type"):
    try:
        lines.append("--- %s\n%s" % (n, getattr(bel, n).__doc__))
    except Exception as e:
        lines.append("--- %s ERR %s" % (n, e))
try:
    lines.append("--- EdGraphPinType fields: %s" % ", ".join(k for k in dir(unreal.EdGraphPinType) if not k.startswith("_")))
except Exception as e:
    lines.append("EdGraphPinType ERR %s" % e)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
