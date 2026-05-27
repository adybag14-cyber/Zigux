#!/usr/bin/env python3
"""Fail-closed checker for the Phase 12 libbpf reviewability build packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


CHECK_NAME = "PHASE12_LIBBPF_REVIEWABILITY_BUILD"

BUILD_PATH = Path("zigux/tests/phase12_libbpf_reviewability_build.zig")
REVIEWABILITY_PATH = Path("zigux/tests/phase12_libbpf_reviewability.zig")
VERIFY_NOTE_PATH = Path("Documentation/zigux/phase12-libbpf-verify-shard-note.md")
SURVEY_PATH = Path("Documentation/zigux/phase12-libbpf-segment-survey.md")
SNAPSHOT_PATH = Path("zigux/tests/fixtures/phase12_libbpf_snapshot.json")
SNAPSHOT_DETERMINISM_PATH = Path(
    "zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json"
)

REQUIRED_FILES = (
    BUILD_PATH,
    REVIEWABILITY_PATH,
    VERIFY_NOTE_PATH,
    SURVEY_PATH,
    SNAPSHOT_PATH,
    SNAPSHOT_DETERMINISM_PATH,
)

BUILD_MARKERS = (
    '../../tools/lib/bpf/zigux_segments/cpu_mask.zig',
    '../../tools/lib/bpf/zigux_segments/type_names.zig',
    '../../tools/lib/bpf/zigux_segments/logging.zig',
    '../../tools/lib/bpf/zigux_segments/pin_path.zig',
    '../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig',
    '../../tools/lib/bpf/zigux_segments/online_cpu_routing.zig',
    'phase12_libbpf_reviewability.zig',
    'reviewability_root_module.addImport("cpu_mask", cpu_mask_module);',
    'reviewability_root_module.addImport("bpf_type_names", type_names_module);',
    'reviewability_root_module.addImport("logging", logging_module);',
    'reviewability_root_module.addImport("pin_path", pin_path_module);',
    'reviewability_root_module.addImport("perf_buffer_poll", perf_buffer_poll_module);',
    'reviewability_root_module.addImport("online_cpu_routing", online_cpu_routing_module);',
    '.name = "phase12-libbpf-reviewability-tests",',
    'const test_step = b.step(',
    '"test"',
    '"Run the Phase 12 libbpf reviewability tests"',
)

REVIEWABILITY_MARKERS = (
    'test "phase12 libbpf reviewability gate keeps the current snapshot anchor exact"',
    'test "phase12 libbpf reviewability gate keeps the helper-local determinism fixture exact"',
    'test "phase12 libbpf reviewability gate keeps the parked replay boundaries and note-owned anchors explicit"',
    'test "phase12 libbpf reviewability gate still compiles the surviving helper-first footing"',
    '"P12-L16"',
    '"P12-L17"',
    'zigux/tests/fixtures/phase12_libbpf_snapshot.json',
    'zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json',
    'Documentation/zigux/phase12-libbpf-segment-survey.md',
    'Documentation/zigux/phase12-libbpf-verify-shard-note.md',
    'Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md',
    'Documentation/zigux/phase12-release-coordination-matrix.md',
)

VERIFY_NOTE_MARKERS = (
    '- focused reviewability-lab build route: `zig build test --build-file zigux/tests/phase12_libbpf_reviewability_build.zig --summary all`',
    '- lane-marker guard: `scripts/zigux/check-phase12-libbpf-lane-marker.py`',
    '- snapshot checker: `scripts/zigux/check-phase12-libbpf-snapshot.py`',
)

SURVEY_MARKERS = (
    'checked-in `zigux/tests/phase12_libbpf_reviewability.zig` gate',
    '`zigux/tests/fixtures/phase12_libbpf_snapshot.json`',
    '`zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`',
)


class CheckFailure(RuntimeError):
    pass


def read_text(root: Path, rel_path: Path) -> str:
    try:
        return (root / rel_path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CheckFailure(f"missing file: {rel_path}") from exc


def require_markers(label: Path, text: str, markers: tuple[str, ...]) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckFailure(f"{label} missing marker: {marker}")


def check(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).is_file():
            raise CheckFailure(f"missing file: {rel_path}")

    require_markers(BUILD_PATH, read_text(root, BUILD_PATH), BUILD_MARKERS)
    require_markers(
        REVIEWABILITY_PATH,
        read_text(root, REVIEWABILITY_PATH),
        REVIEWABILITY_MARKERS,
    )
    require_markers(
        VERIFY_NOTE_PATH,
        read_text(root, VERIFY_NOTE_PATH),
        VERIFY_NOTE_MARKERS,
    )
    require_markers(SURVEY_PATH, read_text(root, SURVEY_PATH), SURVEY_MARKERS)


def write_fixture(root: Path) -> None:
    fixture_map = {
        BUILD_PATH: "\n".join(
            [
                "const std = @import(\"std\");",
                *BUILD_MARKERS,
            ]
        )
        + "\n",
        REVIEWABILITY_PATH: "\n".join(
            [
                "const std = @import(\"std\");",
                *REVIEWABILITY_MARKERS,
            ]
        )
        + "\n",
        VERIFY_NOTE_PATH: "# verify note\n" + "\n".join(VERIFY_NOTE_MARKERS) + "\n",
        SURVEY_PATH: "# survey\n" + "\n".join(SURVEY_MARKERS) + "\n",
        SNAPSHOT_PATH: '{\n  "lane_key": "P12-L16"\n}\n',
        SNAPSHOT_DETERMINISM_PATH: '{\n  "lane_key": "P12-L17"\n}\n',
    }

    for rel_path, text in fixture_map.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")


def expect_failure(root: Path, fragment: str) -> None:
    try:
        check(root)
    except CheckFailure as exc:
        if fragment not in str(exc):
            raise
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase12-libbpf-reviewability-build-") as tmp:
        root = Path(tmp)

        write_fixture(root)
        check(root)
        cases += 1

        write_fixture(root)
        (root / BUILD_PATH).write_text("const std = @import(\"std\");\n", encoding="utf-8")
        expect_failure(root, str(BUILD_PATH))
        cases += 1

        write_fixture(root)
        (root / REVIEWABILITY_PATH).write_text(
            "const std = @import(\"std\");\n", encoding="utf-8"
        )
        expect_failure(root, str(REVIEWABILITY_PATH))
        cases += 1

        write_fixture(root)
        (root / VERIFY_NOTE_PATH).write_text("# verify note\n", encoding="utf-8")
        expect_failure(root, str(VERIFY_NOTE_PATH))
        cases += 1

        write_fixture(root)
        (root / SURVEY_PATH).write_text("# survey\n", encoding="utf-8")
        expect_failure(root, str(SURVEY_PATH))
        cases += 1

        write_fixture(root)
        (root / SNAPSHOT_PATH).unlink()
        expect_failure(root, str(SNAPSHOT_PATH))
        cases += 1

        write_fixture(root)
        (root / SNAPSHOT_DETERMINISM_PATH).unlink()
        expect_failure(root, str(SNAPSHOT_DETERMINISM_PATH))
        cases += 1

    print(f"{CHECK_NAME}_SELF_TEST=pass")
    print(f"{CHECK_NAME}_SELF_TEST_CASES={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root to inspect.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run fixture-backed self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        check(args.root)
    except CheckFailure as exc:
        print(f"{CHECK_NAME}=fail:{exc}")
        return 1

    print(f"{CHECK_NAME}=pass")
    print(f"{CHECK_NAME}_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
