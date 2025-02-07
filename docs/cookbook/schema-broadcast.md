---
label: "Schema Broadcast"
icon: versions
order: -1
---

Imagine generating a dynamic rubric and passing each rubric item to a JudgeUnit for execution. Normally, you could use the `broadcast` keyword to link up each rubric item to a JudgeUnit 1-1 in a Layer.

```python
from verdict import Layer

class RubricUnit(Unit):
    class ResponseSchema(Schema):
        criteria: List[str]
    
    def validate(self, input: Schema, response: ResponseSchema) -> OutputSchema:
        assert len(response.criteria) == 3, "Rubric must contain exactly 3 criteria"
```

There are two ways to do this. You could reference the `criteria` field in the `JudgeUnit`'s prompt.

```python
RubricUnit().prompt("Generate 3 criteria to...") \
>> Layer([
    JudgeUnit().prompt(f"""
        {{previous.rubric.criteria[{i}]}}
    """)
    for i in range(3)
])
```

Alternatively, you can use a `Layer` of `MapUnit`s to broadcast each rubric item to a `JudgeUnit`.

```python
RubricUnit().prompt("Generate 3 criteria to...") \
>> Layer([
    MapUnit(lambda rubric, i=i: Schema.of(criteria=rubric.criteria[i]))
    for i in range(3)
], outer='broadcast') \
>> Layer(JudgeUnit(), 3)
```

This same technique can be used to broadcast a `Schema` across its fields, etc.
