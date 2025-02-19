<div align="center">

[<img src="https://verdict.haizelabs.com/hero.png?" alt="Verdict Logo" width="77.8%"/>](https://verdict.haizelabs.com/docs)

**[Whitepaper](https://verdict.haizelabs.com/whitepaper.pdf) | [Docs](https://verdict.haizelabs.com/docs) | [Results](https://verdict.haizelabs.com)**

``` bash
pip install verdict
```
</div>

----

[![PyPI version](https://img.shields.io/pypi/v/verdict)](https://pypi.org/project/verdict/)
[![Downloads](https://img.shields.io/pypi/dm/verdict)](https://pypistats.org/packages/verdict)
[![Discord](https://img.shields.io/discord/1333947884462149682)](https://discord.gg/CzfKnCMvwx)

## Table of Contents
1. [Building Judges that Actually Work](#building-judges-that-actually-work)
2. [Verdict Scales Up Judge-Time Compute](#verdict-scales-up-judge-time-compute)
3. [A Simple Example of Hierarchical Reasoning](#a-simple-example-of-hierarchical-reasoning)
4. [Verdict for Evaluation, Guardrails, Verification, and Reinforcement Learning](#verdict-for-evaluation-guardrails-verification-and-reinforcement-learning)
5. [Learn More](#learn-more)

## Building Judges that Actually Work
Automated correctness checks using LLMs, a.k.a. *LLM-as-a-judge*, is a widely adopted practice for both developers and researchers building LLM-powered applications. However, LLM judges are painfully unreliable. Today's LLM judges struggle with inconsistent output formats, mode collapse, miscalibrated confidence, superficial biases towards answer positioning, data frequency, model family, length, style, tone, safety, and numerous other failure modes. This makes the problem of evaluation twice the trouble, as both the evaluator and evaluatee may be unreliable. 

One promising solution is to **scale up judge-time compute** &mdash; the number of inference tokens used for judging. We do this in a very particular way: by composing judge architectural primitives grounded in the scalable oversight, automated evaluation, and generative reward modeling research. 

This is the foundation of **Verdict**, our library for scaling up judge-time compute. 

<figure>
  <img src="https://verdict.haizelabs.com/debate.png" alt="">
  <figcaption>Example of a Verdict judge protocol: three pairs of LLMs engage in debates, and the outcomes of these debates are aggregated to produce a final verdict.</figcaption>
</figure>

## Verdict Scales Up Judge-Time Compute
Verdict provides the primitives (`Unit`; `Layer`; `Block`), composition of primitives, and execution framework for building complex, composable, compound judge protocols. Instead of a single LLM call, Verdict judges synthesize multiple units of reasoning, verification, debate, and aggregation. 

Verdict's primary contributions are as follows:

> [!IMPORTANT]
> 
> 1. Verdict provides a **single interface** for implementing a potpourri of prompting strategies, bias mitigations, and architectures grounded in frontier research. We support insights from the fields of automated evaluation, scalable oversight, safety, fact-checking, reward modeling, and more. 
> 2. Verdict naturally introduces **powerful reasoning primitives and patterns** for automated evaluation, such as hierarchical reasoning verification and debate-aggregation.
> 3. Verdict is **fully composable**, allowing arbitrary reasoning patterns to be stacked into **expressive and powerful architectures**.
> 4. Judges built using Verdict require **no special fitting** but still achieve **SOTA or near-SOTA** performance on a wide variety of challenging automated evaluation tasks spanning safety moderation, hallucination detection, reward modeling, and more.

<!-- These features enable researchers and practitioners to iterate towards super-frontier judging capabilities with ease. -->

Scaling judge-time compute works astonishingly well. For example, Verdict judges achieve [SOTA or near-SOTA](https://verdict.haizelabs.com/) for content moderation, hallucination detection, and fact-checking. 

## A Simple Example of Hierarchical Reasoning
Say you have an AI agent that you'd like to evaluate on politeness. A first stab may be to simply prompt a Verdict `JudgeUnit` as follows

```python
Pipeline() \
  >> JudgeUnit(DiscreteScale((1, 5))).prompt("""
    Evaluate the following customer support interaction on politeness.

    {source.conversation}

    Respond with a score between 1 and 5.
    - 1: Extremely impolite, rude, hostile, or disrespectful
         ...
    - 5: Extremely polite. Consistently respectful, friendly, and courteous.
  """).via('gpt-4o-mini', retries=3, temperature=0.4)
```

Chain-of-thought prompting can improve response quality. Most Verdict built-ins simulate this by prepending a reasoning/thinking/explanation to the requested response.

```python
  >> JudgeUnit(DiscreteScale((1, 5)), explanation=True).prompt(""" ...
```

As shown by the recent success of reasoning models like the `o3`-family, complex reasoning chains can provide major boost in model performance. However, these models are far too slow for many automated evaluation applications, particularly real-time guardrails. Rather than have a powerful model solve the meta-problem of deciding how much reasoning to use each time, Verdict allows you to manually specify the structure of a simpler reasoning chain best suited for the task. For example, we may find that a single round of self-contemplation on if the explanation is reasonable is sufficient to match your intended preference alignment. This allows us to replace an `o1` call with two `gpt-4o-mini` calls.

```python
Pipeline() \
  >> JudgeUnit(DiscreteScale((1, 5)), explanation=True).prompt("""
    ...
  """).via('gpt-4o-mini', retries=3, temperature=0.4) \
  >> JudgeUnit(BooleanScale()).prompt("""
    Check if the given explanation correctly references the source conversation.

    Conversation: {source.conversation}
    Politeness Score: {previous.score}
    Explanation: {previous.explanation}

    Return "yes" if the explanation correctly references the source, and "no" otherwise.
  """).via('gpt-4o-mini', retries=3, temperature=0.0)
```

Applying this principle in various configurations allows us to approach the pareto-frontier of performance and inference time. Read on in our [Getting Started](https://verdict.haizelabs.com/docs) guide!

## Verdict for Evaluation, Guardrails, Verification, and Reinforcement Learning
Verdict judges can be used anywhere to replace human feedback and verification. Naturally, they apply to at least the following scenarios:

> [!TIP]
> 1. **Automated Evaluation of AI Applications**. Verdict judges enable *tailored* and *automated* evaluation of AI applications.
> 2. **Run-Time Guardrails**. Verdict judges are *guardrails* that sit on top of AI applications running in production.
> 3. **Test-Time Compute Scaling**. Verdict judges are *verifiers* that help rank, prune, and select candidates during test-time compute scaling.
> 4. **Reward Modeling & Reinforcement Learning**. Verdict judges provide *signal* in reinforcement learning &mdash; particularly in settings where rewards are not verifiable.

<!-- In each of the above scenarios, Verdict judges are the clear choice of Evaluator, Verifier, or Reward Model for at least the following reasons:

1. **Generalizability**. Verdict judges are more general than task-specific fine-tuned models. Verdict readily applies across different tasks and domains, as seen by our experiments on safety moderation, factual and logical correctness, and hallucination detection.
2. **Reliability**. Verdict judges are more stable, accurate, and reliable compared to simple LLM judges. Verdict judges beat out simple LLM judges, fine-tuned evaluators, and even `o1`-style reasoning models on our benchmarks.
3. **Saliency**. Verdict judges are capable of generating dense partial rewards, unlike (non-ML) verifiers in settings like mathematics or programming.
4. **Efficiency**. Verdic judges are just as powerful as –– if not more powerful than –– `o1`-style models at evaluation while being much lower-latency and cost-efficient. This is necessary for any method leveraging heavy inference-time compute. -->


## Learn More
To learn more about applying Verdict for your judging use cases, please find us at `contact@haizelabs.com`.
