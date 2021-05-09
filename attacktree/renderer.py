import json
from graphviz import Digraph
from attacktree.models import Action, Block, Detect, Discovery, Edge, Root, Goal, Node

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
        if self.renderOnExit == True:
            self.render()
        return None
 
    # A recursive function that walks the node tree
    # And creates a graph for turning into graphviz
    def _buildDot(self, node: Node, dot: Digraph, renderUnimplemented: bool, mappedEdges: dict={}, dotformat: dict={}):
        node_attr = None # .dot formatting
        unimplemented = False

        if hasattr(node, "implemented") and node.implemented == False:
            unimplemented = True
        #TODO fix this wierd inverted logic
        
        # The node is marked as unimplemented and we are told not to render those nodes
        if renderUnimplemented == False and unimplemented == True:
            return

        if node.__class__.__name__ in dotformat.keys():
            node_attr = dotformat[node.__class__.__name__]
            # Overload the default formatting shape if the Node is flagged as unimplemented
            if unimplemented:
                node_attr = node_attr | dotformat['_unimplemented_override'] # Style the unimplemented node

            nodeLabel = node.label
            if isinstance(node, (Action, Discovery)):
                nodeLabel += f"\n{node.pSuccess}"
            if isinstance(node, (Block)):
                nodeLabel += f"\n{node.pDefend}"
            dot.node(node.uniq, node.label, **node_attr)
        else:
            dot.node(node.uniq, node.label)
        
        for edge in node.getEdges():
            # Make sure we don't draw a connection to an unimplemented node, if that renderUnimplemented == False
            
            edgeImplemented = True # default drawing style is to assume implemented

            if isinstance(node, Block) and node.implemented == False:
                edgeImplemented = False

            if isinstance(edge.childNode, Block) and edge.childNode.implemented == False:
                edgeImplemented = False

            # See if we should proceed with rendering the edge.
            # If not, we actually don't need to follow this branch any further
            # Short circuit the loop with a 'continue'
            if renderUnimplemented == False and edgeImplemented == False:
                continue

            # Setup default edge rendering style
            edge_attr = dotformat['Edge']

            # Override style for unimplemented edge
            if edgeImplemented == False:
                edge_attr = edge_attr | dotformat['_unimplemented_edge'] # style the unimplemented edge

            label = edge.label
            if edge.pSuccess != None and edge.pSuccess != -1:
                label = label + f"\n {edge.pSuccess}%"

            #TODO: Replace edge mapping string (fancy) with dict of Edge object (simple)
            if f"{node.uniq}:{edge.childNode.uniq}" not in mappedEdges:
                dot.edge(node.uniq, edge.childNode.uniq, label=label, **edge_attr) # This is where the percentage % gets added
                mappedEdges[f"{node.uniq}:{edge.childNode.uniq}"] = True # Keeps track of edge mapping so we don't get duplicates as we walk the tree, avoids never ending recursion
                self._buildDot(node=edge.childNode, dot=dot, renderUnimplemented=renderUnimplemented, mappedEdges=mappedEdges, dotformat=dotformat) #recurse

    def loadStyle(self, path: str):
        # TODO: Do error handling
        with open(path) as json_file:
            style = json.load(json_file)
        
        return style

    def render(self, root: Node=None, renderUnimplemented: bool=True, style: dict={}, fname: str="attacktree-graph", fout: str="png", renderOnExit=False):
        if root is not None:
            self.root = root

        if self.root is None:
            # No graph to render
            logging.error("No graph to render")
            return
        
        # TODO: move this out to a config:
        
        self.renderOnExit = renderOnExit # In case render is called multiple times, e.g jupyter 
        dot = Digraph()
        dot.graph_attr['overlap']='false'
        dot.graph_attr['splines']='True'
        dot.graph_attr['nodesep']="0.2"
        dot.graph_attr['ranksep']="0.4"
 
        if len(style) == 0: #TODO: Make this a better check
            with resources.open_text("attacktree", "style.json") as fid:
                style = json.load(fid)

        self._buildDot(self.root, dot, dotformat=style, renderUnimplemented=renderUnimplemented) #recursive call
        dot.format = fout
        dot.render(fname, view=True)
