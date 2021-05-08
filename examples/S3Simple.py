from attacktree.models import Action, Block, Detect, Discovery, Edge
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
    graph.root.add(apiCache, edge_label="#Yolosec")

    s3urls = Discovery(
        label="S3 Urls",
        description="The URL paths to various S3 buckets",
        sensitivity=3,
        value=0
    )
    apiCache.add(s3urls, edge_label="#Yolosec")

    downloadFiles = Action(
        chain="exfiltration",
        label="Download files from all buckets",
        cost=0,
        time=1,
        objective="Access confidential information stored in S3",
        pSuccess=1.0,
        detections=["CloudWatch","DLP"]
    )
    s3urls.add(downloadFiles, edge_label="#Yolosec")
    downloadFiles.add(graph.goal, edge_label="#Yolosec")

    graph.render(
        renderUnimplemented=True,
        fname="example_S3Simple",
        fout="png"
    )