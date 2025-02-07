---
label: "Programming Model"
order: 7
icon: terminal
expanded: true
---

A Verdict `Pipeline` is managed at two stages.
1. **Define** a judging `Pipeline`, which consists of the execution flow, dependencies, and parameter passing transformations using our high-level DSL. This implicitly builds a directed acyclic graph (DAG) of `Unit`s.
2. **Execute** the `Pipeline` over a single sample or an entire dataset via our parallel graph execution engine.
