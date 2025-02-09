---
label: "Quickstart"
icon: zap
order: 9
---

# Quickstart

Getting started with Verdict is easy!

Here, we show an example of a Verdict judging pipeline that enables us to achieve SOTA  **(+14.5% over GPT4o)** on the ExpertQA hallucination detection dataset. The intuition is simple. We define a judging protocol that is an ensemble of three copies of a sub-protocol, which contains:

1. A judge who initially determines whether a hallucination is present.
2. A second verification judge who reviews and validates the first judge's reasoning and decision.

The results of each verification judge are then aggregated using a majority vote.

### Datasets and Imports

Let's get started with imports and dataset loading. We'll pull in the `LLM-AggreFact` dataset from HuggingFace and massage it into a Verdict-compatible format. Critically, `lambda row: Schema.of(claim=row["claim"], doc=row["doc"], label=row["label"])` defines how the columns in the HuggingFace dataset are accessed by Verdict Units.
```python
# Don't forget to set your API key!
# $ export OPENAI_API_KEY=*************************

from datasets import load_dataset
from pandas import DataFrame
from verdict import Pipeline, Block, Layer
from verdict.common.judge import CategoricalJudgeUnit
from verdict.dataset import DatasetWrapper
from verdict.scale import DiscreteScale
from verdict.schema import Schema
from verdict.transform import MaxPoolUnit
from verdict.util import ratelimit

# We recommend disabling Verdict rate-limiting
ratelimit.disable()

# Load the ExpertQA dataset (https://arxiv.org/pdf/2309.07852), one of the tasks in the LLM-AggreFact leaderboard (https://llm-aggrefact.github.io/)
hf_dataset = load_dataset("lytang/LLM-AggreFact")["test"].filter(
    lambda example: example["dataset"] == "ExpertQA"
)
# Wrap dataset in Verdict format, mapping columns to the Schema fields
# We'll cap the number of examples at 10 for demo purposes
verdict_dataset = DatasetWrapper.from_hf(
    {"test": hf_dataset},
    lambda row: Schema.of(
        claim=row["claim"],
        doc=row["doc"],
        label=row["label"],
    ),
    max_samples=10,
)
```

### Setting Up Prompts

Once we have the Verdict-ready dataset set up, we can define prompts that can reference 1) raw inputs from the dataset, and 2) outputs of other (previous) Units. Below, we define `judge_prompt` for the initial judge, and `verify_prompt` for the verification judge.

Notice that we can ingest and format variables from the input data by writing, for example `{source.doc}`. These variables were defined via `lambda row: Schema.of(claim=row["claim"], doc=row["doc"], label=row["label"])`.

Similarly, you can reference outputs from previous Units by using placeholders like `{previous.choice}`. All variables from the previous Unit's ResponseSchema are available for use in the current prompt.

```python
# Initial Judge prompt
# - Injects raw inputs via `source.schema_variable`
judge_prompt = """
Determine whether the provided claim is consistent with the corresponding document. Consistency in this context implies that
all information presented in the claim is substantiated by the document. If not, it should be considered inconsistent.
Document: {source.doc}
Claim: {source.claim}
Please assess the claim’s consistency with the document by responding with either "yes" or "no".
Answer:
"""

# Verification prompt
# - Injects raw inputs via `source.schema_variable`
# - Accesses prior layer info via `previous.unit_output_variable`
# - `unit_output_variables` are defined in the `ResponseSchema` of the `Unit`
verify_prompt = """
Check if the given answer correctly reflects whether the claim is consistent with the corresponding document. Consistency in this context implies that
all information presented in the claim is substantiated by the document. If not, it should be considered inconsistent. "yes" means the claim is consistent with the document, and "no" means the claim is not consistent with the document.

Document: {source.doc}
Claim: {source.claim}
Answer: {previous.choice}
Answer Justification: {previous.explanation}

If you think the answer is correct, return the answer as is. If it's incorrect, return the opposite (if answer = "yes", return "no", and if answer = "no", return "yes").
"""
```

### Defining Verdict Pipelines

With these prompts in hand, we can define the actual Verdict judge protocol. As mentioned above, this protocol is an ensemble of three judge-then-verify subprotocols, and results are aggregated using a majority vote.

We do this by creating a `Pipeline` object and inserting each component of execution into the `Pipeline` using the `>>` operator. The judge-then-verify protocol makes use of the promtps defined above, and information flows from the first `CategoricalJudgeUnit` to the second `CategoricalJudgeUnit`. Note each `CategoricalJudgeUnit` can specify its inference modle (in this case `gpt-4o`), as well as inference parameters like `temperature` or retry parameters. 

Since the judge-then-verify subprotocol will be used repeatedly, we can define a `hierarchical_protocol` to encapsulate this subprotocol for reuse. Within the `Pipeline`, we can then instantiate 3 instances of the `hierarchical_protocol` using `Layer([hierarchical_protocol], repeat=3)`, and aggregate the outputs of the three `hierarchical_protocols` with a `MaxPoolUnit`.

Note that the result of using the `>>` operator to connect two protocols is **closed,** meaning that the combination will always yield a valid and functional protocol. Indeed, we can compose arbitrarily complex judge protocols by nesting more and more subprotocols. 

```python
# A Verdict subsystem consisting of:
#   - CategoricalJudgeUnit that decides if a hallucination is present, followed by
#   - Another CategoricalJudgeUnit that verifies the initial judge's explanation and decision.
# Both units use `gpt-4o``
hierarchical_protocol = (
    Block()
    >> CategoricalJudgeUnit(
        name="judge", categories=DiscreteScale(["yes", "no"]), explanation=True
    )
    .prompt(judge_prompt)
    .via(policy_or_name="gpt-4o", retries=3, temperature=0.7)
    >> CategoricalJudgeUnit(name="verify", categories=DiscreteScale(["yes", "no"]))
    .prompt(verify_prompt)
    .via(policy_or_name="gpt-4o", retries=3, temperature=0)
)

