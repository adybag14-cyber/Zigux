#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=rollback_trigger_gap

Fail-closed checker for the current Phase 14 rollback-trigger gap survey.

This packet stays intentionally narrow. It validates that the exact trigger
catalog is still published in the shared smoke note and rollback-threshold
sequencing checker, while the adjacent shared reminder notes still stop short
of republishing that catalog. If the surrounding notes later gain the exact
trigger heading, this gap note should be revisited instead of drifting forward
silently.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

MARKER = "PHASE14_CHECK_PACKET=rollback_trigger_gap"

SMOKE_NOTE_PATH = Path("Documentation/zigux/phase14-end-to-end-smoke-survey.md")
SEQUENCING_CHECKER_PATH = Path(
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py"
)
PRODUCTIZATION_GAP_PATH = Path(
    "Documentation/zigux/phase14-productization-gap-survey.md"
)
RELEASE_BOUNDARY_PATH = Path("Documentation/zigux/phase14-release-boundary-survey.md")
ATTACHED_TOOLCHAIN_PATH = Path(
    "Documentation/zigux/phase14-attached-toolchain-guidance-gap.md"
)
GAP_NOTE_PATH = Path("Documentation/zigux/phase14-rollback-trigger-gap-survey.md")

TRIGGER_HEADING = "automatic return-to-blocked triggers:"
TRIGGER_MARKERS = [
    "recovered documentation packet drift",
    "route-checker-versus-reminder-surface drift",
    "tests-root-checker-versus-reminder-surface drift",
    "validator-versus-reminder-surface drift",
    "workqueue-boundary-shard drift",
    "ring-buffer-survey drift",
    "wrapper-route drift",
    "build-side exact-readback-gap drift",
    "broader executable-layer exact-readback-gap drift",
    "attached-toolchain guidance drift inside the shared smoke note",
]

GAP_NOTE_MARKERS = [
    "- `PHASE14_ROLLBACK_TRIGGER_GAP=present`",
    "- `PHASE14_ROLLBACK_TRIGGER_GAP_KIND=shared_reminder_trigger_catalog_split`",
    "- `PHASE14_ROLLBACK_TRIGGER_GAP_SCOPE=shared_smoke_packet_only`",
    "- `PHASE14_ROLLBACK_TRIGGER_GAP_STATUS_BUCKET=study_only`",
    "- `PHASE14_ROLLBACK_TRIGGER_GAP_OWNER=Repo Tooling Pod`",
    "- `Documentation/zigux/phase14-productization-gap-survey.md`",
    "- `Documentation/zigux/phase14-release-boundary-survey.md`",
    "- `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`",
    "do not yet publish that exact trigger catalog",
    "points back to `Documentation/zigux/phase14-end-to-end-smoke-survey.md` and",
    "`scripts/zigux/check-phase14-rollback-threshold-sequencing.py` as the trigger",
]

ADJACENT_REMINDER_MARKERS = [
    "phase14-validate",
    "study-only",
]


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def source_text() -> str:
    return Path(__file__).read_text(encoding="utf-8")


def require_present(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"missing marker in {rel.as_posix()}: {marker}")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    if MARKER not in source_text():
        errors.append("checker marker missing from checker source")

    required = [
        SMOKE_NOTE_PATH,
        SEQUENCING_CHECKER_PATH,
        PRODUCTIZATION_GAP_PATH,
        RELEASE_BOUNDARY_PATH,
        ATTACHED_TOOLCHAIN_PATH,
        GAP_NOTE_PATH,
    ]
    for rel in required:
        if not (root / rel).exists():
            errors.append(f"missing file: {rel.as_posix()}")
    if errors:
        return errors

    smoke_note = read_text(root, SMOKE_NOTE_PATH)
    sequencing_checker = read_text(root, SEQUENCING_CHECKER_PATH)
    productization_gap = read_text(root, PRODUCTIZATION_GAP_PATH)
    release_boundary = read_text(root, RELEASE_BOUNDARY_PATH)
    attached_toolchain = read_text(root, ATTACHED_TOOLCHAIN_PATH)
    gap_note = read_text(root, GAP_NOTE_PATH)

    if TRIGGER_HEADING not in smoke_note:
        errors.append(f"missing trigger heading in {SMOKE_NOTE_PATH.as_posix()}")
    require_present(errors, SMOKE_NOTE_PATH, smoke_note, TRIGGER_MARKERS)
    require_present(errors, SEQUENCING_CHECKER_PATH, sequencing_checker, TRIGGER_MARKERS)
    require_present(errors, GAP_NOTE_PATH, gap_note, GAP_NOTE_MARKERS)

    for rel, text in [
        (PRODUCTIZATION_GAP_PATH, productization_gap),
        (RELEASE_BOUNDARY_PATH, release_boundary),
        (ATTACHED_TOOLCHAIN_PATH, attached_toolchain),
    ]:
        require_present(errors, rel, text, ADJACENT_REMINDER_MARKERS)
        if TRIGGER_HEADING in text:
            errors.append(
                f"gap note is stale because {rel.as_posix()} now republishes the trigger heading"
            )

    return errors


def fixture_smoke_note() -> str:
    lines = [
        "# Phase 14 End-to-End Smoke Survey",
        "",
        "  * automatic return-to-blocked triggers:",
    ]
    lines.extend(f"    * {marker}" for marker in TRIGGER_MARKERS)
    return "\n".join(lines) + "\n"


