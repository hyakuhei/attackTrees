import json
from graphviz import Digraph
from attacktree.models import Action, Block, Discovery, Root, Goal, Node

from importlib import resources
import logging


class Renderer(object):
    def __init__(self, root="Root", goal="Goal"):
        self.rootLabel = root
        self.goalLabel = goal
        self.renderOnExit = True

    def __enter__(self):
        self.root = Root(label=self.rootLabel)
        self.goal = Goal(label=self.goalLabel)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.renderOnExit is True:
            self.render()
        return None

    # Addresses https://github.com/hyakuhei/attackTrees/issues/22
    # will replace _buildDot()
    def _buildDot(
        self,
        node: Node,
        dot: Digraph,
        mappedEdges: dict = {},
        dotformat: dict = {},
        defendedPath: bool = False,
    ):
        node_attr = None
        if node.__class__.__name__ in dotformat.keys():
            node_attr = dotformat[node.__class__.__name__]

        implemented = (
            True  # common case, most things will be implemented, we default to that.
        )
        # TODO: Move this default logic elsewhere, maybe force it into the basic node?
        if hasattr(node, "implemented") and node.implemented is False:
            implemented = False

        if node.__class__.__name__ in dotformat.keys():
            node_attr = dotformat[node.__class__.__name__]
            # Overload the default formatting shape if the Node is flagged as unimplemented

            nodeLabel = node.label
            if isinstance(node, (Action, Discovery)):
                nodeLabel += f"\n{node.pSuccess}"
            if isinstance(node, (Block)):
                nodeLabel += f"\n{node.pDefend}"
                defendedPath = True
            dot.node(node.uniq, node.label, **node_attr)
        else:
            dot.node(node.uniq, node.label)

        for edge in node.getEdges():
            # Setup default edge rendering style
            # TODO: Decide if we are talking about "path" or "edge"
            if defendedPath is True:
                edge_attr = dotformat["defendedEdge"]
            else:
                edge_attr = dotformat["Edge"]

            label = edge.label
            if edge.pSuccess is not None and edge.pSuccess != -1:
                label = label + f"\n {edge.pSuccess}%"

            # TODO: Replace edge mapping string (fancy) with dict of Edge object (simple)
            if f"{node.uniq}:{edge.childNode.uniq}" not in mappedEdges:
                # This is where the percentage % gets added
                dot.edge(node.uniq, edge.childNode.uniq, label=label, **edge_attr)
                # Keeps track of edge mapping so we don't get duplicates as we walk the tree, avoids never ending recursion
                mappedEdges[f"{node.uniq}:{edge.childNode.uniq}"] = True
                self._buildDot(
                    node=edge.childNode,
                    dot=dot,
                    mappedEdges=mappedEdges,
                    dotformat=dotformat,
                    defendedPath=defendedPath
                )  # recurse

    
    def loadStyle(self, path: str):
        # TODO: Do error handling
        with open(path) as json_file:
            style = json.load(json_file)

        return style

    def buildDot(
        self, root: Node = None, includeUnimplemented: bool = True, style: dict = None
    ):
        if root is None:
            return None

        # In case render is called multiple times, e.g jupyter
        dot = Digraph()
        dot.graph_attr["overlap"] = "false"
        dot.graph_attr["splines"] = "True"
        dot.graph_attr["nodesep"] = "0.2"
        dot.graph_attr["ranksep"] = "0.4"

        if style is None:
            with resources.open_text("attacktree", "style.json") as fid:
                style = json.load(fid)

        self._buildDot(root, dot, dotformat=style)  # recursive call
        return dot

    def render(
        self,
        root: Node = None,
        style: dict = None,
        fname: str = "attacktree-graph",
        fout: str = "png",
        renderOnExit=False,
        renderUnimplemented=False
    ):
        logging.warning("renderUnimplemented is deprectaed")
        self.renderOnExit = renderOnExit
        if root is None and self.root is not None:
            root = self.root  # sometimes we invoke as a context manager

        dot = self.buildDot(
            root=root, style=style
        )
        dot.format = fout
        dot.render(fname, view=True)
