#!/usr/bin/env python3
"""Fail closed when the Phase 10 validator-first review guide drops key route or evidence markers."""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

GUIDE_PATH = "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md"

REQUIRED_ROUTE_MARKERS = [
    "python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test",
    "python3 scripts/zigux/check-phase10-docs-readme-shared-packet.py --self-test",
    "python3 scripts/zigux/check-phase10-docs-readme-shared-packet.py",
    "python3 scripts/zigux/check-phase10-core-packet.py",
    "python3 scripts/zigux/check-phase10-closure-manifest-counts.py",
    "python3 scripts/zigux/validate-phase10.py",
    "python3 scripts/zigux/validate-phase10-closure.py",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
]

REQUIRED_SURFACE_MARKERS = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "scripts/zigux/README.md",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux/tests/phase10_build.zig",
    "zigux/Makefile",
]

REQUIRED_BOUNDARY_MARKERS = [
    "queue-local `P10-L10` freeze-boundary packet",
    "bounded `P10-L11` MMIO helper packet",
    "shared Phase 10 packet still read as one validator-first lab bundle",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str]]:
    guide = root / GUIDE_PATH
    if not guide.exists():
        return ([GUIDE_PATH], [])

    text = read_text(guide)
    drift: list[str] = []
    for marker in REQUIRED_ROUTE_MARKERS:
        if marker not in text:
            drift.append(f"route:{marker}")
    for marker in REQUIRED_SURFACE_MARKERS:
        if marker not in text:
            drift.append(f"surface:{marker}")
    for marker in REQUIRED_BOUNDARY_MARKERS:
        if marker not in text:
            drift.append(f"boundary:{marker}")
    return ([], drift)


def write_fixture(root: Path) -> None:
    lines = [
        "# Phase 10, 11, and 13 Validator-First Review Guide",
        "",
        "## Phase 10: Virtio lab packet",
        "",
        "Keep the current validator-first route explicit:",
        "",
    ]
    lines.extend(f"- `{marker}`" for marker in REQUIRED_ROUTE_MARKERS)
    lines.extend(
        [
            "",
            "Keep these evidence surfaces aligned in the same review:",
            "",
        ]
    )
    lines.extend(f"- `{marker}`" for marker in REQUIRED_SURFACE_MARKERS)
    lines.extend(
        [
            "",
            "Keep the current repo-reality split explicit too:",
            "",
            "- Keep the lane-owner split explicit in reviewer wording: the queue-local `P10-L10` freeze-boundary packet stays distinct from the bounded `P10-L11` MMIO helper packet.",
            "- Reviewer prompts should confirm the shared Phase 10 packet still read as one validator-first lab bundle.",
            "",
        ]
    )
    write_text(root / GUIDE_PATH, "\n".join(lines))


def expect_contains(items: list[str], expected: str, label: str) -> None:
    if expected not in items:
        actual = ",".join(items) if items else "none"
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_review_guide_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, drift = validate(root)
        if missing_files or drift:
            raise SystemExit(
                "phase10-review-guide-self-test:baseline_failed:"
                f"files={','.join(missing_files) or 'none'}:"
                f"drift={','.join(drift) or 'none'}"
            )

        guide = root / GUIDE_PATH
        original = read_text(guide)
        cases = 0

        guide.write_text(
            original.replace(
                "python3 scripts/zigux/check-phase10-docs-readme-shared-packet.py",
                "python3 scripts/zigux/check-phase10-docs-readme-shared-packet-missing.py",
                1,
            ),
            encoding="utf-8",
        )
        expect_contains(
            validate(root)[1],
            "route:python3 scripts/zigux/check-phase10-docs-readme-shared-packet.py",
            "phase10-review-guide-self-test",
        )
        cases += 1
        write_fixture(root)

        guide.write_text(
            original.replace(
                "python3 scripts/zigux/check-phase10-closure-manifest-counts.py",
                "python3 scripts/zigux/check-phase10-missing.py",
                1,
            ),
            encoding="utf-8",
        )
        expect_contains(
            validate(root)[1],
            "route:python3 scripts/zigux/check-phase10-closure-manifest-counts.py",
            "phase10-review-guide-self-test",
        )
        cases += 1
        write_fixture(root)

        guide.write_text(
            original.replace("scripts/zigux/README.md", "scripts/zigux/MISSING.md", 1),
            encoding="utf-8",
        )
        expect_contains(
            validate(root)[1],
            "surface:scripts/zigux/README.md",
            "phase10-review-guide-self-test",
        )
        cases += 1
        write_fixture(root)

        guide.write_text(
            original.replace(
                "queue-local `P10-L10` freeze-boundary packet",
                "queue-local freeze packet",
                1,
            ),
            encoding="utf-8",
        )
        expect_contains(
            validate(root)[1],
            "boundary:queue-local `P10-L10` freeze-boundary packet",
            "phase10-review-guide-self-test",
        )
        cases += 1
        write_fixture(root)

        guide.unlink()
        missing_files, drift = validate(root)
        if drift:
            actual = ",".join(drift)
            raise SystemExit(
                f"phase10-review-guide-self-test:unexpected_drift={actual}"
            )
        if missing_files != [GUIDE_PATH]:
            actual = ",".join(missing_files) if missing_files else "none"
            raise SystemExit(
                "phase10-review-guide-self-test:"
                f"expected_missing={GUIDE_PATH}:actual={actual}"
            )
        cases += 1

    print("PHASE10_REVIEW_GUIDE_PACKET_SELF_TEST=pass")
    print(f"PHASE10_REVIEW_GUIDE_PACKET_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 10 validator-first review guide packet."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, drift = validate(args.repo_root)
    if missing_files:
        print("PHASE10_REVIEW_GUIDE_PACKET=fail")
        print("PHASE10_REVIEW_GUIDE_PACKET_MISSING_FILES_START")
        for item in missing_files:
            print(item)
        print("PHASE10_REVIEW_GUIDE_PACKET_MISSING_FILES_END")
        return 1

    if drift:
        print("PHASE10_REVIEW_GUIDE_PACKET=fail")
        print("PHASE10_REVIEW_GUIDE_PACKET_DRIFT_START")
        for item in drift:
            print(item)
        print("PHASE10_REVIEW_GUIDE_PACKET_DRIFT_END")
        return 1

    print("PHASE10_REVIEW_GUIDE_PACKET=pass")
    print(f"PHASE10_REVIEW_GUIDE_PACKET_ROUTE_MARKER_COUNT={len(REQUIRED_ROUTE_MARKERS)}")
    print(
        f"PHASE10_REVIEW_GUIDE_PACKET_SURFACE_MARKER_COUNT={len(REQUIRED_SURFACE_MARKERS)}"
    )
    print(
        f"PHASE10_REVIEW_GUIDE_PACKET_BOUNDARY_MARKER_COUNT={len(REQUIRED_BOUNDARY_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
