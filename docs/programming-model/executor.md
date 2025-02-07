---
label: Execution Lifecycle
icon: issue-reopened
---

## Unit Execution Lifecycle
1. Obtain the next provider client via the [Model Selection Policy](../concept/model/model.md).
2. [Cast the input](../concept/schema/schema.md#automatic-name-casting) to the optional `InputSchema`
3. Populate the [Prompt](../concept/prompt.md) template using the current execution context
4. Perform inference and [extract](../concept/extractor.md) the response into the unit's `ResponseSchema`
5. [Validate](../concept/unit.md#subclass-checklist) the response using `validate`
6. [Post-process](../concept/unit.md#subclass-checklist) the response into the unit's `OutputSchema` using `process`
7. Run any custom logic to adapt a Unit's `OutputSchema` to the next Unit's `InputSchema` using [`.propagate`](../concept/transform.md#propagate)
8. If at any point an error occurs, refer to the pipeline [failure/termination](../concept/pipeline.md#failuretermination) section.

## Pipeline Execution Lifecycle
The underlying concurrency model is a `ThreadPoolExecutor` with a configurable `max_workers` parameter. Since a bulk of the execution time is spent waiting for network I/O, we can set `max_workers` to a high value. CPU-bound tasks (e.g., [`MapUnit`](../concept/transform.md#maptransform)) are assumed to be lightweight and are handled by a separate executor with a configurable `max_workers` parameter.

For a single sample, the execution lifecycle is as follows:
1. [Materialize](../concept/advanced/block.md#materialization) the graph of primitives into a graph of `Unit`s
2. Queue all the root nodes for execution
3. Once a `Unit`'s execution lifecycle is complete, store the output
4. Queue the ready dependent `Unit`s for execution
5. Repeat until all `Unit`s have been executed
6. Gather the outputs of all leaf nodes

For an entire dataset, we perform the same steps but build a copy of the graph for each sample and queue up all samples for execution using the same `ThreadPoolExecutor`. Hence, execution occurs across all samples in parallel.
