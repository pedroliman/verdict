---
label: "Installation"
icon: download
order: 11
---

# Installation

Simply create a new Python 3.9+ environment and install the [`verdict` PyPI package](https://pypi.org/project/verdict/).

```bash
conda create -n verdict python=3.9 # or any other environment manager
conda activate verdict

# using uv...
uv pip install verdict

# or using pip
pip install verdict
```

To support `.plot`ing execution graphs, you must additionally ensure that the Graphviz binaries are installed (refer to the [Graphviz docs](https://graphviz.org/download/) for more information).
