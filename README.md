The idea here, is to programatically model trees like those described by (Kelly Shortridge)[https://twitter.com/swagitda_] (here)[https://swagitda.com/blog/posts/security-decision-trees-with-graphviz/]

The goal is to decouple the model from the view. In reality I'm removing the need for the user to understand Graphviz and introducing a need for them to understand python.

Models differentiate between controls that are *imlemented* and those that are not; modelling both the current security posture, and a potential (improved) posture.

The `renderer.render()` function can toggle whether to include unimplemented things in it's graph.

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

To run the attack tree with potential (but unimplemented) mitigations turned off, edit the last line of `exampleTree_complex.py` and change `renderUnimplemented` from `False` to `True`
```
renderer.render(node=root, renderUnimplemented=True, style=style)
```
