from attacktree.models import Action, Block, Detect, Discovery, Edge, Node
from attacktree.renderer import Renderer

with Renderer(root = "Reality", goal= "Attacker gets data from bucket") as graph:
    
    apiCache = Action(
        label="Search API Caches",
        chain="recon",
        cost=0,
        time=3,
        objective="Discover bucket paths",
        pSuccess=1.0
    )
    graph.root.connectTo(apiCache, label="#Yolosec")

    s3urls = Discovery(
        label="S3 Urls",
        description="The URL paths to various S3 buckets",
        sensitivity=3,
        value=0
    )
    apiCache.createEdge(s3urls, label="#Yolosec")

    downloadFiles = Action(
        chain="exfiltration",
        label="Download files from all buckets",
        cost=0,
        time=1,
        objective="Access confidential information stored in S3",
        pSuccess=1.0,
        detections=["CloudWatch","DLP"]
    )
    s3urls.createEdge(downloadFiles, label="#Yolosec")
    downloadFiles.createEdge(goal, label="#Yolosec")

    style = renderer.loadStyle('style.json')
    renderer.render(
        node=root,
        renderUnimplemented=True,
        style=style,
        fname="example_simpleS3",
        fout="png"
    )