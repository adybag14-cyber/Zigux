#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parent

CHECKER = Path("scripts/zigux/check-phase1-bench.py")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
DOCS_ROOT = Path("Documentation/zigux/README.md")
CLOSURE = Path("Documentation/zigux/phase1-closure.md")
CHECKLIST = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_ROOT = Path("scripts/zigux/README.md")
TESTS_ROOT = Path("zigux/tests/README.md")

REQUIRED_FILES = (
    CHECKER,
    WORKFLOW,
    DOCS_ROOT,
    CLOSURE,
    CHECKLIST,
    SCRIPTS_ROOT,
    TESTS_ROOT,
)

EXACT_FAMILY_MARKERS = {
    "bitmap": (
        "BITMAP_REQUIRED_EXACT_CHECKSUMS = {",
        '"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",',
        '"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",',
        'return ("expectations_checksums_bitmap_exact_required", key)',
        'return ("missing_bitmap_exact_checksums", missing_bitmap_exact)',
    ),
    "find_bit": (
        "FIND_BIT_REQUIRED_EXACT_CHECKSUMS = {",
        '"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",',
        '"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",',
        'return ("expectations_checksums_find_bit_exact_required", key)',
        'return ("missing_find_bit_exact_checksums", missing_find_bit_exact)',
    ),
    "string": (
        "STRING_REQUIRED_EXACT_CHECKSUMS = {",
        '"PHASE1_BENCH_STRING_CHECKSUM",',
        'return ("expectations_checksums_string_exact_required", key)',
        'return ("missing_string_exact_checksums", missing_string_exact)',
    ),
    "hweight": (
        "HWEIGHT_REQUIRED_EXACT_CHECKSUMS = {",
        '"PHASE1_BENCH_HWEIGHT_CHECKSUM",',
        'return ("expectations_checksums_hweight_exact_required", key)',
        'return ("missing_hweight_exact_checksums", missing_hweight_exact)',
    ),
    "list_sort": (
        "LIST_SORT_REQUIRED_EXACT_CHECKSUMS = {",
        '"PHASE1_BENCH_LIST_SORT_CHECKSUM",',
        'return ("expectations_checksums_list_sort_exact_required", key)',
        'return ("missing_list_sort_exact_checksums", missing_list_sort_exact)',
    ),
    "rbtree": (
        "RBTREE_REQUIRED_EXACT_CHECKSUMS = {",
        '"PHASE1_BENCH_RBTREE_CHECKSUM",',
        '"PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",',
        '"PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",',
        '"PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",',
        '"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",',
        "RBTREE_REQUIRED_ITERATIONS = {",
        '"PHASE1_BENCH_RBTREE_ITERATIONS",',
        'return ("expectations_checksums_rbtree_exact_required", key)',
        'return ("missing_rbtree_exact_checksums", missing_rbtree_exact)',
        'return ("expectations_missing_rbtree_iterations", missing_rbtree_iterations)',
        'return ("missing_rbtree_iterations", [key])',
    ),
}

REMINDER_MARKERS = {
    DOCS_ROOT: (
        "`scripts/zigux/check-phase1-bench.py`",
        "the shipped bench checker",
    ),
    CLOSURE: (
        "`PHASE1_FIND_BIT_BENCH_GUARD=`",
        "the bench checker at self-test coverage only",
    ),
    CHECKLIST: (
        "`scripts/zigux/check-phase1-bench.py`",
        "`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    ),
    SCRIPTS_ROOT: (
        "`python3 scripts/zigux/check-phase1-bench.py --self-test`",
        "`scripts/zigux/check-phase1-bench.py`",
    ),
    TESTS_ROOT: (
        "`scripts/zigux/check-phase1-bench.py`",
        "broader Phase 1 closure companions stay outside the narrow direct-readback packet",
    ),
    WORKFLOW: (
        "python3 scripts/zigux/check-phase1-bench.py --self-test",
    ),
}


def load_text(root: Path, relpath: Path) -> str:
    path = root / relpath
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"missing required file: {relpath}")


