"""Version control demo - semantic diff and merge."""

import shutil
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from ontologyops import OntologyVersionControl
from ontologyops.version_control import MergeStrategy

base = Path(__file__).parent / "ontologies"
work = base / "_demo_work.owl"
shutil.copy(base / "supply_chain.owl", work)
vc = OntologyVersionControl(str(work))
v1 = vc.create_snapshot(author="dev@example.com", message="Initial")
shutil.copy(base / "supply_chain_v2.owl", work)
v2 = vc.create_snapshot(author="dev@example.com", message="Added Subscription")
diff = vc.diff(v1, v2)
print("Semantic diff:", diff)
print("Added entities:", list(diff.entities_added)[:5])
