#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=rollback_threshold_sequencing

Fail-closed checker for the current Phase 14 rollback-threshold packet.

This checker stays inside the rollback-automation lane. It validates that the
shared smoke reminder surfaces still agree on the current study-only rollback
contract and on the current repo-reality split where the Makefile is readable
but still does not ship any `phase14-*` wrapper targets.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

MARKER = "PHASE14_CHECK_PACKET=rollback_threshold_sequencing"
ROLLBACK_OWNER = "Repo Tooling Pod"
STATUS_BUCKET = "study_only"

SMOKE_NOTE_PATH = Path("Documentation/zigux/phase14-end-to-end-smoke-survey.md")
RELEASE_BOUNDARY_PATH = Path("Documentation/zigux/phase14-release-boundary-survey.md")
PRODUCTIZATION_GAP_PATH = Path("Documentation/zigux/phase14-productization-gap-survey.md")
CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
MAKEFILE_PATH = Path("zigux/Makefile")

ROLLBACK_THRESHOLD_MARKER = (
    "  * rollback threshold: `0` tolerated same-packet drifts across the "
    "recovered documentation packet, the blob-readable validator path, the "
    "readable current Makefile body, the directly readable workqueue boundary "
    "shard, and the still-missing executable packet members"
)
ROLLBACK_FALLBACK_MARKER = (
    "  * fallback path: keep this shared smoke lane aligned with the current "
    "gap notes until the broader shared reminder packet stops treating the "
    "current Makefile body as if it still shipped the older `phase14-*` "
    "routes, and until the missing executable packet members above return "
    "through exact current-`master` contents readback; once they do, rerun the "
    "packet-local commands below before restoring any stronger validator-first "
    "claim"
)
ROLLBACK_TRIGGER_MARKERS = [
    "    * recovered documentation packet drift",
    "    * validator-versus-reminder-surface drift",
    "    * workqueue-boundary-shard drift",
    "    * executable packet member drift",
    "    * anchor-local reminder drift",
    "    * attached-toolchain guidance drift inside the shared smoke note",
]
ATTACHED_TOOLCHAIN_EXAMPLES = [
    "    * `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-smoke`",
    "    * `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-test`",
    "    * `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14`",
]
MAKEFILE_ROUTE_ABSENCE_MARKER = (
    "`phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets"
)
RETURNED_PHASE4_ROUTE_MARKERS = [
    "`phase4-validate`",
    "`phase4-test`",
    "`phase4`",
]
PRODUCTIZATION_GAP_MARKERS = [
    "Given the roadmap, the correct Phase 14 posture remains study-only and wrapper-first.",
    "The higher-value same-lane task is reminder-surface truthfulness:",
    "the blob-readable validator surface",
    "the current Makefile posture",
]
CHECKLIST_MARKERS = [
    "if the change touches the shared Phase 14 smoke packet",
    "keep `zigux/Makefile` framed as a readable non-owner surface",
    "while still omitting all `phase14-*` targets",
]
MAKEFILE_PRESENT_ROUTE_MARKERS = [
    "phase3-validate:",
    "phase4-validate:",
    "phase4-test:",
    "phase4: phase4-validate phase4-test",
    "phase6-base64-test:",
    "phase8-validate:",
    "phase10-validate:",
    "phase12-smoke:",
]
MAKEFILE_ABSENT_ROUTE_MARKERS = [
    "phase14-validate:",
    "phase14-smoke:",
    "phase14-test:",
    "phase14: phase14-validate phase14-smoke phase14-test",
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


def require_absent(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            errors.append(f"unexpected stale marker in {rel.as_posix()}: {marker}")


def check(root: Path) -> list[str]:
    errors: list[str] = []

    if MARKER not in source_text():
        errors.append("checker marker missing from checker source")

    required_paths = [
        SMOKE_NOTE_PATH,
        RELEASE_BOUNDARY_PATH,
        PRODUCTIZATION_GAP_PATH,
        CHECKLIST_PATH,
        MAKEFILE_PATH,
    ]
    for rel in required_paths:
        if not (root / rel).exists():
            errors.append(f"missing file: {rel.as_posix()}")
    if errors:
        return errors

    smoke_note = read_text(root, SMOKE_NOTE_PATH)
    require_present(
        errors,
        SMOKE_NOTE_PATH,
        smoke_note,
        [
            "  * `PHASE14_STAY_IN_C_BOUNDARY=explicit`",
            "  * `PHASE14_EXECUTABLE_PACKET_READBACK=partial`",
            "  * `PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE=packet_local_only`",
            f"  * rollback owner: `{ROLLBACK_OWNER}`",
            f"  * status bucket: `{STATUS_BUCKET}`",
            ROLLBACK_THRESHOLD_MARKER,
            ROLLBACK_FALLBACK_MARKER,
            "  * automatic return-to-blocked triggers:",
            *ROLLBACK_TRIGGER_MARKERS,
            *ATTACHED_TOOLCHAIN_EXAMPLES,
            MAKEFILE_ROUTE_ABSENCE_MARKER,
            *RETURNED_PHASE4_ROUTE_MARKERS,
            "the next honest same-lane follow-through is reminder-surface truthfulness, not a validator-local exact-line sync against `phase14-validate`",
        ],
    )

    release_boundary = read_text(root, RELEASE_BOUNDARY_PATH)
    require_present(
        errors,
        RELEASE_BOUNDARY_PATH,
        release_boundary,
        [
            MAKEFILE_ROUTE_ABSENCE_MARKER,
            *RETURNED_PHASE4_ROUTE_MARKERS,
            "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`",
            "- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`",
        ],
    )

    productization_gap = read_text(root, PRODUCTIZATION_GAP_PATH)
    require_present(
        errors,
        PRODUCTIZATION_GAP_PATH,
        productization_gap,
        PRODUCTIZATION_GAP_MARKERS,
    )

    checklist = read_text(root, CHECKLIST_PATH)
    require_present(errors, CHECKLIST_PATH, checklist, CHECKLIST_MARKERS)

    makefile = read_text(root, MAKEFILE_PATH)
    require_present(errors, MAKEFILE_PATH, makefile, MAKEFILE_PRESENT_ROUTE_MARKERS)
    require_absent(errors, MAKEFILE_PATH, makefile, MAKEFILE_ABSENT_ROUTE_MARKERS)

    return errors


def fixture_smoke_note() -> str:
    return "\n".join(
        [
            "# Phase 14 End-to-End Smoke Survey",
            "  * `PHASE14_EXECUTABLE_PACKET_READBACK=partial`",
            "  * `PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE=packet_local_only`",
            "  * `PHASE14_STAY_IN_C_BOUNDARY=explicit`",
            f"  * rollback owner: `{ROLLBACK_OWNER}`",
            f"  * status bucket: `{STATUS_BUCKET}`",
            ROLLBACK_THRESHOLD_MARKER,
            ROLLBACK_FALLBACK_MARKER,
            "  * automatic return-to-blocked triggers:",
            *ROLLBACK_TRIGGER_MARKERS,
            "  * attached-toolchain fallback examples for this note's bounded smoke routes:",
            *ATTACHED_TOOLCHAIN_EXAMPLES,
            (
                "    * `zigux/Makefile` is directly readable again through the current "
                "contents path, and its live body now exposes the shipped Phase 2 "
                "toolchain and kbuild routes together with the bounded `phase3-validate`, "
                "`phase3`, `phase4-validate`, `phase4-test`, `phase4`, "
                "`phase6-base64-test`, `phase6-base64-perf`, `phase6-bsearch-test`, "
                "`phase6-checksum-test`, `phase6-checksum-perf`, `phase6-hexdump-review`, "
                "`phase6-hexdump-test`, `phase6-hexdump-perf`, `phase8-validate`, "
                "`phase8-test`, `phase8`, `phase10-validate`, `phase10-test`, `phase10`, "
                "`phase12-smoke`, `phase12-test`, and `phase12`, but no `phase14-validate`, "
                "`phase14-smoke`, `phase14-test`, or `phase14` targets"
            ),
            "    * that means the next honest same-lane follow-through is reminder-surface truthfulness, not a validator-local exact-line sync against `phase14-validate`",
            "",
        ]
    )


def fixture_release_boundary() -> str:
    return "\n".join(
        [
            "# Phase 14 Release Boundary Survey",
            f"- current Makefile posture: `zigux/Makefile` is readable again on current `master`, and its live body now exposes the shipped Phase 2 toolchain and kbuild routes together with the bounded `phase3-validate`, `phase3`, `phase4-validate`, `phase4-test`, `phase4`, `phase6-base64-test`, `phase6-base64-perf`, `phase6-bsearch-test`, `phase6-checksum-test`, `phase6-checksum-perf`, `phase6-hexdump-review`, `phase6-hexdump-test`, `phase6-hexdump-perf`, `phase8-validate`, `phase8-test`, `phase8`, `phase10-validate`, `phase10-test`, and `phase10`, `phase12-smoke`, `phase12-test`, and `phase12` routes, and no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets",
            "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`",
            "- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`",
            "",
        ]
    )


def fixture_productization_gap() -> str:
    return "\n".join(
        [
            "# Phase 14 Productization Gap Survey",
            "Given the roadmap, the correct Phase 14 posture remains study-only and wrapper-first.",
            "The higher-value same-lane task is reminder-surface truthfulness: keep shared notes aligned with the recovered documentation packet, the blob-readable validator surface, the directly readable workqueue reviewability shard, and the current Makefile posture instead of repeating the older story that the broader shared smoke packet is simply unreadable or that the Makefile still ships the old `phase14-*` routes.",
            "",
        ]
    )


def fixture_checklist() -> str:
    return "\n".join(
        [
            "# Zigux Review Checklist",
            "if the change touches the shared Phase 14 smoke packet",
            "keep `zigux/Makefile` framed as a readable non-owner surface whose live body now exposes shipped Phase 2 toolchain and kbuild routes together with the bounded Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 route families while still omitting all `phase14-*` targets",
            "",
        ]
    )


def fixture_makefile() -> str:
    return "\n".join(
        [
            "phase3-validate:",
            "phase4-validate:",
            "phase4-test:",
            "phase4: phase4-validate phase4-test",
            "phase6-base64-test:",
            "phase8-validate:",
            "phase10-validate:",
            "phase12-smoke:",
            "",
        ]
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write(root, SMOKE_NOTE_PATH, fixture_smoke_note())
        write(root, RELEASE_BOUNDARY_PATH, fixture_release_boundary())
        write(root, PRODUCTIZATION_GAP_PATH, fixture_productization_gap())
        write(root, CHECKLIST_PATH, fixture_checklist())
        write(root, MAKEFILE_PATH, fixture_makefile())

        if errors := check(root):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        write(
            root,
            SMOKE_NOTE_PATH,
            fixture_smoke_note().replace(
                "    * executable packet member drift\n",
                "",
                1,
            ),
        )
        if not any("executable packet member drift" in error for error in check(root)):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected trigger-catalog drift to fail")
            return 1

        write(root, SMOKE_NOTE_PATH, fixture_smoke_note())
        write(root, MAKEFILE_PATH, fixture_makefile() + "phase14-validate:\n")
        if not any("unexpected stale marker" in error for error in check(root)):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected stale phase14 make route to fail")
            return 1

        write(root, MAKEFILE_PATH, fixture_makefile())
        write(
            root,
            RELEASE_BOUNDARY_PATH,
            fixture_release_boundary().replace(MAKEFILE_ROUTE_ABSENCE_MARKER, "missing marker", 1),
        )
        if not any(MAKEFILE_ROUTE_ABSENCE_MARKER in error for error in check(root)):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected release-boundary makefile posture drift to fail")
            return 1

        write(root, RELEASE_BOUNDARY_PATH, fixture_release_boundary())
        write(
            root,
            CHECKLIST_PATH,
            fixture_checklist().replace("while still omitting all `phase14-*` targets", "", 1),
        )
        if not any("while still omitting all `phase14-*` targets" in error for error in check(root)):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected checklist route-absence drift to fail")
            return 1

        write(root, CHECKLIST_PATH, fixture_checklist())
        write(
            root,
            RELEASE_BOUNDARY_PATH,
            fixture_release_boundary().replace("`phase4-test`", "missing phase4-test", 1),
        )
        if not any("`phase4-test`" in error for error in check(root)):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected returned Phase 4 route drift in release boundary note to fail")
            return 1

        write(root, RELEASE_BOUNDARY_PATH, fixture_release_boundary())
        write(
            root,
            MAKEFILE_PATH,
            fixture_makefile().replace("phase4-test:\n", "", 1),
        )
        if not any("phase4-test:" in error for error in check(root)):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected returned Phase 4 makefile route drift to fail")
            return 1

    print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=pass")
    print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST_CASE_COUNT=7")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()

    errors = check(Path.cwd())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("phase14 rollback-threshold sequencing packet validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
