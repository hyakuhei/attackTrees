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
    
    siteMapsDisabled = Block(
        label="Sitemaps disabled",
        cost=0,
        description="Ensure sitemaps are disabled",
        complexity=1,
        implemented=False,
        pSuccess=1.0
    )
    
    awsPublicBucketSearch = Action(
        label="AWS Public Bucket Search",
        chain="recon",
        cost=200,
        time=1,
        objective="Discover bucket paths",
        pSuccess=1.0
    )

    s3urls = Discovery(
        label="S3 Urls",
        description="The URL paths to various S3 buckets",
        sensitivity=3,
        value=0
    )
    
    downloadFiles = Action(
        chain="exfiltration",
        label="Download files from all buckets",
        cost=0,
        time=1,
        objective="Access confidential information stored in S3",
        pSuccess=1.0,
        detections=["CloudWatch","DLP"]
    )
    
    bucketACLs = Block(
        label="Buckets are private",
        cost=0,
        description="All S3 buckets are set to private",
        complexity=0,
        implemented=False,
        pSuccess=1.0
    )

    root.connectTo(apiCache,label="#Yolosec") \
        .connectTo(siteMapsDisabled, label="Fail") \
        .connectTo(awsPublicBucketSearch, label="Next") \
        .connectTo(s3urls, label="Next") \
        .connectTo(downloadFiles, label="#Yolosec") \
        .connectTo(goal,label="#Yolosec")

    apiCache.connectTo(s3urls, label="#Yolosec")
    downloadFiles.connectTo(bucketACLs, label="Fail")
    awsPublicBucketSearch.connectTo(bucketACLs, label="Fail")

    renderer.render(
        node=root,
        renderUnimplemented=True,
        fname="example_complexS3",
        fout="png"
    )