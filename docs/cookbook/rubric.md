---
label: "Rubric Architecture"
icon: project-roadmap
order: 8
---

As shown by Saad-Falcon, et al. (2024) in [*LMUnit: Fine-grained Evaluation with Natural Language Unit Tests*](https://arxiv.org/abs/2412.13091), a dynamic rubric can be generated at evaluation-time to effectively break a large task down into sub-components. Below we implement a similar idea as a Verdict pipeline using a [custom `Unit`](../concept/unit.md#defining-a-custom-unit) for a question-answering task.

```python
from verdict import Unit
from verdict.schema import Schema
from typing import List

NUM_SUB_TASKS = 5

# attributed to Table 8 in the paper
INSTRUCTION = "How does the integration of healthcare analytics with electronic health records (EHRs) and the establishment of common technical standards contribute to improving patient care?"
RESPONSES = [
    "The integration of healthcare analytics with electronic health records (EHRs) and the establishment of common technical standards significantly contribute to improving patient care by providing a more coordinated, efficient, and data-driven approach to healthcare delivery...",
    "**Integration of Healthcare Analytics with Electronic Health Records (EHRs)**\n * Enables the collection, aggregation, and analysis of vast amounts of clinical data from diverse sources, including EHRs, medical devices, and laboratory results.\n * Provides insights and analytics that help identify trends, predict outcomes, and improve patient care."
]

class RubricUnit(Unit):
    class ResponseSchema(Schema):
        class SubQuestion(Schema):
            justification: str
            sub_question: str

        thinking: str
        sub_questions: List[SubQuestion]

    def validate(self, input, response: ResponseSchema):
        assert len(response.sub_questions) == NUM_SUB_TASKS, f"Expected {NUM_SUB_TASKS} sub-tasks, got {len(response.sub_tasks)}"
```

See the [following notebook for an example pipeline using this RubricUnit](https://colab.research.google.com/github/haizelabs/verdict/blob/main/notebooks/papers/lmunit.ipynb).
