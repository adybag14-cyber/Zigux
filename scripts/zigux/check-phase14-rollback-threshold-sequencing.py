#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=rollback_threshold_sequencing

Fail-closed checker for the current Phase 14 rollback-threshold packet.

This checker stays inside the rollback-automation lane. It validates that the
shared smoke reminder surfaces still agree on the current study-only rollback
contract, on the returned route checker and tests-root reminder checker, on the
returned ring-buffer survey companion and shared smoke manifest, and on the
current repo-reality split where the Makefile is readable, ships
`phase14-validate`, and still does not ship the broader `phase14-smoke`,
`phase14-test`, or `phase14` wrapper targets.
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
    "recovered documentation packet, the directly readable shared-smoke route "
    "checker, the directly readable tests-root reminder checker, the directly "
    "readable validator path, the readable current Makefile body, the directly "
    "readable release-boundary exact-count guard, the directly readable "
    "workqueue boundary shard, the directly readable ring-buffer survey "
    "companion, the directly readable shared smoke manifest, and the "
    "still-missing broader wrapper-backed rerun routes"
)
ROLLBACK_FALLBACK_MARKER = (
    "  * fallback path: keep this shared smoke lane aligned with the current "
    "gap notes until the broader shared reminder packet stops treating the "
    "current Makefile body as if it still shipped `phase14-smoke`, "
    "`phase14-test`, and `phase14`, and until the build-side and broader "
    "executable packet members return through exact current-`master` readback; "
    "once they do, rerun the packet-local commands below before restoring any "
    "stronger validator-first claim"
)
ROLLBACK_TRIGGER_MARKERS = [
    "    * recovered documentation packet drift",
    "    * route-checker-versus-reminder-surface drift",
    "    * tests-root-checker-versus-reminder-surface drift",
    "    * validator-versus-reminder-surface drift",
    "    * workqueue-boundary-shard drift",
    "    * ring-buffer-survey drift",
    "    * wrapper-route drift",
    "    * build-side exact-readback-gap drift",
    "    * broader executable-layer exact-readback-gap drift",
    "    * attached-toolchain guidance drift inside the shared smoke note",
]
HISTORICAL_ROUTE_VOCABULARY_MARKERS = [
    "`phase14-smoke`",
    "`phase14-test`",
    "`phase14`",
]
MAKEFILE_ROUTE_ABSENCE_MARKER = (
    "`phase14-smoke`, `phase14-test`, or `phase14` targets"
)
RETURNED_PHASE4_ROUTE_MARKERS = [
    "`phase4-validate`",
    "`phase4-test`",
    "`phase4`",
]
PRODUCTIZATION_GAP_MARKERS = [
    "Given the roadmap, the correct Phase 14 posture remains study-only and wrapper-first.",
    "The higher-value same-lane task is reminder-surface truthfulness:",
    "the directly readable shared-smoke route checker",
    "the directly readable tests-root reminder checker",
    "the directly readable validator surface",
    "the directly readable release-boundary exact-count guard",
    "the directly readable shared smoke manifest",
    "the current Makefile posture",
]
CHECKLIST_MARKERS = [
    "if the change touches the shared Phase 14 smoke packet",
    "keep `zigux/Makefile` framed as readable current evidence",
    "`phase14-validate`, `phase14-smoke`, `phase14-test`, and `phase14` stay packet-local or repo-reality-gap vocabulary",
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
    "phase14-validate:",
]
MAKEFILE_ABSENT_ROUTE_MARKERS = [
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
            "  * packet-local command posture preserved by this note:",
            "no current attached-toolchain `make -C zigux phase14-smoke`, `make -C zigux phase14-test`, or `make -C zigux phase14` fallback is usable from this note",
            "keep those older wrapper names recorded only as historical packet vocabulary",
            *HISTORICAL_ROUTE_VOCABULARY_MARKERS,
            MAKEFILE_ROUTE_ABSENCE_MARKER,
            *RETURNED_PHASE4_ROUTE_MARKERS,
            "same-lane follow-through should only touch the smallest shared reminder surface that drifts against this returned Makefile split",
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
            "- current shared-smoke route: `make -C zigux phase14-validate`",
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
            "  * packet-local command posture preserved by this note:",
            (
                "    * the current readable route layer still stops at `make -C zigux "
                "phase14-validate`; no current attached-toolchain `make -C zigux "
                "phase14-smoke`, `make -C zigux phase14-test`, or `make -C zigux "
                "phase14` fallback is usable from this note because the readable "
                "`zigux/Makefile` body still omits those targets"
            ),
            (
                "    * `zigux/Makefile` is directly readable again through the current "
                "contents path, and its live body now exposes the shipped Phase 2 "
                "toolchain and kbuild routes together with the bounded `phase3-validate`, "
                "`phase3`, `phase4-validate`, `phase4-test`, `phase4`, "
                "`phase6-base64-test`, `phase6-base64-perf`, `phase6-bsearch-test`, "
                "`phase6-checksum-test`, `phase6-checksum-perf`, `phase6-hexdump-review`, "
                "`phase6-hexdump-test`, `phase6-hexdump-perf`, `phase8-validate`, "
                "`phase8-test`, `phase8`, `phase10-validate`, `phase10-test`, `phase10`, "
                "`phase12-smoke`, `phase12-test`, `phase12`, and `phase14-validate`, but "
                "no `phase14-smoke`, `phase14-test`, or `phase14` targets"
            ),
            (
                "    * keep those older wrapper names recorded only as historical packet "
                "vocabulary until the same exact readback mode restores the broader "
                "Phase 14 Makefile routes on current `master`"
            ),
            (
                "    * that means later same-lane follow-through should only touch the "
                "smallest shared reminder surface that drifts against this returned "
                "Makefile split"
            ),
            (
                "    * that means later same-lane follow-through should only touch the "
                "smallest shared reminder surface that drifts against this returned "
                "Makefile split, not default back to a validator-local exact-line sync "
                "or an already-aligned tests-root rewrite"
            ),
            "",
        ]
    )


