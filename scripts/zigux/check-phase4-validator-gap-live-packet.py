#!/usr/bin/env python3
"""Guard the live Phase 4 validator-gap reminder packet against drift."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

NOTE = Path("Documentation/zigux/phase4-validator-gate-evidence-exactness-gap.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")

NOTE_MARKERS = (
    "`PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP=present`",
    "`PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_LANE_KEY=validation-perf`",
    "`PHASE4_VALIDATOR_TARGET=scripts/zigux/validate-phase4.py`",
    "parked validator-local follow-through, not a current-head exactness claim",
    "`Documentation/zigux/phase4-reversible-delivery-evidence.md`",
    "`scripts/zigux/check-phase4-repo-reality-warning.py`",
    "`scripts/zigux/check-phase4-reversible-delivery-pins.py`",
    "Current `master` no longer exposes direct authenticated readback for `scripts/zigux/validate-phase4.py` or `Documentation/zigux/phase4-gate-evidence.md`.",
    "Reopen this validator-local exactness follow-through only after a same-family lane republishes one missing broader Phase 4 companion",
)

SCRIPTS_MARKERS = (
    "## Phase 4",
    "the current shared rollback reminder packet is kept reviewable through the directly readable docs-root, tests-root, and scripts-root surfaces",
    "`Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, and `scripts/zigux/check-phase4-reversible-delivery-pins.py` keep the current direct-readback rollback-owner wording",
    "authenticated contents reads on current `master` still return missing for `Documentation/zigux/phase4-gate-evidence.md`",
    "`scripts/zigux/validate-phase4.py`",
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` still return missing on current `master`",
)

TESTS_MARKERS = (
    "roadmap-backed Phase 4 differential-gate destinations still missing on current `master`: `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig`",
    "current direct-readback Phase 4 rollback packet: `Documentation/zigux/phase4-reversible-delivery-evidence.md` `Documentation/zigux/review-checklist.md` `zigux/tests/README.md` `scripts/zigux/check-phase4-repo-reality-warning.py` `scripts/zigux/check-phase4-reversible-delivery-pins.py`",
    "repo-reality warning for the broader Phase 4 validator, lab-matrix, and local-only perf packet",
    "`Documentation/zigux/phase4-gate-evidence.md`",
    "`scripts/zigux/validate-phase4.py`",
    "historical Phase 4 route names such as the parked kprobe and `test_fsmount` survey companions",
)

STALE_MARKERS = (
    "current `master` already records the exact Phase 4 gate-evidence contract",
    "shared validator still accepts prefix-only markers today",
    "fresh current-head validator proof",
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


def require_absent_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    present = [marker for marker in markers if marker in text]
    if present:
        raise RuntimeError(f"{label} still carries stale current-head claims: {present}")


def check(root: Path) -> None:
    note = read(root, NOTE)
    scripts = read(root, SCRIPTS_README)
    tests = read(root, TESTS_README)
    require_markers(note, NOTE_MARKERS, NOTE.as_posix())
    require_markers(scripts, SCRIPTS_MARKERS, SCRIPTS_README.as_posix())
    require_markers(tests, TESTS_MARKERS, TESTS_README.as_posix())
    require_absent_markers(note, STALE_MARKERS, NOTE.as_posix())


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_root(root: Path) -> None:
    write(
        root / NOTE,
        """# Phase 4 Validator Gate-Evidence Exactness Gap

## Status
- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP=present`
- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_LANE_KEY=validation-perf`
- `PHASE4_VALIDATOR_TARGET=scripts/zigux/validate-phase4.py`

This note now records a parked validator-local follow-through, not a current-head exactness claim.
Current `master` no longer exposes direct authenticated readback for `scripts/zigux/validate-phase4.py` or `Documentation/zigux/phase4-gate-evidence.md`.
The live shared Phase 4 packet is instead the repo-reality warning anchored by:
- `Documentation/zigux/phase4-reversible-delivery-evidence.md`
- `scripts/zigux/check-phase4-repo-reality-warning.py`
- `scripts/zigux/check-phase4-reversible-delivery-pins.py`

Reopen this validator-local exactness follow-through only after a same-family lane republishes one missing broader Phase 4 companion or direct readback once again proves the missing pair is present on current `master`.
""",
    )
    write(
        root / SCRIPTS_README,
        """# scripts/zigux

