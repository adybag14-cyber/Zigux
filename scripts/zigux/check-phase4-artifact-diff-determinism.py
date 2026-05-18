#!/usr/bin/env python3
"""Guard the current Phase 4 artifact-diff determinism handoff against repo reality."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

PHASE4_NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
DOCS_ROOT = Path("Documentation/zigux/README.md")
SCRIPTS_ROOT = Path("scripts/zigux/README.md")
REPO_WARNING = Path("scripts/zigux/check-phase4-repo-reality-warning.py")
SELF_PATH = Path("scripts/zigux/check-phase4-artifact-diff-determinism.py")

HISTORICAL_ARTIFACT_DIFF_PACKET = (
    "Documentation/zigux/artifact-diff.md",
    "Documentation/zigux/phase4-gate-evidence.md",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "scripts/zigux/validate-phase4.py",
)

CURRENT_DIRECT_PACKET = (
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
)

NOTE_MARKERS = (
    "The broader Phase 4 validator, lab-matrix, and local-only perf companions are still repo-reality gaps in this run",
    "Historical broader validator and owner-map packet members:",
    "host-side artifact-diff tooling contract",
    "historical provenance, not current-head proof",
)

DOCS_ROOT_MARKERS = (
    "Phase 4 notes - `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, and `scripts/zigux/check-phase4-reversible-delivery-pins.py` now keep the current direct-readback rollback packet reviewable from the docs root while the broader validator, lab-matrix, local-only perf, and bitmap-diff companions remain repo-reality gaps on current `master`.",
    "scripts/zigux/validate-phase4.py",
    "host-side artifact-diff tooling contract",
)

SCRIPTS_ROOT_MARKERS = (
    "Phase 4 flow - the current shared rollback reminder packet is kept reviewable through the directly readable docs-root, tests-root, and scripts-root surfaces while the broader validator, lab-matrix, and local-only perf packet is currently a repo-reality gap on `master`, so this note should stay aligned with the direct-readback warning instead of treating that older packet as freshly present",
    "host-side artifact-diff contract references",
    "scripts/zigux/validate-phase4.py",
)

REPO_WARNING_MARKERS = (
    "\"scripts/zigux/validate-phase4.py\"",
    "MISSING_BROADER_PACKET",
    "broader packet entries are now present and the repo-reality warning must be narrowed",
)

ABSENT_HISTORICAL_MEMBERS = (
    "Documentation/zigux/artifact-diff.md",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/validate-phase4.py",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def read(root: Path, rel: Path) -> str:
    try:
        return (root / rel).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing required file: {rel.as_posix()}") from exc


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required fragments: {missing}")


def require_paths_listed(text: str, paths: tuple[str, ...], label: str) -> None:
    missing = [path for path in paths if f"`{path}`" not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required path markers: {missing}")


def require_current_repo_reality(root: Path) -> None:
    if not (root / SELF_PATH).exists():
        raise RuntimeError(
            f"current tree is missing the determinism handoff checker: {SELF_PATH.as_posix()}"
        )

    present = [path for path in ABSENT_HISTORICAL_MEMBERS if (root / Path(path)).exists()]
    if present:
        raise RuntimeError(
            "historical artifact-diff packet members returned on current master and this "
            f"handoff must be narrowed: {present}"
        )


def check(root: Path) -> None:
    note = read(root, PHASE4_NOTE)
    docs_root = read(root, DOCS_ROOT)
    scripts_root = read(root, SCRIPTS_ROOT)
    repo_warning = read(root, REPO_WARNING)

    require_markers(note, NOTE_MARKERS, PHASE4_NOTE.as_posix())
    require_paths_listed(note, HISTORICAL_ARTIFACT_DIFF_PACKET, PHASE4_NOTE.as_posix())
    require_paths_listed(note, CURRENT_DIRECT_PACKET, PHASE4_NOTE.as_posix())
    require_markers(docs_root, DOCS_ROOT_MARKERS, DOCS_ROOT.as_posix())
    require_markers(scripts_root, SCRIPTS_ROOT_MARKERS, SCRIPTS_ROOT.as_posix())
    require_markers(repo_warning, REPO_WARNING_MARKERS, REPO_WARNING.as_posix())
    require_current_repo_reality(root)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_root(root: Path) -> None:
    write(
        root / PHASE4_NOTE,
        """# Phase 4 Reversible Delivery Evidence

The broader Phase 4 validator, lab-matrix, and local-only perf companions are still repo-reality gaps in this run, so the older host-side artifact-diff tooling contract remains historical provenance, not current-head proof.

Current direct-readback packet members:
  * `Documentation/zigux/phase4-reversible-delivery-evidence.md`
  * `Documentation/zigux/review-checklist.md`
  * `zigux/tests/README.md`
  * `scripts/zigux/check-phase4-repo-reality-warning.py`
  * `scripts/zigux/check-phase4-reversible-delivery-pins.py`

