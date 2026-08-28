# run.py — tap in Pythonista or `python3 run.py` in iSH
# Edit these two lines. No argv needed.

AGENT = "sequence-map"  # sequence-map | find-gaps | force-cli | living-notes
TOPIC = "genomics-for-builders"
QUERY = ""
ERROR = ""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
sys.path.insert(0, os.path.join(HERE, "scripts"))
os.chdir(HERE)

from run_agent import find_gaps, force_cli, living_notes, sequence_map

if AGENT == "sequence-map":
    sequence_map(TOPIC)
elif AGENT == "find-gaps":
    find_gaps(QUERY or "unmapped-region")
elif AGENT == "force-cli":
    force_cli(QUERY)
elif AGENT == "living-notes":
    living_notes(ERROR)
else:
    print("unknown AGENT", AGENT)
