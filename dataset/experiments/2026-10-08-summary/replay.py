"""Recorded answers through the summary code again -- no request leaves.

    replay.py <round> <meeting>

Runs ``measure_summary``'s setup in count mode (the key is "not-a-key"), and
answers each request with the answer round <round> recorded, in order. Prints
what the code under PYTHONPATH keeps of them.
"""
import io
import json
import os
import sys

rnd, name = sys.argv[1], sys.argv[2]
sys.argv = ["measure_summary.py", "count"]
here = os.path.dirname(os.path.abspath(__file__))
src = io.open(os.path.join(here, "measure_summary.py"), encoding="utf-8").read()
ns = {"__file__": os.path.join(here, "measure_summary.py"), "__name__": "ms"}
exec(compile(src[: src.index("def main()")], "measure_summary.py", "exec"), ns)  # noqa: S102

recorded = json.load(io.open(os.path.join(here, f"r{rnd}_summary_{name}.json"), encoding="utf-8"))
queue = list(recorded["calls"])
same = []


def request(self, method, path, *, json):  # noqa: A002
    prompt = "".join(part["text"] for c in json["contents"] for part in c["parts"])
    rec = queue.pop(0)
    same.append(prompt == rec["prompt"])
    self.calls.append({"final": rec["final"], "answer": rec["answer"]})
    return {"candidates": [{"content": {"parts": [{"text": rec["answer"]}]}}]}


ns["Counted"].request = request
r = ns["one"](name, board=True, send=False)
import autune_extraction

print(json.dumps({
    "code": autune_extraction.__file__.split("scratchpad")[-1][1:4],
    "round": rnd, "meeting": name, "requests": r["requests"], "prompt_same": same,
    "left_in_queue": len(queue), "overview": r["overview"], "points": r["points"],
    "same_as_recorded": r["points"] == recorded["points"] and r["overview"] == recorded["overview"],
}, ensure_ascii=False, indent=1))
