import uuid

# Todo, introduce sentinel value 

class Node:
    def __init__(self, label="Anonymous", metadata={}, nodeType=""):
        self.label = label
        self.nodeType = nodeType
        self.uniq = uuid.uuid4().hex
        self.edges = []
        self.metadata = {}

    #Backref means we don't actually create a real edge, we just maintain a list of backward references that we can draw in later. 
    #It's clunky but
    def connectTo(self, endNode, label=""):
        edge = Edge(endNode=endNode, label=label)
        edge.label = label
        self.edges.append(edge)
        return endNode

    def getEdges(self):
        return self.edges

    #shortcut to create a connected action
    def action(self, label: str, edge_label: str="Next"): 
        a = Action(label)
        self.connectTo(a, edge_label)
        return a

    #shortcut to create a connected block
    def block(self, label: str, implemented: bool, edge_label: str="Fail"):
        b = Block(label, implemented=implemented)
        self.connectTo(b, edge_label)
        return b

    #shortcut to create a connected detection
    def detect(self, label: str, implemented: bool, edge_label: str="Detect"):
        d = Detect(label, implemented=implemented)
        self.connectTo(d, edge_label)
        return d

    #shortcut to create a connected discovery
    def discovery(self, label: str, edge_label: str="Learn"):
        d = Discovery(label)
        self.connectTo(d, edge_label)
        return d

    def __repr__(self):
        return f"[{self.label}]"

class Edge:
    endNode = None
    label = ""
    metadata = None

    def __init__(self, endNode, label, metadata={}):
        self.endNode = endNode
        self.label = label
        self.metadata = metadata

    # Edge types:
    # Succeeds Undetected
    # Succeeds Detected
    # Fails Undetected
    # Fails Detected
    def __repr__(self):
        return f"---{self.label}-->"

# label: 'The name of the node',
# chain: 'The stage of the Mitre Att&ck chain represented, e.g "recon"'
# cost: 'Estimate of any material cost to this path, in dollars, does not include time'
# time: 'Estimate of time taken to complete the activity in hours
# pSuccess: Likelihood of success, 0-1
# detections: 'Any known detections for this activity that _could_ be 
class Action(Node):
    def __init__(self, 
                 label: str,
                 chain: str = "",
                 cost: int = 0,
                 time: int = 0,
                 objective: str = "",
                 pSuccess: float = 1.0,
                 detections: list = []):
        super().__init__(label=label, nodeType="Action")
        self.metadata = {}
        self.metadata['chain'] = chain
        self.metadata['cost'] = cost
        self.metadata['time'] = time
        self.metadata['pSuccess'] = pSuccess
        self.metadata['detections'] = detections
        self.edges = []

class Detect(Node):
    def __init__(self,
                 label: str,
                 implemented: bool,
                 cost: int = 0,
                 description: str = "",
                 complexity: int = 0,
                 latency: int = 0,
                 pSuccess: float = 1.0):
        super().__init__(label=label, nodeType="Detect")
        self.metadata = {}
        self.metadata['cost'] = cost
        self.metadata['description'] = description
        self.metadata['complexity'] = complexity
        self.metadata['latency'] = latency
        self.metadata['implemented'] = implemented
        self.metadata['pSuccess'] = pSuccess
        self.edges = []

class Block(Node):
    def __init__(self,
                 label: str,
                 implemented: bool,
                 cost: int = 0,
                 description: str = "",
                 complexity: int = 0,
                 pSuccess: float = 1.0):
        super().__init__(label=label, nodeType="Block")
        self.metadata = {}
        self.metadata['cost'] = cost
        self.metadata['description'] = description
        self.metadata['complexity'] = complexity
        self.metadata['implemented'] = implemented
        self.metadata['pSuccess'] = pSuccess
        self.edges = []

# label: 'The name of the node'
# description: 'A description of the data/information 
# sensitivity: 'A description of how sensitive the data is considered to be
# value: 'Perceived monetary value if applicable'
# markings: 'Any specific markings for the data, like PII, SPI, HIPPA etc'
class Discovery(Node):
    def __init__(self,
                 label: str,
                 description: str = "",
                 sensitivity: int = 0,
                 value: int = 0,
                 markings: list = []):
        super().__init__(label=label)
        self.metadata={}
        self.metadata['description'] = description
        self.metadata['sensitivity'] = sensitivity
        self.metadata['value'] = value
        self.metadata['markings'] = markings
        self.edges = []