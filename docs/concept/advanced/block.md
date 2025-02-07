---
label: "Block"
#icon: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><circle cx="6" cy="6" r="3.5" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="18" cy="6" r="3.5" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="6" cy="18" r="3.5" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="18" cy="18" r="3.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path stroke="currentColor" stroke-width="1.5" d="M9.5 6h5m-5 12h5M6 9.5v5m12-5v5"/></svg>
icon: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><circle cx="6" cy="6" r="3.5" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="18" cy="6" r="3.5" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="6" cy="18" r="3.5" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="18" cy="18" r="3.5" fill="none" stroke="currentColor" stroke-width="1.5"/><line x1="9.5" y1="6" x2="14.5" y2="6" stroke="currentColor" stroke-width="1.5"/><line x1="9.5" y1="18" x2="14.5" y2="18" stroke="currentColor" stroke-width="1.5"/><line x1="6" y1="9.5" x2="6" y2="14.5" stroke="currentColor" stroke-width="1.5"/><line x1="18" y1="9.5" x2="18" y2="14.5" stroke="currentColor" stroke-width="1.5"/><line x1="8.5" y1="8.5" x2="16" y2="16" stroke="currentColor" stroke-width="1.5"/><line x1="15.5" y1="8.5" x2="8.5" y2="16" stroke="currentColor" stroke-width="1.5"/></svg>
order: -3
---

A `Block` is a recursive graph structure composed of `Unit`s, `Layer`s, and `Block`s. A `Block` is implicitly created using the `>>` operator.

## Export as Module
Sometimes you may want to export a `Block` as a module. We recommend wrapping it in its own `Block` for clarity.

```python
# model/ensemble.py
Ensemble = Block() >> Layer(...)

# experiment.py
from verdict import Pipeline
from .model.ensemble import Ensemble

pipeline = Pipeline() >> Ensemble()
```


## Materialization
As mentioned in the [Programming Model](../../programming-model/primitives.md#materialization) section, a `Block` is a recursive graph structure. The `materialize` method recursively flattens all sub-graphs into a flat list of `Unit`s.

### Prefix
Through the materialization process, we interatively construct a unique `prefix` for each `Unit` using the following rules.

{.compact}
| Primitive | Prefix Concatenation |
|-----------|----------------------|
| Unit | `unit[shortname name]` |
| Layer | `layer[i]` |
| Block | `block` |
