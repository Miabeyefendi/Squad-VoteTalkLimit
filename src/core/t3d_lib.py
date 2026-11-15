"""Generate pasteable Blueprint node text for BP_SmartShuffleDump (UE5 T3D clipboard format)."""
import uuid

OUT = None
BP = "/VoteTalkLimit/BP_VoteTalkLimit.BP_VoteTalkLimit:EventGraph"

SQ_PS = "/Script/CoreUObject.Class'/Script/Squad.SQPlayerState'"
SQ_LIB = "/Script/CoreUObject.Class'/Script/Squad.SQBlueprintLibrary'"
SQ_STATS = "/Script/CoreUObject.Class'/Script/Squad.SQStatsCollectorSubsystem'"
STR_LIB = "/Script/CoreUObject.Class'/Script/Engine.KismetStringLibrary'"
GPS = "/Script/CoreUObject.Class'/Script/Engine.GameplayStatics'"
GSB = "/Script/CoreUObject.Class'/Script/Engine.GameStateBase'"
PSB = "/Script/CoreUObject.Class'/Script/Engine.PlayerState'"
OBJ = "/Script/CoreUObject.Class'/Script/CoreUObject.Object'"
STATS_ENUM = "/Script/CoreUObject.Enum'/Script/Squad.ESQStatsType'"


def gid():
    return uuid.uuid4().hex.upper()


class Pin:
    def __init__(self, node, name, cat, out=False, subobj=None, container="None", ref=False, const=False,
                 default=None, defobj=None, hidden=False, friendly=None, wrapper=False, subcat='', valtype=None):
        self.node, self.name, self.cat, self.out = node, name, cat, out
        self.subobj, self.container, self.ref, self.const = subobj, container, ref, const
        self.default, self.defobj, self.hidden, self.friendly, self.wrapper = default, defobj, hidden, friendly, wrapper
        self.subcat, self.valtype = subcat, valtype
        self.id = gid()
        self.links = []

    def text(self):
        f = ["PinId=%s" % self.id, 'PinName="%s"' % self.name]
        if self.friendly:
            f.append("PinFriendlyName=%s" % self.friendly)
        if self.out:
            f.append('Direction="EGPD_Output"')
        f.append('PinType.PinCategory="%s"' % self.cat)
        f.append('PinType.PinSubCategory="%s"' % self.subcat)
        f.append('PinType.PinSubCategoryObject=%s' % ('"%s"' % self.subobj if self.subobj else "None"))
        f.append("PinType.PinSubCategoryMemberReference=()")
        vt = ('(TerminalCategory="%s",TerminalSubCategory="%s")' % self.valtype) if self.valtype else '()'
        f.append('PinType.PinValueType=%s' % vt)
        f.append("PinType.ContainerType=%s" % self.container)
        f.append("PinType.bIsReference=%s" % self.ref)
        f.append("PinType.bIsConst=%s" % self.const)
        f.append("PinType.bIsWeakPointer=False")
        f.append("PinType.bIsUObjectWrapper=%s" % self.wrapper)
        f.append("PinType.bSerializeAsSinglePrecisionFloat=False")
        if self.default is not None:
            f.append('DefaultValue="%s"' % self.default)
        if self.defobj:
            f.append('DefaultObject="%s"' % self.defobj)
        if self.links:
            f.append("LinkedTo=(%s)" % "".join("%s %s," % (p.node.name, p.id) for p in self.links))
        f.append("PersistentGuid=00000000000000000000000000000000")
        f.append("bHidden=%s" % self.hidden)
        f.append("bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,"
                 "bAdvancedView=False,bOrphanedPin=False")
        return "   CustomProperties Pin (%s,)" % ",".join(f)


class Node:
    counts = {}

    def __init__(self, cls, props, x, y):
        n = Node.counts.get(cls, 900)
        Node.counts[cls] = n + 1
        self.cls, self.props, self.x, self.y = cls, props, x, y
        self.name = "%s_%d" % (cls, n)
        self.pins = {}
        NODES.append(self)

    def pin(self, name, *a, **k):
        p = Pin(self, name, *a, **k)
        self.pins[name] = p
        return p

    def __getitem__(self, k):
        return self.pins[k]

    def text(self):
        lines = ['Begin Object Class=/Script/BlueprintGraph.%s Name="%s" ExportPath="/Script/BlueprintGraph.%s\'%s.%s\'"'
                 % (self.cls, self.name, self.cls, BP, self.name)]
        lines += ["   " + p for p in self.props]
        lines += ["   NodePosX=%d" % self.x, "   NodePosY=%d" % self.y, "   NodeGuid=%s" % gid()]
        lines += [p.text() for p in self.pins.values()]
        lines.append("End Object")
        return "\r\n".join(lines)


NODES = []
TARGET = 'NSLOCTEXT("K2Node", "Target", "Target")'


def link(a, b):
    a.links.append(b)
    b.links.append(a)


def call(parent, member, x, y, pure=False, static_obj=None):
    props = (["bDefaultsToPureFunc=True"] if pure else []) + [
        'FunctionReference=(MemberParent="%s",MemberName="%s")' % (parent, member)]
    n = Node("K2Node_CallFunction", props, x, y)
    if not pure:
        n.pin("execute", "exec")
        n.pin("then", "exec", out=True)
    n.pin("self", "object", subobj=parent, defobj=static_obj, hidden=bool(static_obj), friendly=TARGET)
    return n


def log_error(x, y, text=None):
    n = call(SQ_LIB, "LogError", x, y, static_obj="/Script/Squad.Default__SQBlueprintLibrary")
    n.pin("Contents", "string", default=text)
    return n


def concat(x, y, a_default=None, b_default=None):
    n = call(STR_LIB, "Concat_StrStr", x, y, pure=True, static_obj="/Script/Engine.Default__KismetStringLibrary")
    n.pin("A", "string", default=a_default)
    n.pin("B", "string", default=b_default)
    n.pin("ReturnValue", "string", out=True)
    return n


def to_str(kind, x, y):
    fn = "Conv_IntToString" if kind == "int" else "Conv_Int64ToString"
    n = call(STR_LIB, fn, x, y, pure=True, static_obj="/Script/Engine.Default__KismetStringLibrary")
    n.pin("InInt", kind, default="0")
    n.pin("ReturnValue", "string", out=True)
    return n


def camel(upper):
    return "".join(w.capitalize() for w in upper.split("_"))


