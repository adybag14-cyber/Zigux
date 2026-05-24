#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SURVEY_PATH = Path("Documentation/zigux/phase5-kobject-sample-survey.md")
SAMPLE_PATH = Path("samples/zigux/kobject_example.zig")
COMPANION_PATH = Path("samples/zigux/kobject_example_attr_group_contract.zig")
REPLAY_PATH = Path("zigux/tests/phase5_kobject_attr_group_contract.zig")
SURVEY_GUARD_PATH = Path("zigux/tests/phase5_kobject_attr_group_contract_survey.zig")
BUILD_PATH = Path("zigux/tests/phase5_build.zig")
MANIFEST_PATH = Path("zigux/tests/phase5_kobject_example_manifest.json")
PUBLIC_SURVEY_PATH = Path("zigux/tests/phase5_kobject_example_survey.zig")

SURVEY_MARKERS = (
    "`samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, and `zigux/tests/phase5_kobject_attr_group_contract_survey.zig` together keep the bounded `foo`/`baz`/`bar` attribute-group contract, shared `0664` mode cues, unnamed-group marker, NULL-terminated attribute-list slot, and shared build-route linkage explicit rather than turning that companion into a fifth Phase 5 sample",
    "`zig test samples/zigux/kobject_example.zig` stays the sample-owned self-check for the ownership-and-lifetime packet",
    "`zig test --dep kobject_example_sample -Mroot=zigux/tests/phase5_kobject_example.zig -Mkobject_example_sample=samples/zigux/kobject_example.zig` stays the focused replay route for the same packet",
    "`zig test zigux/tests/phase5_kobject_example_survey.zig` stays the survey-packet guard for the sample-owned replay, the public-tree-backed manifest-and-survey split, and the shared build-route companion in this runtime",
    "`zig test samples/zigux/kobject_example_attr_group_contract.zig` stays the sample-owned self-check for the bounded attr-group companion",
    "`zig test --dep kobject_attr_group_contract -Mroot=zigux/tests/phase5_kobject_attr_group_contract.zig -Mkobject_attr_group_contract=samples/zigux/kobject_example_attr_group_contract.zig` stays the focused replay route for the same attr-group packet",
    "`zig test zigux/tests/phase5_kobject_attr_group_contract_survey.zig` stays the survey-guard route that checks the companion, focused replay, and shared build-route markers together",
    "does the note still treat `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` as current public-tree-backed companions instead of direct readback proof in this runtime?",
    "- sysfs file creation parity",
    "- `kernel_kobj` integration",
    "- uevent delivery",
    "- loadable module registration",
)

COMPANION_MARKERS = (
    'pub const linux_anchor = "samples/kobject/kobject-example.c";',
    'pub const directory_name = "kobject_example";',
    '.{ .name = "foo", .mode = 0o664, .uses_shared_b_handlers = false }',
    '.{ .name = "baz", .mode = 0o664, .uses_shared_b_handlers = true }',
    '.{ .name = "bar", .mode = 0o664, .uses_shared_b_handlers = true }',
    ".attr_slots_including_null_terminator = specs.len + 1",
    ".group_is_named = false",
)

REPLAY_MARKERS = (
    'const companion = @import("kobject_attr_group_contract");',
    "phase 5 kobject attr-group companion keeps the anchor-local contract reviewable through a focused test surface",
    "phase 5 kobject attr-group companion keeps the foo/baz/bar ownership-facing shape explicit",
    'const expected_names = [_][]const u8{ "foo", "baz", "bar" };',
    "contract.all_modes_match_reference",
    "contract.shared_b_handler_pair_consistent",
)

SURVEY_GUARD_MARKERS = (
    'readFileAlloc(',
    '"samples/zigux/kobject_example_attr_group_contract.zig"',
    '"zigux/tests/phase5_kobject_attr_group_contract.zig"',
    '"zigux/tests/phase5_build.zig"',
    '"phase5-kobject-attr-group-contract-survey-tests"',
    "test_step.dependOn(&run_phase5_kobject_attr_group_contract_tests.step);",
    "test_step.dependOn(&run_phase5_kobject_attr_group_contract_survey_tests.step);",
)

