---
label: "SOTA Tips"
icon: light-bulb
order: 8
---

# Best Practices / Learnings
> *...aka, how to get SOTA*

* ask for an explanation/justification (**before** the score)
* hierarchical verifier is a must
    * try a different model for the verifier to avoid self-preference bias
* study the output distribution of provider models carefully
    * for example, we find that the gpt-4o family of models has an upward skew for numerical scales and exhibit mode collapse even when using logprobs
        * likely due to their user-facing alignment tuning
    * llama models exhibit higher-entropy distributions (more filled out)
        * this provides more expressiveness and discriminative power for a JudgeUnit
* watch for any positional bias -- flip scales, shuffle positions, etc.
