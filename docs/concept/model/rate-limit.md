---
label: "Rate Limiting"
icon: clock
---

!!!
Place the following snippet at the top of your script to disable any client-side rate-limiting globally.

```python
from verdict.util import ratelimit
ratelimit.disable()
```
!!!

## Usage
In addition to the [`max_workers` parameter](../pipeline.md#usage), which controls the number of worker threads, we provide native support for fine-grained and configurable client-side rate limiting at the `token` and `request`-count level. This is particularly useful when running large ad-hoc experiments in parallel against serverless providers and/or in live production settings. It is also a useful tool for managing/controlling the request pressure on self/dedicated-hosted models, as well as for specifying an upper-bound on inference cost per unit-time.

All rate limiters are tied to the [`Model`](./model.md) they are used with. For provider models accessed by [`litellm` model name](./model.md#usage) using provider rate-limit defaults, these are implicitly shared across all instances. For other `Model` objects, you must share the `Model` object manually.

```python
from verdict import config
from verdict.util.ratelimit import RateLimitPolicy

# modify the default rate limiter for the openai provider
config.PROVIDER_RATE_LIMITER['openai'] = RateLimitPolicy.of(rpm=1_000, tpm=100_000)

...
>> JudgeUnit.via('gpt-4o-mini') # shares the same rate limiter specified above
>> JudgeUnit.via('gpt-4o')      # shares the same rate limiter specified above
```

```python
from verdict.model import ProviderModel
from verdict.util.ratelimit import RateLimitPolicy, ConcurrentRateLimiter, TimeWindowRateLimiter

model = ProviderModel(
    name="o1",
    rate_limiter=RateLimitPolicy.using( # manually share this object if you want to restrict across multiple models from the same provider
        requests=ConcurrentRateLimiter(max_concurrent_requests=10),         # 10 concurrent requests
        tokens=TimeWindowRateLimiter(max_value=10_000, window_seconds=60),  # 10k tokens/minute
    )
)

...
>> JudgeUnit.via(model)
```

## Disable Rate Limiting
```python
from verdict.util import ratelimit
ratelimit.disable() # sets all default rate limiters to the `UnlimitedRateLimiter`
```

## Provider Defaults
See the provider defaults in [config.py](https://github.com/haizelabs/verdict/blob/main/verdict/config.py#L11-L24). As a fallback, we use the OpenAI Tier 1 rate limits for `gpt-4o-mini`.

## Output Token Estimation
Since the output token usage of a request is unknown until the request is complete, we use a running average of the output token count of peer `Unit`s (i.e., run on other samples) to estimate the total token count of the current sample. In addition, we use a customizable `smoothing_factor` (default `0.9`) to prevent sending out requests that will trigger a rate limit error on the provider-side.

## Combining Rate Limiters
You can arbitrarily combine rate-limiters for a specific metric (i.e., `requests` or `tokens`) and `Verdict` will wait until all rate-limiters are below their respective limits before releasing the request. For example, the OpenAI Tier 1 rate-limit for `gpt-4o-mini` has two request-level rate limits (tokens per minute and tokens per day).

```python
RateLimitPolicy({ # tier 1 for gpt-4o-mini
    TimeWindowRateLimiter(max_value=500, window_seconds=60): 'requests',
    TimeWindowRateLimiter(max_value=10_000, window_seconds=60*60*24): 'requests',
    TimeWindowRateLimiter(max_value=200_000, window_seconds=60): 'tokens'
})
```

