from attacktree.models import Action, Block, Detect, Discovery, Edge
from attacktree.renderer import Renderer

with Renderer(root="Internet", goal="Launch Containers") as graph:

    breakApplication = Action(label="RCE in application")
    graph.root.add(breakApplication)

    patch = Block(label="Keep containers up to date", implemented=True)
    breakApplication.add(patch)

    executeSiloScape = Action(label="Execute Siloscape")
    breakApplication.add(executeSiloScape)

    systemPrivileges = Discovery(label="Privileged Access")
    executeSiloScape.add(systemPrivileges)

    symLinkDrive = Action(label="SymLink root volume")
    systemPrivileges.add(symLinkDrive)

    kubeConfig = Action(label="Find Kubernetes creds on disk")
    symLinkDrive.add(kubeConfig)

    deployMalicious = Action(label="Deploy malicious containers")
    kubeConfig.add(deployMalicious)

    runWindowsContainersWithLowPrivilege = Block(
        label="Windows containers have low privilege", implemented=False
    )
    deployMalicious.add(runWindowsContainersWithLowPrivilege)
    deployMalicious.add(graph.goal)

    graph.render(renderUnimplemented=True, fname="siloscape", fout="png")
