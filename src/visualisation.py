from src.utils import Edge
import os

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.weighted_push_relabel import WeightedPushRelabel


frames = 0

ENABLED = os.environ.get("VISUALISE", False)

def graphviz_frame(instance: "WeightedPushRelabel", kind: str = "", aug_path: set[Edge] | None = None):
    global frames

    if not ENABLED:
        return

    if aug_path is None:
        aug_path = set()

    path = f"frames/iter_{frames}.dot"
    frames += 1

    all_edges: set[Edge] = set()
    for v in instance.G.V:
        all_edges.update(instance.outgoing[v])

    nodes: set[str] = set()
    edges: list[str] = list()

    for e in all_edges:
        def mk_node(v: int):
            color = "black" if v in instance.alive else "firebrick3"
            style = "solid" if v in instance.alive else "dashed"
            return f'{v} [label="{v} ({instance.l[v]:>2})", color="{color}", fontcolor="{color}", style="{style}"];'

        nodes.add(mk_node(e.u))
        nodes.add(mk_node(e.v))

        if not e.forward:
            continue

        dir = "forward"
        if instance.c_f(e.reversed()) > 0:
            if instance.c_f(e) == 0:
                dir = "back"
            else:
                dir = "both"

        color = "black"
        style = "solid"
        if instance.c_f(e) == 0:
            color = "firebrick3"
        elif instance.f[e] > 0:
            if e in instance.admissible_outgoing[e.start()]:
                color = "chartreuse4"
            else:
                color = "goldenrod"
                style = "dashed"
        elif e not in instance.admissible_outgoing[e.start()]:
            color = "gray"
            style = "dashed"

        if e in aug_path or e.reversed() in aug_path:
            color = "blue"

        attrs = {
            "label": f"{instance.c_f(e)}/{instance.c_f(e.reversed())}/{e.c}\\lw={instance.w(e)}",
            "color": color,
            "style": style,
            "dir": dir,
            "arrowtail": "empty",
            "penwidth": 2
        }

        attrs_str = ",".join(f'{k}="{v}"' for k, v in attrs.items())
        edges.append(f'{e.u} -> {e.v} [{attrs_str}];')

    with open(path, "w") as f:
        _ = f.write("digraph G {\n")
        _ = f.write(f'   labelloc="t"; label="{kind}";ordering=out;\n')
        f.writelines(f"   {node}\n" for node in nodes)
        f.writelines(f"   {edge}\n" for edge in edges)
        _ = f.write("}\n")
