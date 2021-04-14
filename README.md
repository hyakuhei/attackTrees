Basic.py contains a basic attack tree

## Prerequisites
Your system needs an installed version of graphviz for rendering to work.
On MacOS this can be installed using `brew install graphviz`

See https://graphviz.org/download/ for other options.

## Instructions for setup
`python3 -m venv .venv`
`source .venv/bin/activate`
`pip install -r requirements.txt`

## Instructions for running
There's a made up tree that includes both current and possible mitigations in `basic.py`

To run the attack tree, simply run `python3 basic.py`

To run the attack tree with potential (but unimplemented) mitigations turned on, edit the last line of `basic.py` and change `renderUnimplemented` from `False` to `True`

```
    renderer.render(node=root, renderUnimplemented=False)
```
