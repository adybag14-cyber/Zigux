#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]

required_files = [
    ROOT / 'scripts' / 'zigux' / 'fixdep.zig',
    ROOT / 'scripts' / 'zigux' / 'check-fixdep-diff.py',
    ROOT / 'scripts' / 'zigux' / 'genksyms_crc.zig',
    ROOT / 'scripts' / 'zigux' / 'check-genksyms-crc-diff.py',
    ROOT / 'scripts' / 'zigux' / 'mk_elfconfig.zig',
    ROOT / 'scripts' / 'zigux' / 'check-mk-elfconfig-diff.py',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'cases.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample.d',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample.c',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample.h',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample-config.h',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample.rmeta',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample_expected.txt',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample_multi_target.d',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample2.c',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample2-config.h',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample2.so',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'shared#config.h',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample_multi_target_expected.txt',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_crc' / 'genksyms_crc_c_harness.c',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_crc' / 'inputs.txt',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_crc' / 'expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig' / 'cases.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig' / 'elf32.hex',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig' / 'elf64.hex',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig' / 'invalid_class.hex',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig' / 'not_elf.hex',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig' / 'truncated.hex',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig' / 'elf32_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig' / 'elf64_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig' / 'invalid_class_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig' / 'not_elf_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig' / 'truncated_expected.json',
]

missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print('PHASE2_VALIDATION=fail')
    print('MISSING_PHASE2_FILES_START')
    for item in missing:
        print(item)
    print('MISSING_PHASE2_FILES_END')
    sys.exit(1)

ledger = (ROOT / 'zigux-alpha' / 'BOOTSTRAP_COMMIT_LEDGER.md').read_text(encoding='utf-8')
workflow = (ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml').read_text(encoding='utf-8')
artifact_doc = (ROOT / 'Documentation' / 'zigux' / 'artifact-diff.md').read_text(encoding='utf-8')
script_readme = (ROOT / 'scripts' / 'zigux' / 'README.md').read_text(encoding='utf-8')

required_ledger_markers = [
    'feat(tools/lib): add phase-1 memory and formatting helper ports',
    'feat(scripts/zigux): add bounded Phase 2 fixdep dual-implementation lane',
    'test(zigux): widen bounded fixdep parity fixtures',
    'feat(scripts/zigux): start bounded Phase 2 genksyms lane',
    'feat(scripts/zigux): add bounded Phase 2 mk_elfconfig lane',
]
required_workflow_markers = [
    'python3 scripts/zigux/validate-phase2.py',
    'python3 scripts/zigux/check-fixdep-diff.py',
    'python3 scripts/zigux/check-genksyms-crc-diff.py',
    'python3 scripts/zigux/check-mk-elfconfig-diff.py',
    'zig test scripts/zigux/fixdep.zig',
    'zig test scripts/zigux/genksyms_crc.zig',
    'zig test scripts/zigux/mk_elfconfig.zig',
]
required_doc_markers = [
    'fixdep',
    'sample_multi_target_expected.txt',
    'genksyms_crc',
    'zigux/tests/fixtures/genksyms_crc/expected.json',
    'mk_elfconfig',
    'elf32_expected.json',
]
required_script_markers = [
    'check-fixdep-diff.py',
    'check-genksyms-crc-diff.py',
    'genksyms_crc.zig',
    'check-mk-elfconfig-diff.py',
    'mk_elfconfig.zig',
]

missing_markers = []
for marker in required_ledger_markers:
    if marker not in ledger:
        missing_markers.append(f'ledger:{marker}')
for marker in required_workflow_markers:
    if marker not in workflow:
        missing_markers.append(f'workflow:{marker}')
for marker in required_doc_markers:
    if marker not in artifact_doc:
        missing_markers.append(f'doc:{marker}')
for marker in required_script_markers:
    if marker not in script_readme:
        missing_markers.append(f'scripts:{marker}')

if missing_markers:
    print('PHASE2_VALIDATION=fail')
    print('MISSING_PHASE2_MARKERS_START')
    for marker in missing_markers:
        print(marker)
    print('MISSING_PHASE2_MARKERS_END')
    sys.exit(1)

print('PHASE2_VALIDATION=pass')
print(f'PHASE2_REQUIRED_FILE_COUNT={len(required_files)}')
print(f'PHASE2_REQUIRED_MARKER_COUNT={len(required_ledger_markers) + len(required_workflow_markers) + len(required_doc_markers) + len(required_script_markers)}')
