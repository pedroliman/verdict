---
label: "Dataset"
icon: table
---

We provide a simple wrapper around a HuggingFace `datasets` or `pd.DataFrame` to run Verdict pipelines across samples in parallel.

A `DatasetWrapper` maps each sample in the dataset to a [`Schema`](./schema/schema.md), which can be referenced by any node in the Pipeline using `{input.field}` in the [Prompt](./prompt.md). In the example below, we sample 20 random rows from the HuggingFace `EdinburghNLP/xsum` dataset and expose some columns.

## Wrapper
### HuggingFace

```python
from verdict.dataset import DatasetWrapper

dataset = DatasetWrapper.from_hf( # or .from_pandas(df, ...)
    load_dataset("EdinburghNLP/xsum"),
    columns=["document", "summary"],
    max_samples=20
)

# ... somewhere in the Pipeline
JudgeUnit().prompt("""
    ...
    {input.document}
    ...
""")
```

!!!
You can also write a custom pre-processing function that returns a `Schema` for each sample. Schema fields will be accessible in the final result dataframe (i.e. output of `pipeline.run_from_dataset(dataset[split])`) as `!{field_name}`.

```python
dataset = DatasetWrapper.from_hf(
    load_dataset("EdinburghNLP/xsum"),
    lambda row: Schema.of(article=row["document"])
)
```
!!!

### Pandas

In addition, for a `pandas.DataFrame`, you can specify the name of a column that contains the sample's split.

```python
from verdict.dataset import DatasetWrapper

dataset = DatasetWrapper.from_pandas(
    pd.read_csv("data_all.csv"),
    split_column="split",
    max_samples=20
)

pipeline.run_from_dataset(dataset['eval'])
```

## Pinning results
We can force any Verdict node to run just once and share the output across all samples using the `pin()` method.

```python
pipeline = Pipeline() \
    >> Layer([
        CoTUnit(criteria).pin() # runs once across dataset, shares result across all samples
        >> JudgeUnit(criteria)  # runs once per sample
    ], 5) \
    >> MeanVariancePoolUnit()

pipeline.run_from_dataset(dataset)
```
