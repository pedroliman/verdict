<div align="center">

![](https://verdict.haizelabs.com/hero.png?)

[Paper](https://verdict.haizelabs.com/draft.pdf) |
[Docs](https://verdict.haizelabs.com/docs)

``` bash
pip install verdict
```
</div>

----

[![PyPI version](https://img.shields.io/pypi/v/verdict)](https://pypi.org/project/verdict/)
[![Downloads](https://img.shields.io/pypi/dm/verdict)](https://pypistats.org/packages/verdict)
[![Discord](https://img.shields.io/discord/1333947884462149682)](https://discord.gg/CzfKnCMvwx)

### Building Judges that Actually Work

Automated evaluation using LLMs, a.k.a. *LLMs-as-a-judge*, is a widely adopted practice for both developers and researchers building LLM-powered applications. However, LLM judges still face a variety of reliability issues, such as inconsistent output formats, missing or miscalibrated uncertainty quantification, biases towards superficial qualities like answer positioning, style and tone, safety, pretraining data frequency, the underlying LLM being judged, and numerous other failure modes. They are simply unreliable.

One simple but powerful approach to mitigating these shortcomings is by **scaling up inference-time compute** of the judge while leveraging well-established architectural priors from the research community. 

To that end, we introduce **Verdict**, a library for building complex, compound LLM judge systems.

### Verdict Enables Arbitrarily Complex Judges

Verdict provides both the primitives (`Unit`; `Layer` or list; `Block` or sub-graph) and execution framework for building such systems. Instead of a single LLM call to produce a judge result, Verdict judges combine multiple units of reasoning, verification, debate, and aggregation into a single judge system. When applied, these judge architectures leverage additional inference-time compute to yield impressive results on automatic evaluation of LLMs and LLM applications. 

Verdict's primary contributions are as follows:
1. Verdict provides a **single interface** for implementing a potpourri of prompting strategies, bias mitigation methods, and architectures grounded in frontier research. We support approaches from the fields of automated evaluation, scalable oversight, safety, fact-checking, reward modeling, and more. 
2. Verdict naturally introduces **powerful reasoning primitives and patterns** for automated evaluation, such as hierarchical reasoning verification and debate-aggregation.
3. Verdict is **fully composable**, allowing arbitrary reasoning patterns to be stacked into **expressive and powerful architectures**.
4. Judges built using Verdict require **no special fitting** but still achieve **SOTA or near-SOTA** performance on a wide variety of challenging automated evaluation tasks spanning safety moderation, hallucination detection, reward modeling, and more.

These features enable researchers and practitioners to iterate towards super-frontier judging capabilities with ease.

### Applications

We see Verdict judges naturally applied to at least the following scenarios:

1. **Automated Evaluation of AI Applications**. Verdict judges enable customized and automated evaluation of your AI application.
2. **Scaling Inference-Time Compute**. Verdict judges can act as verifiers to help rank, prune, and select candidates during inference-time.
3. **Reward Modeling & Reinforcement Learning**. Verdict judges can be used to guide reinforcement learning –– no more separately trained reward models, just Verdict judges.

In each of the above scenarios, Verdict judges are the clear choice of Evaluator, Verifier, or Reward Model for at least the following reasons:

1. **Generalizability**. Verdict judges are more general than task-specific fine-tuned models. Verdict readily applies across different tasks and domains, as seen by our experiments on safety moderation, factual and logical correctness, and hallucination detection.
2. **Reliability**. Verdict judges are more stable, accurate, and reliable compared to simple LLM judges. Verdict judges beat out simple LLM judges, fine-tuned evaluators, and even `o1`-style reasoning models on our benchmarks.
3. **Saliency**. Verdict judges are capable of generating dense partial rewards, unlike (non-ML) verifiers in settings like mathematics or programming.
4. **Efficiency**. Verdic judges are just as powerful as –– if not more powerful than –– `o1`-style models at evaluation while being much lower-latency and cost-efficient. This is necessary for any method leveraging heavy inference-time compute.
