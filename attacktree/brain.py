
# import Node classes
from attacktree.models import Action, Block, Detect, Discovery, Edge, Root, Goal, Node

# import some useful dicts
from attacktree.models import mitreAttack, rules

import logging
import copy

class Brain(object):
    def __init__(self):
        self.exploitChain = []

    # Walk throught the nodes of tree and print if metadata is missing
    def lint(self, root: Node, walked: dict={}):
        pass
        # Walk and print metadata

    # Walk the tree, adding to the chain (DFS)
    # If we hit the goal, add that chain to our paths 
    def pathsToVictory(self,
                       node: Node,
                       paths: list=None,
                       chain: list=None,
                       walked: dict=None):
        
        if walked == None:
            walked = {}

        if paths == None:
            paths = []

        if chain == None:
            chain = []

        chain.append(node)
        
        # If this node is a Goal then YAY! We have a goal
        if isinstance(node, Goal):
            paths.append(chain.copy())
            return paths
        
        edges = node.getEdges()
        for edge in edges:
            if edge not in walked:
                self.pathsToVictory(edge.childNode, paths, chain=chain.copy(), walked=walked)
                walked[edge] = True # Stops walking a cycle more than once

        return paths

    def evaluatePath(self, path):
        #TODO: Replace concrete numbers with ranges and confidence intervals.
        # It's not the nodes we need to evaluate, it's the edges. As those are what get changed adding a block
        results = {}
        for key in rules: #Pre-load data from rules
            results[key] = rules[key]['startWith']
 
        prevNode = None
        for node in path:
            if isinstance(node, (Action)):
                results['attackCost'] += node.metadata['cost']
                results['time'] += node.metadata['time']
                results['pSuccess'] = int((results['pSuccess'] * node.metadata['pSuccess']) / 100)
            if isinstance(node, (Block)):
                results['defenceCost']  += node.metadata['cost']
                results['pSuccess'] -= node.metadata['pDefend']
                #TODO block time

            if prevNode is not None:
                edgeToThisNode = None 
                for edge in prevNode.edges:
                    if edge.childNode == node:
                        edgeToThisNode = edge

                if edgeToThisNode is None: # This shouldn't happen and we should try to get rid of this check.
                    print(f"Could not find an edge to {node.label}")
                    print(f"PrevNode: {prevNode.label}")
                    print(f"Path: {path}\n")
                else:
                    edgeToThisNode.pSuccess = results['pSuccess']
            
            prevNode = node
            # Can't just throw in a backfref because a node can have multiple parents
            # End outer for by setting current node as the next (prevNode )

        return results        


        