BUILD_MARKERS = (
    '"../../samples/zigux/kobject_example_attr_group_contract.zig"',
    '"phase5_kobject_attr_group_contract.zig"',
    '"phase5_kobject_attr_group_contract_survey.zig"',
    '"phase5-kobject-attr-group-contract-tests"',
    '"phase5-kobject-attr-group-contract-survey-tests"',
    '"phase5-kobject-attr-group-contract"',
    '"phase5-kobject-attr-group-contract-survey"',
)

REQUIRED_PATHS = (
    SAMPLE_PATH,
    COMPANION_PATH,
    REPLAY_PATH,
    SURVEY_GUARD_PATH,
    BUILD_PATH,
    MANIFEST_PATH,
    PUBLIC_SURVEY_PATH,
)


def read_text(root: Path, rel: Path) -> str:
    try:
        return (root / rel).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {rel}") from exc


def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    survey_text = read_text(root, SURVEY_PATH)
    companion_text = read_text(root, COMPANION_PATH)
    replay_text = read_text(root, REPLAY_PATH)
    survey_guard_text = read_text(root, SURVEY_GUARD_PATH)
    build_text = read_text(root, BUILD_PATH)

    for marker in SURVEY_MARKERS:
        if marker not in survey_text:
            failures.append(f"survey:missing_marker:{marker}")

    for marker in COMPANION_MARKERS:
        if marker not in companion_text:
            failures.append(f"companion:missing_marker:{marker}")

    for marker in REPLAY_MARKERS:
        if marker not in replay_text:
            failures.append(f"replay:missing_marker:{marker}")

    for marker in SURVEY_GUARD_MARKERS:
        if marker not in survey_guard_text:
            failures.append(f"survey_guard:missing_marker:{marker}")

    for marker in BUILD_MARKERS:
        if marker not in build_text:
            failures.append(f"build:missing_marker:{marker}")

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            failures.append(f"repo:missing_path:{rel}")

    return failures


def placeholder_survey() -> str:
    return "\n".join(
        [
            "# Phase 5 Kobject Sample Survey",
            "",
            *SURVEY_MARKERS,
            "",
            f"`{MANIFEST_PATH}`",
            f"`{PUBLIC_SURVEY_PATH}`",
        ]
    ) + "\n"


def placeholder_companion() -> str:
    return "\n".join(
        [
            "pub const linux_anchor = \"samples/kobject/kobject-example.c\";",
            "pub const directory_name = \"kobject_example\";",
            ".{ .name = \"foo\", .mode = 0o664, .uses_shared_b_handlers = false }",
            ".{ .name = \"baz\", .mode = 0o664, .uses_shared_b_handlers = true }",
            ".{ .name = \"bar\", .mode = 0o664, .uses_shared_b_handlers = true }",
            ".attr_slots_including_null_terminator = specs.len + 1",
            ".group_is_named = false",
        ]
    ) + "\n"


def placeholder_replay() -> str:
    return "\n".join(REPLAY_MARKERS) + "\n"


def placeholder_survey_guard() -> str:
    return "\n".join(SURVEY_GUARD_MARKERS) + "\n"


def placeholder_build() -> str:
    return "\n".join(BUILD_MARKERS) + "\n"


def seed(root: Path) -> None:
    write_text(root, SURVEY_PATH, placeholder_survey())
    write_text(root, SAMPLE_PATH, "sample present\n")
    write_text(root, COMPANION_PATH, placeholder_companion())
    write_text(root, REPLAY_PATH, placeholder_replay())
    write_text(root, SURVEY_GUARD_PATH, placeholder_survey_guard())
    write_text(root, BUILD_PATH, placeholder_build())
    write_text(root, MANIFEST_PATH, "{}\n")
    write_text(root, PUBLIC_SURVEY_PATH, "survey present\n")


