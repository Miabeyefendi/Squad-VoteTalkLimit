import io
import os
import re

sp = os.path.dirname(os.path.abspath(__file__))
src = io.open(os.path.join(sp, "gen_graph.py"), encoding="utf-8").read()
head = src.split("# ---- graph ----")[0]
head = re.sub(r'^OUT = .*$', 'OUT = None', head, count=1, flags=re.M)
head = re.sub(r'^BP = ".*"$', 'BP = "/VoteTalkLimit/BP_VoteTalkLimit.BP_VoteTalkLimit:EventGraph"', head, count=1, flags=re.M)
assert "VoteTalkLimit" in head and "OUT = None" in head
io.open(os.path.join(sp, "t3d_lib.py"), "w", encoding="utf-8", newline="\n").write(head)
print("lib lines", head.count("\n"))
