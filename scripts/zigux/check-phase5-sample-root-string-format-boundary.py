#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SAMPLE_ROOT_PATH = Path("samples/zigux/README.md")

REQUIRED_MARKERS = (
    "Current `master` also keeps the bounded non-runtime trace-events packet visible through the broader sample-root companion `samples/zigux/trace_events_sample.zig`, the direct formatting companion `samples/zigux/trace_events_string_formatting_sample.zig`, and the shared Phase 5 reminder packet.",
    "* `samples/zigux/trace_events_string_formatting_sample.zig` stays the direct sample-root proof for the bounded formatting companion, while `samples/zigux/trace_events_sample.zig` stays broader public-tree-backed companion evidence rather than a returned full trace-events port or a fifth sample",
    "Current `master` does ship one bounded `*string*` companion through `samples/zigux/trace_events_string_formatting_sample.zig`, but keep it tied to the non-runtime `trace_events` anchor instead of treating it as a standalone helper packet or a fifth Phase 5 sample.",
    "Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here. Keep that formatting boundary tied to `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md` and the bounded `samples/zigux/trace_events_string_formatting_sample.zig` companion.",
)

FORBIDDEN_MARKERS = (
    "returned full trace-events port",
    "standalone helper packet or a fifth Phase 5 sample",
)


def read_text(root: Path, path: Path) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, path: Path, text: str) -> None:
    full = root / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(text, encoding="utf-8")


def placeholder() -> str:
    return "# README.md\n\n" + "\n\n".join(REQUIRED_MARKERS) + "\n"


def seed(root: Path) -> None:
    write_text(root, SAMPLE_ROOT_PATH, placeholder())


def collect_failures(root: Path) -> list[str]:
    text = read_text(root, SAMPLE_ROOT_PATH)
    failures: list[str] = []

    for marker in REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"missing_text:{marker}")

    if "treating it as a standalone helper packet or a fifth Phase 5 sample" not in text:
        failures.append("missing_boundary_phrase:string_companion")

    if "Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here." not in text:
        failures.append("missing_boundary_phrase:broad_format")

    if FORBIDDEN_MARKERS[0] not in text:
        failures.append(f"missing_boundary_phrase:{FORBIDDEN_MARKERS[0]}")

    return failures


def expect_exact(label: str, failures: list[str], expected: list[str]) -> None:
    if failures != expected:
        raise AssertionError(f"{label}: expected {expected}, got {failures}")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 5

    with tempfile.TemporaryDirectory(prefix="phase5_sample_root_string_format_") as tmpdir:
        root = Path(tmpdir)

        seed(root)
        expect_exact("baseline", collect_failures(root), [])
        checks_run += 1

        mutated = root / "missing_packet_marker"
        seed(mutated)
        write_text(mutated, SAMPLE_ROOT_PATH, placeholder().replace(REQUIRED_MARKERS[0], ""))
        expect_exact(
            "missing_packet_marker",
            collect_failures(mutated),
            [f"missing_text:{REQUIRED_MARKERS[0]}"],
        )
        checks_run += 1

        mutated = root / "missing_direct_companion_marker"
        seed(mutated)
        write_text(mutated, SAMPLE_ROOT_PATH, placeholder().replace(REQUIRED_MARKERS[1], ""))
        expect_exact(
            "missing_direct_companion_marker",
            collect_failures(mutated),
            [
                f"missing_text:{REQUIRED_MARKERS[1]}",
                f"missing_boundary_phrase:{FORBIDDEN_MARKERS[0]}",
            ],
        )
        checks_run += 1

        mutated = root / "missing_string_boundary_marker"
        seed(mutated)
        write_text(mutated, SAMPLE_ROOT_PATH, placeholder().replace(REQUIRED_MARKERS[2], ""))
        expect_exact(
            "missing_string_boundary_marker",
            collect_failures(mutated),
            [
                f"missing_text:{REQUIRED_MARKERS[2]}",
                "missing_boundary_phrase:string_companion",
            ],
        )
        checks_run += 1

        mutated = root / "missing_broad_format_marker"
        seed(mutated)
        write_text(mutated, SAMPLE_ROOT_PATH, placeholder().replace(REQUIRED_MARKERS[3], ""))
        expect_exact(
            "missing_broad_format_marker",
            collect_failures(mutated),
            [
                f"missing_text:{REQUIRED_MARKERS[3]}",
                "missing_boundary_phrase:broad_format",
            ],
        )
        checks_run += 1

    if checks_run != expected_case_count:
        raise AssertionError(f"expected {expected_case_count} checks, ran {checks_run}")

    print("PHASE5_SAMPLE_ROOT_STRING_FORMAT_BOUNDARY_SELF_TEST=pass")
    print(f"PHASE5_SAMPLE_ROOT_STRING_FORMAT_BOUNDARY_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 5 sample-root README keeps the bounded trace-events string/formatting companion boundary explicit."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE5_SAMPLE_ROOT_STRING_FORMAT_BOUNDARY=pass")
    print(f"PHASE5_SAMPLE_ROOT_STRING_FORMAT_BOUNDARY_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
