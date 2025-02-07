---
label: "Pipeline"
#icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="8" width="6" height="8" rx="1" /><rect x="16" y="8" width="6" height="8" rx="1" /><circle cx="12" cy="12" r="2" /><path d="M8 12h2M14 12h2M10 12a4 4 0 0 1 4 0" /></svg>
#icon: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#2196F3" d="M3 8a4 4 0 0 0 4 4 4 4 0 0 0-4 4m4.5-4h9m4.5-4a4 4 0 0 1-4 4 4 4 0 0 1 4 4"/><path fill="#2196F3" d="M6 6h3v3H6zM15 15h3v3h-3z"/><circle fill="#2196F3" cx="12" cy="12" r="2"/><path fill="#fff" d="M7 7h1v1H7zm9 9h1v1h-1z"/></svg>
icon: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="currentColor" d="M3 8a4 4 0 0 0 4 4 4 4 0 0 0-4 4m4.5-4h9m4.5-4a4 4 0 0 1-4 4 4 4 0 0 1 4 4M6 6h3v3H6zm9 9h3v3h-3z"/><circle fill="currentColor" cx="12" cy="12" r="2"/></svg>
order: 5
---

A `Pipeline` is a wrapper that enables the execution of `Unit`s over a single sample or a [dataset](./dataset.md). Refer to the [Pipeline Execution Lifecycle](../programming-model/executor.md#pipeline-execution-lifecycle) section for specific details.

||| Run Single Sample
~~~python
from verdict import Pipeline

pipeline = Pipeline() \
  >> Layer(
    JudgeUnit(BooleanScale()).prompt(f"""
      Is this funny?

      {source.joke}
    """)
  , 5) \
  >> MeanPoolUnit()

response, leaf_node_prefixes = pipeline.run(
  Schema.of(joke="Why did the chicken cross the road? To get to the other side."))
~~~
||| Run Dataset
~~~python
from verdict.dataset import DatasetWrapper

dataset = DatasetWrapper.from_hf(
  load_dataset("jokes-ai/jokes"),
  columns=["joke"]
)

response, leaf_node_prefixes = pipeline.run_from_dataset(
    dataset,
    max_workers=128,
    display=True,
    graceful=True
)
~~~
|||

## Usage
Both `run` and `run_from_dataset` accept the following arguments:
* `max_workers`: max number of worker threads[^1]
* `display`: visualize the progress of the pipeline.
* `graceful`: controls whether an error will cause the program to exit.

!!!info
We use a separate `ThreadPoolExecutor` for CPU-bound tasks (e.g., `MapUnit`s).

```python
from verdict import config
config.LIGHTWEIGHT_EXECUTOR_WORKER_COUNT = 128 # default is 32
```
!!!

[^1]: We will adjust your system's process file descriptor limit (equivalent to `ulimit -n max_workers`) accordingly.

To refer to a particular `Unit` in the pipeline, we generate determinstic human-readable prefixes for each `Unit` in the pipeline. Refer to the [Prefix](./advanced/block.md#prefix) section for more details. After the pipeline has completed execution, you can inspect all intermediate and leaf node prefixes.
* `run`: we return a dictionary mapping prefix to `OutputSchema`.
* `run_from_dataset`: we return a `pd.DataFrame` where the columns are `{prefix}_{field_name}` for each field in the `OutputSchema`.

## Failure/Termination
Failures in threads are handled by the executor differently depending on the cause:
* declaration-time errors (e.g., a Prompt contains an invalid field name), fail immediately
* runtime errors (e.g., inference provider downtime, ResponseSchema not obeyed by Structured Output extractor), retry until the Model Selection Policy is exhausted

## Visualization
Pass `display=True` to visualize the progress of a pipeline within the current `stdout`.
If running a single sample, the results of each `Unit` will be displayed alongside the progress tree.

### Streaming
Mark a `Unit` with `.stream()` to enable streaming output. If visualization is enabled, five `Unit`'s at a time will be streamed to the right-half of the `stdout`.

## Experiment Config
Pass an optional `ExperimentConfig` to `run_from_dataset` via the `experiment_config` parameter. Refer to the [Experiment](./experiment.md) section for more details.
