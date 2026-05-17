#!/usr/bin/env python3
"""Guard the current-head Phase 4 reversible-delivery repo-reality packet."""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
DOCS_README = Path("Documentation/zigux/README.md")
CHECKLIST = Path("Documentation/zigux/review-checklist.md")
README = Path("zigux/tests/README.md")
SELF = Path("scripts/zigux/check-phase4-repo-reality-warning.py")
PINS = Path("scripts/zigux/check-phase4-reversible-delivery-pins.py")

DIRECT_READBACK_PACKET = (
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
)

MISSING_BROADER_PACKET = (
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/check-phase4-remaining-gap-matrix.py",
    "scripts/zigux/check-phase4-perf-baseline-packet.py",
    "scripts/zigux/validate-phase4.py",
    "zigux/tests/phase4_build.zig",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
)

PIN_SELF_TEST_COUNT_LABEL = "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT"
REPO_REALITY_WARNING_SELF_TEST_COUNT_LABEL = "PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES"
EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 11
EXPECTED_PIN_SELF_TEST_CASES = 7

NOTE_REQ = (
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-artifact-diff-contract.py",
    "The broader Phase 4 validator, lab-matrix, local-only perf, and bitmap-diff companions are still repo-reality gaps in this run",
    "The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain historical provenance, not current-head proof",
    "The Phase 4 repo-reality warning in `zigux/tests/README.md` should stay open",
    "The tests-root guide already keeps the broader packet missing-warning aligned, and the repo-reality warning checker now fails closed on that broader-packet distinction between authenticated direct-readback gaps and public current-`master` fallback visibility.",
    "`PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
    "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=11` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=7` here",
)

DOCS_README_PENDING_REQ = (
    "Phase 4 notes - `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, and `scripts/zigux/check-phase4-reversible-delivery-pins.py` now keep the current direct-readback rollback packet reviewable from the docs root while the broader validator, lab-matrix, local-only perf, and bitmap-diff companions remain repo-reality gaps on current `master`.",
    "`Documentation/zigux/phase4-gate-evidence.md`",
    "`Documentation/zigux/phase4-validation-matrix.md`",
    "`scripts/zigux/check-phase4-gate-evidence.py`",
    "`scripts/zigux/check-phase4-perf-baseline-packet.py`",
    "`scripts/zigux/validate-phase4.py`",
    "`zigux/tests/phase4_build.zig`",
    "`zigux/tests/phase4_perf_baseline_manifest.json`",
    "`zigux/tests/phase4_perf_baseline_survey.zig`",
    "`zigux/tests/atomic64_diff.zig`",
    "`zigux/tests/runtime_atomic64_diff.zig`",
    "`zigux/tests/bitmap_diff.zig`",
    "`zigux/tests/phase4_bitmap_live_helper_replay.zig`",
    "keep the pending shared-CI perf-promotion posture explicit instead of implying those broader Phase 4 routes are live current-head evidence.",
)

README_OWNER_MARKERS = (
    "current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md` instead of reconstructing the broader packet from older route names alone",
    "historical Phase 4 route names such as the parked kprobe and `test_fsmount` survey companions, the validator-first routes, and the direct local-only perf routes stay owned by the reversible-delivery handoff note until the dedicated exact-pin refresh or a broader republish makes those companion blob values directly readable again",
)

README_ATOMIC64_GAP_MARKERS = (
    "roadmap-backed Phase 4 differential-gate destinations still missing on current `master`: `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig`",
)

README_PUBLIC_FALLBACK_MARKERS = (
    "public current-`master` fallback rereads can still expose older broader Phase 4 companions",
    "keep that fallback visibility separate from authenticated direct-readback proof in this tests-root reminder until the same files return through direct contents reads",
)

README_PENDING_REQ = (
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "repo-reality warning for the broader Phase 4 validator, lab-matrix, and local-only perf packet",
    "historical provenance for that missing broader packet",
) + README_OWNER_MARKERS + README_ATOMIC64_GAP_MARKERS + README_PUBLIC_FALLBACK_MARKERS

