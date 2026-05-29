#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SLICE_PATH = Path("Documentation/zigux/phase13-devres-slice.md")
SURVEY_PATH = Path("Documentation/zigux/phase13-devres-survey.md")
HELPER_PATH = Path("lib/devres.zig")
CURRENT_PACKET_CHECKER_PATH = Path("scripts/zigux/check-phase13-devres-current-packet.py")

REQUIRED_FILES = [
    SLICE_PATH,
    SURVEY_PATH,
    HELPER_PATH,
    CURRENT_PACKET_CHECKER_PATH,
]

SLICE_MARKERS = [
    "helper-local ioport unmap planning",
    "live ioport-unmap execution",
    "`planManagedIoportUnmap(...)` as a helper-local ioport release-match foothold",
    "still-missing live `devm_ioport_unmap()` call remains in the same blocked live-MMIO gap family",
]

SURVEY_MARKERS = [
    "helper-local ioport unmap planning",
    "still-missing non-posted wrapper, live ioport-unmap call, and arch-memtype safety gaps",
    "helper-local ioport unmap call planner in `lib/devres.zig`",
    "`.provides_ioport_unmap_call_planning = true`",
    "devm_ioport_unmap(`",
    "blocked `phase13-devres-live-ioport-unmap-call`",
]

HELPER_REQUIRED_MARKERS = [
    ".provides_ioport_unmap_call_planning = true",
    ".touches_live_mmio = false",
    "pub fn planManagedIoportUnmap(",
    "release_matches = tracked_address == candidate_address",
]

CURRENT_PACKET_CHECKER_MARKERS = [
    "devm_ioport_unmap(",
    "helper_scope:unexpected_marker:devm_ioremap_np(",
    "PHASE13_DEVRES_CURRENT_PACKET=pass",
]

FORBIDDEN_HELPER_MARKERS = [
    "devm_ioport_unmap(",
    "devm_ioremap_np(",
    "devm_of_iomap(",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_missing(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:missing_marker:{marker}" for marker in markers if marker not in text]


def collect_unexpected(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:unexpected_marker:{marker}" for marker in markers if marker in text]


def validate(root: Path) -> list[str]:
    issues = [f"missing_file:{rel.as_posix()}" for rel in REQUIRED_FILES if not (root / rel).exists()]
    if issues:
        return issues

    issues.extend(collect_missing(read_text(root / SLICE_PATH), SLICE_MARKERS, "slice"))
    issues.extend(collect_missing(read_text(root / SURVEY_PATH), SURVEY_MARKERS, "survey"))
    issues.extend(collect_missing(read_text(root / HELPER_PATH), HELPER_REQUIRED_MARKERS, "helper"))
    issues.extend(
        collect_missing(
            read_text(root / CURRENT_PACKET_CHECKER_PATH),
            CURRENT_PACKET_CHECKER_MARKERS,
            "current_packet_checker",
        )
    )
    issues.extend(collect_unexpected(read_text(root / HELPER_PATH), FORBIDDEN_HELPER_MARKERS, "helper_live_mmio"))
    return issues


def seed_fixture_tree(root: Path) -> None:
    write_text(root / SLICE_PATH, "\n".join(SLICE_MARKERS) + "\n")
    write_text(root / SURVEY_PATH, "\n".join(SURVEY_MARKERS) + "\n")
    write_text(root / HELPER_PATH, "\n".join(HELPER_REQUIRED_MARKERS) + "\n")
    write_text(root / CURRENT_PACKET_CHECKER_PATH, "\n".join(CURRENT_PACKET_CHECKER_MARKERS) + "\n")


def assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        actual_text = ",".join(actual) or "none"
        expected_text = ",".join(expected) or "none"
        raise AssertionError(f"{label}: actual={actual_text} expected={expected_text}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase13-devres-mmio-ioport-boundary-") as temp_dir:
        root = Path(temp_dir)

        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        seed_fixture_tree(root)
        (root / SURVEY_PATH).unlink()
        assert_only(
            validate(root),
            [f"missing_file:{SURVEY_PATH.as_posix()}"],
            "missing_survey_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / SLICE_PATH,
            "\n".join(marker for marker in SLICE_MARKERS if marker != "live ioport-unmap execution") + "\n",
        )
        assert_only(
            validate(root),
            ["slice:missing_marker:live ioport-unmap execution"],
            "missing_slice_live_ioport_boundary_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / SURVEY_PATH,
            "\n".join(
                marker for marker in SURVEY_MARKERS if marker != "blocked `phase13-devres-live-ioport-unmap-call`"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            ["survey:missing_marker:blocked `phase13-devres-live-ioport-unmap-call`"],
            "missing_survey_live_ioport_gap_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / HELPER_PATH,
            "\n".join(
                marker for marker in HELPER_REQUIRED_MARKERS if marker != ".provides_ioport_unmap_call_planning = true"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            ["helper:missing_marker:.provides_ioport_unmap_call_planning = true"],
            "missing_helper_ioport_planning_flag_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / HELPER_PATH, "\n".join(HELPER_REQUIRED_MARKERS + ["devm_ioport_unmap("]) + "\n")
        assert_only(
            validate(root),
            ["helper_live_mmio:unexpected_marker:devm_ioport_unmap("],
            "unexpected_live_ioport_unmap_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / CURRENT_PACKET_CHECKER_PATH,
            "\n".join(marker for marker in CURRENT_PACKET_CHECKER_MARKERS if marker != "devm_ioport_unmap(") + "\n",
        )
        assert_only(
            validate(root),
            ["current_packet_checker:missing_marker:devm_ioport_unmap("],
            "missing_current_packet_forbidden_ioport_marker_failed",
        )
        case_count += 1

    print("PHASE13_DEVRES_MMIO_IOPORT_BOUNDARY_SELF_TEST=pass")
    print(f"PHASE13_DEVRES_MMIO_IOPORT_BOUNDARY_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 13 devres MMIO/ioport boundary remains helper-first and live-MMIO-free."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        for issue in issues:
            print(issue)
        print("PHASE13_DEVRES_MMIO_IOPORT_BOUNDARY=fail")
        return 1

    print("PHASE13_DEVRES_MMIO_IOPORT_BOUNDARY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
