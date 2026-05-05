#!/usr/bin/env python3
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

required_files = [
    ROOT / "Documentation" / "zigux" / "phase9-module-metadata-depmod-bridge-survey.md",
    ROOT / "scripts" / "zigux" / "check-phase9-module-metadata-packet.py",
    ROOT / "scripts" / "zigux" / "README.md",
    ROOT / "zigux" / "tests" / "README.md",
    ROOT / "zigux" / "tests" / "runtime_module_metadata_manifest.json",
    ROOT / "zigux" / "tests" / "runtime_module_metadata_survey.zig",
]

missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print("PHASE9_MODULE_METADATA_PACKET=fail")
    print("MISSING_PHASE9_MODULE_METADATA_FILES_START")
    for item in missing:
        print(item)
    print("MISSING_PHASE9_MODULE_METADATA_FILES_END")
    sys.exit(1)

survey_doc = (ROOT / "Documentation" / "zigux" / "phase9-module-metadata-depmod-bridge-survey.md").read_text(encoding="utf-8")
script_readme = (ROOT / "scripts" / "zigux" / "README.md").read_text(encoding="utf-8")
tests_readme = (ROOT / "zigux" / "tests" / "README.md").read_text(encoding="utf-8")
manifest = (ROOT / "zigux" / "tests" / "runtime_module_metadata_manifest.json").read_text(encoding="utf-8")
survey_test = (ROOT / "zigux" / "tests" / "runtime_module_metadata_survey.zig").read_text(encoding="utf-8")

required_doc_markers = [
    "PHASE9_SLICE=module-metadata-depmod-bridge-survey",
    "zigux/tests/runtime_module_metadata_manifest.json",
    "zigux/tests/runtime_module_metadata_survey.zig",
    "scripts/zigux/check-phase9-module-metadata-packet.py",
    "four runtime starter samples exist",
    "three loader-plan files exist",
]

required_script_readme_markers = [
    "check-phase9-module-metadata-packet.py",
    "phase9-module-metadata-depmod-bridge-survey.md",
    "runtime_module_metadata_survey.zig",
]

required_tests_readme_markers = [
    "zigux/tests/runtime_module_metadata_manifest.json",
    "zigux/tests/runtime_module_metadata_survey.zig",
    "scripts/zigux/check-phase9-module-metadata-packet.py",
]

required_manifest_markers = [
    '"lane_key": "P9-L09"',
    '"runtime_sample_files": [',
    '"runtime_loader_files": [',
    '"absent_depmod_markers": [',
    '"trace_events_loader_present": false',
    '"depmod_bridge_present": false',
]

required_survey_markers = [
    'Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md',
    'zigux/tests/runtime_module_metadata_manifest.json',
    'scripts/zigux/check-phase9-module-metadata-packet.py',
    'module metadata survey doc records the exact evidence and missing depmod bridge',
]

missing_markers = []

for marker in required_doc_markers:
    if marker not in survey_doc:
        missing_markers.append(f"survey_doc:{marker}")
for marker in required_script_readme_markers:
    if marker not in script_readme:
        missing_markers.append(f"script_readme:{marker}")
for marker in required_tests_readme_markers:
    if marker not in tests_readme:
        missing_markers.append(f"tests_readme:{marker}")
for marker in required_manifest_markers:
    if marker not in manifest:
        missing_markers.append(f"manifest:{marker}")
for marker in required_survey_markers:
    if marker not in survey_test:
        missing_markers.append(f"survey_test:{marker}")

if missing_markers:
    print("PHASE9_MODULE_METADATA_PACKET=fail")
    print("MISSING_PHASE9_MODULE_METADATA_MARKERS_START")
    for item in missing_markers:
        print(item)
    print("MISSING_PHASE9_MODULE_METADATA_MARKERS_END")
    sys.exit(1)

print("PHASE9_MODULE_METADATA_PACKET=pass")
print(f"PHASE9_MODULE_METADATA_REQUIRED_FILE_COUNT={len(required_files)}")
print(
    "PHASE9_MODULE_METADATA_REQUIRED_MARKER_COUNT="
    f"{len(required_doc_markers) + len(required_script_readme_markers) + len(required_tests_readme_markers) + len(required_manifest_markers) + len(required_survey_markers)}"
)
