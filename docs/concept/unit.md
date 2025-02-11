---
label: "Unit"
icon: git-commit
order: 11
expanded: true
---

```python
JudgeUnit(DiscreteScale((1, 5)), name="CXEmpathyJudge")
    .via('gpt-4o', retries=3, temperature=1.4)
    .prompt("""
        Score the following customer support conversation on empathy.

        <conversation>
        ...
        </conversation>
    """)
    .extract(RegexExtractor(pattern=RegexExtractor.FIRST_INT))
    .propagate(lambda output: Schema.of(score=output.score / 5))
```

Verdict comes bundled with common LLM-as-a-Judge system building blocks. These wrappers, or **units**,
* Have well-defined inputs and outputs (see [Schema](./schema/schema.md))
* Support [arbitrary dependency structures](../programming-model/primitives.md#layers-are-ensembles-of-judges) with other units using the `>>` operator
* Are configured using chainable directives for
    * [Model selection](./model/model.md#usage) with `.via`
    * [Prompt specification](./prompt.md) (templatable with dependency outputs) with `.prompt`
    * [Structured extraction](./extractor.md) (regex, uncertainty quantification, etc.) with `.extract`
    * [Arbitrary transformation](./transform.md#propagate) with `.propagate`
* Are executed in [parallel](../programming-model/executor.md#pipeline-execution-lifecycle) with client-side [rate-limiting](./model/rate-limit.md)
* Output [validation and post-processing](#subclass-checklist)

## Anatomy of a Unit
At its heart, a `Unit` is simply a wrapper around an LLM inference call with a well-specified input and output. We break this requirement into three components.
* (optional) `InputSchema`, which dependency units must provide (we perform append-only [name-casting](./schema/schema.md#automatic-name-casting))
* **(required)** `ResponseSchema`: the raw response from the LLM inference call
* (optional) `OutputSchema`: by default, this is the unprocessed `ResponseSchema`

Refer to the [Unit Execution Lifecycle](../programming-model/executor.md#unit-execution-lifecycle) section for specific details.

## Unit Registry
Reusing the same Unit name across different files is not permitted. This is to avoid ambiguity when using the `previous` context variable.

## Built-Ins
{.compact}
| Unit | Description | Example Notebook |
| ---: | --- | --- |
| `JudgeUnit` | Direct score judge with customizable score [`Scale`](./schema/scale.md#usage) and optional preceeding explanation/CoT. | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/haizelabs/verdict/blob/main/notebooks/common/judge.ipynb) |
| `PairwiseJudgeUnit` | Pairwise judge with customizable score [`Scale`](./schema/scale.md#usage) and optional preceeding explanation/CoT. | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/haizelabs/verdict/blob/main/notebooks/common/judge.ipynb) |
| `BestOfKJudgeUnit` | Best of `k` inputs with customizable score [`Scale`](./schema/scale.md#usage) and optional preceeding explanation/CoT. | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/haizelabs/verdict/blob/main/notebooks/common/judge.ipynb) |
| `CategoricalJudgeUnit` | Judge unit for categorical decisions (e.g., 'Harmful' or 'Not Harmful', 'Hallucination' or 'No Hallucination'). | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/haizelabs/verdict/blob/main/notebooks/common/judge.ipynb) |
| `RankerUnit` | Rank `k` inputs with optional preceeding explanation/CoT. | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/haizelabs/verdict/blob/main/notebooks/common/ranker.ipynb) |
| `ConversationalUnit` | Supports roles and a shared conversation history. Useful for debate, etc. | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/haizelabs/verdict/blob/main/notebooks/common/conversational.ipynb) |
| `CoTUnit` | Simple reasoning unit with single string field `thinking`. | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/haizelabs/verdict/blob/main/notebooks/common/cot.ipynb) |

## Defining a Custom Unit
Subclass `Unit` to define your own units. We'll walk through the implementation of the `PairwiseJudgeUnit` as a case study.

```python
from verdict import Unit
from verdict.schema import Schema

class PairwiseJudgeUnit(Unit):
    _char: str = "PairwiseJudge"

    class InputSchema(Schema):
        A: str
        B: str

    # This Unit's default Prompt template
    _prompt: Prompt = Prompt.from_template("""
        You must choose the better option between the following two options based on how well they satisfy the following single criteria:

        A:
        {input.A}

        B:
        {input.B}
    """)

    # This Unit's response produced from LLM inference
    #   * validate(ResponseSchema) must pass
    #   * process(ResponseSchema, InputSchema) -> OutputSchema
    class ResponseSchema(Schema):
        winner: DiscreteScale = DiscreteScale(['A', 'B'])

    # This Unit's output
    class OutputSchema(Schema):
        winner: str

    # Validate the ResponseSchema. This is called after the LLM inference call.
    def validate(self, response: ResponseSchema, input: InputSchema) -> None:
        pass

    # Post-process the ResponseSchema into the OutputSchema.
    def process(self, response: ResponseSchema, input: InputSchema) -> OutputSchema:
        return self.OutputSchema(winner=input.A if response.winner == 'A' else input.B)
```

### Subclass Checklist
You can override the following components when creating a custom `Unit`.

{.compact}
| Component         | Optional? | Description                                                                             |
| ----------------: | :-------: |-----------------------------------------------------------------------------------------|
| **InputSchema**   | ✅        | Previous `Unit`'s `OutputSchema` [casted](./schema/schema.md#automatic-name-casting) to the current `Unit`'s `InputSchema`.          |
| **ResponseSchema**| ❌        | Schema of response generated via inference using the specified [extractor](./extractor.md). |
| **validate**      | ✅        | Validates that the `ResponseSchema` is valid. Will trigger a retry if validation fails. |
| **process**       | ✅        | Populates the `OutputSchema` from the `ResponseSchema`.                                 |
| **OutputSchema**  | ✅        | Passed to the next `Unit`.
| **_char**         | ✅        | Unique identifier for the `Unit`.