# A full Verdict system consisting of an ensemble of 3 `hierarchical_protocols`, with results aggregated by a `MaxPoolUnit`
pipeline = Pipeline() >> Layer([hierarchical_protocol], repeat=3) >> MaxPoolUnit()
# Graphical representation of the Verdict system
pipeline.plot(display=True)
```

### Running Pipelines

Finally, we can run this `Pipeline` on the ExpertQA dataset and report the final hallcuinatino detection accuracy:

```python
results_df, leaf_node_columns = pipeline.run_from_dataset(
    verdict_dataset["test"], max_workers=512, display=True
)


def report_performance(df: DataFrame, col_name: str):
    df["pred_label"] = df[col_name].str.strip().map({"yes": 1, "no": 0}).astype(float)
    if df["pred_label"].isna().any():
        print(
            "Warning: Some rows had invalid values for prediction and are marked as NaN."
        )

    correct_count = (df["pred_label"] == df["label"]).sum()
    print(
        f"Judge Accuracy: ({correct_count} / {len(df)}) ==> {round(correct_count / len(df) * 100, 2)}%"
    )
    df.to_csv("verdict_expertqa_results.csv")


report_performance(results_df, leaf_node_columns[0])
```

---

### Putting it All Together

The full script is as follows:

```python
# Don't forget to set your API key!
# $ export OPENAI_API_KEY=*************************

from datasets import load_dataset
from pandas import DataFrame
from verdict import Pipeline, Block, Layer
from verdict.common.judge import CategoricalJudgeUnit
from verdict.dataset import DatasetWrapper
from verdict.scale import DiscreteScale
from verdict.schema import Schema
from verdict.transform import MaxPoolUnit
from verdict.util import ratelimit

# We recommend disabling Verdict rate-limiting
ratelimit.disable()

# Load the ExpertQA dataset (https://arxiv.org/pdf/2309.07852), one of the tasks in the LLM-AggreFact leaderboard
hf_dataset = load_dataset("lytang/LLM-AggreFact")["test"].filter(
    lambda example: example["dataset"] == "ExpertQA"
)
# Wrap dataset in Verdict format, mapping columns to the Schema fields
verdict_dataset = DatasetWrapper.from_hf(
    {"test": hf_dataset},
    lambda row: Schema.of(
        claim=row["claim"],
        doc=row["doc"],
        label=row["label"],
    ),
    max_samples=10,
)

# Initial Judge prompt
# - Injects raw inputs via `source.schema_variable`
judge_prompt = """
Determine whether the provided claim is consistent with the corresponding document. Consistency in this context implies that
all information presented in the claim is substantiated by the document. If not, it should be considered inconsistent.
Document: {source.doc}
Claim: {source.claim}
Please assess the claim’s consistency with the document by responding with either "yes" or "no".
Answer:
"""

# Verification prompt
# - Injects raw inputs via `source.schema_variable`
# - Accesses prior layer info via `previous.unit_output_variable`
# - `unit_output_variables` are defined in the `ResponseSchema` of the `Unit`
verify_prompt = """
Check if the given answer correctly reflects whether the claim is consistent with the corresponding document. Consistency in this context implies that
all information presented in the claim is substantiated by the document. If not, it should be considered inconsistent. "yes" means the claim is consistent with the document, and "no" means the claim is not consistent with the document.

Document: {source.doc}
Claim: {source.claim}
Answer: {previous.choice}
Answer Justification: {previous.explanation}

If you think the answer is correct, return the answer as is. If it's incorrect, return the opposite (if answer = "yes", return "no", and if answer = "no", return "yes").
"""

# A Verdict subsystem consisting of:
#   - CategoricalJudgeUnit that decides if a hallucination is present, followed by
#   - Another CategoricalJudgeUnit that verifies the initial judge's explanation and decision.
# Both units use `gpt-4o``
hierarchical_protocol = (
    Block()
    >> CategoricalJudgeUnit(
        name="judge", categories=DiscreteScale(["yes", "no"]), explanation=True
    )
    .prompt(judge_prompt)
    .via(policy_or_name="gpt-4o", retries=3, temperature=0.7)
    >> CategoricalJudgeUnit(name="verify", categories=DiscreteScale(["yes", "no"]))
    .prompt(verify_prompt)
    .via(policy_or_name="gpt-4o", retries=3, temperature=0)
)

# A full Verdict system consisting of an ensemble of 3 `hierarchical_protocols`, with results aggregated by a `MaxPoolUnit`
pipeline = Pipeline() >> Layer([hierarchical_protocol], repeat=3) >> MaxPoolUnit()
# Graphical representation of the Verdict system
pipeline.plot(display=True)
results_df, leaf_node_columns = pipeline.run_from_dataset(
    verdict_dataset["test"], max_workers=512, display=True
)


def report_performance(df: DataFrame, col_name: str):
    df["pred_label"] = df[col_name].str.strip().map({"yes": 1, "no": 0}).astype(float)
    if df["pred_label"].isna().any():
        print(
            "Warning: Some rows had invalid values for prediction and are marked as NaN."
        )

    correct_count = (df["pred_label"] == df["label"]).sum()
    print(
        f"Judge Accuracy: ({correct_count} / {len(df)}) ==> {round(correct_count / len(df) * 100, 2)}%"
    )
    df.to_csv("verdict_expertqa_results.csv")


report_performance(results_df, leaf_node_columns[0])
```

Now you're ready for prime time!