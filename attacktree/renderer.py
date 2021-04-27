import json
from graphviz import Digraph
from attacktree.models import Action, Block, Detect, Discovery, Edge, Node

from importlib import resources

class Renderer(object):

    def __init__(self, root="Root", goal="Goal"):
        self.rootLabel = root
        self.goalLabel = goal

    def __enter__(self):
        self.root = Node(label=self.rootLabel)
        self.goal = Node(label=self.goalLabel)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        return None
 
    # A recursive function that walks the node tree
    # And creates a graph for turning into graphviz
    def _buildDot(self, node: Node, dot: Digraph, renderUnimplemented: bool, mappedEdges: dict={}, dotformat: dict={}):
        node_attr = None # .dot formatting
        unimplemented = False
        if 'implemented' in node.metadata.keys() and node.metadata['implemented']==False:
            unimplemented = True
        
        # The node is marked as unimplemented and we are told not to render those nodes
        if renderUnimplemented == False and unimplemented == True:
            return

        if node.__class__.__name__ in dotformat.keys():
            node_attr = dotformat[node.__class__.__name__]
            # Overload the default formatting shape if the Node is flagged as unimplemented
            if unimplemented:
                node_attr = node_attr | dotformat['_unimplemented_override']

            dot.node(node.uniq, node.label, **node_attr)
        else:
            dot.node(node.uniq, node.label)
        
        for edge in node.getEdges():
            # Make sure we don't draw a connection to an unimplemented node, if that renderUnimplemented == False
            
            edgeImplemented = True # default drawing style is to assume implemented
            if 'implemented' in node.metadata.keys() and node.metadata['implemented'] == False:
                edgeImplemented = False
            if 'implemented' in edge.endNode.metadata.keys() and edge.endNode.metadata['implemented'] == False:
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
                edge_attr = edge_attr | dotformat['_unimplemented_edge']

            if f"{node.uniq}:{edge.endNode.uniq}" not in mappedEdges:
                dot.edge(node.uniq, edge.endNode.uniq, label=edge.label, **edge_attr)
                mappedEdges[f"{node.uniq}:{edge.endNode.uniq}"] = True # Keeps track of edge mapping so we don't get duplicates as we walk the tree, avoids never ending recursion
                self._buildDot(node=edge.endNode, dot=dot, renderUnimplemented=renderUnimplemented, mappedEdges=mappedEdges, dotformat=dotformat) #recurse

    def loadStyle(self, path: str):
        # TODO: Do error handling
        with open(path) as json_file:
            style = json.load(json_file)
        
        return style

    def render(self, renderUnimplemented: bool=True, style: dict={}, fname: str="AttackTree", fout: str="png"):
        # TODO: move this out to a config:
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
