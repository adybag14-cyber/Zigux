#!/usr/bin/env python3
"""Guard the current Phase 1 review-checklist reminder gap packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
DOCS_README_REL = Path("Documentation/zigux/README.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
DIRECT_ANCHOR_GATE_REL = Path("scripts/zigux/check-phase1-direct-anchor-manifest-gate.py")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    REVIEW_CHECKLIST_REL,
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

REVIEW_CHECKLIST_PHASE1_LINE = (
    "  * if the change touches the shared Phase 1 host-tools closure packet, do "
    "`Documentation/zigux/phase1-closure.md`, "
    "`Documentation/zigux/phase1-host-helper-lane-sequencing.md`, "
    "`Documentation/zigux/README.md`, "
    "`Documentation/zigux/review-checklist.md`, "
    "`scripts/zigux/README.md`, "
    "`scripts/zigux/validate-phase1-closure.py`, "
    "`scripts/zigux/check-phase1-string-review-packet.py`, "
    "`scripts/zigux/check-phase1-direct-owner-markers.py`, "
    "`scripts/zigux/check-phase1-bench.py`, "
    "`scripts/zigux/check-phase1-shared-reminder-packet.py`, "
    "`zigux/tests/README.md`, "
    "`zigux/tests/build.zig`, "
    "`zigux/tests/phase1_host_tools_smoke.zig`, "
    "`.github/workflows/zigux-bootstrap.yml`, "
    "`zigux/tests/fixtures/phase1_helper_manifest.json`, and "
    "`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the "
    "current closed-helper reminder packet, keep `scripts/zigux/check-phase1-route-summary-counts.py`, "
    "`make -C zigux phase1-route-summary`, and `zigux/Makefile` explicit as the adjacent Phase 1 "
    "route-summary evidence for the returned Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, "
    "Phase 12, and Phase 14 route families, while the older validator-first, parity, bench-route, "
    "and replay names stay framed as historical packet members until current `master` materializes "
    "them again?"
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

VALIDATOR_PACKET_WITHOUT_GATE = (
    "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,"
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,"
    "Documentation/zigux/review-checklist.md,scripts/zigux/README.md,"
    "scripts/zigux/check-phase1-string-review-packet.py,"
    "scripts/zigux/check-phase1-direct-owner-markers.py,"
    "scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,"
    "scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,"
    "zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,"
    "zigux/tests/fixtures/phase1_helper_manifest.json`"
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


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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
    review_text = load_text(root, REVIEW_CHECKLIST_REL)
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
            f"{PHASE1_CLOSURE_REL.as_posix()}:current_reminder_packet_with_gate",
            CLOSURE_PACKET_WITH_GATE,
        )
    )

    failures.extend(
        require_once(
            review_text,
            f"{REVIEW_CHECKLIST_REL.as_posix()}:phase1_packet_without_gate",
            REVIEW_CHECKLIST_PHASE1_LINE,
        )
    )
    failures.extend(
        require_absent(
            review_text,
            f"{REVIEW_CHECKLIST_REL.as_posix()}:direct_anchor_gate_absent",
            "`scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`",
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
            f"{VALIDATOR_REL.as_posix()}:direct_anchor_gate_symbol_absent",
            "DIRECT_ANCHOR_MANIFEST_GATE_REL",
        )
    )

    return failures


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
        root / REVIEW_CHECKLIST_REL,
        "# Zigux Review Checklist\n\n"
        f"{REVIEW_CHECKLIST_PHASE1_LINE}\n",
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
            "missing_review_checklist_line",
            lambda root: write_text(
                root / REVIEW_CHECKLIST_REL,
                load_text(root, REVIEW_CHECKLIST_REL).replace(REVIEW_CHECKLIST_PHASE1_LINE + "\n", "", 1),
            ),
        ),
        (
            "review_checklist_reintroduced_gate",
            lambda root: write_text(
                root / REVIEW_CHECKLIST_REL,
                load_text(root, REVIEW_CHECKLIST_REL)
                + "`scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`\n",
            ),
        ),
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
            "docs_reintroduced_gate",
            lambda root: write_text(
                root / DOCS_README_REL,
                load_text(root, DOCS_README_REL)
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
            "validator_packet_with_gate",
            lambda root: write_text(
                root / VALIDATOR_REL,
                load_text(root, VALIDATOR_REL).replace(VALIDATOR_PACKET_WITHOUT_GATE, CLOSURE_PACKET_WITH_GATE),
            ),
        ),
    )

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-review-checklist-reminder-gap-") as tmp:
            root = Path(tmp)
            write_sample_root(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-review-checklist-reminder-gap-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-review-checklist-reminder-gap-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_REVIEW_CHECKLIST_REMINDER_GAP_SELF_TEST=pass")
    print(f"PHASE1_REVIEW_CHECKLIST_REMINDER_GAP_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run embedded self-tests")
    parser.add_argument("--write-sample-root", help="write a current-like sample root")
    args = parser.parse_args()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        print("PHASE1_REVIEW_CHECKLIST_REMINDER_GAP_SAMPLE_ROOT=written")
        return 0

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_REVIEW_CHECKLIST_REMINDER_GAP=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_REVIEW_CHECKLIST_REMINDER_GAP=pass")
    print("PHASE1_REVIEW_CHECKLIST_REMINDER_GAP_SPLIT=current_master")
    print("PHASE1_REVIEW_CHECKLIST_REMINDER_GAP_REQUIRED_FILE_COUNT=7")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
