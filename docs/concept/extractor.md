---
label: "Extractor"
#icon: sign-out
icon: tab-external
order: 7
---

We provide a number of techniques to extract a well-defined [`ResponseSchema`](./schema/schema.md) from the model inference at execution-time. Each approach has various tradeoffs in compute cost, distributional bias, and uncertainty calibration.

{.compact}
| Extractor                                 | Setting                    | Calls | + Input Tokens | + Output Tokens | No Bias from Extraction Method  | Uncertainty Calibration  |
| ----------------------------------------: | :------------------------: | :---: | :------------: | :-------------: | :-----------------------------: | :----------------------: |
| [Structured Output ](#structured-output)  | any                        | 1x    | —              | +structure[^1]  | ❌                              | ❌                       |
| [Raw](#raw)                               | single string field        | 1x    | —              | +language[^2]   | ✅                              | ❌                       |
| [Regular Expression](#regular-expression) | any                        | 1x    | —              | +language       | ✅                              | ❌                       |
| [Post-Hoc](#post-hoc)                     | any                        | 2x    | +language      | +structure      | ✅                              | ❌                       |
| [Token Probability](#token-probability)   | single DiscreteScale field | 1x    | —              | -language       | ✅                              | ✅                       |

[^1]: `+structure` represents the added token usage from enforcing a JSON/XML schema during the decoding process
[^2]: `+language` represents the added token usage from using a general chat-tuned model.

To use an extractor, you can simply pass an instance to the `.extract()` directive.

```python
from verdict.extractor import WeightedSummedScoreExtractor
from verdict.scale import DiscreteScale

...
# use the structured output mode
>> JudgeUnit(DiscreteScale((1, 5))).extract()

# use the token logprobs of the model and compute the expected value over the score support
>> JudgeUnit(DiscreteScale((1, 5))).extract(WeightedSummedScoreExtractor())

# apply a regex to the raw output
>> JudgeUnit(DiscreteScale((1, 5))).extract(RegexExtractor(fields={"height": RegexExtractor.FIRST_FLOAT}))

# use a post-hoc model to perform structured output extraction
>> JudgeUnit(DiscreteScale((1, 5))).extract(PostHocExtractor('gpt-4o-mini', temperature=0.0))
```

## Structured Output
This is the default extractor. Unless overriden, as in the example above, all `Unit`s will use this extractor to populate their `ResponseSchema`. We pass the `ResponseSchema` to [Instructor](https://python.useinstructor.com/) with default settings to use the provider-side constrained decoding mechanism (e.g., json-mode, function calling, etc.) to produce structured output. Refer to the Instructor documentation for more details.

```python
class HeightUnit(Unit):
    class ResponseSchema(Schema):
        height: float

...
>> HeightUnit().prompt("""
    How tall is Bugs Bunny in meters?
""").via('gpt-4o-mini') # uses OpenAI structured output by default
```

## Raw
This only supports `ResponseSchema` with a single `str` field. We simply populate this field with the raw output of the model inference.
```python
from verdict.extractor import RawExtractor

class HeightUnit(Unit):
    class ResponseSchema(Schema):
        height_meters: str

    class OutputSchema(Schema):
        height: float

    def process(self, input: Schema, response: ResponseSchema) -> OutputSchema:
        return OutputSchema(height=float(response.height_meters))

...
>> HeightUnit().prompt("""
    How tall is Bugs Bunny in meters? ONLY RESPOND with the height in meters.
""").extract(RawExtractor()) # dumps the raw model output into the `height_meters` field of `ResponseSchema`
```

## Regular Expression
Specify the extraction regex for each field in the `ResponseSchema`. Retries can be important here. We also recommend using the prompt as a first line of defense to guide the model to a particular format. This extractor is built on [`CustomExtractor`](#custom-extractor).

```python
from verdict.extractor import RegexExtractor

...
>> HeightUnit().prompt("""
    How tall is Bugs Bunny in meters? ONLY RESPOND with the height in meters.
""").via('gpt-4o-mini', retries=10).extract(RegexExtractor(fields={"height": RegexExtractor.FIRST_FLOAT})). # r'[+-]?\d+(\.\d+)?'
```

## Post-Hoc
Sometimes extracting from a raw output using regular expressions is too complex, unreliable, or impossible. We can use a subsequent inference call on the raw output to perform Structured Output extraction.

```python
from verdict.extractor import PostHocExtractor

...
>> JudgeUnit(DiscreteScale((1, 10))).prompt("""
    Is this funny?

    Why did the chicken cross the road?
    To get to the other side.
""").extract(PostHocExtractor())  # by default, will use the same model as the initial inference
```

We can (and usually should) use a much weaker model to perform the extraction than the initial task. Ths constructor has the same signature as the `.via()` directive, allowing us to pass any model and inference parameters.
```python
...
>> JudgeUnit().via('gpt-4o-mini').extract(PostHocExtractor('phi-3', temperature=0.0))
```

## Token Probability
When your `ResponseSchema` has a single `DiscreteScale` field, we can use these discrete values as a support for a probability distribution over the response tokens. We use the logprobs of each support token as a proxy for the model's uncertainty.
```python
from verdict.extractor import ArgmaxScoreExtractor

...
>> JudgeUnit(DiscreteScale((1, 10))).prompt("""
    Is this funny?

    Why did the chicken cross the road?
    To get to the other side.
""").extract(ArgmaxScoreExtractor())
```

We also provide `SampleScoreExtractor` and `WeightedSummedScoreExtractor`, which sample and take the expected value of the token distribution, respectively. Furthermore, we provide a `TokenProbabilityExtractor` base class that can be used to implement custom extractors that use the token distribution, or to obtain the distribution itself (note that this will override the `ResponseSchema` to one with a single field `distribution: Dict[str, float]`).

## Advanced
### Custom Extractor
We provide a base class for custom extractors, `CustomExtractor`, which allows you to implement your own extraction logic atop the raw output of an inference call. Refer to the [`RegexExtractor` implementation](https://github.com/haizelabs/verdict/blob/main/verdict/extractor.py#L153-191) for an example.