def expect_exact(label: str, failures: list[str], expected: list[str]) -> None:
    if failures != expected:
        raise AssertionError(f"{label}: expected {expected}, got {failures}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase5_kobject_survey_packet_") as tmpdir:
        root = Path(tmpdir)
        seed(root)

        cases = 0
        expect_exact("baseline", collect_failures(root), [])
        cases += 1

        mutated = root / "missing_survey_marker"
        seed(mutated)
        write_text(mutated, SURVEY_PATH, placeholder_survey().replace(SURVEY_MARKERS[0], ""))
        expect_exact(
            "missing survey marker",
            collect_failures(mutated),
            [f"survey:missing_marker:{SURVEY_MARKERS[0]}"],
        )
        cases += 1

        mutated = root / "missing_validation_route"
        seed(mutated)
        write_text(mutated, SURVEY_PATH, placeholder_survey().replace(SURVEY_MARKERS[5], ""))
        expect_exact(
            "missing validation route",
            collect_failures(mutated),
            [f"survey:missing_marker:{SURVEY_MARKERS[5]}"],
        )
        cases += 1

        mutated = root / "missing_non_goal"
        seed(mutated)
        write_text(mutated, SURVEY_PATH, placeholder_survey().replace(SURVEY_MARKERS[10], ""))
        expect_exact(
            "missing non-goal",
            collect_failures(mutated),
            [f"survey:missing_marker:{SURVEY_MARKERS[10]}"],
        )
        cases += 1

        mutated = root / "missing_companion_marker"
        seed(mutated)
        write_text(mutated, COMPANION_PATH, placeholder_companion().replace(COMPANION_MARKERS[2], ""))
        expect_exact(
            "missing companion marker",
            collect_failures(mutated),
            [f"companion:missing_marker:{COMPANION_MARKERS[2]}"],
        )
        cases += 1

        mutated = root / "missing_replay_marker"
        seed(mutated)
        write_text(mutated, REPLAY_PATH, placeholder_replay().replace(REPLAY_MARKERS[3], ""))
        expect_exact(
            "missing replay marker",
            collect_failures(mutated),
            [f"replay:missing_marker:{REPLAY_MARKERS[3]}"],
        )
        cases += 1

        mutated = root / "missing_survey_guard_marker"
        seed(mutated)
        write_text(mutated, SURVEY_GUARD_PATH, placeholder_survey_guard().replace(SURVEY_GUARD_MARKERS[4], ""))
        expect_exact(
            "missing survey guard marker",
            collect_failures(mutated),
            [f"survey_guard:missing_marker:{SURVEY_GUARD_MARKERS[4]}"],
        )
        cases += 1

        mutated = root / "missing_build_marker"
        seed(mutated)
        write_text(mutated, BUILD_PATH, placeholder_build().replace(BUILD_MARKERS[3], ""))
        expect_exact(
            "missing build marker",
            collect_failures(mutated),
            [f"build:missing_marker:{BUILD_MARKERS[3]}"],
        )
        cases += 1

        mutated = root / "missing_required_path"
        seed(mutated)
        (mutated / MANIFEST_PATH).unlink()
        expect_exact(
            "missing required path",
            collect_failures(mutated),
            [f"repo:missing_path:{MANIFEST_PATH}"],
        )
        cases += 1

        mutated = root / "allows_extra_context"
        seed(mutated)
        write_text(
            mutated,
            SURVEY_PATH,
            placeholder_survey() + "\nSupporting note: keep the mixed direct-versus-public-tree-backed split explicit.\n",
        )
        expect_exact("allows extra context", collect_failures(mutated), [])
        cases += 1

        expected_case_count = 10
        if cases != expected_case_count:
            raise AssertionError(f"expected {expected_case_count} self-test cases, ran {cases}")

    print("PHASE5_KOBJECT_SURVEY_PACKET_SELF_TEST=pass")
    print(f"PHASE5_KOBJECT_SURVEY_PACKET_SELF_TEST_CASES={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        print("PHASE5_KOBJECT_SURVEY_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE5_KOBJECT_SURVEY_PACKET=pass")
    print(f"PHASE5_KOBJECT_SURVEY_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE5_KOBJECT_SURVEY_PACKET_SURVEY_MARKER_COUNT={len(SURVEY_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
