from models import Action, Block, Detect, Discovery, Edge, Node
from renderer import Renderer

with Renderer(root = "Reality", goal= "Attacker gets data from bucket") as graph:

    # This file shows how to use the .<next node> method to quicly draw
    # a graph. We found this was needed to allow quick development of 
    # graphs in a "live" setting.

    # Build a tree very quickly, using only labels and Node types
    apiCache = graph.root.action("Search API Caches")
    siteMapsDisabled = apiCache.block("Sitemaps Disabled", implemented=False) #action blocked
    awsPublicBucketSearch = apiCache.action("AWS Public Bucket Search") #action succeeded

    s3urls = awsPublicBucketSearch.discovery("S3 URLs")
    downloadFiles = s3urls.action("Download files from all buckets")
    bucketACLs = downloadFiles.block("Buckets are private", implemented=False)

    downloadFiles.connectTo(graph.goal, label="Success")
    
    graph.render(
        renderUnimplemented=True,
        fname="example_complexS3",
        fout="png"
    )