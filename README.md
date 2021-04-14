## WIP warning
This is a work in progress, a toy that I've been working on over the weekend. It's on GitHub just as a safe place to save it. It's in a public repo because it's not sensitive but I'm not encouraging anyone to use it :)

## Idea
Programatically model trees like those described by [Kelly Shortridge](https://twitter.com/swagitda_) [here](https://swagitda.com/blog/posts/security-decision-trees-with-graphviz/)

The goal is to decouple the model from the view. In reality I'm removing the need for the user to understand Graphviz and introducing a need for them to understand python.

Models differentiate between controls that are *imlemented* and those that are not; modelling both the current security posture, and a potential (improved) posture.

The `renderer.render()` function can toggle whether to include unimplemented things in it's graph.

![PNG image showing graph created by exampleTree_simpleS3.py](images/example_simpleS3.png?raw=true "Simple S3")


## Prerequisites
Your system needs an installed version of graphviz for rendering to work.
On MacOS this can be installed using `brew install graphviz`

See https://graphviz.org/download/ for other options.

## Instructions for setup
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate
```

## Instructions for running
`exampleTree_simpleS3.py` is a simple model, containing only the current path. It can be run simply:
```
source .venv/bin/activate
python3 exampleTree_simpleS3.py
deactivate
```

`exampleTree_complexS3.py` contains some potential blocking mitigations, things the security team might be considering but hasn't implemented.
```
source .venv/bin/activate
python3 exampleTree_complexS3.py
deactivate
```

## Methodology
In messing with this idea, I've found the easiest approach is to map the existing paths out first, without consideration for things you might implement. To see what that looks like checkout [exampleTree_simpleS3.py](exampleTree_simpleS3.py). After this one can either create a new tree with potential mitigations _or_ add them to the existing tree, for examples purposes I chose the former; [exampleTree_complexS3.py](exampleTree_complexS3.py).

The last line in each of those files is a call to render the tree:
```
    renderer.render(
        node=root,
        renderUnimplemented=True,
        style=style,
        fname="example_complexS3",
        fout="png"
    )
```

I imagine that in general usage, we'd just want one model for a specific attacker; not a _simple and a _complex_ one. However, it's very useful to be able to see what those different graphs look like, as the latter models things we _could_ do but are currently *unimplemented* - for that reason the `render()` function has a parameter to enable or disable rendering of unimplemented paths. This way you can record everything in one tree (and maybe add that into version control, as a system of record) and render different outputs, one that shows your current reality, and one that shows your potential reality (hopefully improved).

Below is the output of running the _complex example with `renderUnimplemented=True`, note that if you set this to `False` the generated graph looks the same as `exampleTree_simpleS3.py`

![PNG image showing graph created by exampleTree_complexS3.py](images/example_complexS3.png?raw=true "Complex S3")
 