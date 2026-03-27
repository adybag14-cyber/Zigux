#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[2]

required_files = [
    ROOT / 'Documentation' / 'zigux' / 'phase2-closure.md',
    ROOT / 'scripts' / 'zigux' / 'check-kconfig-bridge.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase2-cross.py',
    ROOT / 'scripts' / 'zigux' / 'validate-phase2-closure.py',
    ROOT / 'scripts' / 'zigux' / 'kconfig' / 'conf_bridge.zig',
    ROOT / 'scripts' / 'zigux' / 'kconfig' / 'confdata_bridge.zig',
    ROOT / 'zigux' / 'Makefile',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'kconfig_bridge' / 'cases.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'kconfig_bridge' / 'olddefconfig_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'kconfig_bridge' / 'syncconfig_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'kconfig_bridge' / 'sample.config',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'kconfig_bridge' / 'sample_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase2_tool_manifest.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase2_cross_targets.json',
]

missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print('PHASE2_CLOSURE_VALIDATION=fail')
    print('MISSING_PHASE2_CLOSURE_FILES_START')
    for item in missing:
        print(item)
    print('MISSING_PHASE2_CLOSURE_FILES_END')
    sys.exit(1)

closure = (ROOT / 'Documentation' / 'zigux' / 'phase2-closure.md').read_text(encoding='utf-8')
workflow = (ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml').read_text(encoding='utf-8')
ledger = (ROOT / 'zigux-alpha' / 'BOOTSTRAP_COMMIT_LEDGER.md').read_text(encoding='utf-8')
script_readme = (ROOT / 'scripts' / 'zigux' / 'README.md').read_text(encoding='utf-8')
artifact_doc = (ROOT / 'Documentation' / 'zigux' / 'artifact-diff.md').read_text(encoding='utf-8')
makefile = (ROOT / 'zigux' / 'Makefile').read_text(encoding='utf-8')
tool_manifest = json.loads((ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase2_tool_manifest.json').read_text(encoding='utf-8'))
targets_manifest = json.loads((ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase2_cross_targets.json').read_text(encoding='utf-8'))

required_closure_markers = [
    'PHASE2_STATUS=closed',
    'PHASE2_TOOL_COUNT=5',
    'PHASE2_CROSS_TARGET_COUNT=3',
    'PHASE2_KCONFIG_BRIDGE_GATE=python3 scripts/zigux/check-kconfig-bridge.py',
    'PHASE2_CROSS_GATE=python3 scripts/zigux/check-phase2-cross.py',
    'PHASE2_CLOSURE_GATE=python3 scripts/zigux/validate-phase2-closure.py',
    'PHASE2_ROLLBACK=keep C kbuild tools authoritative and remove failing Zigux bridge/tool from workflow wiring',
]
required_workflow_markers = [
    'python3 scripts/zigux/check-kconfig-bridge.py',
    'python3 scripts/zigux/check-phase2-cross.py --target',
    'python3 scripts/zigux/validate-phase2-closure.py',
    'zig test scripts/zigux/kconfig/conf_bridge.zig',
    'zig test scripts/zigux/kconfig/confdata_bridge.zig',
]
required_ledger_markers = [
    'feat(scripts/zigux): add bounded Phase 2 kconfig bridge scaffolding',
    'ci(zigux): add Phase 2 cross-arch build matrix',
    'docs(zigux): close bounded Phase 2 toolchain tranche',
]
required_readme_markers = [
    'check-kconfig-bridge.py',
    'check-phase2-cross.py',
    'kconfig/conf_bridge.zig',
    'kconfig/confdata_bridge.zig',
]
required_doc_markers = [
    'kconfig_bridge',
    'phase2_cross_targets.json',
]
required_makefile_markers = [
    'phase2-validate:',
    'phase2-kconfig:',
    'phase2-cross:',
]

missing_markers = []
for marker in required_closure_markers:
    if marker not in closure:
        missing_markers.append(f'closure:{marker}')
for marker in required_workflow_markers:
    if marker not in workflow:
        missing_markers.append(f'workflow:{marker}')
for marker in required_ledger_markers:
    if marker not in ledger:
        missing_markers.append(f'ledger:{marker}')
for marker in required_readme_markers:
    if marker not in script_readme:
        missing_markers.append(f'scripts:{marker}')
for marker in required_doc_markers:
    if marker not in artifact_doc:
        missing_markers.append(f'doc:{marker}')
for marker in required_makefile_markers:
    if marker not in makefile:
        missing_markers.append(f'make:{marker}')

if tool_manifest.get('phase') != 'Phase 2':
    missing_markers.append('manifest:phase=Phase 2')
if tool_manifest.get('status') != 'closed':
    missing_markers.append('manifest:status=closed')
if tool_manifest.get('tool_count') != 5:
    missing_markers.append('manifest:tool_count=5')
if len(tool_manifest.get('tools', [])) != 5:
    missing_markers.append(f'manifest:tools_len={len(tool_manifest.get("tools", []))}')
for rel in tool_manifest.get('tools', []):
    if not (ROOT / rel).exists():
        missing_markers.append(f'manifest_file:{rel}')

if targets_manifest.get('phase') != 'Phase 2':
    missing_markers.append('targets:phase=Phase 2')
if targets_manifest.get('status') != 'closed':
    missing_markers.append('targets:status=closed')
if targets_manifest.get('target_count') != 3:
    missing_markers.append('targets:target_count=3')
if len(targets_manifest.get('targets', [])) != 3:
    missing_markers.append(f'targets:len={len(targets_manifest.get("targets", []))}')

if missing_markers:
    print('PHASE2_CLOSURE_VALIDATION=fail')
    print('MISSING_PHASE2_CLOSURE_MARKERS_START')
    for marker in missing_markers:
        print(marker)
    print('MISSING_PHASE2_CLOSURE_MARKERS_END')
    sys.exit(1)

print('PHASE2_CLOSURE_VALIDATION=pass')
print(f'PHASE2_CLOSURE_REQUIRED_FILE_COUNT={len(required_files)}')
print(f'PHASE2_CLOSURE_REQUIRED_MARKER_COUNT={len(required_closure_markers) + len(required_workflow_markers) + len(required_ledger_markers) + len(required_readme_markers) + len(required_doc_markers) + len(required_makefile_markers)}')
