"""Same nodes as gen_vote2, only the positions change: sections, layered left to right, comment boxes with titles."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_rpc2 as G
import t3d_lib as L
from t3d_lib import gid

OUT = os.path.join(HERE, "rpc_graph3.t3d")
NODES = L.NODES
before = [(n.name, n.cls, len(n.pins)) for n in NODES]

# ---------- sections ----------
section_of = {}


def tag(label, items):
    for it in items:
        section_of[id(it)] = label


S1 = "1  Settings and constants (CustomOptions.cfg, rate = T/(T+M))"
S2 = "2  Event Tick and the vote gate"
S3 = "3  Vote is running: read this player's bucket (new player gets a notice)"
S4 = "4  Is the player talking? Budget math"
S5 = "5  Player is muted: refill, resume check"
S6 = "6  Resume: notify, bucket = TH (the helper actor ends itself)"
S7 = "7  Player is not muted: spend budget, warn, mute when empty"
S8 = "8  Empty: spawn the mute helper on this speaker, notify, bucket = -TH"
S9 = "9  Vote is over: unmute whoever is muted, forget everybody"
S10 = "10  Vote is over: destroy every mute helper"

tag(S1, [G.set_t, G.set_m, G.sum_tm, G.rate, G.th, G.neg_th, G.gs, G.pa])
tag(S2, [G.tk, G.en, G.gsc, G.cg, G.vs, G.any_vote, G.end_vote, G.vote_or, G.gate, G.gbr])
tag(S3, [G.loop, G.psq, G.owner.node if hasattr(G.owner, "node") else None, G.pc, G.pid, G.bk1, G.find, G.found_br, G.n_new, G.s_sel])
tag(S4, [G.rv, G.lit, G.talking, G.consume, G.refill, G.is_muted, G.plus, G.minus, G.s2u, G.empty, G.low_a, G.low_b, G.low_and, G.s2m, G.resume])
tag(S5, [G.mbr, G.rbr, G.add_s2m, G.bk3])
tag(S6, [G.n_un, G.add_th, G.bk2])
tag(S7, [G.ebr, G.lbr, G.n_low, G.add_s2u, G.bk5])
tag(S8, [G.n_mu, G.add_neg, G.bk4])
tag(S9, [G.floop, G.fpsq, G.fpid, G.fbk, G.ffind, G.fbr, G.fneg, G.fmb, G.frem, G.fbk2])
mute_ranges = G.TOGGLE_RANGES  # order of creation: unmute(resume), mute, cleanup
tag(S6, NODES[mute_ranges[0][0]:mute_ranges[0][1]])
tag(S8, NODES[mute_ranges[1][0]:mute_ranges[1][1]])
tag(S10, NODES[mute_ranges[2][0]:mute_ranges[2][1]])
# the owner of the first loop is a pin, not a node: find the GetOwner node created right after the loop macro
for n in NODES:
    if id(n) not in section_of and n.cls == "K2Node_CallFunction":
        section_of[id(n)] = S3
for n in NODES:
    section_of.setdefault(id(n), S3)

order = [S1, S2, S3, S4, S5, S6, S7, S8, S9, S10]

# ---------- edges ----------
succ = {id(n): [] for n in NODES}
pred = {id(n): [] for n in NODES}
for n in NODES:
    for p in n.pins.values():
        if p.out:
            for q in p.links:
                if q.node is not n:
                    succ[id(n)].append(q.node)
                    pred[id(q.node)].append(n)


def is_pure(n):
    return n.cls in ("K2Node_VariableGet", "K2Node_EnumLiteral") or (
        n.cls == "K2Node_CallFunction" and "execute" not in n.pins)


def height(n):
    ins = [p for p in n.pins.values() if not p.out and not p.hidden]
    outs = [p for p in n.pins.values() if p.out and not p.hidden]
    h = 70 + 24 * max(len(ins), len(outs))
    h += 28 * sum(1 for p in ins if p.cat == "string" and p.default)
    if "Message" in n.pins:
        h += 90
    return h


def node_w(n):
    if "Message" in n.pins:
        return 520
    if any(p.cat == "string" and p.default for p in n.pins.values()):
        return 320
    return 210


COLGAP = 90
GAP = 36
SEC_GAP = 220
PAD = 70
cursor_y = 0
comments = []
for label in order:
    members = [n for n in NODES if section_of[id(n)] == label]
    mset = {id(n) for n in members}
    layer = {id(n): 0 for n in members}
    for n in members:  # creation order is a topological order for the exec chain, repeat to settle
        pass
    changed = True
    while changed:
        changed = False
        for n in members:
            for m in pred[id(n)]:
                if id(m) in mset and layer[id(n)] < layer[id(m)] + 1:
                    layer[id(n)] = layer[id(m)] + 1
                    changed = True
    # pure nodes sit just left of their first consumer
    changed = True
    while changed:
        changed = False
        for n in members:
            if is_pure(n):
                cons = [layer[id(c)] for c in succ[id(n)] if id(c) in mset]
                if cons and layer[id(n)] != min(cons) - 1 and min(cons) - 1 >= 0:
                    layer[id(n)] = min(cons) - 1
                    changed = True
    cols = {}
    for n in members:
        cols.setdefault(layer[id(n)], []).append(n)
    ypos = {}
    max_h = 0
    xoff = {}
    acc = 0
    for c in sorted(cols):
        xoff[c] = acc
        acc += max(node_w(n) for n in cols[c]) + COLGAP
    for c in sorted(cols):
        items = cols[c]

        def bary(n):
            ys = [ypos[id(m)] for m in pred[id(n)] if id(m) in ypos]
            return sum(ys) / len(ys) if ys else 1e9

        items.sort(key=lambda n: (bary(n), NODES.index(n)))
        y = 0
        for n in items:
            n.x = xoff[c]
            n.y = cursor_y + y
            ypos[id(n)] = y
            y += height(n) + GAP
        max_h = max(max_h, y)
    width = acc
    comments.append((label, -PAD, cursor_y - 2 * PAD, width + PAD, max_h + 2 * PAD))
    cursor_y += max_h + SEC_GAP

# ---------- same nodes, new positions ----------
after = [(n.name, n.cls, len(n.pins)) for n in NODES]
assert before == after, "node set changed"


def comment_text(i, label, x, y, w, h):
    return "\r\n".join([
        'Begin Object Class=/Script/UnrealEd.EdGraphNode_Comment Name="EdGraphNode_Comment_%d" '
        'ExportPath="/Script/UnrealEd.EdGraphNode_Comment\'%s.EdGraphNode_Comment_%d\'"' % (i, L.BP, i),
        "   NodeWidth=%d" % w,
        "   NodeHeight=%d" % h,
        '   NodeComment="%s"' % label,
        "   CommentColor=(R=0.12,G=0.30,B=0.55,A=1.0)",
        "   FontSize=28",
        "   NodePosX=%d" % x,
        "   NodePosY=%d" % y,
        "   NodeGuid=%s" % gid(),
        "End Object"])


with open(OUT, "w", encoding="utf-8", newline="") as f:
    f.write("\r\n".join([n.text() for n in NODES] + [comment_text(i, *c) for i, c in enumerate(comments)]) + "\r\n")
print("nodes", len(NODES), "comments", len(comments), "height", cursor_y)
for label, x, y, w, h in comments:
    print("%-80s x=%d y=%d w=%d h=%d" % (label, x, y, w, h))
