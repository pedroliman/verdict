---
label: "Debugging"
icon: bug
---

# Debugging Tips

Debugging is an unavoidable part of the development process. If your Pipeline fails or your final results are not as expected, the following tips may help.

* Read the [logs](#logging). If there is a runtime exception from user-defined logic, the logs will contain the traceback along with variable state at the time of failure. Logs also contain intermediate steps at each stage of execution (e.g., populating the `Prompt`). Crucially, logs contain a human-readable thread identifier and `Unit` prefix for easy `grep`-ing.
  * e.g., `2025-01-28 05:12:42.080 | DEBUG    |                                 root.block.layer[3].block.unit[DirectScoreJudge] T=52    | ...`
  * We log the exact user/system prompts sent for inference. This is where a majority of judge performance-related bugs are found.
  * Grep for `Traceback` to find the thread that caused the pipeline to terminate.
  * Grep for ` T=... ` to view all logs for a given thread.
* Inspect intermediate outputs. Set `graceful=True` to avoid exiting the program on failure and see the non-NaN outputs for clues.
* Bump retries on brittle units, and/or refactor by adding more instructions in the prompt, reducing the complexity of `ResponseSchema` if using a Structured Output extractor.
* Complex `ResponseSchema`s with a Structured Output extractor can fail many times in the tail case before finally succeeding.
  * We add a default random nonce to the start of provider models to prevent prompt caching from getting in the way of retries. Set `use_nonce=True` in your vLLMModel if needed.
  * We also recommend setting a high `max_retries` in this case (e.g., `max_retries=20` even) to address the stragglers.

## Logging
Verdict produces many logs that can help you understand the execution state of a pipeline. By default, these logs are stored in the `./verdict` in your current working directory as `{pipeline.name}_{timestamp}.log`

Set the `LOG_LEVEL` environment variable (e.g., `DEBUG`, `INFO`, `CRITICAL`) to output logs directly to stderr.
