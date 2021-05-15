from attacktree.models import (
    Action,
    Block,
    Detect,
    Discovery,
    Edge,
    Root,
    Goal,
    mitreAttack,
    rules,
)
from attacktree.renderer import Renderer
from attacktree.brain import Brain

import pytest
import logging
import inspect

# Note, this will be used for testing, so to make life easy,
# we don't use the Renderer context manager

# TODO: It would be nice to build/find a database of Mitre attack techniques so you could just reference(or search for) a technique


def basicTree():
    root = Root("Root")
    goal = Goal("Systems Access")

    # Create three top tier actions
    networkRecon = root.add(
        Action(
            label="Network Recon",
            chain=mitreAttack["recon"],
            cost=0,
            time=24,
            objective="Find network attack surface",
            pSuccess=100,
            detections=None,
        )
    )

    dnsEnumeration = root.add(
        Action(
            label="DNS Enumeration",
            chain=mitreAttack["recon"],
            cost=0,
            time=4,
            objective="Identify all subdomains",
            pSuccess=100,
        )
    )

    linkedInResearch = root.add(
        Action(
            label="LinkedIn Research",
            chain=mitreAttack["recon"],
            cost=0,
            time=6,
            objective="Identify names and email addresses of current employees and customers",
            pSuccess=100,
        )
    )

    # Stuff learned from those activities
    vpnEndpoint = networkRecon.discovery("VPN Endpoints")
    sshEndpoint = networkRecon.discovery("SSH Endpoints")
    subdomains = dnsEnumeration.discovery("subdomains")
    employeeNames = linkedInResearch.discovery("Employee Names")
    keyCustomerNames = linkedInResearch.discovery("Key Customer Details")

    # Actions taken based on those discoveries
    credentialStuffing = Action(
        label="Credential Stuffing",
        chain=mitreAttack["credStuffing"],
        cost=500,
        time=12,
        objective="Try known username/password",
        pSuccess=100,
    )
    _ = sshEndpoint.add(credentialStuffing)
    _ = vpnEndpoint.add(credentialStuffing)
    _ = employeeNames.add(credentialStuffing)

    sqlmap = subdomains.add(
        Action(
            label="sqlmap", chain=mitreAttack["execution"], cost=0, time=2, pSuccess=75
        )
    )

    nikto = subdomains.action("nikto")

    phishing = employeeNames.action("SET Phishing")
    keyCustomerNames.connectTo(phishing)

    # Action Results
    sqli = sqlmap.add(
        Discovery(
            label="Blind injection, viable RCE",
            description="",
            sensitivity=10,
            value=1000,
        )
    )

    dbExploit = sqli.add(
        Action(
            label="Craft & Deploy RCE",
            chain=mitreAttack["execution"],
            cost=0,
            time=2,
            pSuccess=75,
        )
    )

    # Action Results that get to the goal
    credentialStuffing.connectTo(goal, label="Passwords Reused")
    phishing.connectTo(goal, label="Credentials Stolen")
    dbExploit.connectTo(goal)

    return root


def test_buildTree(render=True):
    root = basicTree()
    brain = Brain()

    # Check root is correct type
    assert isinstance(root, Root)

    paths = brain.pathsToVictory(root)

    for path in paths:
        brain.evaluatePath(path)

    assert len(paths) == 3

    if render:
        Renderer().render(root=root, fname=inspect.currentframe().f_code.co_name)


def test_multiplePathsToVitory():
    root = Root("Root")
    goal = Goal("Goal")

    # Test with just one action
    root.add(Action(label="A")).add(goal)

    assert len(root.parentEdges) == 0
    assert len(goal.parentEdges) == 1
    assert goal.parentEdges[0].parentNode.label == "A"

    brain = Brain()
    paths = brain.pathsToVictory(root)
    assert len(paths) == len(goal.parentEdges)

    brain = Brain()
    paths = brain.pathsToVictory(root)
    assert len(paths) == len(goal.parentEdges)


def test_single_pathToVictory(render=False):
    root = Root("Root")
    goal = Goal("Goal")

    # Test with just one action
    root.add(Action(label="A")).add(goal)
    brain = Brain()
    paths = brain.pathsToVictory(root)
    print(paths)
    assert len(paths) == 1
    assert len(paths[0]) == 3

    if render:
        Renderer().render(root=root, fname=inspect.currentframe().f_code.co_name)


def test_double_pathToVictory(render=True):
    root = Root("Root XX")
    goal = Goal("Goal")

    # Test with just one action
    root.add(Action(label="A")).add(goal)
    root.add(Action(label="B")).add(goal)

    brain = Brain()
    paths = brain.pathsToVictory(root)
    print(paths)
    assert len(paths) == 2
    assert len(paths[0]) == 3
    assert len(paths[1]) == 3

    if render:
        Renderer().render(root=root, fname=inspect.currentframe().f_code.co_name)


def test_quad_pathToVictory(render=True):
    root = Root("Root XXXX")
    goal = Goal("Goal")

    # Test with just one action
    root.add(Action(label="A")).add(goal)
    root.add(Action(label="B")).add(goal)
    root.add(Action(label="C")).add(goal)
    root.add(Action(label="D")).add(goal)

    brain = Brain()
    paths = brain.pathsToVictory(root)
    assert len(paths) == 4
    assert len(paths[0]) == 3
    assert len(paths[1]) == 3
    assert len(paths[2]) == 3
    assert len(paths[3]) == 3

    if render:
        Renderer().render(root=root, fname=inspect.currentframe().f_code.co_name)


def test_pathEvaluation(render=True):
    # TODO: Make this test more useful
    root = Root("Root")
    goal = Goal("Goal")
    brain = Brain()

    # One path to vicotry (Start->a->b>c->goal)
    a = root.add(Action("A", pSuccess=100, cost=500))
    b = a.add(Action("B", pSuccess=50, cost=500))
    c = b.add(Action("C", pSuccess=50, cost=500))
    _ = c.add(goal)

    # Update model with a second path to victory (Start->a->bb->goal)
    bb = a.add(Action("BB", pSuccess=100, cost=20000))
    bb.connectTo(goal)

    paths = []
    _ = Brain().pathsToVictory(root, paths)
    print(paths)
    assert len(paths) == 2

    res = brain.evaluatePath(paths[1])  # a -> bb -> goal
    assert res["attackCost"] == 20500
    assert res["pSuccess"] == 100  # a * bb

    if render:
        Renderer().render(root=root, fname=inspect.currentframe().f_code.co_name)


def test_pathEvaluationWithBlock(render=True):
    root = Root("Root")
    goal = Goal("Goal")
    brain = Brain()

    a = root.add(Action("A", pSuccess=100, cost=500))
    b = a.add(Action("b", pSuccess=70, cost=500))
    b.add(goal)

    paths = []
    _ = brain.pathsToVictory(root, paths)

    assert len(paths) == 1

    res = brain.evaluatePath(paths[0])

    # Check results are correct before we add a block
    assert res["attackCost"] == 1000
    assert res["pSuccess"] == 70

    assert a.pSuccess == 100

    block = Block(label="FIREWALL", implemented=True, cost=0, pDefend=50)
    block.insertBetween(a, b)

    paths = []
    _ = brain.pathsToVictory(root, paths)
    res = brain.evaluatePath(paths[0])

    print(res)

    assert res["attackCost"] == 1000
    assert res["pSuccess"] == 35

    if render:
        Renderer().render(root=root, fname=inspect.currentframe().f_code.co_name)
