from attacktree.models import Action, Block, Detect, Discovery, Edge, Root, Goal  #classes
from attacktree.models import mitreAttack, rules #dicts
from attacktree.renderer import Renderer
from attacktree.brain import Brain

import pytest
import inspect
import math #TODO: Refactor out the floats for probability and replace with 0-100int

def test_insertBetween_50perecent(render=False):
    # Prep
    root = Root("Start")
    goal = Goal("Finish")

    a = root.action("A")
    b = a.action("B")
    c = b.action("C")

    c.connectTo(goal)

    # Verify prep
    assert(len(a.edges)==1)
    assert(a.edges[0].childNode == b)

    # Create a block
    block = Block(
        label="Test Block",
        implemented=True,
        cost=5000,
        pDefend=50)

    # The tested function
    block.insertBetween(a, b)

    # After 
    assert(len(a.edges)==1)
    assert(len(block.edges)==1)
    assert(a.edges[0].childNode.edges[0].childNode == b)

    if render:
        Renderer().render(
            root=root,
            fname=inspect.currentframe().f_code.co_name
        )

def test_insertBlockBetween_100perecent(render=False):
    # Prep
    root = Root("Start")
    goal = Goal("Finish")

    a = root.action("A")
    b = a.action("B")
    c = b.action("C")

    c.connectTo(goal)

    #Before
    assert(len(b.edges)==1)

    # Create a  second block with a pSuccess of 100
    block = Block(
        label="Test Block",
        implemented=True,
        cost=5000,
        pDefend=100)

    # The tested function
    block.insertBetween(b, c)

    # After 
    assert(len(b.edges)==1) # As the block has 100% chance of working, c should be unreachable
    assert(b.edges[0].childNode == block)

    if render:
        Renderer().render(
            root=root,
            fname=inspect.currentframe().f_code.co_name
        )

def test_instertBlockBetweenPatiallySuccessfulActions(render=True):
    # Prep
    root = Root("Start")
    goal = Goal("Finish")

    a = root.add(Action(
        label="A",
        pSuccess=80
    ))

    b = a.action("B")
    c = b.action("C")

    c.connectTo(goal)

    # a has an 80percent chance of working.
    # lets add a blocker that's 20% effective

    block = Block(
        label="Test Block",
        implemented=True,
        cost=5000,
        pDefend=50)

    # The tested function
    block.insertBetween(a, b)

    assert(len(a.edges)==1)
    assert(a.edges[0].childNode==block)
    
    assert(len(block.edges)==1)
    assert(block.edges[0].childNode==b)

    # The tested function:
    if render:
        Renderer().render(
            root=root,
            fname=inspect.currentframe().f_code.co_name
        )

