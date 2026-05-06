#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile

_SELF_PATH = Path(__file__).resolve()
ROOT = _SELF_PATH.parents[2] if len(_SELF_PATH.parents) >= 3 else _SELF_PATH.parent

REQUIRED_FILES = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/string.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/argv_split.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-phase1-parity.py",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
    "zigux/tests/build.zig",
    "zigux/tests/README.md",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
    "zigux/tests/fixtures/phase1_helpers.json",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
]

REQUIRED_LEDGER_MARKERS = [
    "feat(tools/lib): start phase-1 helper ports",
    "test(zigux): add phase-1 helper harness and workflow gate",
    "feat(tools/lib): expand phase-1 helper batch",
    "test(zigux): add phase-1 golden parity fixtures and artifact diff gate",
    "feat(tools/lib): complete bounded phase-1 helper coverage",
]

REQUIRED_WORKFLOW_PRESENCE_MARKERS = [
    "tools/lib/*.zig",
]

REQUIRED_WORKFLOW_EXACT_MARKERS = [
    "python3 scripts/zigux/validate-phase1.py",
    "python3 scripts/zigux/check-phase1-parity.py",
    "zig build test --build-file zigux/tests/build.zig",
]

REQUIRED_TEST_MARKERS = [
    '@import("argv_split")',
    '@import("bitmap")',
    '@import("cmdline")',
    '@import("ctype")',
    '@import("find_bit")',
    '@import("hweight")',
    '@import("list_sort")',
    '@import("slab")',
    '@import("str_error_r")',
    '@import("string")',
    '@import("vsprintf")',
    '@import("zalloc")',
    '@import("rbtree")',
    '@embedFile("fixtures/phase1_helpers.json")',
]

REQUIRED_PHASE1_PARITY_TEST_ANCHORS = [
    'test "phase 1 helper ports match committed parity fixture"',
]

REQUIRED_HELPER_TEST_ANCHORS = [
    'test "phase 1 string replaceChar stops at embedded NUL"',
]

REQUIRED_PHASE1_PARITY_REPLAY_MARKERS = [
    "fixture.find_bit.tail_clamped_first",
    "fixture.find_bit.tail_clamped_next",
    "fixture.find_bit.tail_zero_clamped_first",
    "fixture.find_bit.tail_zero_clamped_next",
    "fixture.find_bit.tail_and_clamped_first",
    "fixture.find_bit.tail_and_clamped_next",
    "fixture.bitmap.weight,",
    "fixture.bitmap.and_result,",
    "fixture.bitmap.and_values);",
    "fixture.bitmap.andnot_result,",
    "fixture.bitmap.andnot_values);",
    "fixture.bitmap.or_values);",
    "fixture.bitmap.xor_values);",
    "fixture.bitmap.partial_xor_nbits",
    "fixture.bitmap.partial_xor_masked_values",
    "fixture.bitmap.range_after_set",
    "fixture.bitmap.range_after_clear",
    "fixture.bitmap.full_after_fill",
    "fixture.bitmap.empty_after_zero",
    "fixture.bitmap.scnprintf",
    "fixture.string.strtobool_y,",
    "fixture.string.strtobool_on,",
    "fixture.string.strtobool_zero,",
    "fixture.string.strtobool_off,",
    "fixture.string.strlcpy_len,",
    "fixture.string.strlcpy_buffer,",
    "fixture.string.skip_spaces,",
    "fixture.string.trim_spaces,",
    "fixture.string.remove_spaces,",
    "fixture.string.replace_char,",
    "fixture.string.replace_char_end,",
    "fixture.string.memchr_inv_index,",
    "fixture.string.memchr_inv_none,",
    "fixture.rbtree.empty_root",
    "fixture.rbtree.insert_order",
    "fixture.rbtree.reverse_order",
    "fixture.rbtree.replace_order",
    "fixture.rbtree.erase_init_order",
    "fixture.rbtree.postorder_count",
    "fixture.rbtree.erase_init_node_empty",
    "fixture.rbtree.cleared_node_empty",
]

REQUIRED_FIND_BIT_TAIL_CLAMP_FIELDS = [
    "tail_clamped_first",
    "tail_clamped_next",
    "tail_zero_clamped_first",
    "tail_zero_clamped_next",
    "tail_and_clamped_first",
    "tail_and_clamped_next",
]

