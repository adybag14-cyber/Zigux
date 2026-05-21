#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
BOOTSTRAP_LEDGER = Path("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")

REQUIRED_FILES = (
    PHASE2_CLOSURE,
    SCRIPTS_README,
    BOOTSTRAP_LEDGER,
)

FILE_MARKERS = {
    PHASE2_CLOSURE: (
        "`scripts/zigux/README.md`",
        "`PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`",
        "The next bounded same-lane follow-through is to keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again.",
        "`PHASE2_NEXT_SAFE_STEP=keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again; if the shared backlog reopens first, start with one smallest truthfulness repair in Documentation/zigux/README.md, zigux/tests/README.md, or the directly coupled shared checker that proves the drift, and keep fixdep-, genksyms-, and kconfig-local follow-through in their dedicated lanes`",
    ),
    SCRIPTS_README: (
        "Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet, `conf_bridge` and `confdata_bridge` helper surfaces, the restored closure-side validator packet, the manifest-backed kconfig fixture roster, the shipped make-wrapper packet, and the surviving Phase 2 alignment guards instead of replaying older missing-route assumptions inside that now-rematerialized toolchain packet",
        "`Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`",
        "if future work widens the installer or direct cross-route packet, update this reminder packet only after rereading those direct current-`master` surfaces together with the live toolchain policy, manifest-backed kconfig fixture roster, the fixture-backed Phase 2 tool packet, and shipped make-wrapper packet so the scripts-root summary stays aligned with the now-returned Phase 2 evidence",
    ),
    BOOTSTRAP_LEDGER: (
        "25. `docs(zigux): reopen and close broadened Phase 2 tranche`",
        "- `Documentation/zigux/phase2-closure.md`",
        "- `Documentation/zigux/artifact-diff.md`",
        "- `scripts/zigux/README.md`",
        "- `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`",
    ),
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write_text(
        root / PHASE2_CLOSURE,
        "\n".join(
            (
                "# Phase 2 Closure",
                "Current packet:",
                *FILE_MARKERS[PHASE2_CLOSURE],
                "",
            )
        ),
    )
    write_text(
        root / SCRIPTS_README,
        "\n".join(
            (
                "# scripts/zigux",
                "Phase 2",
                *FILE_MARKERS[SCRIPTS_README],
                "",
            )
        ),
    )
    write_text(
        root / BOOTSTRAP_LEDGER,
        "\n".join(
            (
                "# Zigux Alpha Bootstrap Commit Ledger",
                "## Commit Train",
                *FILE_MARKERS[BOOTSTRAP_LEDGER],
                "",
            )
        ),
    )


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    for rel_path in REQUIRED_FILES:
        abs_path = root / rel_path
        if not abs_path.is_file():
            issues.append(f"missing_file:{rel_path.as_posix()}")
            continue

        text = read_text(abs_path)
        for marker in FILE_MARKERS[rel_path]:
            if marker not in text:
                issues.append(f"missing_marker:{rel_path.as_posix()}:{marker}")

    return issues


def run_self_test() -> int:
    cases_run = 0

    with tempfile.TemporaryDirectory(prefix="phase2_broadened_tranche_alignment_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        if collect_issues(root):
            raise SystemExit("phase2-broadened-tranche:self-test:good_tree")
        cases_run += 1

        build_sample_root(root)
        (root / PHASE2_CLOSURE).unlink()
        issues = collect_issues(root)
        expected = f"missing_file:{PHASE2_CLOSURE.as_posix()}"
        if issues != [expected]:
            raise SystemExit("phase2-broadened-tranche:self-test:missing_closure")
        cases_run += 1

        build_sample_root(root)
        write_text(root / PHASE2_CLOSURE, "# Phase 2 Closure\n")
        issues = collect_issues(root)
        expected_prefix = f"missing_marker:{PHASE2_CLOSURE.as_posix()}:"
        if not issues or not all(issue.startswith(expected_prefix) for issue in issues):
            raise SystemExit("phase2-broadened-tranche:self-test:closure_markers")
        cases_run += 1

        build_sample_root(root)
        write_text(root / SCRIPTS_README, "# scripts/zigux\n")
        issues = collect_issues(root)
        expected_prefix = f"missing_marker:{SCRIPTS_README.as_posix()}:"
        if not issues or not all(issue.startswith(expected_prefix) for issue in issues):
            raise SystemExit("phase2-broadened-tranche:self-test:scripts_markers")
        cases_run += 1

        build_sample_root(root)
        write_text(root / BOOTSTRAP_LEDGER, "# Zigux Alpha Bootstrap Commit Ledger\n")
        issues = collect_issues(root)
        expected_prefix = f"missing_marker:{BOOTSTRAP_LEDGER.as_posix()}:"
        if not issues or not all(issue.startswith(expected_prefix) for issue in issues):
            raise SystemExit("phase2-broadened-tranche:self-test:ledger_markers")
        cases_run += 1

        build_sample_root(root)
        (root / BOOTSTRAP_LEDGER).unlink()
        issues = collect_issues(root)
        expected = f"missing_file:{BOOTSTRAP_LEDGER.as_posix()}"
        if issues != [expected]:
            raise SystemExit("phase2-broadened-tranche:self-test:missing_ledger")
        cases_run += 1

    print("PHASE2_BROADENED_TRANCHE_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_BROADENED_TRANCHE_ALIGNMENT_SELF_TEST_CASE_COUNT={cases_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the shared Lane 25 Phase 2 closure, scripts-root summary, "
            "and bootstrap ledger stay aligned around the broadened tranche."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root for focused validation",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        print(f"PHASE2_BROADENED_TRANCHE_ALIGNMENT_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    issues = collect_issues(args.root)
    if issues:
        print("PHASE2_BROADENED_TRANCHE_ALIGNMENT=fail")
        print("PHASE2_BROADENED_TRANCHE_ALIGNMENT_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_BROADENED_TRANCHE_ALIGNMENT_ISSUES_END")
        return 1

    print("PHASE2_BROADENED_TRANCHE_ALIGNMENT=pass")
    print(f"PHASE2_BROADENED_TRANCHE_ALIGNMENT_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE2_BROADENED_TRANCHE_ALIGNMENT_MARKER_COUNT="
        f"{sum(len(markers) for markers in FILE_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())