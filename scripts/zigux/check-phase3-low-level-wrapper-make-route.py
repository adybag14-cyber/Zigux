#!/usr/bin/env python3
"""Fail-close Phase 3 low-level wrapper Makefile replay routes."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


MAKEFILE_PATH = Path("zigux/Makefile")

REQUIRED_PHASE3_AGGREGATE = (
    "phase3: phase3-validate phase3-export-uapi-layout phase3-export-shim-test "
    "phase3-low-level-wrappers phase3-policy-unsafe-test phase3-test "
    "phase3-policy-dump phase3-dump"
)
REQUIRED_SHARED_ROUTE = (
    "cd $(ZIGUX_ROOT) && $(ZIG) build phase3-low-level-wrappers "
    "--build-file zigux/tests/build.zig"
)
REQUIRED_FOCUSED_ROUTE = (
    "cd $(ZIGUX_ROOT) && $(ZIG) build phase3-low-level-wrappers-test "
    "--build-file zigux/tests/phase3_low_level_wrappers_build.zig"
)
STALE_PHASE3_AGGREGATES = (
    "phase3: phase3-validate phase3-export-uapi-layout "
    "phase3-low-level-wrappers phase3-test phase3-policy-dump phase3-dump",
    "phase3: phase3-validate phase3-export-uapi-layout "
    "phase3-low-level-wrappers phase3-test phase3-dump",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_text(text: str) -> list[str]:
    issues: list[str] = []

    required_markers = (
        ("current Phase 3 aggregate route", REQUIRED_PHASE3_AGGREGATE),
        ("shared low-level-wrapper replay route", REQUIRED_SHARED_ROUTE),
        ("focused low-level-wrapper replay route", REQUIRED_FOCUSED_ROUTE),
    )
    for label, marker in required_markers:
        if marker not in text:
            issues.append(f"missing {label}: {marker}")

    for stale_marker in STALE_PHASE3_AGGREGATES:
        if stale_marker in text:
            issues.append(f"stale Phase 3 aggregate route still present: {stale_marker}")

    return issues


def validate_repo(repo_root: Path) -> list[str]:
    makefile_path = repo_root / MAKEFILE_PATH
    if not makefile_path.exists():
        return [f"missing required file: {MAKEFILE_PATH.as_posix()}"]
    return validate_text(_read(makefile_path))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        makefile = root / MAKEFILE_PATH
        makefile.parent.mkdir(parents=True, exist_ok=True)

        good = "\n".join(
            (
                "phase3-low-level-wrappers:",
                f"\t{REQUIRED_SHARED_ROUTE}",
                "phase3-low-level-wrappers-test:",
                f"\t{REQUIRED_FOCUSED_ROUTE}",
                REQUIRED_PHASE3_AGGREGATE,
                "",
            )
        )
        makefile.write_text(good, encoding="utf-8")
        if validate_repo(root):
            print("PHASE3_LOW_LEVEL_WRAPPER_MAKE_ROUTE_SELF_TEST=fail")
            print("expected valid fixture to pass")
            return 1

        cases = (
            ("aggregate", REQUIRED_PHASE3_AGGREGATE, "missing current Phase 3 aggregate route:"),
            ("shared", REQUIRED_SHARED_ROUTE, "missing shared low-level-wrapper replay route:"),
            ("focused", REQUIRED_FOCUSED_ROUTE, "missing focused low-level-wrapper replay route:"),
        )
        for label, marker, expected in cases:
            makefile.write_text(good.replace(marker, f"missing-{label}"), encoding="utf-8")
            issues = validate_repo(root)
            if not any(issue.startswith(expected) for issue in issues):
                print("PHASE3_LOW_LEVEL_WRAPPER_MAKE_ROUTE_SELF_TEST=fail")
                print(f"expected {label} marker removal to be reported")
                return 1

        for stale_marker in STALE_PHASE3_AGGREGATES:
            makefile.write_text(good + stale_marker + "\n", encoding="utf-8")
            issues = validate_repo(root)
            if not any(issue.startswith("stale Phase 3 aggregate route still present:") for issue in issues):
                print("PHASE3_LOW_LEVEL_WRAPPER_MAKE_ROUTE_SELF_TEST=fail")
                print("expected stale aggregate route to be reported")
                return 1

    print("PHASE3_LOW_LEVEL_WRAPPER_MAKE_ROUTE_SELF_TEST=pass")
    print("PHASE3_LOW_LEVEL_WRAPPER_MAKE_ROUTE_SELF_TEST_CASE_COUNT=6")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Phase 3 low-level wrapper Makefile replay routes."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains zigux/Makefile",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_LOW_LEVEL_WRAPPER_MAKE_ROUTE=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {MAKEFILE_PATH.as_posix()}")
    print("PHASE3_LOW_LEVEL_WRAPPER_MAKE_ROUTE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
