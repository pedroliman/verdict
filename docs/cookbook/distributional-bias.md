---
label: "Distributional Bias"
icon: alert
order: 9
expanded: true
---

# Distributional Bias in LLM-as-a-Judge
LLMs exhibit a number of distributional biases that can be introduced through model selection, prompt content, extraction methodology, and more. Here, we focus on a few sources of distributional bias to watch out for in your LLM-as-a-judge configurations and provide some methods to calibrate judge outputs.

## Positional Bias
As shown in numerous works, such as [*Large Language Models Sensitivity to The Order of Options in Multiple-Choice Questions*](https://arxiv.org/abs/2308.11483), LLMs are sensitive to the order of presented options. This is particularly prevalent in LLM-as-a-judge configurations, as there are often many stages with ordered lists of candidates.

Some common calibration techniques include
* asking for explanation before scoring (**Multiple Evidence Calibration** à la [Wang et al., 2023](https://arxiv.org/abs/2305.17926))
* averaging across all $k!$ positional configurations (**Balanced Prediction Calibration** à la [Wang et al., 2023](https://arxiv.org/abs/2305.17926))
* max-voting across $k$ random shuffles of options ([Pezeshkpour et al., 2023](https://arxiv.org/abs/2308.11483))
* randomly shuffle the order of the options in your prompt ([Khan et al., 2024](https://arxiv.org/abs/2402.06782))

+++ MEC
```python
pipeline = Pipeline() \
    >> Layer([
        JudgeUnit(DiscreteScale((1, 5)), explanation=True).prompt("""
            ...
            Please first provide a comprehensive explanation of your evaluation,
            avoiding any potential bias and ensuring that the order in which the
            responses were presented does not affect your judgment.
            ...
        """),
    ])
```
+++ BPC
```python
pipeline = Pipeline() \
    >> Layer([
        JudgeUnit(DiscreteScale((1, 5))).prompt("""
            Score from 1 to 5 where 1 is the worst and 5 is the best.
        """),
        JudgeUnit(DiscreteScale((1, 5))).prompt("""
            Score from 1 to 5 where 1 is the best and 5 is the worst.
        """),
    ]) \
    # remember to flip scores if needed!
    >> MapUnit(lambda outputs: Schema.of(score=(outputs[0].score + (6 - outputs[1].score)) / 2))
```
+++ Voting
```python
from verdict.common.judge import BestOfKJudgeUnit
from verdict.transform import MapUnit, MaxPoolUnit

>> Layer(
    MapUnit(lambda input: Schema.of(
        prompt_str='\n'.join(
            f"{letter}: {option}" for letter, option in zip(letters, sample(input.options, 4)))
        )) \
    >> BestOfKJudgeUnit(k=4).prompt("""
        Choose the best of the following options. Respond with only 'A', 'B', 'C', or 'D'.
        {previous.map.prompt_str}
    """)
, 10) \
>> MaxPoolUnit('choice')
```
+++ Shuffle
```python
from verdict.common.judge import BestOfKJudgeUnit
from verdict.transform import MapUnit, MaxPoolUnit

MapUnit(lambda input: Schema.of(
    prompt_str='\n'.join(
        f"{letter}: {option}" for letter, option in zip(letters, sample(input.options, 4)))
    )) \
>> BestOfKJudgeUnit(k=4).prompt("""
    Choose the best of the following options. Respond with only 'A', 'B', 'C', or 'D'.
    {previous.map.prompt_str}
""")
```
+++


## Self-Preference Bias
As shown in [*LLM Evaluators Recognize and Favor Their Own Generations*](https://arxiv.org/abs/2404.13076) and [*Self-Preference Bias in LLM Evaluators*](https://arxiv.org/abs/2410.21819), LLMs tend to favor their own generations. This can lead to a positive-skew when verifying judge explanations as part of a hierarchical verification pipeline, for example. Below, we show the the distribution of yes/no using different models for the heirarchical verification judge in our [quickstart example](../index.md). Note that using the same model for the initial judge and verification judge will result in a positive-skew that may not discriminate faithfully between good and bad explanations.

![](/static/bias/self-preference.png)


## Structured Output Bias
Constrained decoding methods for structured outputs (e.g., JSON-mode) impose an inductive bias on the model's output distribution. We demonstrate this with a toy example: figuring out the contested height of a fictional character -- Willy Wonka. We obtain a distribution over structured outputs and [post-hoc](../concept/extractor.md#post-hoc) by running each 100 times, whereas [TokenProbabilityExtractor](../concept/extractor.md#token-probability) is from a single run. This demonstrates that the logprobs from a single run can provide a proxy for the model's uncertainty.

![](/static/bias/extractor.png)


## Skew Bias
Provider models tend to have a skew distribution of scores due in part to their instruction tuning. While desirable for some consumer-facing applications, this can cause LLM-as-a-judge evaluators to miscalibrated. We demonstrate this with a toy example of coin-flipping.

![](/static/bias/skew.png)
