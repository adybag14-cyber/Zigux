#!/usr/bin/env python3
"""Validate the current Phase 1 direct-anchor reminder gap packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
DOCS_README_REL = Path("Documentation/zigux/README.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
DIRECT_ANCHOR_GATE_REL = Path("scripts/zigux/check-phase1-direct-anchor-manifest-gate.py")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    DOCS_README_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    VALIDATOR_REL,
    DIRECT_ANCHOR_GATE_REL,
)

CLOSURE_PACKET_WITH_GATE = (
    "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,"
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,"
    "Documentation/zigux/review-checklist.md,scripts/zigux/README.md,"
    "scripts/zigux/check-phase1-string-review-packet.py,"
    "scripts/zigux/check-phase1-direct-owner-markers.py,"
    "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py,"
    "scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,"
    "scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,"
    "zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,"
    "zigux/tests/fixtures/phase1_helper_manifest.json`"
)

VALIDATOR_PACKET_WITHOUT_GATE = (
    '`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,'
    'Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,'
    'Documentation/zigux/review-checklist.md,scripts/zigux/README.md,'
    'scripts/zigux/check-phase1-string-review-packet.py,'
    'scripts/zigux/check-phase1-direct-owner-markers.py,'
    'scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,'
    'scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,'
    'zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,'
    'zigux/tests/fixtures/phase1_helper_manifest.json`'
)

DOCS_ROOT_PHASE1_LINE = (
    "- `scripts/zigux/validate-phase1-closure.py`\n"
    "- `scripts/zigux/check-phase1-string-review-packet.py`\n"
    "- `scripts/zigux/check-phase1-direct-owner-markers.py`\n"
    "- `scripts/zigux/check-phase1-shared-reminder-packet.py`\n"
    "- `scripts/zigux/check-phase1-bench.py`"
)

SCRIPTS_ROOT_PACKET_LINE = (
    "- `scripts/zigux/check-phase1-string-review-packet.py`, "
    "`scripts/zigux/check-phase1-direct-owner-markers.py`, "
    "`scripts/zigux/check-phase1-bench.py`, "
    "`scripts/zigux/check-phase1-shared-reminder-packet.py`, and "
    "`scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, "
    "direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root"
)

TESTS_ROOT_PACKET_LINE = (
    "- `scripts/zigux/check-phase1-string-review-packet.py`\n"
    "- `scripts/zigux/check-phase1-direct-owner-markers.py`\n"
    "- `scripts/zigux/check-phase1-bench.py`\n"
    "- `scripts/zigux/check-phase1-shared-reminder-packet.py`\n"
    "- `scripts/zigux/validate-phase1-closure.py`"
)

VALIDATOR_REQUIRED_FILES_FRAGMENT = (
    "    STRING_REVIEW_CHECKER_REL,\n"
    "    FIND_BIT_REVIEW_CHECKER_REL,\n"
    "    RBTREE_REVIEW_CHECKER_REL,\n"
    "    DIRECT_OWNER_CHECKER_REL,\n"
    "    ROUTE_SUMMARY_CHECKER_REL,\n"
    "    BENCH_CHECKER_REL,\n"
    "    FIND_BIT_BENCH_ANCHOR_CHECKER_REL,\n"
    "    BITMAP_DIRECT_ANCHOR_CHECKER_REL,\n"
    "    SHARED_REMINDER_CHECKER_REL,\n"
)


def repo_root(root_arg: str | None) -> Path:
    return Path(root_arg).resolve() if root_arg else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_once(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}"]


def require_absent(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 0 else [f"{label}:expected_absent:actual_count={count}"]


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    closure_text = load_text(root, PHASE1_CLOSURE_REL)
    docs_text = load_text(root, DOCS_README_REL)
    scripts_text = load_text(root, SCRIPTS_README_REL)
    tests_text = load_text(root, TESTS_README_REL)
    validator_text = load_text(root, VALIDATOR_REL)

    failures.extend(
        require_once(
            closure_text,
            f"{PHASE1_CLOSURE_REL.as_posix()}:direct_anchor_gate_bullet",
            "- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`",
        )
    )
    failures.extend(
        require_once(
            closure_text,
            f"{PHASE1_CLOSURE_REL.as_posix()}:current_reminder_packet",
            CLOSURE_PACKET_WITH_GATE,
        )
    )

    failures.extend(
        require_once(
            docs_text,
            f"{DOCS_README_REL.as_posix()}:phase1_list_without_gate",
            DOCS_ROOT_PHASE1_LINE,
        )
    )
    failures.extend(
        require_absent(
            docs_text,
            f"{DOCS_README_REL.as_posix()}:direct_anchor_gate_absent",
            "`scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`",
        )
    )

    failures.extend(
        require_once(
            scripts_text,
            f"{SCRIPTS_README_REL.as_posix()}:scripts_packet_without_gate",
            SCRIPTS_ROOT_PACKET_LINE,
        )
    )
    failures.extend(
        require_absent(
            scripts_text,
            f"{SCRIPTS_README_REL.as_posix()}:direct_anchor_gate_absent",
            "`scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`",
        )
    )

    failures.extend(
        require_once(
            tests_text,
            f"{TESTS_README_REL.as_posix()}:tests_packet_without_gate",
            TESTS_ROOT_PACKET_LINE,
        )
    )
    failures.extend(
        require_absent(
            tests_text,
            f"{TESTS_README_REL.as_posix()}:direct_anchor_gate_absent",
            "`scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`",
        )
    )

    failures.extend(
        require_once(
            validator_text,
            f"{VALIDATOR_REL.as_posix()}:reminder_packet_without_gate",
            VALIDATOR_PACKET_WITHOUT_GATE,
        )
    )
    failures.extend(
        require_once(
            validator_text,
            f"{VALIDATOR_REL.as_posix()}:required_files_without_gate",
            VALIDATOR_REQUIRED_FILES_FRAGMENT,
        )
    )
    failures.extend(
        require_absent(
            validator_text,
            f"{VALIDATOR_REL.as_posix()}:direct_anchor_gate_absent",
            "DIRECT_ANCHOR_MANIFEST_GATE_REL",
        )
    )

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root / relative_path, f"fixture for {relative_path.as_posix()}\n")

    write_text(
        root / PHASE1_CLOSURE_REL,
        "# Phase 1 Closure\n\n"
        "- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`\n"
        f"- {CLOSURE_PACKET_WITH_GATE}\n",
    )
    write_text(
        root / DOCS_README_REL,
        "# Zigux Documentation\n\n"
        "Phase 1 notes\n"
        f"{DOCS_ROOT_PHASE1_LINE}\n",
    )
    write_text(
        root / SCRIPTS_README_REL,
        "# scripts/zigux\n\n"
        f"{SCRIPTS_ROOT_PACKET_LINE}\n",
    )
    write_text(
        root / TESTS_README_REL,
        "# zigux/tests\n\n"
        "Current packet\n"
        f"{TESTS_ROOT_PACKET_LINE}\n",
    )
    write_text(
        root / VALIDATOR_REL,
        "REQUIRED_FILES = (\n"
        f"{VALIDATOR_REQUIRED_FILES_FRAGMENT}"
        ")\n\n"
        "EXPECTED_CLOSURE_MARKERS = {\n"
        f'    "reminder_packet": "{VALIDATOR_PACKET_WITHOUT_GATE}",\n'
        "}\n",
    )
    write_text(root / DIRECT_ANCHOR_GATE_REL, "#!/usr/bin/env python3\nprint('pass')\n")


def run_self_test() -> int:
    cases = (
        ("baseline", None),
        (
            "missing_closure_gate_bullet",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL).replace(
                    "- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`\n", "", 1
                ),
            ),
        ),
        (
            "missing_closure_packet_marker",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL).replace(f"- {CLOSURE_PACKET_WITH_GATE}\n", "", 1),
            ),
        ),
        (
            "docs_reintroduced_gate",
            lambda root: write_text(
                root / DOCS_README_REL,
                load_text(root, DOCS_README_REL) + "- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`\n",
            ),
        ),
        (
            "scripts_reintroduced_gate",
            lambda root: write_text(
                root / SCRIPTS_README_REL,
                load_text(root, SCRIPTS_README_REL)
                + "`scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`\n",
            ),
        ),
        (
            "tests_reintroduced_gate",
            lambda root: write_text(
                root / TESTS_README_REL,
                load_text(root, TESTS_README_REL)
                + "- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`\n",
            ),
        ),
        (
            "validator_reintroduced_gate_symbol",
            lambda root: write_text(
                root / VALIDATOR_REL,
                load_text(root, VALIDATOR_REL) + "DIRECT_ANCHOR_MANIFEST_GATE_REL = Path('x')\n",
            ),
        ),
        (
            "validator_reminder_packet_with_gate",
            lambda root: write_text(
                root / VALIDATOR_REL,
                load_text(root, VALIDATOR_REL).replace(VALIDATOR_PACKET_WITHOUT_GATE, CLOSURE_PACKET_WITH_GATE),
            ),
        ),
        (
            "validator_required_files_changed",
            lambda root: write_text(
                root / VALIDATOR_REL,
                load_text(root, VALIDATOR_REL).replace(
                    "    BITMAP_DIRECT_ANCHOR_CHECKER_REL,\n",
                    "    DIRECT_ANCHOR_MANIFEST_GATE_REL,\n    BITMAP_DIRECT_ANCHOR_CHECKER_REL,\n",
                    1,
                ),
            ),
        ),
    )

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-direct-anchor-reminder-gap-") as tmp:
            root = Path(tmp)
            write_sample_root(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-direct-anchor-reminder-gap-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-direct-anchor-reminder-gap-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_DIRECT_ANCHOR_REMINDER_GAP_PACKET_SELF_TEST=pass")
    print(f"PHASE1_DIRECT_ANCHOR_REMINDER_GAP_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run embedded self-tests")
    parser.add_argument("--write-sample-root", help="write a current-like sample root")
    args = parser.parse_args()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        print("PHASE1_DIRECT_ANCHOR_REMINDER_GAP_PACKET_SAMPLE_ROOT=written")
        return 0

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_DIRECT_ANCHOR_REMINDER_GAP_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_DIRECT_ANCHOR_REMINDER_GAP_PACKET=pass")
    print("PHASE1_DIRECT_ANCHOR_REMINDER_GAP_SPLIT=current_master")
    print("PHASE1_DIRECT_ANCHOR_REMINDER_GAP_CLOSURE_PACKET_COUNT=16")
    print("PHASE1_DIRECT_ANCHOR_REMINDER_GAP_NARROW_PACKET_COUNT=15")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
