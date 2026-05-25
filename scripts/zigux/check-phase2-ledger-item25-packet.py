#!/usr/bin/env python3
"""Guard the bounded Lane 25 bootstrap-ledger item-25 packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
ARTIFACT_DIFF_NOTE = Path("Documentation/zigux/artifact-diff.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
BOOTSTRAP_LEDGER = Path("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")

PHASE2_CLOSURE_MARKERS = (
    "- `Documentation/zigux/artifact-diff.md`",
    "- `scripts/zigux/README.md`",
    "The next bounded same-lane follow-through is to keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again.",
)

ARTIFACT_DIFF_MARKERS = (
    "## Current Phase 2 use",
    "Phase 2 still routes focused host-tool fixture comparisons through the same helper family when validating `fixdep`, `genksyms`, and the kconfig bridge packet.",
)

SCRIPTS_README_MARKERS = (
    "Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet, `conf_bridge` and `confdata_bridge` helper surfaces, the restored closure-side validator packet, the manifest-backed kconfig fixture roster, the shipped make-wrapper packet, and the surviving Phase 2 alignment guards instead of replaying older missing-route assumptions inside that now-rematerialized toolchain packet",
    "`Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, `make -C zigux phase2`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set",
    "if future work widens the installer or direct cross-route packet, update this reminder packet only after rereading those direct current-`master` surfaces together with the live toolchain policy, manifest-backed kconfig fixture roster, the fixture-backed Phase 2 tool packet, and shipped make-wrapper packet so the scripts-root summary stays aligned with the now-returned Phase 2 evidence",
)

BOOTSTRAP_LEDGER_MARKERS = (
    "25. `docs(zigux): reopen and close broadened Phase 2 tranche`",
    "- `Documentation/zigux/phase2-closure.md`",
    "- `Documentation/zigux/artifact-diff.md`",
    "- `scripts/zigux/README.md`",
    "- `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`",
    "- This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.",
    "- Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.",
    "- Keep this ledger authoritative for the reviewed bootstrap commit train through item 25 only.",
    "- Do not backfill later release-planning state here as synthetic commit history when the live repo already exposes the active PMO packet directly.",
    "- `Documentation/zigux/README.md`",
    "- `Documentation/zigux/phase12-release-sequencing.md`",
    "- `Documentation/zigux/phase12-release-readiness-survey.md`",
    "- `Documentation/zigux/phase12-release-closure-checklist.md`",
    "- `Documentation/zigux/phase12-release-coordination-matrix.md`",
    "- `Documentation/zigux/phase14-release-boundary-survey.md`",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_occurrences(text: str, marker: str) -> int:
    return text.count(marker)


def collect_marker_issues(
    text: str,
    markers: tuple[str, ...],
    missing_code: str,
    duplicate_code: str,
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_occurrences(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(
        collect_marker_issues(
            read_text(root / PHASE2_CLOSURE),
            PHASE2_CLOSURE_MARKERS,
            "PHASE2_CLOSURE_MARKER_MISSING",
            "PHASE2_CLOSURE_MARKER_DUPLICATED",
        )
    )
    issues.extend(
        collect_marker_issues(
            read_text(root / ARTIFACT_DIFF_NOTE),
            ARTIFACT_DIFF_MARKERS,
            "ARTIFACT_DIFF_MARKER_MISSING",
            "ARTIFACT_DIFF_MARKER_DUPLICATED",
        )
    )
    issues.extend(
        collect_marker_issues(
            read_text(root / SCRIPTS_README),
            SCRIPTS_README_MARKERS,
            "SCRIPTS_README_MARKER_MISSING",
            "SCRIPTS_README_MARKER_DUPLICATED",
        )
    )
    issues.extend(
        collect_marker_issues(
            read_text(root / BOOTSTRAP_LEDGER),
            BOOTSTRAP_LEDGER_MARKERS,
            "BOOTSTRAP_LEDGER_MARKER_MISSING",
            "BOOTSTRAP_LEDGER_MARKER_DUPLICATED",
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    print("PHASE2_LEDGER_ITEM25_PACKET=fail")
    for code, detail in issues:
        print(f"{code}={detail}")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(root / PHASE2_CLOSURE, "\n".join(PHASE2_CLOSURE_MARKERS) + "\n")
    write_text(root / ARTIFACT_DIFF_NOTE, "\n".join(ARTIFACT_DIFF_MARKERS) + "\n")
    write_text(root / SCRIPTS_README, "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(root / BOOTSTRAP_LEDGER, "\n".join(BOOTSTRAP_LEDGER_MARKERS) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    marker_total = (
        len(PHASE2_CLOSURE_MARKERS)
        + len(ARTIFACT_DIFF_MARKERS)
        + len(SCRIPTS_README_MARKERS)
        + len(BOOTSTRAP_LEDGER_MARKERS)
    )
    file_total = 4
    checks_run = 0
    expected_case_count = 1 + marker_total + file_total

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_ledger_item25_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for rel_path, markers, code in (
            (PHASE2_CLOSURE, PHASE2_CLOSURE_MARKERS, "PHASE2_CLOSURE_MARKER_MISSING"),
            (ARTIFACT_DIFF_NOTE, ARTIFACT_DIFF_MARKERS, "ARTIFACT_DIFF_MARKER_MISSING"),
            (SCRIPTS_README, SCRIPTS_README_MARKERS, "SCRIPTS_README_MARKER_MISSING"),
            (BOOTSTRAP_LEDGER, BOOTSTRAP_LEDGER_MARKERS, "BOOTSTRAP_LEDGER_MARKER_MISSING"),
        ):
            for marker in markers:
                build_sample_root(root)
                path = root / rel_path
                path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
                issues = collect_issues(root)
                assert (code, marker) in issues
                checks_run += 1

        for rel_path in (PHASE2_CLOSURE, ARTIFACT_DIFF_NOTE, SCRIPTS_README, BOOTSTRAP_LEDGER):
            build_sample_root(root)
            (root / rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert checks_run == expected_case_count
    print("PHASE2_LEDGER_ITEM25_PACKET_SELF_TEST=pass")
    print(f"PHASE2_LEDGER_ITEM25_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a focused passing sample root and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        sample_root = args.write_sample_root.resolve()
        build_sample_root(sample_root)
        print(f"PHASE2_LEDGER_ITEM25_PACKET_SAMPLE_ROOT={sample_root}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_LEDGER_ITEM25_PACKET=pass")
    print("PHASE2_LEDGER_ITEM25_PACKET_REQUIRED_PATH_COUNT=4")
    print(
        "PHASE2_LEDGER_ITEM25_PACKET_MARKER_COUNT="
        f"{len(PHASE2_CLOSURE_MARKERS) + len(ARTIFACT_DIFF_MARKERS) + len(SCRIPTS_README_MARKERS) + len(BOOTSTRAP_LEDGER_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
