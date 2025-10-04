# mjai-adapter-3p

Adapt MJAI events from 3-player games to 4-player games

## Intro

This project provides an adapter to patch MJAI events from sanma (three-player mahjong), enabling four-player mahjong AI models to correctly read the input and return reactions recognizable by sanma frontends.

# Why Adapt?

In existing open-source projects and publicly available datasets, training a four-player mahjong model is significantly easier than training a sanma model.

Although the two are completely different games, some fundamental strategies (such as tile efficiency) are somewhat transferable.

Therefore, this adapter allows the use of an existing four-player model as a temporary substitute when a sanma model is urgently needed but no usable weights or model files are available.

## Usage

To adapt 3p events, you need a MJAI Bot implemented `react(self, events)`. Then install the bot to the adapter:

```python
from p3to4 import Adapter3P
from YourMjaiBot import Bot

adapter = Adapter3P()
your_bot = Bot()
adapter.install(your_bot)
```

Then the adapter will automatically adapt the input events. To get reactions, use:

```
adapter.react('{"type":"start_game","id":0'})
```

## Notes

- Do not expect too much from the model's performance, even if the four-player model is strong.
- Due to various limitations, the handling of the 4z (North) tile is quite restricted: the logic provided in this project simply "Nuki" it whenever obtained in hand.
- Similarly, after conversion, the four-player model has no way of knowing that the 4z (North) tile can be regarded as doras. This may lead to potential misjudgments in offensive and defensive strategies.

## TODO
- Convert meta information along with the events (except for Nukidora).
- Provide more robust logic for handling Nukidora.
