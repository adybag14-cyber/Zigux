#!/usr/bin/env python3
"""Guard the bounded Phase 4 reversible-delivery repo-reality handoff."""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
README = Path("zigux/tests/README.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
REPO_REALITY_WARNING = Path("scripts/zigux/check-phase4-repo-reality-warning.py")

PIN_SELF_TEST_COUNT_LABEL = "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT"
REPO_REALITY_WARNING_SELF_TEST_COUNT_LABEL = "PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES"
EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 11
EXPECTED_PIN_SELF_TEST_CASES = 7

STATUS_MARKERS = (
    "`PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
    "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=11` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=7` here",
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
    "`scripts/zigux/check-phase4-remaining-gap-matrix.py`",
    "`scripts/zigux/check-phase4-perf-baseline-packet.py`",
    "`scripts/zigux/validate-phase4.py`",
    "`zigux/tests/phase4_build.zig`",
    "`zigux/tests/phase4_perf_baseline_manifest.json`",
    "`zigux/tests/phase4_perf_baseline_survey.zig`",
)

ATOMIC64_GAP_MARKERS = (
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` also return missing on current `master`",
    "Keep that pair parked as authenticated-readback repo-reality gaps instead of listing them as current direct-readback packet members.",
    "If the roadmap-backed `atomic64_diff` pair returns, refresh the direct-readback posture only after re-reading those exact current `master` paths",
    "restore the roadmap-backed `zigux/tests/atomic64_diff.zig` pair",
)

NOTE_MARKERS = STATUS_MARKERS + DIRECT_MARKERS + MISSING_BROADER_PACKET + ATOMIC64_GAP_MARKERS + (
    "The broader Phase 4 validator, lab-matrix, local-only perf, and bitmap-diff companions are still repo-reality gaps in this run",
    "The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain historical provenance, not current-head proof",
    "The Phase 4 repo-reality warning in `zigux/tests/README.md` should stay open",
)

README_OWNER_MARKERS = (
    "current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md` instead of reconstructing the broader packet from older route names alone",
    "historical Phase 4 route names such as the parked kprobe and `test_fsmount` survey companions, the validator-first routes, and the direct local-only perf routes stay owned by the reversible-delivery handoff note until the dedicated exact-pin refresh or a broader republish makes those companion blob values directly readable again",
)

README_ATOMIC64_GAP_MARKERS = (
    "roadmap-backed Phase 4 differential-gate destinations still missing on current `master`: `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig`",
)

README_PUBLIC_FALLBACK_MARKERS = (
    "public current-`master` fallback rereads can still expose older broader Phase 4 companions, but keep that fallback visibility separate from authenticated direct-readback proof in this tests-root reminder until the same files return through direct contents reads",
)

README_MARKERS = (
    "current direct-readback Phase 4 rollback packet",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "repo-reality warning for the broader Phase 4 validator, lab-matrix, and local-only perf packet",
    "historical provenance for that missing broader packet",
) + README_OWNER_MARKERS + README_ATOMIC64_GAP_MARKERS + README_PUBLIC_FALLBACK_MARKERS

SCRIPTS_README_MARKERS = (
    "Phase 4 flow - the current shared rollback reminder packet is kept reviewable through the directly readable docs-root, tests-root, and scripts-root surfaces while the broader validator, lab-matrix, dedicated local-only perf, bitmap-diff, and roadmap-backed `atomic64_diff` companions remain authenticated-readback repo-reality gaps on current `master`, so this note should stay aligned with that narrower direct-readback packet instead of treating public fallback visibility as the same thing as direct current-head proof",
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "`zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`",
    "keep that broader validator, local-only perf, differential-gate, and helper-backed rollback packet in the missing-packet bucket here even when public current-`master` fallback rereads can still expose older companions",
    "if future same-lane work restores the broader validator, lab-matrix, dedicated local-only perf, bitmap-diff, or roadmap-backed `atomic64_diff` packet to authenticated direct-readback status, refresh this scripts-root reminder only after rereading `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `zigux/tests/README.md`, and the current scripts-root checker packet together on current `master`",
    "Validation and Perf Team",
    "ABI and Runtime Team plus Shared Subsystems Pod",
)

WARNING_MARKERS = (
    "DIRECT_READBACK_PACKET = (",
    "MISSING_BROADER_PACKET = (",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "scripts/zigux/check-phase4-remaining-gap-matrix.py",
    "scripts/zigux/check-phase4-perf-baseline-packet.py",
    "The broader Phase 4 validator, lab-matrix, local-only perf, and bitmap-diff companions are still repo-reality gaps in this run",
    "The Phase 4 repo-reality warning in `zigux/tests/README.md` should stay open",
    'REPO_REALITY_WARNING_SELF_TEST_COUNT_LABEL = "PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES"',
    "EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 11",
    "EXPECTED_PIN_SELF_TEST_CASES = 7",
    "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=11` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=7` here",
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


def require_exact_self_test_count(
    text: str,
    label: str,
    count_label: str,
    expected: int,
) -> None:
    matches = re.findall(rf"`{count_label}=(\d+)`", text)
    if not matches:
        raise RuntimeError(
            f"{label} is missing a numeric `{count_label}=...` marker"
        )
    if any(int(value) != expected for value in matches):
        raise RuntimeError(
            f"{label} must carry `{count_label}={expected}` exactly"
        )


def check(root: Path) -> None:
    note = read(root, NOTE)
    readme = read(root, README)
    scripts_readme = read(root, SCRIPTS_README)
    repo_warning = read(root, REPO_REALITY_WARNING)
    require(note, NOTE_MARKERS, NOTE.as_posix())
    require(readme, README_MARKERS, README.as_posix())
    require(scripts_readme, SCRIPTS_README_MARKERS, SCRIPTS_README.as_posix())
    require(repo_warning, WARNING_MARKERS, REPO_REALITY_WARNING.as_posix())
    require_exact_self_test_count(
        note,
        NOTE.as_posix(),
        REPO_REALITY_WARNING_SELF_TEST_COUNT_LABEL,
        EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES,
    )
    require_exact_self_test_count(
        note,
        NOTE.as_posix(),
        PIN_SELF_TEST_COUNT_LABEL,
        EXPECTED_PIN_SELF_TEST_CASES,
    )


def main() -> int:
    args = parse_args()
    if args.self_test:
        cases = 0
        with tempfile.TemporaryDirectory(prefix="phase4-reversible-delivery-pins-") as tmp:
            root = Path(tmp)
            for rel in (NOTE, README, SCRIPTS_README, REPO_REALITY_WARNING):
                src = args.root.resolve() / rel
                dst = root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            check(root)
            cases += 1

            note_path = root / NOTE
            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(
                    "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=7`",
                    "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=0`",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected non-positive pin self-test count to fail")

            note_path.write_text((args.root.resolve() / NOTE).read_text(encoding="utf-8"), encoding="utf-8")
            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(
                    "`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=11`",
                    "`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=0`",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError(
                    "expected repo-reality warning self-test count drift to fail"
                )

            note_path.write_text((args.root.resolve() / NOTE).read_text(encoding="utf-8"), encoding="utf-8")
            readme_path = root / README
            readme_path.write_text(
                readme_path.read_text(encoding="utf-8").replace(
                    README_ATOMIC64_GAP_MARKERS[0],
                    "roadmap-backed Phase 4 differential-gate warning drifted",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected README atomic64 gap drift to fail")

            readme_path.write_text((args.root.resolve() / README).read_text(encoding="utf-8"), encoding="utf-8")
            scripts_readme_path = root / SCRIPTS_README
            scripts_readme_path.write_text(
                scripts_readme_path.read_text(encoding="utf-8").replace(
                    SCRIPTS_README_MARKERS[6],
                    "atomic64 reminder drifted",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected scripts README atomic64 drift to fail")

            scripts_readme_path.write_text((args.root.resolve() / SCRIPTS_README).read_text(encoding="utf-8"), encoding="utf-8")
            scripts_readme_path.write_text(
                scripts_readme_path.read_text(encoding="utf-8").replace(
                    SCRIPTS_README_MARKERS[0],
                    "Phase 4 flow drifted",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected scripts README packet summary drift to fail")

            scripts_readme_path.write_text((args.root.resolve() / SCRIPTS_README).read_text(encoding="utf-8"), encoding="utf-8")
            repo_warning_path = root / REPO_REALITY_WARNING
            repo_warning_path.write_text(
                repo_warning_path.read_text(encoding="utf-8").replace(
                    "scripts/zigux/check-phase4-remaining-gap-matrix.py",
                    "scripts/zigux/check-phase4-gap-matrix-drifted.py",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected repo-reality warning drift to fail")

            repo_warning_path.write_text((args.root.resolve() / REPO_REALITY_WARNING).read_text(encoding="utf-8"), encoding="utf-8")
            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(
                    ATOMIC64_GAP_MARKERS[2],
                    "atomic64 next-step wording drifted",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected note atomic64 next-step drift to fail")

        print("PHASE4_REVERSIBLE_DELIVERY_PINS_SELF_TEST=pass")
        print(f"PHASE4_REVERSIBLE_DELIVERY_PINS_SELF_TEST_CASES={cases}")
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
