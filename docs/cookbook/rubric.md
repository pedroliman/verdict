---
label: "Rubric Architecture"
icon: project-roadmap
order: 8
---

As shown by [Saad-Falcon, et al. (2024)](https://arxiv.org/abs/2412.13091), a dynamic rubric can be generated at evaluation-time to effectively break a large task down into sub-components. Below we implement a similar idea as a Verdict pipeline.

# TODO: code
```python
class RubricUnit(Unit):
    class ResponseSchema(Schema):
        criteria: List[str]
```