def fixture_sequencing_checker() -> str:
    lines = [
        "#!/usr/bin/env python3",
        "ROLLBACK_TRIGGER_MARKERS = [",
    ]
    lines.extend(f'    "{marker}",' for marker in TRIGGER_MARKERS)
    lines.append("]")
    return "\n".join(lines) + "\n"


def fixture_productization_gap() -> str:
    return """# Phase 14 Productization Gap Survey

Given the roadmap, the correct Phase 14 posture remains study-only and wrapper-first.
The current route split still centers `phase14-validate`.
"""


def fixture_release_boundary() -> str:
    return """# Phase 14 Release Boundary Survey

- current shared-smoke route: `make -C zigux phase14-validate`
- release posture stays study-only
"""


def fixture_attached_toolchain() -> str:
    return """# Phase 14 Attached Toolchain Guidance Gap

- the readable `zigux/Makefile` now exposes `phase14-validate`
- the packet remains study-only and reviewability-first
"""


def fixture_gap_note() -> str:
    return """# Phase 14 Rollback-Trigger Gap Survey

## Status

- `PHASE14_ROLLBACK_TRIGGER_GAP=present`
- `PHASE14_ROLLBACK_TRIGGER_GAP_KIND=shared_reminder_trigger_catalog_split`
- `PHASE14_ROLLBACK_TRIGGER_GAP_SCOPE=shared_smoke_packet_only`
- `PHASE14_ROLLBACK_TRIGGER_GAP_STATUS_BUCKET=study_only`
- `PHASE14_ROLLBACK_TRIGGER_GAP_OWNER=Repo Tooling Pod`

## Current bounded gap

- `Documentation/zigux/phase14-productization-gap-survey.md`
- `Documentation/zigux/phase14-release-boundary-survey.md`
- `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`

These notes do not yet publish that exact trigger catalog.

## Smallest honest same-lane conclusion

Either the next reminder surface points back to `Documentation/zigux/phase14-end-to-end-smoke-survey.md` and
`scripts/zigux/check-phase14-rollback-threshold-sequencing.py` as the trigger
authority, or it republishes the exact same trigger list without widening the delivery claim.
"""


def write_sample_root(root: Path) -> None:
    write(root, SMOKE_NOTE_PATH, fixture_smoke_note())
    write(root, SEQUENCING_CHECKER_PATH, fixture_sequencing_checker())
    write(root, PRODUCTIZATION_GAP_PATH, fixture_productization_gap())
    write(root, RELEASE_BOUNDARY_PATH, fixture_release_boundary())
    write(root, ATTACHED_TOOLCHAIN_PATH, fixture_attached_toolchain())
    write(root, GAP_NOTE_PATH, fixture_gap_note())


def run_self_test() -> int:
    cases = 5
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_sample_root(root)
        errors = check(root)
        if errors:
            print("PHASE14_ROLLBACK_TRIGGER_GAP_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        write(root, GAP_NOTE_PATH, fixture_gap_note().replace(
            "- `PHASE14_ROLLBACK_TRIGGER_GAP_OWNER=Repo Tooling Pod`\n", "", 1
        ))
        if not any("PHASE14_ROLLBACK_TRIGGER_GAP_OWNER=Repo Tooling Pod" in error for error in check(root)):
            print("PHASE14_ROLLBACK_TRIGGER_GAP_SELF_TEST=fail")
            print("expected missing owner marker failure")
            return 1

        write(root, GAP_NOTE_PATH, fixture_gap_note())
        write(root, SMOKE_NOTE_PATH, fixture_smoke_note().replace(
            "    * ring-buffer-survey drift\n", "", 1
        ))
        if not any("ring-buffer-survey drift" in error for error in check(root)):
            print("PHASE14_ROLLBACK_TRIGGER_GAP_SELF_TEST=fail")
            print("expected missing trigger marker failure")
            return 1

        write(root, SMOKE_NOTE_PATH, fixture_smoke_note())
        write(root, RELEASE_BOUNDARY_PATH, fixture_release_boundary() + "\n  * automatic return-to-blocked triggers:\n")
        if not any("gap note is stale" in error for error in check(root)):
            print("PHASE14_ROLLBACK_TRIGGER_GAP_SELF_TEST=fail")
            print("expected adjacent reminder trigger-heading failure")
            return 1

        write(root, RELEASE_BOUNDARY_PATH, fixture_release_boundary())
        write(root, ATTACHED_TOOLCHAIN_PATH, fixture_attached_toolchain().replace(
            "study-only", "reviewability-first", 1
        ))
        if not any("study-only" in error for error in check(root)):
            print("PHASE14_ROLLBACK_TRIGGER_GAP_SELF_TEST=fail")
            print("expected adjacent reminder posture marker failure")
            return 1

    print("PHASE14_ROLLBACK_TRIGGER_GAP_SELF_TEST=pass")
    print(f"PHASE14_ROLLBACK_TRIGGER_GAP_SELF_TEST_CASE_COUNT={cases}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", type=Path)
    parser.add_argument("--write-sample-root", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    root = args.root if args.root is not None else Path.cwd()
    errors = check(root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("phase14 rollback-trigger gap survey validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