REQUIRED_FIND_BIT_TEST_ANCHORS = [
    'test "find first and next set bits across words"',
    'test "find zero bits respects the declared bit count"',
    'test "find and bit returns the first shared set bit"',
    'test "single-word next scans honor start masks"',
    'test "tail mask ignores set bits beyond nbits"',
    'test "tail mask ignores zero bits beyond nbits"',
    'test "tail mask ignores shared bits beyond nbits"',
    'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    'test "next scans past nbits return without reading bitmap words"',
]

REQUIRED_BITMAP_TEST_ANCHORS = [
    'test "bitmap allocator helpers size zero and free their buffers"',
    'test "bitmap set clear weight and empty full helpers"',
    'test "bitmap fill clamps tail bits in partial words"',
    'test "bitmap and andnot equal intersects subset"',
    'test "bitmap and andnot clamp tail bits in partial words"',
    'test "bitmap xor keeps caller-selected bit window"',
    'test "bitmap scnprintf collapses contiguous ranges"',
    'test "bitmap scnprintf reports full length while truncating the buffer"',
    'test "bitmap scnprintf handles terminator-only and zero-length caller views"',
    'test "bitmap copy aliases preserve tail clearing and extension semantics"',
]

REQUIRED_STRING_TEST_ANCHORS = [
    'test "strtobool accepts common Linux forms"',
    'test "strlcpy copies and returns the source length"',
    'test "streq matches C-string equality semantics"',
    'test "skip trim remove and replace spaces work in place"',
    'test "strHasPrefix honors C-string boundaries"',
    'test "memdup and memchrInv preserve byte content"',
    'test "memchrInv keeps long-buffer first-dirty-byte results stable"',
    'test "memparse handles decimal hexadecimal octal and suffixes"',
    'test "memparse keeps original rest when sign is not followed by digits"',
    'test "memparse saturates signed overflow instead of trapping"',
    'test "memparse consumes suffix after saturation"',
]

REQUIRED_RBTREE_TEST_ANCHORS = [
    'test "rbtree inserts and traverses in sorted order"',
    'test "rbtree erase and replace keep traversal consistent"',
    'test "rbtree eraseInit detaches erased node"',
    'test "rbtree postorder and empty node helpers behave"',
    'test "rbtree findAdd keeps the first duplicate and inserts new keys"',
    'test "rbtree nextMatch walks the duplicate range in order"',
    'test "rbtree cached root keeps the leftmost pointer in sync"',
    'test "rbtree eraseCached returns null for a singleton cached tree"',
]

REQUIRED_REVIEW_CHECKLIST_MARKERS = [
    "  * if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`",
    "`scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`",
    "still agree on the same closed helper tranche and validator-first replay path without widening Phase 1 beyond the bounded host-side helper packet?",
]

REQUIRED_DOCS_ROOT_MARKERS = [
    "Phase 1 notes - `Documentation/zigux/phase1-closure.md` - `scripts/zigux/README.md` - `zigux/Makefile` - `zigux/tests/build.zig` - `zigux/tests/phase1_helpers.zig` - `zigux/tests/phase1_bench.zig` - `zigux/tests/fixtures/phase1_helper_manifest.json` - `zigux/tests/fixtures/phase1_bench_expectations.json` - `scripts/zigux/validate-phase1.py` - `scripts/zigux/validate-phase1-closure.py` - `scripts/zigux/check-phase1-parity.py` - `scripts/zigux/check-phase1-bench.py` - `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` keep the closed host-side helper packet reviewable through the shared helper build entrypoint and the Linux-style replay route, while `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the closure, bootstrap-workflow replay, and validator-first contract explicit from the docs root instead of leaving the Phase 1 packet split across later review surfaces.",
]

REQUIRED_TESTS_ROOT_MARKERS = [
    "  * keep the closed Phase 1 host-tools packet explicit in the tests root too: `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` should continue to keep the closed helper tranche reviewable from the tests root instead of leaving the host-tools closure stack split across the docs root, scripts root, and workflow replay surface",
]


def collect_missing_files(root: Path) -> list[str]:
    missing: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            missing.append(rel)
    return missing


