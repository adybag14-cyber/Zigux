#!/usr/bin/env python3
"""Guard the bounded Phase 4 reversible-delivery repo-reality handoff."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
README = Path("zigux/tests/README.md")
REPO_REALITY_WARNING = Path("scripts/zigux/check-phase4-repo-reality-warning.py")

STATUS_MARKERS = (
    "`PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
    "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=",
)

DIRECT_MARKERS = (
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/README.md`",
    "`scripts/zigux/check-phase4-repo-reality-warning.py`",
    "`scripts/zigux/check-phase4-reversible-delivery-pins.py`",
)

MISSING_BROADER_PACKET = (
    "`Documentation/zigux/phase4-gate-evidence.md`",
    "`Documentation/zigux/phase4-validation-matrix.md`",
    "`scripts/zigux/check-phase4-gate-evidence.py`",
    "`scripts/zigux/check-phase4-perf-baseline-packet.py`",
    "`scripts/zigux/validate-phase4.py`",
    "`zigux/tests/phase4_build.zig`",
    "`zigux/tests/phase4_perf_baseline_manifest.json`",
    "`zigux/tests/phase4_perf_baseline_survey.zig`",
)

ATOMIC64_GAP_MARKERS = (
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` also return missing on current `master`",
    "keep those roadmap-backed Phase 4 differential-gate destinations parked as repo-reality gaps",
    "If the roadmap-backed `atomic64_diff` pair returns, refresh the direct-readback posture only after re-reading those exact current `master` paths",
    "restore the roadmap-backed `zigux/tests/atomic64_diff.zig` pair",
)

NOTE_MARKERS = STATUS_MARKERS + DIRECT_MARKERS + MISSING_BROADER_PACKET + ATOMIC64_GAP_MARKERS + (
    "The broader Phase 4 validator, lab-matrix, and local-only perf companions are still repo-reality gaps in this run",
    "The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain historical provenance, not current-head proof",
    "The Phase 4 repo-reality warning in `zigux/tests/README.md` should stay open",
)

README_OWNER_MARKERS = (
    "current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md` instead of reconstructing the broader packet from older route names alone",
    "historical Phase 4 route names such as the parked kprobe and `test_fsmount` survey companions, the validator-first routes, and the direct local-only perf routes stay owned by the reversible-delivery handoff note until the dedicated exact-pin refresh or a broader republish makes those companion blob values directly readable again",
)

README_MARKERS = (
    "current direct-readback Phase 4 rollback packet",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "repo-reality warning for the broader Phase 4 validator, lab-matrix, and local-only perf packet",
    "historical provenance for that missing broader packet",
) + README_OWNER_MARKERS

WARNING_MARKERS = (
    "DIRECT_READBACK_PACKET = (",
    "MISSING_BROADER_PACKET = (",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "scripts/zigux/check-phase4-perf-baseline-packet.py",
    "The broader Phase 4 validator, lab-matrix, and local-only perf companions are still repo-reality gaps in this run",
    "The Phase 4 repo-reality warning in `zigux/tests/README.md` should stay open",
    "PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true",
    "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=",
) + README_OWNER_MARKERS


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


def require(text: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required fragments: {missing}")


def check(root: Path) -> None:
    note = read(root, NOTE)
    readme = read(root, README)
    repo_warning = read(root, REPO_REALITY_WARNING)
    require(note, NOTE_MARKERS, NOTE.as_posix())
    require(readme, README_MARKERS, README.as_posix())
    require(repo_warning, WARNING_MARKERS, REPO_REALITY_WARNING.as_posix())


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_root(root: Path) -> None:
    missing = "\n".join(f"  * {item}" for item in MISSING_BROADER_PACKET)
    write(
        root / NOTE,
        "# Phase 4 Reversible Delivery Evidence\n\n"
        "Current direct readback in this run confirmed `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, and `scripts/zigux/check-phase4-reversible-delivery-pins.py` on current `master`. The broader Phase 4 validator, lab-matrix, and local-only perf companions are still repo-reality gaps in this run. The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain historical provenance, not current-head proof.\n\n"
        "Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` also return missing on current `master`, so keep those roadmap-backed Phase 4 differential-gate destinations parked as repo-reality gaps instead of listing them as current direct-readback packet members.\n\n"
        "The Phase 4 repo-reality warning in `zigux/tests/README.md` should stay open until that broader packet is directly readable again.\n\n"
        "* `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`\n"
        "* `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=5`\n\n"
        "If the roadmap-backed `atomic64_diff` pair returns, refresh the direct-readback posture only after re-reading those exact current `master` paths.\n\n"
        "Use this note only as a truthful current-head handoff for the directly readable reminder surfaces. The next honest same-family follow-through is to repair the smallest repo-reality-warning packet drift first, republish one missing broader companion, or restore the roadmap-backed `zigux/tests/atomic64_diff.zig` pair.\n\n"
        f"{missing}\n",
    )
    write(
        root / README,
        "# zigux/tests\n\n"
        "  * current direct-readback Phase 4 rollback packet: `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, and `scripts/zigux/check-phase4-reversible-delivery-pins.py`\n"
        "  * repo-reality warning for the broader Phase 4 validator, lab-matrix, and local-only perf packet: `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` are still missing on current `master`\n"
        "  * Phase 4 follow-through should treat the stale `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines in `Documentation/zigux/phase4-reversible-delivery-evidence.md` as historical provenance for that missing broader packet\n"
        "  * current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md` instead of reconstructing the broader packet from older route names alone\n"
        "  * historical Phase 4 route names such as the parked kprobe and `test_fsmount` survey companions, the validator-first routes, and the direct local-only perf routes stay owned by the reversible-delivery handoff note until the dedicated exact-pin refresh or a broader republish makes those companion blob values directly readable again\n",
    )
    write(
        root / REPO_REALITY_WARNING,
        "#!/usr/bin/env python3\n"
        "DIRECT_READBACK_PACKET = (\n"
        "    \"scripts/zigux/check-phase4-reversible-delivery-pins.py\",\n"
        ")\n"
        "MISSING_BROADER_PACKET = (\n"
        "    \"scripts/zigux/check-phase4-perf-baseline-packet.py\",\n"
        ")\n"
        "NOTE_REQ = (\n"
        "    \"The broader Phase 4 validator, lab-matrix, and local-only perf companions are still repo-reality gaps in this run\",\n"
        "    \"The Phase 4 repo-reality warning in `zigux/tests/README.md` should stay open\",\n"
        "    \"PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true\",\n"
        "    \"PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=\",\n"
        ")\n"
        "README_PENDING_REQ = (\n"
        "    \"current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md` instead of reconstructing the broader packet from older route names alone\",\n"
        "    \"historical Phase 4 route names such as the parked kprobe and `test_fsmount` survey companions, the validator-first routes, and the direct local-only perf routes stay owned by the reversible-delivery handoff note until the dedicated exact-pin refresh or a broader republish makes those companion blob values directly readable again\",\n"
        ")\n",
    )


def self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase4-reversible-delivery-pins-") as tmp:
        root = Path(tmp)
        fixture_root(root)
        check(root)
        cases += 1

        write(root / NOTE, read(root, NOTE).replace(STATUS_MARKERS[0], "`PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=false`"))
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected note pin-checker marker drift to fail")

        fixture_root(root)
        write(root / NOTE, read(root, NOTE).replace(MISSING_BROADER_PACKET[0], "`Documentation/zigux/not-the-right-file.md`"))
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected note missing-packet drift to fail")

        fixture_root(root)
        write(root / README, read(root, README).replace(README_OWNER_MARKERS[0], "current shared ownership reminder drifted"))
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected README ownership reminder drift to fail")

        fixture_root(root)
        write(root / README, read(root, README).replace(README_OWNER_MARKERS[1], "historical route handoff drifted"))
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected README historical route drift to fail")

        fixture_root(root)
        write(
            root / REPO_REALITY_WARNING,
            read(root, REPO_REALITY_WARNING).replace(
                README_OWNER_MARKERS[0],
                "current shared ownership reminder drifted",
            ),
        )
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected repo-reality warning ownership drift to fail")

        fixture_root(root)
        write(
            root / REPO_REALITY_WARNING,
            read(root, REPO_REALITY_WARNING).replace(
                README_OWNER_MARKERS[1],
                "historical route handoff drifted",
            ),
        )
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected repo-reality warning historical route drift to fail")

    print("PHASE4_REVERSIBLE_DELIVERY_PINS_SELF_TEST=pass")
    print(f"PHASE4_REVERSIBLE_DELIVERY_PINS_SELF_TEST_CASES={cases}")


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    try:
        check(args.root.resolve())
    except RuntimeError as exc:
        print(f"PHASE4_REVERSIBLE_DELIVERY_PINS=fail: {exc}", file=sys.stderr)
        return 1
    print("PHASE4_REVERSIBLE_DELIVERY_PINS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
