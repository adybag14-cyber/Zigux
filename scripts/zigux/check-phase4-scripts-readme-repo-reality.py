#!/usr/bin/env python3
"""Guard the current Phase 4 scripts-root repo-reality packet."""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

README = Path("scripts/zigux/README.md")
NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
DOCS_README = Path("Documentation/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
CHECKLIST = Path("Documentation/zigux/review-checklist.md")
REPO_WARNING = Path("scripts/zigux/check-phase4-repo-reality-warning.py")
PINS = Path("scripts/zigux/check-phase4-reversible-delivery-pins.py")

DIRECT_PACKET = (
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
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
)

ROADMAP_DIFF_GAPS = (
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
)

README_REQUIRED = (
    "Phase 4 flow - the current shared rollback reminder packet is kept reviewable through the directly readable docs-root, tests-root, and scripts-root surfaces while the broader validator, lab-matrix, dedicated local-only perf, bitmap-diff, and roadmap-backed `atomic64_diff` companions remain authenticated-readback repo-reality gaps on current `master`",
    "keep the current direct-readback rollback-owner wording, the host-side artifact-diff contract references, the broader-packet warning, the roadmap-backed `atomic64_diff` repo-reality wording, and the pending shared-CI perf-promotion posture explicit",
    "authenticated contents reads on current `master` still return missing for",
    "keep that broader validator, local-only perf, differential-gate, and helper-backed rollback packet in the missing-packet bucket here even when public current-`master` fallback rereads can still expose older companions",
    "keep the dedicated local-only perf packet and any broader shared-CI perf-promotion decision owned by the Validation and Perf Team",
)

NOTE_REQUIRED = (
    "The direct checker pair now publishes `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=9` and `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=7` here",
    "The broader Phase 4 validator, lab-matrix, local-only perf, and bitmap-diff companions are still repo-reality gaps in this run",
    "Public current-`master` fallback readback still exposes those broader companions, so keep the shared owner map narrow until authenticated exact reads recover instead of treating public fallback visibility as current direct-readback proof.",
    "The `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines therefore remain historical provenance, not current-head proof.",
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` also return missing on current `master`",
    "The next same-family follow-through inside this live warning packet is therefore either one tests-root wording sync for that fallback-visibility distinction or one checker repair that fails closed on that distinction before any fresh exact-pin pass against still-missing companions.",
)

DOCS_README_REQUIRED = (
    "Phase 4 notes - `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, and `scripts/zigux/check-phase4-reversible-delivery-pins.py` now keep the current direct-readback rollback packet reviewable from the docs root while the broader validator, lab-matrix, local-only perf, and bitmap-diff companions remain repo-reality gaps on current `master`.",
    "keep the pending shared-CI perf-promotion posture explicit instead of implying those broader Phase 4 routes are live current-head evidence.",
)

TESTS_README_REQUIRED = (
    "current direct-readback Phase 4 rollback packet:",
    "repo-reality warning for the broader Phase 4 validator, lab-matrix, and local-only perf packet: authenticated contents reads on current `master` still return missing for",
    "Phase 4 follow-through should treat the stale `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines in `Documentation/zigux/phase4-reversible-delivery-evidence.md` as historical provenance for that missing broader packet until fresh current-head evidence lands",
    "The Phase 4 repo-reality warning in `zigux/tests/README.md` should stay open until that broader validator, lab-matrix, and local-only perf packet is directly readable again",
    "current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md` instead of reconstructing the broader packet from older route names alone",
    "historical Phase 4 route names such as the parked kprobe and `test_fsmount` survey companions, the validator-first routes, and the direct local-only perf routes stay owned by the reversible-delivery handoff note until the dedicated exact-pin refresh or a broader republish makes those companion blob values directly readable again",
    "roadmap-backed Phase 4 differential-gate destinations still missing on current `master`: `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig`",
)

CHECKLIST_REQUIRED = (
    "Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase4-repo-reality-warning.py` and `scripts/zigux/check-phase4-reversible-delivery-pins.py` still agree on the current direct-readback packet",
    "keep the repo-reality warning explicit for the missing broader Phase 4 validator, lab-matrix, and local-only perf companions",
    "keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
    "keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call",
    "keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval?",
)

EXPECTED_REPO_WARNING_SELF_TEST_CASES = 9
EXPECTED_PIN_SELF_TEST_CASES = 7


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


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require(text: str, fragments: tuple[str, ...], label: str) -> None:
    missing = [fragment for fragment in fragments if fragment not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required fragments: {missing}")


def require_paths(text: str, paths: tuple[str, ...], label: str) -> None:
    missing = [path for path in paths if f"`{path}`" not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required path markers: {missing}")


def require_exact_count(text: str, label: str, name: str, expected: int) -> None:
    matches = re.findall(rf"`{re.escape(name)}=(\d+)`", text)
    if not matches:
        raise RuntimeError(f"{label} is missing `{name}=...`")
    if any(int(value) != expected for value in matches):
        raise RuntimeError(f"{label} must carry `{name}={expected}` exactly")


def require_direct_packet(root: Path) -> None:
    missing = [path for path in DIRECT_PACKET if not (root / path).exists()]
    if missing:
        raise RuntimeError(
            "direct-readback packet no longer matches the current tree: "
            + ", ".join(missing)
        )


def check(root: Path) -> None:
    readme = read(root, README)
    note = read(root, NOTE)
    docs_readme = read(root, DOCS_README)
    tests_readme = read(root, TESTS_README)
    checklist = read(root, CHECKLIST)

    require(readme, README_REQUIRED, README.as_posix())
    require_paths(readme, DIRECT_PACKET, README.as_posix())
    require_paths(readme, MISSING_BROADER_PACKET, README.as_posix())
    require_paths(readme, ROADMAP_DIFF_GAPS, README.as_posix())

    require(note, NOTE_REQUIRED, NOTE.as_posix())
    require_paths(note, DIRECT_PACKET, NOTE.as_posix())
    require_paths(note, MISSING_BROADER_PACKET, NOTE.as_posix())
    require_paths(note, ROADMAP_DIFF_GAPS, NOTE.as_posix())
    require_exact_count(
        note,
        NOTE.as_posix(),
        "PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES",
        EXPECTED_REPO_WARNING_SELF_TEST_CASES,
    )
    require_exact_count(
        note,
        NOTE.as_posix(),
        "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT",
        EXPECTED_PIN_SELF_TEST_CASES,
    )

    require(docs_readme, DOCS_README_REQUIRED, DOCS_README.as_posix())
    require_paths(docs_readme, MISSING_BROADER_PACKET, DOCS_README.as_posix())
    require_paths(docs_readme, ROADMAP_DIFF_GAPS, DOCS_README.as_posix())

    require(tests_readme, TESTS_README_REQUIRED, TESTS_README.as_posix())
    require_paths(tests_readme, DIRECT_PACKET, TESTS_README.as_posix())
    require_paths(
        tests_readme,
        MISSING_BROADER_PACKET[:9],
        TESTS_README.as_posix(),
    )

    require(checklist, CHECKLIST_REQUIRED, CHECKLIST.as_posix())

    require_direct_packet(root)


def baseline_docs_readme() -> str:
    broader_paths = " ".join(f"`{path}`" for path in MISSING_BROADER_PACKET)
    diff_paths = " ".join(f"`{path}`" for path in ROADMAP_DIFF_GAPS)
    return (
        "# Zigux Documentation\n"
        + DOCS_README_REQUIRED[0]
        + "\n"
        + broader_paths
        + "\n"
        + diff_paths
        + "\n"
        + DOCS_README_REQUIRED[1]
        + "\n"
    )


def baseline_readme() -> str:
    direct_paths = " ".join(f"`{path}`" for path in DIRECT_PACKET)
    broader_paths = " ".join(f"`{path}`" for path in MISSING_BROADER_PACKET)
    diff_paths = " ".join(f"`{path}`" for path in ROADMAP_DIFF_GAPS)
    return "\n".join(
        [
            "# scripts/zigux",
            "",
            README_REQUIRED[0],
            direct_paths,
            README_REQUIRED[1],
            README_REQUIRED[2],
            broader_paths,
            diff_paths,
            README_REQUIRED[3],
            README_REQUIRED[4],
            "",
        ]
    )


def baseline_note() -> str:
    direct_paths = " ".join(f"`{path}`" for path in DIRECT_PACKET)
    broader_paths = " ".join(f"`{path}`" for path in MISSING_BROADER_PACKET)
    diff_paths = " ".join(f"`{path}`" for path in ROADMAP_DIFF_GAPS)
    return "\n".join(
        [
            "# Phase 4 Reversible Delivery Evidence",
            "",
            direct_paths,
            NOTE_REQUIRED[0],
            f"`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES={EXPECTED_REPO_WARNING_SELF_TEST_CASES}`",
            f"`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT={EXPECTED_PIN_SELF_TEST_CASES}`",
            NOTE_REQUIRED[1],
            broader_paths,
            NOTE_REQUIRED[2],
            NOTE_REQUIRED[3],
            NOTE_REQUIRED[4],
            diff_paths,
            NOTE_REQUIRED[5],
            "",
        ]
    )


def baseline_tests_readme() -> str:
    direct_paths = " ".join(f"`{path}`" for path in DIRECT_PACKET)
    broader_paths = " ".join(
        f"`{path}`" for path in MISSING_BROADER_PACKET[:9]
    )
    return "\n".join(
        [
            "# zigux/tests",
            "",
            TESTS_README_REQUIRED[0],
            direct_paths,
            TESTS_README_REQUIRED[1],
            broader_paths,
            TESTS_README_REQUIRED[2],
            TESTS_README_REQUIRED[3],
            TESTS_README_REQUIRED[4],
            TESTS_README_REQUIRED[5],
            TESTS_README_REQUIRED[6],
            "",
        ]
    )


def baseline_checklist() -> str:
    return "# Zigux Review Checklist\n\n- " + "\n- ".join(CHECKLIST_REQUIRED) + "\n"


def build_baseline_tree(root: Path) -> None:
    write(root / README, baseline_readme())
    write(root / NOTE, baseline_note())
    write(root / DOCS_README, baseline_docs_readme())
    write(root / TESTS_README, baseline_tests_readme())
    write(root / CHECKLIST, baseline_checklist())
    write(root / REPO_WARNING, "# repo-reality warning checker placeholder\n")
    write(root / PINS, "# reversible-delivery pin checker placeholder\n")


def self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase4-scripts-readme-reality-") as tmp:
        root = Path(tmp)

        build_baseline_tree(root)
        check(root)
        cases += 1

        write(
            root / README,
            read(root, README).replace(
                "pending shared-CI perf-promotion posture explicit",
                "pending perf posture drifted",
                1,
            ),
        )
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected scripts README drift to fail")

        build_baseline_tree(root)
        write(
            root / NOTE,
            read(root, NOTE).replace(
                "`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=9`",
                "`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=8`",
                1,
            ),
        )
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected note count drift to fail")

        build_baseline_tree(root)
        write(
            root / TESTS_README,
            read(root, TESTS_README).replace(
                TESTS_README_REQUIRED[6],
                "roadmap-backed Phase 4 differential-gate warning drifted",
                1,
            ),
        )
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected tests README drift to fail")

        build_baseline_tree(root)
        write(
            root / CHECKLIST,
            read(root, CHECKLIST).replace(
                "keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call",
                "coordination owners drifted",
                1,
            ),
        )
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected checklist drift to fail")

        build_baseline_tree(root)
        (root / PINS).unlink()
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected missing direct packet member to fail")

        build_baseline_tree(root)
        write(
            root / DOCS_README,
            read(root, DOCS_README).replace(
                DOCS_README_REQUIRED[1],
                "pending perf posture drifted",
                1,
            ),
        )
        try:
            check(root)
        except RuntimeError:
            cases += 1
        else:
            raise AssertionError("expected docs README drift to fail")

    print("PHASE4_SCRIPTS_README_REPO_REALITY_SELF_TEST=pass")
    print(f"PHASE4_SCRIPTS_README_REPO_REALITY_SELF_TEST_CASES={cases}")


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0

    try:
        check(args.root.resolve())
    except RuntimeError as exc:
        print(f"PHASE4_SCRIPTS_README_REPO_REALITY=fail: {exc}", file=sys.stderr)
        return 1

    print("PHASE4_SCRIPTS_README_REPO_REALITY=pass")
    print(
        f"PHASE4_SCRIPTS_README_REPO_REALITY_DIRECT_PACKET_MEMBERS={len(DIRECT_PACKET)}"
    )
    print(
        "PHASE4_SCRIPTS_README_REPO_REALITY_MISSING_BROADER_PACKET_MEMBERS="
        f"{len(MISSING_BROADER_PACKET)}"
    )
    print(
        "PHASE4_SCRIPTS_README_REPO_REALITY_ROADMAP_DIFF_GAPS="
        f"{len(ROADMAP_DIFF_GAPS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