Historical broader validator and owner-map packet members:
  * `Documentation/zigux/artifact-diff.md`
  * `Documentation/zigux/phase4-gate-evidence.md`
  * `scripts/zigux/artifact_diff.py`
  * `scripts/zigux/check-artifact-diff-contract.py`
  * `scripts/zigux/check-phase4-artifact-diff-determinism.py`
  * `scripts/zigux/validate-phase4.py`
""",
    )
    write(
        root / DOCS_ROOT,
        """# Zigux Documentation

Phase 4 notes - `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, and `scripts/zigux/check-phase4-reversible-delivery-pins.py` now keep the current direct-readback rollback packet reviewable from the docs root while the broader validator, lab-matrix, local-only perf, and bitmap-diff companions remain repo-reality gaps on current `master`.
  * treat `Documentation/zigux/phase4-gate-evidence.md`, `scripts/zigux/validate-phase4.py`, and the older host-side artifact-diff tooling contract as historical or missing packet members until a same-family lane republishes them.
""",
    )
    write(
        root / SCRIPTS_ROOT,
        """# scripts/zigux

## Phase 4

- Phase 4 flow - the current shared rollback reminder packet is kept reviewable through the directly readable docs-root, tests-root, and scripts-root surfaces while the broader validator, lab-matrix, and local-only perf packet is currently a repo-reality gap on `master`, so this note should stay aligned with the direct-readback warning instead of treating that older packet as freshly present
- `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, and `scripts/zigux/check-phase4-reversible-delivery-pins.py` keep the current direct-readback rollback-owner wording, the host-side artifact-diff contract references, the broader-packet warning, and the pending shared-CI perf-promotion posture explicit, and this scripts-root note should mirror that same present-current-master posture
- authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase4.py`, so treat those broader validator, lab-matrix, and local-only perf surfaces as historical packet members or stale provenance until a same-lane republish makes them directly readable again
""",
    )
    write(
        root / REPO_WARNING,
        """#!/usr/bin/env python3
MISSING_BROADER_PACKET = (
    "Documentation/zigux/phase4-gate-evidence.md",
    "scripts/zigux/validate-phase4.py",
)
ERROR_TEXT = "broader packet entries are now present and the repo-reality warning must be narrowed"
""",
    )
    write(root / SELF_PATH, "# current checker\n")
    write(root / Path("Documentation/zigux/review-checklist.md"), "# checklist\n")
    write(root / Path("zigux/tests/README.md"), "# tests guide\n")
    write(root / Path("scripts/zigux/check-phase4-reversible-delivery-pins.py"), "# pins\n")


def self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase4-artifact-diff-history-") as tmp:
        root = Path(tmp)
        fixture_root(root)
        check(root)
        cases += 1

        write(
            root / PHASE4_NOTE,
            read(root, PHASE4_NOTE).replace(
                "`scripts/zigux/check-artifact-diff-contract.py`",
                "`scripts/zigux/not-the-right-checker.py`",
            ),
        )
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected historical packet drift to fail")

        fixture_root(root)
        write(
            root / DOCS_ROOT,
            read(root, DOCS_ROOT).replace(
                "host-side artifact-diff tooling contract",
                "other tooling contract",
            ),
        )
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected docs-root drift to fail")

        fixture_root(root)
        write(
            root / SCRIPTS_ROOT,
            read(root, SCRIPTS_ROOT).replace(
                "host-side artifact-diff contract references",
                "other contract references",
            ),
        )
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected scripts-root drift to fail")

        fixture_root(root)
        write(
            root / Path("scripts/zigux/artifact_diff.py"),
            "# republished helper\n",
        )
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected republished historical member to fail")

        fixture_root(root)
        write(
            root / REPO_WARNING,
            read(root, REPO_WARNING).replace(
                "\"scripts/zigux/validate-phase4.py\"",
                "\"scripts/zigux/not-the-right-file.py\"",
            ),
        )
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected repo-warning drift to fail")

    print("PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass")
    print(f"PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT={cases}")


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    try:
        check(args.root.resolve())
    except RuntimeError as exc:
        print(f"PHASE4_ARTIFACT_DIFF_DETERMINISM=fail: {exc}", file=sys.stderr)
        return 1
    print("PHASE4_ARTIFACT_DIFF_DETERMINISM=pass")
    print(
        f"PHASE4_ARTIFACT_DIFF_DETERMINISM_HISTORICAL_PACKET_MEMBERS={len(HISTORICAL_ARTIFACT_DIFF_PACKET)}"
    )
    print(
        f"PHASE4_ARTIFACT_DIFF_DETERMINISM_CURRENT_DIRECT_MEMBERS={len(CURRENT_DIRECT_PACKET)}"
    )
    print(
        f"PHASE4_ARTIFACT_DIFF_DETERMINISM_ABSENT_HISTORICAL_MEMBERS={len(ABSENT_HISTORICAL_MEMBERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