def collect_presence_markers(text: str, label: str, markers: list[str]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count < 1:
            missing.append(f"{label}:{marker}:expected>=1:actual={count}")
    return missing


def collect_exact_count_markers(text: str, label: str, markers: list[str]) -> list[str]:
    mismatches: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            mismatches.append(f"{label}:{marker}:expected=1:actual={count}")
    return mismatches


def collect_find_bit_fixture_mismatches(root: Path) -> list[str]:
    fixture_path = root / "zigux" / "tests" / "fixtures" / "phase1_helpers.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    find_bit_fixture = fixture.get("find_bit")
    if not isinstance(find_bit_fixture, dict):
        return ["phase1_fixture_find_bit:find_bit:expected=object:actual=missing"]

    bits_per_long = find_bit_fixture.get("bits_per_long")
    if not isinstance(bits_per_long, int) or bits_per_long <= 0:
        return [
            "phase1_fixture_find_bit:bits_per_long:expected=positive-integer:"
            f"actual={bits_per_long!r}"
        ]

    tail_nbits = bits_per_long + 5
    expected_values = {
        "tail_clamped_first": tail_nbits,
        "tail_clamped_next": tail_nbits,
        "tail_zero_clamped_first": tail_nbits,
        "tail_zero_clamped_next": tail_nbits,
        "tail_and_clamped_first": tail_nbits,
        "tail_and_clamped_next": tail_nbits,
    }

    mismatches: list[str] = []
    for field, expected in expected_values.items():
        actual = find_bit_fixture.get(field)
        if actual != expected:
            mismatches.append(
                f"phase1_fixture_find_bit:{field}:expected={expected}:actual={actual!r}"
            )
    return mismatches


def collect_missing_markers(root: Path) -> list[str]:
    ledger = (root / "zigux-alpha" / "BOOTSTRAP_COMMIT_LEDGER.md").read_text(encoding="utf-8")
    workflow = (root / ".github" / "workflows" / "zigux-bootstrap.yml").read_text(encoding="utf-8")
    test_root = (root / "zigux" / "tests" / "phase1_helpers.zig").read_text(encoding="utf-8")
    tests_readme = (root / "zigux" / "tests" / "README.md").read_text(encoding="utf-8")
    find_bit_source = (root / "tools" / "lib" / "find_bit.zig").read_text(encoding="utf-8")
    bitmap_source = (root / "tools" / "lib" / "bitmap.zig").read_text(encoding="utf-8")
    string_source = (root / "tools" / "lib" / "string.zig").read_text(encoding="utf-8")
    rbtree_source = (root / "tools" / "lib" / "rbtree.zig").read_text(encoding="utf-8")
    docs_readme = (root / "Documentation" / "zigux" / "README.md").read_text(encoding="utf-8")
    review_checklist = (root / "Documentation" / "zigux" / "review-checklist.md").read_text(
        encoding="utf-8"
    )

    missing_markers: list[str] = []
    for marker in REQUIRED_LEDGER_MARKERS:
        if marker not in ledger:
            missing_markers.append(f"ledger:{marker}")

    missing_markers.extend(
        collect_presence_markers(workflow, "workflow", REQUIRED_WORKFLOW_PRESENCE_MARKERS)
    )
    missing_markers.extend(
        collect_exact_count_markers(workflow, "workflow", REQUIRED_WORKFLOW_EXACT_MARKERS)
    )
    missing_markers.extend(collect_exact_count_markers(test_root, "test", REQUIRED_TEST_MARKERS))
    missing_markers.extend(
        collect_exact_count_markers(
            test_root, "phase1_parity_test_anchor", REQUIRED_PHASE1_PARITY_TEST_ANCHORS
        )
    )
    missing_markers.extend(
        collect_exact_count_markers(test_root, "helper_test_anchor", REQUIRED_HELPER_TEST_ANCHORS)
    )
    missing_markers.extend(
        collect_exact_count_markers(
            test_root, "phase1_parity_replay_marker", REQUIRED_PHASE1_PARITY_REPLAY_MARKERS
        )
    )
    missing_markers.extend(collect_find_bit_fixture_mismatches(root))
    missing_markers.extend(
        collect_exact_count_markers(find_bit_source, "find_bit_test_anchor", REQUIRED_FIND_BIT_TEST_ANCHORS)
    )
    missing_markers.extend(
        collect_exact_count_markers(bitmap_source, "bitmap_test_anchor", REQUIRED_BITMAP_TEST_ANCHORS)
    )
    missing_markers.extend(
        collect_exact_count_markers(string_source, "string_test_anchor", REQUIRED_STRING_TEST_ANCHORS)
    )
    missing_markers.extend(
        collect_exact_count_markers(rbtree_source, "rbtree_test_anchor", REQUIRED_RBTREE_TEST_ANCHORS)
    )
    missing_markers.extend(
        collect_exact_count_markers(
            docs_readme,
            "docs_root_phase1_packet",
            REQUIRED_DOCS_ROOT_MARKERS,
        )
    )
    missing_markers.extend(
        collect_exact_count_markers(
            tests_readme,
            "tests_root_phase1_packet",
            REQUIRED_TESTS_ROOT_MARKERS,
        )
    )
    missing_markers.extend(
        collect_presence_markers(
            review_checklist,
            "review_checklist_phase1_packet",
            REQUIRED_REVIEW_CHECKLIST_MARKERS,
        )
    )
    return missing_markers


def make_fixture_root(tmp_root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("// fixture\n", encoding="utf-8")

    workflow_path = tmp_root / ".github" / "workflows" / "zigux-bootstrap.yml"
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text(
        "\n".join(REQUIRED_WORKFLOW_PRESENCE_MARKERS + REQUIRED_WORKFLOW_EXACT_MARKERS) + "\n",
        encoding="utf-8",
    )

    ledger_path = tmp_root / "zigux-alpha" / "BOOTSTRAP_COMMIT_LEDGER.md"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text("\n".join(REQUIRED_LEDGER_MARKERS) + "\n", encoding="utf-8")

    test_path = tmp_root / "zigux" / "tests" / "phase1_helpers.zig"
    test_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.write_text(
        "\n".join(
            REQUIRED_TEST_MARKERS
            + REQUIRED_PHASE1_PARITY_TEST_ANCHORS
            + REQUIRED_HELPER_TEST_ANCHORS
            + REQUIRED_PHASE1_PARITY_REPLAY_MARKERS
        )
        + "\n",
        encoding="utf-8",
    )

    fixture_path = tmp_root / "zigux" / "tests" / "fixtures" / "phase1_helpers.json"
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    fixture_path.write_text(
        json.dumps(
            {
                "find_bit": {
                    "bits_per_long": 64,
                    "tail_clamped_first": 69,
                    "tail_clamped_next": 69,
                    "tail_zero_clamped_first": 69,
                    "tail_zero_clamped_next": 69,
                    "tail_and_clamped_first": 69,
                    "tail_and_clamped_next": 69,
                }
            },
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )

    docs_readme_path = tmp_root / "Documentation" / "zigux" / "README.md"
    docs_readme_path.parent.mkdir(parents=True, exist_ok=True)
    docs_readme_path.write_text(
        "\n".join(REQUIRED_DOCS_ROOT_MARKERS) + "\n",
        encoding="utf-8",
    )

    review_checklist_path = tmp_root / "Documentation" / "zigux" / "review-checklist.md"
    review_checklist_path.parent.mkdir(parents=True, exist_ok=True)
    review_checklist_path.write_text(
        "\n".join(REQUIRED_REVIEW_CHECKLIST_MARKERS) + "\n",
        encoding="utf-8",
    )

    tests_readme_path = tmp_root / "zigux" / "tests" / "README.md"
    tests_readme_path.parent.mkdir(parents=True, exist_ok=True)
    tests_readme_path.write_text(
        "\n".join(REQUIRED_TESTS_ROOT_MARKERS) + "\n",
        encoding="utf-8",
    )

    for rel, markers in [
        ("tools/lib/find_bit.zig", REQUIRED_FIND_BIT_TEST_ANCHORS),
        ("tools/lib/bitmap.zig", REQUIRED_BITMAP_TEST_ANCHORS),
        ("tools/lib/string.zig", REQUIRED_STRING_TEST_ANCHORS),
        ("tools/lib/rbtree.zig", REQUIRED_RBTREE_TEST_ANCHORS),
    ]:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(markers) + "\n", encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_validator_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)

        make_fixture_root(tmp_root)

        workflow_path = tmp_root / ".github" / "workflows" / "zigux-bootstrap.yml"
        workflow_path.write_text(
            "\n".join(REQUIRED_WORKFLOW_PRESENCE_MARKERS + REQUIRED_WORKFLOW_EXACT_MARKERS[:-2]) + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert "workflow:python3 scripts/zigux/check-phase1-parity.py:expected=1:actual=0" in missing_markers
        assert "workflow:zig build test --build-file zigux/tests/build.zig:expected=1:actual=0" in missing_markers

        make_fixture_root(tmp_root)
        workflow_path.write_text(
            "\n".join(
                REQUIRED_WORKFLOW_PRESENCE_MARKERS
                + REQUIRED_WORKFLOW_EXACT_MARKERS
                + REQUIRED_WORKFLOW_PRESENCE_MARKERS
            )
            + "\n",
            encoding="utf-8",
        )
        assert collect_missing_markers(tmp_root) == []

        make_fixture_root(tmp_root)
        workflow_path.write_text(
            "\n".join(
                REQUIRED_WORKFLOW_PRESENCE_MARKERS
                + REQUIRED_WORKFLOW_EXACT_MARKERS
                + [REQUIRED_WORKFLOW_EXACT_MARKERS[1]]
            )
            + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert "workflow:python3 scripts/zigux/check-phase1-parity.py:expected=1:actual=2" in missing_markers

        make_fixture_root(tmp_root)
        test_path = tmp_root / "zigux" / "tests" / "phase1_helpers.zig"
        test_path.write_text(
            "\n".join(
                REQUIRED_TEST_MARKERS
                + REQUIRED_PHASE1_PARITY_TEST_ANCHORS
                + REQUIRED_HELPER_TEST_ANCHORS
                + REQUIRED_PHASE1_PARITY_REPLAY_MARKERS
                + [REQUIRED_TEST_MARKERS[4]]
            )
            + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert 'test:@import("find_bit"):expected=1:actual=2' in missing_markers

        make_fixture_root(tmp_root)
        test_path.write_text(
            "\n".join(REQUIRED_TEST_MARKERS + REQUIRED_HELPER_TEST_ANCHORS + REQUIRED_PHASE1_PARITY_REPLAY_MARKERS)
            + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'phase1_parity_test_anchor:test "phase 1 helper ports match committed parity fixture":expected=1:actual=0'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        test_path.write_text(
            "\n".join(REQUIRED_TEST_MARKERS + REQUIRED_PHASE1_PARITY_TEST_ANCHORS + REQUIRED_HELPER_TEST_ANCHORS)
            + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert "phase1_parity_replay_marker:fixture.find_bit.tail_clamped_first:expected=1:actual=0" in missing_markers

        make_fixture_root(tmp_root)
        test_path.write_text(
            "\n".join(
                REQUIRED_TEST_MARKERS
                + REQUIRED_PHASE1_PARITY_TEST_ANCHORS
                + REQUIRED_HELPER_TEST_ANCHORS
                + [
                    marker
                    for marker in REQUIRED_PHASE1_PARITY_REPLAY_MARKERS
                    if marker != "fixture.string.memchr_inv_index,"
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert "phase1_parity_replay_marker:fixture.string.memchr_inv_index,:expected=1:actual=0" in missing_markers

        make_fixture_root(tmp_root)
        test_path.write_text(
            "\n".join(
                REQUIRED_TEST_MARKERS
                + REQUIRED_PHASE1_PARITY_TEST_ANCHORS
                + REQUIRED_HELPER_TEST_ANCHORS
                + REQUIRED_PHASE1_PARITY_REPLAY_MARKERS
                + ["fixture.string.memchr_inv_index,"]
            )
            + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert "phase1_parity_replay_marker:fixture.string.memchr_inv_index,:expected=1:actual=2" in missing_markers

        make_fixture_root(tmp_root)
        test_path.write_text(
            "\n".join(
                REQUIRED_TEST_MARKERS
                + REQUIRED_PHASE1_PARITY_TEST_ANCHORS
                + REQUIRED_HELPER_TEST_ANCHORS
                + [
                    marker
                    for marker in REQUIRED_PHASE1_PARITY_REPLAY_MARKERS
                    if marker != "fixture.bitmap.scnprintf"
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert "phase1_parity_replay_marker:fixture.bitmap.scnprintf:expected=1:actual=0" in missing_markers

        make_fixture_root(tmp_root)
        test_path.write_text(
            "\n".join(
                REQUIRED_TEST_MARKERS
                + REQUIRED_PHASE1_PARITY_TEST_ANCHORS
                + REQUIRED_HELPER_TEST_ANCHORS
                + REQUIRED_PHASE1_PARITY_REPLAY_MARKERS
                + ["fixture.bitmap.scnprintf"]
            )
            + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert "phase1_parity_replay_marker:fixture.bitmap.scnprintf:expected=1:actual=2" in missing_markers

        make_fixture_root(tmp_root)
        test_path.write_text(
            "\n".join(
                REQUIRED_TEST_MARKERS
                + REQUIRED_PHASE1_PARITY_TEST_ANCHORS
                + REQUIRED_HELPER_TEST_ANCHORS
                + [
                    marker
                    for marker in REQUIRED_PHASE1_PARITY_REPLAY_MARKERS
                    if marker != "fixture.rbtree.reverse_order"
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert "phase1_parity_replay_marker:fixture.rbtree.reverse_order:expected=1:actual=0" in missing_markers

        make_fixture_root(tmp_root)
        test_path.write_text(
            "\n".join(
                REQUIRED_TEST_MARKERS
                + REQUIRED_PHASE1_PARITY_TEST_ANCHORS
                + REQUIRED_HELPER_TEST_ANCHORS
                + REQUIRED_PHASE1_PARITY_REPLAY_MARKERS
                + ["fixture.rbtree.reverse_order"]
            )
            + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert "phase1_parity_replay_marker:fixture.rbtree.reverse_order:expected=1:actual=2" in missing_markers

        make_fixture_root(tmp_root)
        test_path.write_text(
            "\n".join(REQUIRED_TEST_MARKERS + REQUIRED_PHASE1_PARITY_TEST_ANCHORS) + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'helper_test_anchor:test "phase 1 string replaceChar stops at embedded NUL":expected=1:actual=0'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        fixture_path = tmp_root / "zigux" / "tests" / "fixtures" / "phase1_helpers.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["find_bit"]["tail_clamped_first"] = 67
        fixture_path.write_text(json.dumps(fixture, separators=(",", ":")), encoding="utf-8")
        missing_markers = collect_missing_markers(tmp_root)
        assert "phase1_fixture_find_bit:tail_clamped_first:expected=69:actual=67" in missing_markers

        make_fixture_root(tmp_root)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["find_bit"]["tail_and_clamped_next"] = 67
        fixture_path.write_text(json.dumps(fixture, separators=(",", ":")), encoding="utf-8")
        missing_markers = collect_missing_markers(tmp_root)
        assert "phase1_fixture_find_bit:tail_and_clamped_next:expected=69:actual=67" in missing_markers

        make_fixture_root(tmp_root)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["find_bit"]["bits_per_long"] = 0
        fixture_path.write_text(json.dumps(fixture, separators=(",", ":")), encoding="utf-8")
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            "phase1_fixture_find_bit:bits_per_long:expected=positive-integer:actual=0"
            in missing_markers
        )

        make_fixture_root(tmp_root)
        find_bit_path = tmp_root / "tools" / "lib" / "find_bit.zig"
        find_bit_path.write_text("\n".join(REQUIRED_FIND_BIT_TEST_ANCHORS[1:]) + "\n", encoding="utf-8")
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'find_bit_test_anchor:test "find first and next set bits across words":expected=1:actual=0'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        find_bit_path.write_text(
            "\n".join(REQUIRED_FIND_BIT_TEST_ANCHORS[:3] + REQUIRED_FIND_BIT_TEST_ANCHORS[4:]) + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'find_bit_test_anchor:test "single-word next scans honor start masks":expected=1:actual=0'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        find_bit_path.write_text(
            "\n".join(REQUIRED_FIND_BIT_TEST_ANCHORS + [REQUIRED_FIND_BIT_TEST_ANCHORS[3]]) + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'find_bit_test_anchor:test "single-word next scans honor start masks":expected=1:actual=2'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        find_bit_path.write_text(
            "\n".join(REQUIRED_FIND_BIT_TEST_ANCHORS + [REQUIRED_FIND_BIT_TEST_ANCHORS[2]]) + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'find_bit_test_anchor:test "find and bit returns the first shared set bit":expected=1:actual=2'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        find_bit_path.write_text(
            "\n".join(REQUIRED_FIND_BIT_TEST_ANCHORS[:6] + REQUIRED_FIND_BIT_TEST_ANCHORS[7:]) + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'find_bit_test_anchor:test "tail mask ignores shared bits beyond nbits":expected=1:actual=0'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        find_bit_path.write_text(
            "\n".join(REQUIRED_FIND_BIT_TEST_ANCHORS[:7] + REQUIRED_FIND_BIT_TEST_ANCHORS[8:]) + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'find_bit_test_anchor:test "head-word boundary scans keep the last in-range bit reachable from an inclusive start":expected=1:actual=0'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        find_bit_path.write_text(
            "\n".join(REQUIRED_FIND_BIT_TEST_ANCHORS[:-1]) + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'find_bit_test_anchor:test "next scans past nbits return without reading bitmap words":expected=1:actual=0'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        bitmap_path = tmp_root / "tools" / "lib" / "bitmap.zig"
        bitmap_path.write_text("\n".join(REQUIRED_BITMAP_TEST_ANCHORS[1:]) + "\n", encoding="utf-8")
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'bitmap_test_anchor:test "bitmap allocator helpers size zero and free their buffers":expected=1:actual=0'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        bitmap_path.write_text(
            "\n".join(REQUIRED_BITMAP_TEST_ANCHORS[:1] + REQUIRED_BITMAP_TEST_ANCHORS[2:]) + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'bitmap_test_anchor:test "bitmap set clear weight and empty full helpers":expected=1:actual=0'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        bitmap_path.write_text(
            "\n".join(REQUIRED_BITMAP_TEST_ANCHORS[:2] + REQUIRED_BITMAP_TEST_ANCHORS[3:]) + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'bitmap_test_anchor:test "bitmap fill clamps tail bits in partial words":expected=1:actual=0'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        bitmap_path.write_text(
            "\n".join(REQUIRED_BITMAP_TEST_ANCHORS[:8] + REQUIRED_BITMAP_TEST_ANCHORS[9:]) + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'bitmap_test_anchor:test "bitmap scnprintf handles terminator-only and zero-length caller views":expected=1:actual=0'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        bitmap_path.write_text(
            "\n".join(REQUIRED_BITMAP_TEST_ANCHORS[:-1]) + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'bitmap_test_anchor:test "bitmap copy aliases preserve tail clearing and extension semantics":expected=1:actual=0'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        bitmap_path.write_text(
            "\n".join(REQUIRED_BITMAP_TEST_ANCHORS[:4] + REQUIRED_BITMAP_TEST_ANCHORS[5:]) + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'bitmap_test_anchor:test "bitmap and andnot clamp tail bits in partial words":expected=1:actual=0'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        bitmap_path.write_text(
            "\n".join(REQUIRED_BITMAP_TEST_ANCHORS[:7] + REQUIRED_BITMAP_TEST_ANCHORS[8:]) + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'bitmap_test_anchor:test "bitmap scnprintf reports full length while truncating the buffer":expected=1:actual=0'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        bitmap_path.write_text(
            "\n".join(REQUIRED_BITMAP_TEST_ANCHORS + [REQUIRED_BITMAP_TEST_ANCHORS[5]]) + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'bitmap_test_anchor:test "bitmap xor keeps caller-selected bit window":expected=1:actual=2'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        string_path = tmp_root / "tools" / "lib" / "string.zig"
        string_path.write_text("\n".join(REQUIRED_STRING_TEST_ANCHORS[1:]) + "\n", encoding="utf-8")
        missing_markers = collect_missing_markers(tmp_root)
        assert 'string_test_anchor:test "strtobool accepts common Linux forms":expected=1:actual=0' in missing_markers

        make_fixture_root(tmp_root)
        string_path.write_text(
            "\n".join(REQUIRED_STRING_TEST_ANCHORS[:2] + REQUIRED_STRING_TEST_ANCHORS[3:]) + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'string_test_anchor:test "streq matches C-string equality semantics":expected=1:actual=0'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        string_path.write_text(
            "\n".join(REQUIRED_STRING_TEST_ANCHORS + [REQUIRED_STRING_TEST_ANCHORS[3]]) + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'string_test_anchor:test "skip trim remove and replace spaces work in place":expected=1:actual=2'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        string_path.write_text(
            "\n".join(REQUIRED_STRING_TEST_ANCHORS[:-1]) + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'string_test_anchor:test "memparse consumes suffix after saturation":expected=1:actual=0'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        rbtree_path = tmp_root / "tools" / "lib" / "rbtree.zig"
        rbtree_path.write_text("\n".join(REQUIRED_RBTREE_TEST_ANCHORS[1:]) + "\n", encoding="utf-8")
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'rbtree_test_anchor:test "rbtree inserts and traverses in sorted order":expected=1:actual=0'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        rbtree_path.write_text(
            "\n".join(REQUIRED_RBTREE_TEST_ANCHORS + [REQUIRED_RBTREE_TEST_ANCHORS[5]]) + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'rbtree_test_anchor:test "rbtree nextMatch walks the duplicate range in order":expected=1:actual=2'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        rbtree_path.write_text(
            "\n".join(REQUIRED_RBTREE_TEST_ANCHORS[:6] + REQUIRED_RBTREE_TEST_ANCHORS[7:]) + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'rbtree_test_anchor:test "rbtree cached root keeps the leftmost pointer in sync":expected=1:actual=0'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        rbtree_path.write_text(
            "\n".join(REQUIRED_RBTREE_TEST_ANCHORS + [REQUIRED_RBTREE_TEST_ANCHORS[7]]) + "\n",
            encoding="utf-8",
        )
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            'rbtree_test_anchor:test "rbtree eraseCached returns null for a singleton cached tree":expected=1:actual=2'
            in missing_markers
        )

        make_fixture_root(tmp_root)
        docs_readme_path = tmp_root / "Documentation" / "zigux" / "README.md"
        docs_readme_path.write_text("", encoding="utf-8")
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            "docs_root_phase1_packet:Phase 1 notes - `Documentation/zigux/phase1-closure.md` - `scripts/zigux/README.md` - `zigux/Makefile` - `zigux/tests/build.zig` - `zigux/tests/phase1_helpers.zig` - `zigux/tests/phase1_bench.zig` - `zigux/tests/fixtures/phase1_helper_manifest.json` - `zigux/tests/fixtures/phase1_bench_expectations.json` - `scripts/zigux/validate-phase1.py` - `scripts/zigux/validate-phase1-closure.py` - `scripts/zigux/check-phase1-parity.py` - `scripts/zigux/check-phase1-bench.py` - `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` keep the closed host-side helper packet reviewable through the shared helper build entrypoint and the Linux-style replay route, while `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the closure, bootstrap-workflow replay, and validator-first contract explicit from the docs root instead of leaving the Phase 1 packet split across later review surfaces.:expected=1:actual=0"
            in missing_markers
        )

        make_fixture_root(tmp_root)
        tests_readme_path = tmp_root / "zigux" / "tests" / "README.md"
        tests_readme_path.write_text("", encoding="utf-8")
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            "tests_root_phase1_packet:  * keep the closed Phase 1 host-tools packet explicit in the tests root too: `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` should continue to keep the closed helper tranche reviewable from the tests root instead of leaving the host-tools closure stack split across the docs root, scripts root, and workflow replay surface:expected=1:actual=0"
            in missing_markers
        )

        make_fixture_root(tmp_root)
        review_checklist_path = tmp_root / "Documentation" / "zigux" / "review-checklist.md"
        review_checklist_path.write_text("", encoding="utf-8")
        missing_markers = collect_missing_markers(tmp_root)
        assert (
            "review_checklist_phase1_packet:  * if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`:expected>=1:actual=0"
            in missing_markers
        )

        print("PHASE1_VALIDATION_SELF_TEST=pass")
        print("PHASE1_VALIDATION_SELF_TEST_CASE_COUNT=44")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 1 helper packet.")
    parser.add_argument("--self-test", action="store_true", help="Run validator self-test cases without reading repo files.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing = collect_missing_files(ROOT)
    if missing:
        print("PHASE1_VALIDATION=fail")
        print("MISSING_PHASE1_FILES_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE1_FILES_END")
        return 1

    missing_markers = collect_missing_markers(ROOT)
    if missing_markers:
        print("PHASE1_VALIDATION=fail")
        print("MISSING_PHASE1_MARKERS_START")
        for marker in missing_markers:
            print(marker)
        print("MISSING_PHASE1_MARKERS_END")
        return 1

    print("PHASE1_VALIDATION=pass")
    print(f"PHASE1_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_REQUIRED_MARKER_COUNT="
        f"{len(REQUIRED_LEDGER_MARKERS) + len(REQUIRED_WORKFLOW_PRESENCE_MARKERS) + len(REQUIRED_WORKFLOW_EXACT_MARKERS) + len(REQUIRED_TEST_MARKERS) + len(REQUIRED_PHASE1_PARITY_TEST_ANCHORS) + len(REQUIRED_HELPER_TEST_ANCHORS) + len(REQUIRED_PHASE1_PARITY_REPLAY_MARKERS) + len(REQUIRED_FIND_BIT_TAIL_CLAMP_FIELDS) + len(REQUIRED_FIND_BIT_TEST_ANCHORS) + len(REQUIRED_BITMAP_TEST_ANCHORS) + len(REQUIRED_STRING_TEST_ANCHORS) + len(REQUIRED_RBTREE_TEST_ANCHORS) + len(REQUIRED_DOCS_ROOT_MARKERS) + len(REQUIRED_TESTS_ROOT_MARKERS) + len(REQUIRED_REVIEW_CHECKLIST_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