## Phase 4
- the current shared rollback reminder packet is kept reviewable through the directly readable docs-root, tests-root, and scripts-root surfaces while the broader validator, lab-matrix, and local-only perf packet is currently a repo-reality gap on `master`, so this note should stay aligned with the direct-readback warning instead of treating that older packet as freshly present
- `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, and `scripts/zigux/check-phase4-reversible-delivery-pins.py` keep the current direct-readback rollback-owner wording, the host-side artifact-diff contract references, the broader-packet warning, the roadmap-backed `atomic64_diff` repo-reality warning, and the pending shared-CI perf-promotion posture explicit, and this scripts-root note should mirror that same present-current-master posture
- authenticated contents reads on current `master` still return missing for `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig`, so treat those broader validator, lab-matrix, and local-only perf surfaces as historical packet members or stale provenance until a same-lane republish makes them directly readable again
- Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` still return missing on current `master`, so keep those roadmap-backed differential-gate destinations parked as repo-reality gaps here too instead of treating older exact-readback pins as current scripts-root evidence
""",
    )
    write(
        root / TESTS_README,
        """# zigux/tests

- roadmap-backed Phase 4 differential-gate destinations still missing on current `master`: `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig`
- current direct-readback Phase 4 rollback packet: `Documentation/zigux/phase4-reversible-delivery-evidence.md` `Documentation/zigux/review-checklist.md` `zigux/tests/README.md` `scripts/zigux/check-phase4-repo-reality-warning.py` `scripts/zigux/check-phase4-reversible-delivery-pins.py`
- repo-reality warning for the broader Phase 4 validator, lab-matrix, and local-only perf packet: authenticated contents reads on current `master` still return missing for `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig`
- historical Phase 4 route names such as the parked kprobe and `test_fsmount` survey companions, the validator-first routes, and the direct local-only perf routes stay owned by the reversible-delivery handoff note until the dedicated exact-pin refresh or a broader republish makes those companion blob values directly readable again
""",
    )


def self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase4-gap-live-packet-") as tmp:
        root = Path(tmp)
        fixture_root(root)
        check(root)
        cases += 1

        write(
            root / NOTE,
            read(root, NOTE).replace(
                "parked validator-local follow-through, not a current-head exactness claim",
                "fresh current-head validator proof",
            ),
        )
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected stale note posture drift to fail")

        fixture_root(root)
        write(
            root / SCRIPTS_README,
            read(root, SCRIPTS_README).replace(
                "`scripts/zigux/check-phase4-reversible-delivery-pins.py`",
                "`scripts/zigux/not-the-right-checker.py`",
                1,
            ),
        )
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected scripts-root packet drift to fail")

        fixture_root(root)
        write(
            root / TESTS_README,
            read(root, TESTS_README).replace(
                "historical Phase 4 route names such as the parked kprobe and `test_fsmount` survey companions",
                "route ownership wording drifted",
            ),
        )
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected tests-root route wording drift to fail")

        fixture_root(root)
        write(
            root / NOTE,
            read(root, NOTE).replace(
                "`scripts/zigux/check-phase4-repo-reality-warning.py`",
                "`scripts/zigux/not-the-right-warning.py`",
                1,
            ),
        )
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected live packet anchor drift to fail")

        fixture_root(root)
        (root / TESTS_README).unlink()
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected missing tests README to fail")

    print("PHASE4_VALIDATOR_GAP_LIVE_PACKET_SELF_TEST=pass")
    print(f"PHASE4_VALIDATOR_GAP_LIVE_PACKET_SELF_TEST_CASES={cases}")


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0

    try:
        check(args.root.resolve())
    except RuntimeError as exc:
        print(f"PHASE4_VALIDATOR_GAP_LIVE_PACKET=fail: {exc}", file=sys.stderr)
        return 1

    print("PHASE4_VALIDATOR_GAP_LIVE_PACKET=pass")
    print(f"PHASE4_VALIDATOR_GAP_LIVE_PACKET_NOTE={NOTE.as_posix()}")
    print(f"PHASE4_VALIDATOR_GAP_LIVE_PACKET_SCRIPTS_README={SCRIPTS_README.as_posix()}")
    print(f"PHASE4_VALIDATOR_GAP_LIVE_PACKET_TESTS_README={TESTS_README.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
