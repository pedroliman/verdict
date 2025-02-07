---
label: "Motivation"
icon: law
order: 10
---

# Motivation

*TODO: rewrite; convey the lack of tooling in the emerging theme of scaling inference-time compute*
* no training needed
* a single reasoning trace (much faster than o1/o3)
* vast applications (reward model, verifiers, ad-hoc judges from natural language, etc.)
* single interface

Automated evaluation using LLMs, a.k.a. *LLMs-as-a-judge*, is a widely adopted practice for both developers and researchers building LLM-powered applications. However, LLM judges still face a variety of reliability issues, such as inconsistent output formats, missing or miscalibrated uncertainty quantification, biases towards superficial qualities such as answer positioning, style and tone, safety, numerical frequency and preferences, the type of underlying LLM being judged, and numerous other failure modes.

To mitigate these shortcomings, we developed Verdict, a library for building compound LLM judge systems. Verdict provides both the primitives (`Unit`; `Layer` or list; `Block` or sub-graph) and execution framework for building such systems. Instead of a single LLM call to produce a judge result, Verdict judges combine multiple units of reasoning, verification, debate, and aggregation into a single judge system. When applied, these judge architectures leverage additional inference-time compute to yield impressive results on automatic evaluation of LLMs and LLM applications. 

Verdict's primary contributions are as follows:
1. Verdict provides a **single interface** for implementing a potpourri of prompting strategies, bias mitigation methods, architectures, and other principles grounded in frontier research. We support approaches from the disciplines of automated evaluation, scalable oversight, safety moderation, and fact-checking, reward modeling, and more. 
2. Verdict introduces **powerful reasoning primitives and patterns** for automated evaluation, such as hierarchical reasoning verification and debate-aggregation.
3. Verdict is **fully composable**, allowing arbitrary reasoning patterns to be stacked into expressive and powerful architectures.
4. Judges built using Verdict require **no special fitting** but still achieve **SOTA or near-SOTA** performance on a wide variety of challenging automated evaluation tasks spanning safety moderation, hallucination detection, reward modeling, and more.

These features enable researchers and practitioners to quickly reproduce large-scale experimental results and iterate on them with ease. 