def validate(root: Path) -> tuple[str, object]:
    missing_files = [str(path) for path in REQUIRED_FILES if not (root / path).is_file()]
    if missing_files:
        return ("missing_files", missing_files)

    checker_text = load_text(root, CHECKER)
    workflow_text = load_text(root, WORKFLOW)

    if "python3 scripts/zigux/check-phase1-bench.py --self-test" not in workflow_text:
        return ("workflow_missing_bench_self_test", str(WORKFLOW))

    missing_family_markers: list[str] = []
    for family, markers in EXACT_FAMILY_MARKERS.items():
        for marker in markers:
            if marker not in checker_text:
                missing_family_markers.append(f"{family}:{marker}")
    if missing_family_markers:
        return ("missing_family_markers", missing_family_markers)

    missing_reminder_markers: list[str] = []
    for relpath, markers in REMINDER_MARKERS.items():
        text = workflow_text if relpath == WORKFLOW else load_text(root, relpath)
        for marker in markers:
            if marker not in text:
                missing_reminder_markers.append(f"{relpath}:{marker}")
    if missing_reminder_markers:
        return ("missing_reminder_markers", missing_reminder_markers)

    return (
        "pass",
        {
            "required_file_count": len(REQUIRED_FILES),
            "family_count": len(EXACT_FAMILY_MARKERS),
            "family_marker_count": sum(len(markers) for markers in EXACT_FAMILY_MARKERS.values()),
            "reminder_marker_count": sum(len(markers) for markers in REMINDER_MARKERS.values()),
        },
    )


