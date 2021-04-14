from models import Action, Block, Detect, Discovery, Edge, Node
import renderer

if __name__ == "__main__":
    root = Node(label="Reality")
    goal = Node(label="Attacker gets data from bucket")

    apiCache = Action(
        label="Search API Caches",
        chain="recon",
        cost=0,
        time=3,
        objective="Discover bucket paths",
        pSuccess=1.0
    )
    root.createEdge(apiCache,label="#Yolosec")

    siteMapsDisabled = Block(
        label="Sitemaps disabled",
        cost=0,
        description="Ensure sitemaps are disabled",
        complexity=1,
        implemented=False,
        pSuccess=1.0
    )
    apiCache.createEdge(siteMapsDisabled, label="Fail")

    awsPublicBucketSearch = Action(
        label="AWS Public Bucket Search",
        chain="recon",
        cost=200,
        time=1,
        objective="Discover bucket paths",
        pSuccess=1.0
    )
    siteMapsDisabled.createEdge(awsPublicBucketSearch, label="Next")

    s3urls = Discovery(
        label="S3 Urls",
        description="The URL paths to various S3 buckets",
        sensitivity=3,
        value=0
    )
    apiCache.createEdge(s3urls, label="#Yolosec")
    awsPublicBucketSearch.createEdge(s3urls, label="Next")

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

    bucketACLs = Block(
        label="Buckets are private",
        cost=0,
        description="All S3 buckets are set to private",
        complexity=0,
        implemented=False,
        pSuccess=1.0
    )
    downloadFiles.createEdge(bucketACLs, label="Fail")

    style = renderer.loadStyle('style.json')
    renderer.render(
        node=root,
        renderUnimplemented=True,
        style=style,
        fname="example_complexS3",
        fout="png"
    )