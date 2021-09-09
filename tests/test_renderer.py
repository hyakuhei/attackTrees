from attacktree.models import (
    Action,
    Block,
    Detect,
    Discovery,
    Edge,
    Node,
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


def test_contextManager(render=False):
    with Renderer(root="Reality", goal="Attacker gets data from bucket") as graph:
        pwd = graph.root.action("Use password")
        block = pwd.block("Block", implemented=False)
        block.connectTo(graph.goal)
