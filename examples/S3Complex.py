from attacktree.models import Action, Block, Detect, Discovery
from attacktree.renderer import Renderer

with Renderer(root="Reality", goal="Attacker gets data from bucket") as graph:

    apiCache = Action(
        label="Search API Caches",
        chain="recon",
        cost=0,
        time=3,
        objective="Discover bucket paths",
        pSuccess=1.0,
    )

    siteMapsDisabled = Block(
        label="Sitemaps disabled",
        cost=0,
        description="Ensure sitemaps are disabled",
        complexity=1,
        implemented=False,
        pDefend=1.0,
    )

    awsPublicBucketSearch = Action(
        label="AWS Public Bucket Search",
        chain="recon",
        cost=200,
        time=1,
        objective="Discover bucket paths",
        pSuccess=1.0,
    )

    s3urls = Discovery(
        label="S3 Urls",
        description="The URL paths to various S3 buckets",
        sensitivity=3,
        value=0,
    )

    downloadFiles = Action(
        chain="exfiltration",
        label="Download files from all buckets",
        cost=0,
        time=1,
        objective="Access confidential information stored in S3",
        pSuccess=1.0,
        detections=["CloudWatch", "DLP"],
    )

    bucketACLs = Block(
        label="Buckets are private",
        cost=0,
        description="All S3 buckets are set to private",
        complexity=0,
        implemented=False,
        pDefend=1.0,
    )

    graph.root.connectTo(apiCache, label="#Yolosec").connectTo(
        siteMapsDisabled, label="Fail"
    ).connectTo(awsPublicBucketSearch, label="Next").connectTo(
        s3urls, label="Next"
    ).connectTo(
        downloadFiles, label="#Yolosec"
    ).connectTo(
        graph.goal, label="#Yolosec"
    )

    apiCache.connectTo(s3urls, label="#Yolosec")
    downloadFiles.connectTo(bucketACLs, label="Fail")
    awsPublicBucketSearch.connectTo(bucketACLs, label="Fail")

    graph.render(renderUnimplemented=True, fname="example_complexS3", fout="png")
