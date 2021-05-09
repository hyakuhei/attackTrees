import uuid

# TODO: introduce sentinel value UNSET to replace None where the user simply hasn't given a value yet
# When a value is set to "None" - That shoud have meaning i.e:
#   detections = None means that there are no detections, not that the user just hasn't set them yet.

# TODO: Replace metadata with class values

defaultEdgeLabels={
    'Action':'Next',
    'Discovery':'Learn',
    'Block':'Fail',
    'Detect':'Detect'
}

rules = {
    'pSuccess':{
        'math':"multiply",
        'startWith':100,
        'unit':"probability",
        'formatString':"{}",
        'description':"pSuccess: int value between 0 and 1 that describes the probability of an `Action` or `Block` being effective within the given time"
    },
    "attackCost":{
        'math':"add",
        'startWith':0,
        'unit':"dollars",
        'formatString':"${}",
        'description':"cost: estimate of the number of dollars required to be invested to effectively run an `Action` or `Block`"
    },
    "time":{
        'math':"add",
        'startWith':0,
        'unit':"hours",
        'formatString':"{}h",
        'description':"time: estimate of how long this `Action` or `Block` will take to be effective"
    },
    "defenceCost":{
        'math':"add",
        'startWith':0,
        'unit':"dollars",
        'formatString':"${}",
        'description':"Cost of defensive controls"
    }
}

mitreAttack = {
    'recon':{
        'shortName': "recon",
        'friendlyName': "Reconnaissance",
        'objective': "The adversary is trying to gather information they can use to plan future operations",
        'url': "https://attack.mitre.org/tactics/TA0043/"
    },
    'resourceDev':{
        'shortName': "resourceDev",
        'friendlyName': "Resource Development",
        'objective': "The adversary is trying to establish resources they can use to support operations.",
        'url': "https://attack.mitre.org/tactics/TA0042/"
    },
    'credStuffing':{
        'shortName': "credStuffing",
        'friendlyName': "Credential Stuffing",
        'objective': "Adversaries may use credentials obtained from breach dumps of unrelated accounts to gain access to target accounts through credential overlap.",
        'url': "https://attack.mitre.org/techniques/T1110/004/"
    },
    'execution':{
        'shortName': "execution",
        'friendlyName': "Execution",
        'objective': "The adversary is trying to run malicious code.",
        'url': "https://attack.mitre.org/tactics/TA0002/"
    }
}

        #TODO: Replace concrete numbers with ranges and confidence intervals.

class Node(object):
    def __init__(self, label="Anonymous", metadata={}):
        self.label = label
        self.uniq = uuid.uuid4().hex #TODO: Remove this it's not needed, it's kinda here to make rendering work
        self.metadata = {}
        self.edges = []
        self.parentEdges = [] # backref

    #Backref means we don't actually create a real edge, we just maintain a list of backward references that we can draw in later. 
    #It's clunky but
    def connectTo(self, childNode, label=""):
        edge = Edge(parentNode=self, childNode=childNode, label=label)
        
        self.edges.append(edge)
        childNode.parentEdges.append(edge)
        return childNode

    def getEdges(self):
        return self.edges

    #shortcut to create a connected action
    def action(self, label: str, edge_label: str="Next"): 
        a = Action(label)
        self.connectTo(a, edge_label)
        return a

    # add (might replace connectTo)
    # add an action, provide a default edge_label and return the action
    # Makes writing models and declaring detailed actions easier

    # TODO: I had to drop type-hinting because the Node class can't resolve itself
    def add(self, node, edge_label: str=None):
        if edge_label == None:
            if node.__class__.__name__ in defaultEdgeLabels:
                edge_label = defaultEdgeLabels[node.__class__.__name__]
            else:
                edge_label = ""

        self.connectTo(node, edge_label)
        return node

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
        return f"{self.__class__.__name__}:{id(self)}"

class Edge:
    childNode = None
    label = ""
    metadata = None

    def __init__(self, parentNode, childNode, label, metadata={}, pSuccess=-1):
        self.parentNode = parentNode
        self.childNode = childNode
        self.pSuccess = pSuccess
        self.metadata = metadata
        self.label = label
        self.evaluated = False

    # Edge types:
    # Succeeds Undetected
    # Succeeds Detected
    # Fails Undetected
    
    def describe(self):
        return f"Edge '{self.label}' connects '{self.parentNode.label}' to '{self.childNode.label}'"

    def __repr__(self):
        return describe()

class Root(Node):
    def __init__(self,
                 label: str):
        super().__init__(label=label)

class Goal(Node):
    def __init__(self,
                 label: str):
        super().__init__(label=label)

# label: 'The name of the node',
# chain: 'The stage of the Mitre Att&ck chain represented, e.g "recon"'
# cost: 'Estimate of any material cost to this path, in dollars, does not include time'
# time: 'Estimate of time taken to complete the activity in hours
# pSuccess: Likelihood of success, 0-1
# detections: 'Any known detections for this activity that _could_ be 
class Action(Node):
    def __init__(self, 
                 label: str,
                 chain: dict = None,
                 cost: int = 0,
                 time: int = 0,
                 objective: str = "",
                 pSuccess: int = 100,
                 detections: list = []):
        super().__init__(label=label)
        self.pSuccess = pSuccess
        self.chain = chain
        self.cost = cost
        self.time = time
        # self.metadata = [] ## I don't have a need for this right now, so removing it,but I expect to need it later.

class Detect(Node):
    def __init__(self,
                 label: str,
                 implemented: bool,
                 cost: int = 0,
                 description: str = "",
                 complexity: int = 0,
                 latency: int = 0,
                 pDetect: int = 100):
        super().__init__(label=label)
        self.implemented = implemented
        self.cost = cost
        self.description = description
        self.complexity = complexity
        self.latency = latency
        self.pDetect = pDetect

class Block(Node):
    def __init__(self,
                 label: str,
                 implemented: bool,
                 cost: int = 0,
                 description: str = "",
                 complexity: int = 0,
                 pDefend: int = 100):
        super().__init__(label=label)
        self.implemented = implemented
        self.cost = cost
        self.description = description
        self.complexity = complexity
        self.pDefend = pDefend
    
    def insertBetween(self, a: Node, b: Node):
        # When two nodes are connected, insert a blocking node between them, replacing or updating the existing connection.
        # Add 'block' to a -> b

        #New rule. All Blocks are _inline_
        # a -> b becomes a-> block -> b


        # See if this block will work 100% (so it severes the connection) or partial, meaning we need to re-balance 
        # Connect A to the new block
        a.connectTo(self)

        # Blocks are always inline, so remove the a -> b edge
        for edge in a.edges:
            if edge.childNode == b:
                a.edges.remove(edge)
        else:
            self.connectTo(b)

            # a.metadata['pSuccess'] == the probability of the technique working
            # block.metadata['pDefend'] == the probability of the techniuqe being subsequently blocked
            # edge.pSuccess is the probability of progressing


# label: 'The name of the node'
# description: 'A description of the data/information 
# sensitivity: 'A description of how sensitive the data is considered to be
# value: 'Perceived monetary value if applicable'
# markings: 'Any specific markings for the data, like PII, SPI, HIPPA etc'
class Discovery(Node):
    def __init__(self,
                 label: str,
                 pSuccess: int = 100,
                 description: str = "",
                 sensitivity: int = 0,
                 value: int = 0,
                 markings: list = []):
        super().__init__(label=label)
        self.pSuccess = pSuccess
        self.description = description
        self.sensitivity = sensitivity
        self.value = value
        self.markings = markings