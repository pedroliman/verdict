---
label: "Overview"
icon: milestone #list-unordered
order: 17
---

1. Design a Verdict [**Pipeline**](./pipeline.md) composed of **Units** ([built-ins](./unit.md#built-ins), [custom](./unit.md#defining-a-custom-unit), and arbitrary [map operators](./transform.md#maptransform)) and [**Layers**](./layer.md). These are building blocks that can be composed into arbitrary [dependency graphs](./advanced/block.md) using the `>>` operator. We can customize the
    a) **[Model](./model/model.md):** provider/vLLM model to use, client-side [rate-limiting](./model/rate-limit.md), inference parameters, prefix caching, fallbacks, etc.
    b) **[Prompt](./prompt.md):** with templated references to the input data, upstream/[previous](./prompt.md#previous) Unit output, and instance fields.
    c) **[Schema](./schema.md):** the well-specified input (optional), LLM response, and output (optional) to be extracted from the LLM response.
        i) **[Scale](./scale.md):** discrete (1..5), continuous (0-1), categorical (yes/no), particularly useful for logprobs uncertainty estimation.
    d) **[Extractor](./extractor.md):** how we marshall the LLM response into the output schema — structured, regex, post-hoc, logprobs, etc.

2) Specify a [**DatasetWrapper**](./dataset.md) on top of Huggingface datasets or pandas DataFrames.

3) [Run](./pipeline.md#usage) the pipeline on the dataset, [visualize](./pipeline.md#visualization) its progress, and compute [correlation metrics](./experiment.md).
