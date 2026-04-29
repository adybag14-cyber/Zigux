#!/usr/bin/env python3
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]

required_files = [
    ROOT / 'scripts' / 'zigux' / 'validate-phase6.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase6-base64-c-parity.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase6-bsearch-c-parity.py',
    ROOT / 'scripts' / 'zigux' / 'README.md',
    ROOT / 'Documentation' / 'zigux' / 'README.md',
    ROOT / 'Documentation' / 'zigux' / 'phase6-helper-parity-catalog.md',
    ROOT / 'Documentation' / 'zigux' / 'phase6-base64-slice.md',
    ROOT / 'Documentation' / 'zigux' / 'phase6-bsearch-slice.md',
    ROOT / 'Documentation' / 'zigux' / 'phase6-checksum-slice.md',
    ROOT / 'Documentation' / 'zigux' / 'phase6-hexdump-slice.md',
    ROOT / 'zigux' / 'Makefile',
    ROOT / 'zigux' / 'tests' / 'README.md',
    ROOT / 'zigux' / 'tests' / 'phase6_base64.zig',
    ROOT / 'zigux' / 'tests' / 'phase6_base64_perf.zig',
    ROOT / 'zigux' / 'tests' / 'phase6_base64_c_parity.zig',
    ROOT / 'zigux' / 'tests' / 'phase6_base64_c_casegen.zig',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase6_base64_vectors.zig',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase6_base64_c_harness.c',
    ROOT / 'zigux' / 'tests' / 'phase6_bsearch.zig',
    ROOT / 'zigux' / 'tests' / 'phase6_bsearch_perf.zig',
    ROOT / 'zigux' / 'tests' / 'phase6_bsearch_c_parity.zig',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase6_bsearch_c_harness.c',
    ROOT / 'zigux' / 'tests' / 'phase6_checksum.zig',
    ROOT / 'zigux' / 'tests' / 'phase6_checksum_perf.zig',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase6_checksum_vectors.zig',
    ROOT / 'zigux' / 'tests' / 'phase6_hexdump.zig',
    ROOT / 'zigux' / 'tests' / 'phase6_hexdump_perf.zig',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase6_hexdump_vectors.zig',
    ROOT / 'zigux' / 'tests' / 'phase6_helper_parity_manifest.json',
    ROOT / 'zigux' / 'tests' / 'phase6_build.zig',
    ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml',
]

missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print('PHASE6_VALIDATION=fail')
    print('MISSING_PHASE6_FILES_START')
    for item in missing:
        print(item)
    print('MISSING_PHASE6_FILES_END')
    sys.exit(1)

makefile = (ROOT / 'zigux' / 'Makefile').read_text(encoding='utf-8')
workflow = (ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml').read_text(encoding='utf-8')
script_readme = (ROOT / 'scripts' / 'zigux' / 'README.md').read_text(encoding='utf-8')
tests_readme = (ROOT / 'zigux' / 'tests' / 'README.md').read_text(encoding='utf-8')
doc_readme = (ROOT / 'Documentation' / 'zigux' / 'README.md').read_text(encoding='utf-8')
phase6_catalog = (ROOT / 'Documentation' / 'zigux' / 'phase6-helper-parity-catalog.md').read_text(encoding='utf-8')
phase6_manifest = json.loads(
    (ROOT / 'zigux' / 'tests' / 'phase6_helper_parity_manifest.json').read_text(encoding='utf-8')
)
phase6_build = (ROOT / 'zigux' / 'tests' / 'phase6_build.zig').read_text(encoding='utf-8')
phase6_base64 = (ROOT / 'zigux' / 'tests' / 'phase6_base64.zig').read_text(encoding='utf-8')
phase6_base64_perf = (ROOT / 'zigux' / 'tests' / 'phase6_base64_perf.zig').read_text(encoding='utf-8')
phase6_bsearch = (ROOT / 'zigux' / 'tests' / 'phase6_bsearch.zig').read_text(encoding='utf-8')
phase6_bsearch_perf = (ROOT / 'zigux' / 'tests' / 'phase6_bsearch_perf.zig').read_text(encoding='utf-8')
phase6_hexdump = (ROOT / 'zigux' / 'tests' / 'phase6_hexdump.zig').read_text(encoding='utf-8')

phase6_catalog_verified_head_match = re.search(r'- verified head: `([0-9a-f]{40})`', phase6_catalog)
if phase6_catalog_verified_head_match is None:
    print('PHASE6_VALIDATION=fail')
    print('PHASE6_CATALOG_HEAD_STATUS=missing')
    sys.exit(1)

phase6_catalog_verified_head = phase6_catalog_verified_head_match.group(1)

slice_docs = {
    'phase6-base64-slice.md': (ROOT / 'Documentation' / 'zigux' / 'phase6-base64-slice.md').read_text(encoding='utf-8'),
    'phase6-bsearch-slice.md': (ROOT / 'Documentation' / 'zigux' / 'phase6-bsearch-slice.md').read_text(encoding='utf-8'),
    'phase6-checksum-slice.md': (ROOT / 'Documentation' / 'zigux' / 'phase6-checksum-slice.md').read_text(encoding='utf-8'),
    'phase6-hexdump-slice.md': (ROOT / 'Documentation' / 'zigux' / 'phase6-hexdump-slice.md').read_text(encoding='utf-8'),
}

required_make_markers = [
    'PHONY += phase6-validate phase6-test phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf phase6-hexdump-perf phase6',
    'phase6-validate:',
    'scripts/zigux/validate-phase6.py',
    'phase6-test:',
    'zigux/tests/phase6_build.zig',
    'phase6-base64-perf:',
    'base64-perf --build-file zigux/tests/phase6_build.zig',
    'phase6-bsearch-perf:',
    'bsearch-perf --build-file zigux/tests/phase6_build.zig',
    'phase6-checksum-perf:',
    'checksum-perf --build-file zigux/tests/phase6_build.zig',
    'phase6-hexdump-perf:',
    'hexdump-perf --build-file zigux/tests/phase6_build.zig',
]
