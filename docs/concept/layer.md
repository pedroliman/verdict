---
label: "Layer"
icon: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><circle cx="6.5" cy="12" r="3.5" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="17.5" cy="12" r="3.5" fill="none" stroke="currentColor" stroke-width="1.5"/><line x1="0" y1="12" x2="3" y2="12" stroke="currentColor" stroke-width="1.5"/><line x1="9.5" y1="12" x2="14.5" y2="12" stroke="currentColor" stroke-width="1.5"/><line x1="21" y1="12" x2="24" y2="12" stroke="currentColor" stroke-width="1.5"/></svg>
order: 10
---

A `Layer` is simply a list of `Unit`s grouped together in a stage of execution for the purposes of organization and shared configuration (e.g., sharing a model + inference parameters with `.via` will apply to all `Unit`s in the `Layer`). This container allows you to quickly re-organize and scale up `Unit`s in an ensemble, round-robin, or other arbitrary configurations.

By default, a Layer propagates information through a judge system in a feedforward fashion with the `Unit`s of a subsequent `Layer` receive the output of a previous `Layer`'s `Unit`s in a fully-connected fashion; furthermore, `Unit`s within a `Layer` are fully independent of one another.

||| Ensemble with 3 Judges
~~~python
from verdict import Layer
from verdict.common.judge import JudgeUnit
from verdict.transform import MeanPoolUnit

ensemble = Layer(JudgeUnit(), 3).via('gpt-4o', temperature=0.8) \
    >> MeanPoolUnit("score")
~~~
||| Plot
![](/static/demo/layer/ensemble.png)
|||

However, it is possible to customize Unit behavior both within a Layer (using keyword inner=) and between current and subsequent Layers (using keyword outer=). Below are common instances of how Units can be stitched together from Layer to Layer. Using the `inner='chain'` keyword, we can stitch together subsequent `JudgeUnit`'s within the `Layer`.

||| Round-Robin with 3 Judges
~~~python
from verdict.schema import Schema, Field
from verdict.scale import DiscreteScale

class JudgeRoundRobinUnit(JudgeUnit):
    class InputSchema(Schema):
        explanation: str = Field(default="")

round_robin = Layer(
    JudgeRoundRobinUnit(DiscreteScale((1, 5)), explanation=True).prompt("""
        Rate how funny this joke is.
        {source.joke}

        Consider the previous Judge's explanation to produce your own judgement
        {input.explanation}
""")
, 3, inner='chain').via('gpt-4o', temperature=0.8) \
    >> MeanPoolUnit("score")
~~~
||| Plot
![](/static/demo/layer/round-robin.png)
|||

Perhaps we only want to output the final Judge's score. Of course, you can simply reference the final `previous.judge[2].score` using the [Previous](./prompt.md#previous) keyword in a subsequent [Prompt](./prompt.md). We also can also use the `last` keyword.

||| Round-Robin with 3 Judges
~~~python
from verdict import Unit

round_robin = Layer(
    JudgeRoundRobinUnit()
, 3, inner='chain', outer='last') \
    >> Unit() # dummy Unit for demonstration
~~~
||| Plot
![](/static/demo/layer/last.png)
|||

We can also customize the root/leaf node indices that are used to connect Layers.

||| Conversation; Only Take Opponent Arguments
~~~python
from verdict.common.conversational import ConversationalUnit
from verdict.common.judge import JudgeUnit

conversation = Layer([
    ConversationalUnit(role_name='Proponent'),
    ConversationalUnit(role_name='Opponent')
], 3, inner='chain', outer='broadcast').with_leaf([1, 3, 5]) \
    >> Layer(JudgeUnit(), 3)
~~~
||| Plot
![](/static/demo/layer/with_leaf.png)
|||

## Usage
||| Parameters
{.compact}
| `inner=` | Description |
|------|------------|
| **none** | Independent (i.e., ensemble) |
| chain | U -> U -> U (i.e., round-robin) |

{.compact}
| `outer=` | Description |
|------|------------|
| **dense** | fully-connected to nodes of next Layer |
| broadcast | broadcast 1-1<br>next Layer must have same length |
| cumulative | each Unit receives one more previous Unit<br>next Layer must have same length |
| last | Units between Layers are connected in a last fashion. |

||| Glossary
![](/static/demo/layer/figure.png)--
|||

## Unraveling
By default, a `Layer` takes a single primitive (i.e., `Unit`/`Layer`/`Block`); however, you can also pass a list of primitives to a `Layer` and it will be unraveled appropriately.
