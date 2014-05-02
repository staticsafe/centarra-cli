"""
So, we've had some horrid string formatting in this program.

We need to fix that, because it just sucks.

---

So, since we can get all local variables, we need a way to make a compact concatenation way where information topples
dumb logic - we need to handle it somewhere else, the plugins are not where flag checking should be.

{a=b}
{b|c|d}
{b|c|d/i your text here e [optional text here]}

"""

import re

m = re.compile(r"\{((?:\{.+\}|[^\}])+)\}")  # only one nested curly works here. we probably won't need it.
c = re.compile(r"^(?:([^=]+=[^=]+)|((\w+\|)+)|((\w+(\|\w+))+\/i .+ e( .+)?))$")

def s_f(str, **kwargs):
    v = {}
