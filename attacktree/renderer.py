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

    # A recursive function that walks the node tree
    # And creates a graph for turning into graphviz
    # TODO: Fix complexity PEP8 C901
    def _buildDot(
        self,
        node: Node,
        dot: Digraph,
        renderUnimplemented: bool,
        mappedEdges: dict = {},
        dotformat: dict = {},
    ):
        node_attr = None  # .dot formatting
        unimplemented = False

        if hasattr(node, "implemented") and node.implemented is False:
            unimplemented = True
        # TODO fix this wierd inverted logic

        # The node is marked as unimplemented and we are told not to render those nodes
        if renderUnimplemented is False and unimplemented is True:
            return

        if node.__class__.__name__ in dotformat.keys():
            node_attr = dotformat[node.__class__.__name__]
            # Overload the default formatting shape if the Node is flagged as unimplemented
            if unimplemented:
                # Style the unimplemented node
                node_attr = node_attr | dotformat["_unimplemented_override"]

            nodeLabel = node.label
            if isinstance(node, (Action, Discovery)):
                nodeLabel += f"\n{node.pSuccess}"
            if isinstance(node, (Block)):
                nodeLabel += f"\n{node.pDefend}"
            dot.node(node.uniq, node.label, **node_attr)
        else:
            dot.node(node.uniq, node.label)

        for edge in node.getEdges():
            # Make sure we don't draw a connection to an unimplemented node, if that renderUnimplemented is False

            edgeImplemented = True  # default drawing style is to assume implemented

            if isinstance(node, Block) and node.implemented is False:
                edgeImplemented = False

            if (
                isinstance(edge.childNode, Block)
                and edge.childNode.implemented is False
            ):
                edgeImplemented = False

            # See if we should proceed with rendering the edge.
            # If not, we actually don't need to follow this branch any further
            # Short circuit the loop with a 'continue'
            if renderUnimplemented is False and edgeImplemented is False:
                continue

            # Setup default edge rendering style
            edge_attr = dotformat["Edge"]

            # Override style for unimplemented edge
            if edgeImplemented is False:
                # style the unimplemented edge
                edge_attr = edge_attr | dotformat["_unimplemented_edge"]

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
                    renderUnimplemented=renderUnimplemented,
                    mappedEdges=mappedEdges,
                    dotformat=dotformat,
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

        self._buildDot(
            root, dot, dotformat=style, renderUnimplemented=includeUnimplemented
        )  # recursive call
        return dot

    def render(
        self,
        root: Node = None,
        renderUnimplemented: bool = True,
        style: dict = None,
        fname: str = "attacktree-graph",
        fout: str = "png",
        renderOnExit=False,
    ):

        self.renderOnExit = renderOnExit
        if root is None and self.root is not None:
            root = self.root # sometimes we invoke as a context manager

        dot = self.buildDot(
            root=root, includeUnimplemented=renderUnimplemented, style=style
        )
        dot.format = fout
        dot.render(fname, view=True)