def write_sample_root(root: Path) -> None:
    checker_text = """#!/usr/bin/env python3
RBTREE_REQUIRED_ITERATIONS = {
    \"PHASE1_BENCH_RBTREE_ITERATIONS\",
}
BITMAP_REQUIRED_EXACT_CHECKSUMS = {
    \"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM\",
    \"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM\",
}
FIND_BIT_REQUIRED_EXACT_CHECKSUMS = {
    \"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM\",
    \"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM\",
}
STRING_REQUIRED_EXACT_CHECKSUMS = {
    \"PHASE1_BENCH_STRING_CHECKSUM\",
}
HWEIGHT_REQUIRED_EXACT_CHECKSUMS = {
    \"PHASE1_BENCH_HWEIGHT_CHECKSUM\",
}
LIST_SORT_REQUIRED_EXACT_CHECKSUMS = {
    \"PHASE1_BENCH_LIST_SORT_CHECKSUM\",
}
RBTREE_REQUIRED_EXACT_CHECKSUMS = {
    \"PHASE1_BENCH_RBTREE_CHECKSUM\",
    \"PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM\",
    \"PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM\",
    \"PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM\",
    \"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM\",
}
def validate_expectations():
    return (\"expectations_checksums_bitmap_exact_required\", key)
    return (\"expectations_checksums_find_bit_exact_required\", key)
    return (\"expectations_checksums_string_exact_required\", key)
    return (\"expectations_checksums_hweight_exact_required\", key)
    return (\"expectations_checksums_list_sort_exact_required\", key)
    return (\"expectations_checksums_rbtree_exact_required\", key)
    return (\"expectations_missing_rbtree_iterations\", missing_rbtree_iterations)
def validate_output():
    return (\"missing_bitmap_exact_checksums\", missing_bitmap_exact)
    return (\"missing_find_bit_exact_checksums\", missing_find_bit_exact)
    return (\"missing_string_exact_checksums\", missing_string_exact)
    return (\"missing_hweight_exact_checksums\", missing_hweight_exact)
    return (\"missing_list_sort_exact_checksums\", missing_list_sort_exact)
    return (\"missing_rbtree_exact_checksums\", missing_rbtree_exact)
    return (\"missing_rbtree_iterations\", [key])
"""
    workflow_text = """- name: Self-test current Phase 1 bench checker
  run: python3 scripts/zigux/check-phase1-bench.py --self-test
"""
    docs_root_text = """`scripts/zigux/check-phase1-bench.py`
the shipped bench checker
"""
    closure_text = """`PHASE1_FIND_BIT_BENCH_GUARD=`
the bench checker at self-test coverage only
"""
    checklist_text = """`scripts/zigux/check-phase1-bench.py`
`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
"""
    scripts_root_text = """`python3 scripts/zigux/check-phase1-bench.py --self-test`
`scripts/zigux/check-phase1-bench.py`
"""
    tests_root_text = """`scripts/zigux/check-phase1-bench.py`
broader Phase 1 closure companions stay outside the narrow direct-readback packet
"""

    files = {
        CHECKER: checker_text,
        WORKFLOW: workflow_text,
        DOCS_ROOT: docs_root_text,
        CLOSURE: closure_text,
        CHECKLIST: checklist_text,
        SCRIPTS_ROOT: scripts_root_text,
        TESTS_ROOT: tests_root_text,
    }
    for relpath, content in files.items():
        path = root / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-bench-exact-families-") as tmp:
        sample_root = Path(tmp) / "sample"
        write_sample_root(sample_root)
        kind, payload = validate(sample_root)
        assert kind == "pass", (kind, payload)
        case_count += 1

        missing_self_test_root = Path(tmp) / "missing-self-test"
        write_sample_root(missing_self_test_root)
        workflow_path = missing_self_test_root / WORKFLOW
        workflow_path.write_text("- name: Other\n  run: true\n", encoding="utf-8")
        kind, payload = validate(missing_self_test_root)
        assert kind == "workflow_missing_bench_self_test", (kind, payload)
        case_count += 1

        missing_string_root = Path(tmp) / "missing-string"
        write_sample_root(missing_string_root)
        checker_path = missing_string_root / CHECKER
        checker_text = checker_path.read_text(encoding="utf-8").replace(
            'return (\"missing_string_exact_checksums\", missing_string_exact)\n',
            "",
        )
        checker_path.write_text(checker_text, encoding="utf-8")
        kind, payload = validate(missing_string_root)
        assert kind == "missing_family_markers", (kind, payload)
        assert payload == ['string:return ("missing_string_exact_checksums", missing_string_exact)']
        case_count += 1

        missing_docs_root = Path(tmp) / "missing-docs-root"
        write_sample_root(missing_docs_root)
        docs_path = missing_docs_root / DOCS_ROOT
        docs_text = docs_path.read_text(encoding="utf-8").replace(
            "the shipped bench checker\n",
            "",
        )
        docs_path.write_text(docs_text, encoding="utf-8")
        kind, payload = validate(missing_docs_root)
        assert kind == "missing_reminder_markers", (kind, payload)
        assert payload == [f"{DOCS_ROOT}:the shipped bench checker"]
        case_count += 1

        missing_file_root = Path(tmp) / "missing-file"
        write_sample_root(missing_file_root)
        (missing_file_root / CHECKLIST).unlink()
        kind, payload = validate(missing_file_root)
        assert kind == "missing_files", (kind, payload)
        assert payload == [str(CHECKLIST)]
        case_count += 1

    print("PHASE1_BENCH_EXACT_FAMILIES_SELF_TEST=pass")
    print(f"PHASE1_BENCH_EXACT_FAMILIES_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the shipped Phase 1 bench exact-checksum family contract and reminder packet."
    )
    parser.add_argument("--root", default=str(ROOT), help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests")
    parser.add_argument("--write-sample-root", help="Write a passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root))
        return 0

    kind, payload = validate(Path(args.root))
    if kind != "pass":
        print("PHASE1_BENCH_EXACT_FAMILIES=fail")
        print(f"PHASE1_BENCH_EXACT_FAMILIES_REASON={kind}")
        print(payload)
        return 1

    assert isinstance(payload, dict)
    print("PHASE1_BENCH_EXACT_FAMILIES=pass")
    print(f"PHASE1_BENCH_EXACT_FAMILIES_REQUIRED_FILE_COUNT={payload['required_file_count']}")
    print(f"PHASE1_BENCH_EXACT_FAMILIES_FAMILY_COUNT={payload['family_count']}")
    print(
        "PHASE1_BENCH_EXACT_FAMILIES_FAMILY_MARKER_COUNT="
        f"{payload['family_marker_count']}"
    )
    print(
        "PHASE1_BENCH_EXACT_FAMILIES_REMINDER_MARKER_COUNT="
        f"{payload['reminder_marker_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
