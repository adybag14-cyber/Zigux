#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[2]
KCONFIG_BRIDGE_DIR = ROOT / 'zigux' / 'tests' / 'fixtures' / 'kconfig_bridge'
FIXDEP_DIR = ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep'


def case_files_from_groups(cases_path: Path, *group_specs: tuple[str, str]) -> list[Path]:
    data = json.loads(cases_path.read_text(encoding='utf-8'))
    discovered: list[Path] = []
    for group_name, field_name in group_specs:
        for case in data.get(group_name, []):
            rel = case.get(field_name)
            if rel:
                discovered.append(cases_path.parent / rel)
    return discovered


def validate_kconfig_bridge_manifest_shape(cases_path: Path) -> list[str]:
    data = json.loads(cases_path.read_text(encoding='utf-8'))
    issues: list[str] = []

    if not isinstance(data, dict):
        return ['kconfig_bridge:manifest:expected_object']

    expected_top_level = {'conf_cases', 'confdata_cases'}
    unexpected_top_level = sorted(set(data) - expected_top_level)
    for name in unexpected_top_level:
        issues.append(f'kconfig_bridge:manifest:unexpected_top_level:{name}')

    for group_name in sorted(expected_top_level):
        group = data.get(group_name)
        if not isinstance(group, list):
            issues.append(f'kconfig_bridge:manifest:{group_name}:expected_list')
            continue
        if not group:
            issues.append(f'kconfig_bridge:manifest:{group_name}:empty')

    return issues


required_files = [
    ROOT / 'Documentation' / 'zigux' / 'phase2-closure.md',
    ROOT / 'scripts' / 'zigux' / 'check-genksyms-bridge.py',
    ROOT / 'scripts' / 'zigux' / 'check-kconfig-bridge.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase2-cross.py',
    ROOT / 'scripts' / 'zigux' / 'validate-phase2-closure.py',
    ROOT / 'scripts' / 'zigux' / 'genksyms.zig',
    ROOT / 'scripts' / 'zigux' / 'kconfig' / 'conf_bridge.zig',
    ROOT / 'scripts' / 'zigux' / 'kconfig' / 'confdata_bridge.zig',
    ROOT / 'zigux' / 'Makefile',
    FIXDEP_DIR / 'cases.json',
    FIXDEP_DIR / 'sample_concatenated_expected.txt',
    FIXDEP_DIR / 'sample_output_write_expected.txt',
    FIXDEP_DIR / 'sample_output_write_expected.stderr.txt',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'genksyms_bridge_c_harness.c',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'cases.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'minimal_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'debug_reference_types_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'long_options_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'abbreviated_long_options_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'quiet_overrides_warning_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'explicit_option_terminator_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'positional_passthrough_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'help_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'version_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'invalid_option_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'missing_reference_argument_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'unsupported_long_option_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'ambiguous_abbreviated_long_option_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'missing_long_reference_argument_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'missing_long_dump_types_argument_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'unexpected_long_option_argument_expected.json',
    KCONFIG_BRIDGE_DIR / 'cases.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase2_tool_manifest.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase2_cross_targets.json',
]
required_files.extend(case_files_from_groups(
    KCONFIG_BRIDGE_DIR / 'cases.json',
    ('conf_cases', 'expected'),
    ('confdata_cases', 'input'),
    ('confdata_cases', 'expected'),
))

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
    'PHASE2_TOOL_COUNT=6',
    'PHASE2_CROSS_TARGET_COUNT=3',
    'PHASE2_FIXDEP_GATE=python3 scripts/zigux/check-fixdep-diff.py',
    'PHASE2_FIXDEP_DETERMINISM=check-fixdep-diff.py replays C and Zig outputs twice before comparing artifacts',
    'PHASE2_FIXDEP_FULL_READ_POLICY=fixdep.zig reads dependency files at full C-helper size and maps short writes to fixdep output errors',
    'PHASE2_FIXDEP_CASE_COUNT=7',
    'PHASE2_FIXDEP_OUTPUT_WRITE_CASE=zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt',
    'PHASE2_GENKSYMS_BRIDGE_GATE=python3 scripts/zigux/check-genksyms-bridge.py',
    'PHASE2_KCONFIG_BRIDGE_GATE=python3 scripts/zigux/check-kconfig-bridge.py',
    'PHASE2_CROSS_GATE=python3 scripts/zigux/check-phase2-cross.py',
    'PHASE2_CLOSURE_GATE=python3 scripts/zigux/validate-phase2-closure.py',
    'dep parsing keeps the first source across concatenated target entries',
    'output writer maps print and flush failures to fixdep output-write errors',
    'PHASE2_FIXDEP_EVIDENCE=artifact fixtures plus direct concatenated-target and output-write unit anchors are required for closure',
    'PHASE2_ROLLBACK=keep C kbuild tools authoritative and remove failing Zigux bridge/tool from workflow wiring',
]
required_workflow_markers = [
    'python3 scripts/zigux/check-fixdep-diff.py',
    'python3 scripts/zigux/check-genksyms-bridge.py',
    'python3 scripts/zigux/check-kconfig-bridge.py',
    'python3 scripts/zigux/check-phase2-cross.py --target',
    'python3 scripts/zigux/validate-phase2-closure.py',
    'zig test scripts/zigux/fixdep.zig',
    'zig test scripts/zigux/genksyms.zig',
    'zig test scripts/zigux/kconfig/conf_bridge.zig',
    'zig test scripts/zigux/kconfig/confdata_bridge.zig',
]
required_ledger_markers = [
    'feat(scripts/zigux): add bounded Phase 2 genksyms wrapper lane',
    'ci(zigux): widen Phase 2 closure matrix',
    'docs(zigux): reopen and close broadened Phase 2 tranche',
    'feat(scripts/zigux): add bounded Phase 2 kconfig bridge scaffolding',
    'ci(zigux): add Phase 2 cross-arch build matrix',
    'docs(zigux): close bounded Phase 2 toolchain tranche',
]
required_readme_markers = [
    'check-genksyms-bridge.py',
    'check-kconfig-bridge.py',
    'check-phase2-cross.py',
    'genksyms.zig',
    'kconfig/conf_bridge.zig',
    'kconfig/confdata_bridge.zig',
]
required_doc_markers = [
    'genksyms_bridge',
    'kconfig_bridge',
    'phase2_cross_targets.json',
]
required_makefile_markers = [
    'phase2-validate:',
    'phase2-tools:',
    'phase2-kconfig:',
    'phase2-cross:',
    'check-fixdep-diff.py',
    'check-genksyms-bridge.py',
    '$(ZIG) test scripts/zigux/fixdep.zig',
    '$(ZIG) test scripts/zigux/genksyms.zig',
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
if tool_manifest.get('tool_count') != 6:
    missing_markers.append('manifest:tool_count=6')
if len(tool_manifest.get('tools', [])) != 6:
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

missing_markers.extend(validate_kconfig_bridge_manifest_shape(KCONFIG_BRIDGE_DIR / 'cases.json'))

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