CHECKLIST_PENDING_REQ = (
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
    "ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call",
    "pending shared-CI perf-promotion posture explicit",
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
        raise RuntimeError(f"missing required file: {rel}") from exc


def write(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require(text: str, parts: tuple[str, ...], label: str) -> None:
    missing = [part for part in parts if part not in text]
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


def _require_direct_packet(root: Path) -> None:
    missing_direct = [
        rel for rel in DIRECT_READBACK_PACKET if not (root / Path(rel)).exists()
    ]
    if missing_direct:
        raise RuntimeError(
            "direct-readback packet no longer matches the current tree: "
            + ", ".join(missing_direct)
        )


def check(root: Path) -> None:
    note = read(root, NOTE)
    docs_readme = read(root, DOCS_README)
    checklist = read(root, CHECKLIST)
    readme = read(root, README)
    require(note, NOTE_REQ + DIRECT_READBACK_PACKET + MISSING_BROADER_PACKET, "phase4 note")
    require(docs_readme, DOCS_README_PENDING_REQ, "docs README")
    require(readme, README_PENDING_REQ + MISSING_BROADER_PACKET, "tests README")
    require(checklist, CHECKLIST_PENDING_REQ, "review checklist")
    require_exact_self_test_count(
        note,
        "phase4 note",
        REPO_REALITY_WARNING_SELF_TEST_COUNT_LABEL,
        EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES,
    )
    require_exact_self_test_count(
        note,
        "phase4 note",
        PIN_SELF_TEST_COUNT_LABEL,
        EXPECTED_PIN_SELF_TEST_CASES,
    )
    _require_direct_packet(root)


def baseline_note() -> str:
    broader_packet = ", ".join(f"`{item}`" for item in MISSING_BROADER_PACKET)
    direct_packet = ", ".join(f"`{item}`" for item in DIRECT_READBACK_PACKET)
    return "\n".join(
        [
            "# Phase 4 Reversible Delivery Evidence",
            "",
            "Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, and `scripts/zigux/check-phase4-reversible-delivery-pins.py` on current `master`.",
            f"Current direct-readback packet members: {direct_packet}.",
            "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=11` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=7` here, so future exact-readback passes can fail closed on stale checker-coverage claims as well as stale packet-member claims.",
            f"The broader Phase 4 validator, lab-matrix, local-only perf, and bitmap-diff companions are still repo-reality gaps in this run: authenticated contents reads returned missing for {broader_packet}.",
            "Historical broader packet references still include `scripts/zigux/artifact_diff.py` and `scripts/zigux/check-artifact-diff-contract.py`, so the shared repo-reality warning must keep those contract anchors explicit even while the broader packet stays historical here.",
            "The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain historical provenance, not current-head proof.",
            "The Phase 4 repo-reality warning in `zigux/tests/README.md` should stay open until that broader validator, lab-matrix, local-only perf, and bitmap-diff packet is directly readable again.",
            "The tests-root guide already keeps the broader packet missing-warning aligned, and the repo-reality warning checker now fails closed on that broader-packet distinction between authenticated direct-readback gaps and public current-`master` fallback visibility.",
            "`PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
            "`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=11`",
            "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=7`",
        ]
    ) + "\n"


def baseline_docs_readme() -> str:
    return "\n".join(
        [
            "# Zigux Documentation",
            DOCS_README_PENDING_REQ[0],
            *DOCS_README_PENDING_REQ[1:],
        ]
    ) + "\n"


def baseline_tests_readme() -> str:
    return "\n".join(
        [
            "# zigux/tests",
            "current direct-readback Phase 4 rollback packet",
            *README_PENDING_REQ,
            *MISSING_BROADER_PACKET,
        ]
    ) + "\n"


def baseline_checklist() -> str:
    return "\n".join(
        [
            "# Zigux Review Checklist",
            *CHECKLIST_PENDING_REQ,
        ]
    ) + "\n"


def build_baseline_tree(root: Path) -> None:
    write(root, NOTE, baseline_note())
    write(root, DOCS_README, baseline_docs_readme())
    write(root, README, baseline_tests_readme())
    write(root, CHECKLIST, baseline_checklist())
    write(root, SELF, "# repo-reality warning checker placeholder\n")
    write(root, PINS, "# reversible-delivery pin checker placeholder\n")


def main() -> int:
    args = parse_args()
    if args.self_test:
        cases = 0
        with tempfile.TemporaryDirectory(prefix="phase4-repo-reality-") as tmp:
            root = Path(tmp)
            build_baseline_tree(root)
            check(root)
            cases += 1

            drifted = root / NOTE
            drifted.write_text(
                drifted.read_text(encoding="utf-8").replace(
                    "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=7`",
                    "`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=zero`",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected non-numeric pin self-test count to fail")

            build_baseline_tree(root)
            drifted = root / NOTE
            drifted.write_text(
                drifted.read_text(encoding="utf-8").replace(
                    "`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=11`",
                    "`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=99`",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError(
                    "expected stale repo-reality warning self-test count to fail"
                )

            build_baseline_tree(root)
            docs_readme_path = root / DOCS_README
            docs_readme_path.write_text(
                docs_readme_path.read_text(encoding="utf-8").replace(
                    DOCS_README_PENDING_REQ[-1],
                    "pending perf posture drifted",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected docs README repo-reality drift to fail")

            build_baseline_tree(root)
            readme_path = root / README
            readme_path.write_text(
                readme_path.read_text(encoding="utf-8").replace(
                    README_PUBLIC_FALLBACK_MARKERS[1],
                    "fallback visibility wording drifted",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected tests README fallback-visibility drift to fail")

            build_baseline_tree(root)
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
                raise AssertionError("expected tests README atomic64 warning drift to fail")

            build_baseline_tree(root)
            readme_path = root / README
            readme_path.write_text(
                readme_path.read_text(encoding="utf-8").replace(
                    README_OWNER_MARKERS[0],
                    "shared Phase 4 ownership reminder drifted",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected tests README owner reminder drift to fail")

            build_baseline_tree(root)
            checklist_path = root / CHECKLIST
            checklist_path.write_text(
                checklist_path.read_text(encoding="utf-8").replace(
                    CHECKLIST_PENDING_REQ[3],
                    "decision-owner wording drifted",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected review checklist decision-owner drift to fail")

            build_baseline_tree(root)
            checklist_path = root / CHECKLIST
            checklist_path.write_text(
                checklist_path.read_text(encoding="utf-8").replace(
                    CHECKLIST_PENDING_REQ[4],
                    "coordination-owner wording drifted",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected review checklist drift to fail")

            build_baselineTree(root)
            direct_packet_checker = root / PINS
            direct_packet_checker.unlink()
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError("expected missing direct packet member to fail")

            build_baseline_tree(root)
            note_path = root / NOTE
            note_path.write_text(
                note_path.read_text(encoding="utf-8").replace(
                    "scripts/zigux/check-artifact-diff-contract.py",
                    "scripts/zigux/check-artifact-diff-contract-drift.py",
                ),
                encoding="utf-8",
            )
            try:
                check(root)
            except RuntimeError:
                cases += 1
            else:
                raise AssertionError(
                    "expected missing artifact-diff contract marker to fail"
                )

        print("PHASE4_REPO_REALITY_WARNING_SELF_TEST=pass")
        print(f"PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES={cases}")
        return 0
    try:
        check(args.root.resolve())
    except RuntimeError as exc:
        print(f"PHASE4_REPO_REALITY_WARNING=fail: {exc}", file=sys.stderr)
        return 1
    print("PHASE4_REPO_REALITY_WARNING=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