def fixture_release_boundary() -> str:
    return "\n".join(
        [
            "# Phase 14 Release Boundary Survey",
            "- current Makefile posture: `zigux/Makefile` is readable again on current `master`, and its live body now exposes the shipped Phase 2 toolchain and kbuild routes together with the bounded `phase3-validate`, `phase3`, `phase4-validate`, `phase4-test`, `phase4`, `phase6-base64-test`, `phase6-base64-perf`, `phase6-bsearch-test`, `phase6-checksum-test`, `phase6-checksum-perf`, `phase6-hexdump-review`, `phase6-hexdump-test`, `phase6-hexdump-perf`, `phase8-validate`, `phase8-test`, `phase8`, `phase10-validate`, `phase10-test`, `phase10`, `phase12-smoke`, `phase12-test`, `phase12`, and `phase14-validate` routes, and no `phase14-smoke`, `phase14-test`, or `phase14` targets",
            "- current shared-smoke route: `make -C zigux phase14-validate`",
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
            "The higher-value same-lane task is reminder-surface truthfulness: keep shared notes aligned with the recovered documentation packet, the directly readable shared-smoke route checker, the directly readable tests-root reminder checker, the directly readable validator surface, the directly readable release-boundary exact-count guard, the directly readable shared smoke manifest, the directly readable workqueue reviewability shard, the directly readable ring-buffer survey companion, and the current Makefile posture instead of repeating the older story that the broader shared smoke packet is simply unreadable or that the Makefile still ships the old `phase14-*` routes.",
            "",
        ]
    )


def fixture_checklist() -> str:
    return "\n".join(
        [
            "# Zigux Review Checklist",
            "if the change touches the shared Phase 14 smoke packet",
            "keep `zigux/Makefile` framed as readable current evidence for the shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes while `phase14-validate`, `phase14-smoke`, `phase14-test`, and `phase14` stay packet-local or repo-reality-gap vocabulary",
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
            "phase14-validate:",
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
                "    * route-checker-versus-reminder-surface drift\n",
                "",
                1,
            ),
        )
        if not any("route-checker-versus-reminder-surface drift" in error for error in check(root)):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected route-checker trigger drift to fail")
            return 1

        write(root, SMOKE_NOTE_PATH, fixture_smoke_note())
        write(
            root,
            SMOKE_NOTE_PATH,
            fixture_smoke_note().replace(
                "    * tests-root-checker-versus-reminder-surface drift\n",
                "",
                1,
            ),
        )
        if not any("tests-root-checker-versus-reminder-surface drift" in error for error in check(root)):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected tests-root trigger drift to fail")
            return 1

        write(root, SMOKE_NOTE_PATH, fixture_smoke_note())
        write(
            root,
            SMOKE_NOTE_PATH,
            fixture_smoke_note().replace(
                "    * ring-buffer-survey drift\n",
                "",
                1,
            ),
        )
        if not any("ring-buffer-survey drift" in error for error in check(root)):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected ring-buffer trigger drift to fail")
            return 1

        write(root, SMOKE_NOTE_PATH, fixture_smoke_note())
        write(
            root,
            SMOKE_NOTE_PATH,
            fixture_smoke_note().replace(
                "    * wrapper-route drift\n",
                "",
                1,
            ),
        )
        if not any("wrapper-route drift" in error for error in check(root)):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected trigger-catalog drift to fail")
            return 1

        write(root, SMOKE_NOTE_PATH, fixture_smoke_note())
        write(root, MAKEFILE_PATH, fixture_makefile().replace("phase14-validate:\n", "", 1))
        if not any("phase14-validate:" in error for error in check(root)):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected returned phase14 validate route to fail")
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
            fixture_checklist().replace(
                "`phase14-validate`, `phase14-smoke`, `phase14-test`, and `phase14` stay packet-local or repo-reality-gap vocabulary",
                "",
                1,
            ),
        )
        if not any("packet-local or repo-reality-gap vocabulary" in error for error in check(root)):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected checklist route-vocabulary drift to fail")
            return 1

        write(root, CHECKLIST_PATH, fixture_checklist())
        write(
            root,
            PRODUCTIZATION_GAP_PATH,
            fixture_productization_gap().replace(
                "the directly readable shared smoke manifest",
                "missing shared smoke manifest",
                1,
            ),
        )
        if not any("the directly readable shared smoke manifest" in error for error in check(root)):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected productization-gap shared-manifest drift to fail")
            return 1

        write(root, PRODUCTIZATION_GAP_PATH, fixture_productization_gap())
        write(
            root,
            MAKEFILE_PATH,
            fixture_makefile() + "phase14-smoke:\n",
        )
        if not any("unexpected stale marker" in error for error in check(root)):
            print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
            print("expected stale phase14 smoke route to fail")
            return 1

    print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=pass")
    print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST_CASE_COUNT=10")
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