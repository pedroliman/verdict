---
label: "Prompt Templating"
icon: comment-discussion
order: 9
---

## Usage
Your choice of prompt can make or break an LLM judge system. `Verdict` allows you to define your own prompts in-line or use those curated from the research literature in our [`PromptRegistry`](https://github.com/haizelabs/verdict/blob/main/verdict/common/prompt.py).

```python
from verdict import Unit
from verdict.schema import Schema
from typing import List

class RubricUnit(Unit):
    class ResponseSchema(Schema):
        rubric: List[str]

RubricUnit().prompt("""
    Design an evaluation rubric to evaluate the following support response on politeness.

    Support Response:
    {source.support_response}
""") \
>> JudgeUnit().prompt("""
    @system
    You are the best LLM judge in the world.

    @user
    Use the following rubric to evaluate the following support response on politeness.

    Rubric:
    {"\n".join(f"{i+1}. {item}" for i, item in enumerate(previous.rubric))}

    Support Response:
    {source.support_response}
""")
```

In the example above, we use `previous.rubric` to access the output of the preceeding `RubricUnit`. Note that the exposed context can be used in conjunction with arbitrary Python code, creating a powerful way to quickly prototype with including new information in your prompts.

## Anatomy of a Prompt
A `Prompt` is a template string that is injected with the following special variables at execution-time:

- `source`: the [original input](./dataset) to the Pipeline
- `previous`: the execution output of upstream dependencies of the current `Unit`
- `input`: the current `Unit`'s execution input
- `unit`: the current `Unit` object's instance fields

### Previous
We expose the execution outputs of all dependencies of the current Unit in the `previous` variable. We use the following rules to ambiguate between multiple dependencies.

```python
# if there is a single dependency, its unit name is inferred
{previous.score}

# `score` field of the previous (single) JudgeUnit's output
{previous.judge.score}

# ...the 3rd JudgeUnit's output...
{previous.judge[2].explanation}
```

Names are automatically inferred from the class name of the dependency by stripping the `Unit` suffix and converting to lowercase.

### User/System Prompt
`@user` is implicitly added to the prompt. You can preface a section of the prompt string with `@system` to add a system message.

### Whitespace / `@no_format`
By default, all leading newlines and whitespace is removed. You can disable this behavior by adding the `@no_format` tag anywhere in the prompt string.

## Registering a Prompt
Simply subclass `Prompt` and define your desired prompt template in the class docstring.
```python
from verdict.prompt import Prompt

class HallucinationDetectionPrompt(Prompt):
    """
        Judge the following response on a hallucination detection task.

        Question:
        {source.question}

        Answer:
        {source.answer}
    """
```

## Pinned Units
Note that a `.pin`'d Unit cannot include `{source.*}` variables in its prompt, since this directs the execution engine to run once and share results across all samples, the `source` context is not available at runtime.