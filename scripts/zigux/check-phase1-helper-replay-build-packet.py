#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

BUILD_REL = Path("zigux/tests/phase1_helpers_build.zig")
REPLAY_REL = Path("zigux/tests/phase1_helpers.zig")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
PARITY_REL = Path("scripts/zigux/check-phase1-parity.py")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")

EXPECTED_HELPER_MODULES = (
    "argv_split",
    "cmdline",
    "find_bit",
    "bitmap",
    "ctype",
    "hweight",
    "list_sort",
    "rbtree",
    "string",
    "slab",
    "str_error_r",
    "vsprintf",
    "zalloc",
)

EXPECTED_BUILD_MARKERS = (
    '.root_source_file = b.path("phase1_helpers.zig"),',
    '.name = "phase1-helpers",',
    '"Run the focused Phase 1 helper replay anchor from zigux/tests",',
)

EXPECTED_REPLAY_MARKERS = (
    'const fixture_bytes = @embedFile("fixtures/phase1_helpers.json");',
    "const Fixture = struct {",
    'test "phase 1 helper ports match committed parity fixture" {',
)

EXPECTED_FOCUSED_ROUTE = (
    "zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig"
)

EXPECTED_FIXTURE_SECTIONS = (
    "find_bit",
    "bitmap",
    "string",
    "rbtree",
    "argv_split",
    "cmdline",
    "ctype",
    "hweight",
    "list_sort",
    "zalloc",
    "str_error_r",
    "slab",
    "vsprintf",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def ensure(condition: bool, issue: str, issues: list[str]) -> None:
    if not condition:
        issues.append(issue)


def ensure_exact_once(text: str, marker: str, label: str, issues: list[str]) -> None:
    count = text.count(marker)
    if count != 1:
        issues.append(f"{label}:expected=1:actual={count}")


def check_build_file(root: Path, issues: list[str]) -> None:
    build_text = read_text(root / BUILD_REL)
    for marker in EXPECTED_BUILD_MARKERS:
        ensure_exact_once(build_text, marker, f"build_marker:{marker}", issues)
    for module in EXPECTED_HELPER_MODULES:
        ensure(
            f'const {module}_module = b.createModule' in build_text,
            f"build_helper_module_missing:{module}",
            issues,
        )
        ensure(
            f'root_module.addImport("{module}", {module}_module);' in build_text,
            f"build_root_import_missing:{module}",
            issues,
        )
    ensure(
        'bitmap_module.addImport("find_bit", find_bit_module);' in build_text,
        "build_bitmap_find_bit_link_missing",
        issues,
    )


def check_replay_file(root: Path, issues: list[str]) -> None:
    replay_text = read_text(root / REPLAY_REL)
    for marker in EXPECTED_REPLAY_MARKERS:
        ensure_exact_once(replay_text, marker, f"replay_marker:{marker}", issues)


def check_fixture(root: Path, issues: list[str]) -> None:
    try:
        payload = json.loads(read_text(root / FIXTURE_REL))
    except json.JSONDecodeError as exc:
        issues.append(f"fixture_invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}")
        return
    ensure(isinstance(payload, dict), "fixture_not_object", issues)
    if isinstance(payload, dict):
        ensure(
            tuple(payload.keys()) == EXPECTED_FIXTURE_SECTIONS,
            "fixture_section_order_drift",
            issues,
        )
        slab = payload.get("slab")
        ensure(isinstance(slab, dict), "fixture_slab_not_object", issues)
        if isinstance(slab, dict):
            ensure(
                slab.get("zero_after_kmalloc") is True,
                "fixture_slab_zero_after_kmalloc_drift",
                issues,
            )


def check_parity_checker(root: Path, issues: list[str]) -> None:
    parity_text = read_text(root / PARITY_REL)
    ensure_exact_once(
        parity_text,
        'REPLAY_BUILD_REL = Path("zigux/tests/phase1_helpers_build.zig")',
        "parity_replay_build_rel",
        issues,
    )
    for marker in EXPECTED_BUILD_MARKERS:
        ensure(
            marker in parity_text,
            f"parity_build_marker_missing:{marker}",
            issues,
        )
    ensure(
        "PHASE1_PARITY_REPLAY=present" in parity_text,
        "parity_replay_present_output_missing",
        issues,
    )


def check_readmes(root: Path, issues: list[str]) -> None:
    scripts_readme = read_text(root / SCRIPTS_README_REL)
    ensure(
        EXPECTED_FOCUSED_ROUTE in scripts_readme,
        "scripts_readme_focused_route_missing",
        issues,
    )
    tests_readme = read_text(root / TESTS_README_REL)
    ensure(
        EXPECTED_FOCUSED_ROUTE in tests_readme,
        "tests_readme_focused_route_missing",
        issues,
    )
    ensure(
        "- `zigux/tests/phase1_helpers_build.zig`" in tests_readme,
        "tests_readme_build_file_bullet_missing",
        issues,
    )


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in (
        BUILD_REL,
        REPLAY_REL,
        FIXTURE_REL,
        PARITY_REL,
        SCRIPTS_README_REL,
        TESTS_README_REL,
    ):
        ensure((root / rel).exists(), f"missing:{rel.as_posix()}", issues)
    if issues:
        return issues

    check_build_file(root, issues)
    check_replay_file(root, issues)
    check_fixture(root, issues)
    check_parity_checker(root, issues)
    check_readmes(root, issues)
    return issues


def build_sample_root(root: Path) -> None:
    build_text = """const std = @import(\"std\");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path(\"phase1_helpers.zig\"),
        .target = target,
        .optimize = optimize,
    });
"""
    for module in EXPECTED_HELPER_MODULES:
        build_text += f"""    const {module}_module = b.createModule(.{{
        .root_source_file = b.path(\"../../tools/lib/{module}.zig\"),
        .target = target,
        .optimize = optimize,
    }});
"""
    build_text += """
    bitmap_module.addImport(\"find_bit\", find_bit_module);
"""
    for module in EXPECTED_HELPER_MODULES:
        build_text += f'    root_module.addImport(\"{module}\", {module}_module);\n'
    build_text += """

    const tests = b.addTest(.{
        .name = \"phase1-helpers\",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const phase1_helpers = b.step(
        \"phase1-helpers\",
        \"Run the focused Phase 1 helper replay anchor from zigux/tests\",
    );
    phase1_helpers.dependOn(&run_tests.step);
}
"""
    replay_text = "\n".join(
        (
            'const fixture_bytes = @embedFile(\"fixtures/phase1_helpers.json\");',
            "",
            "const Fixture = struct {",
            "    slab: struct {",
            "        zero_after_kmalloc: bool,",
            "    },",
            "};",
            "",
            'test \"phase 1 helper ports match committed parity fixture\" {',
            "    _ = fixture_bytes;",
            "}",
        )
    ) + "\n"
    fixture_payload = {section: {} for section in EXPECTED_FIXTURE_SECTIONS}
    fixture_payload["slab"]["zero_after_kmalloc"] = True
    parity_text = "\n".join(
        (
            'REPLAY_BUILD_REL = Path(\"zigux/tests/phase1_helpers_build.zig\")',
            "EXPECTED_REPLAY_BUILD_MARKERS = (",
            '    \' .root_source_file = b.path(\"phase1_helpers.zig\"),\'',
            '    \' .name = \"phase1-helpers\",\'',
            '    \'\"Run the focused Phase 1 helper replay anchor from zigux/tests\",\'',
            ")",
            'print(\"PHASE1_PARITY_REPLAY=present\")',
        )
    ) + "\n"
    scripts_readme = (
        "# scripts/zigux\n\n"
        f"- `{EXPECTED_FOCUSED_ROUTE}` keeps a focused fixture-backed replay anchor.\n"
    )
    tests_readme = (
        "# zigux/tests\n\n"
        "- `zigux/tests/phase1_helpers_build.zig`\n"
        f"- current focused Phase 1 helper replay route: `{EXPECTED_FOCUSED_ROUTE}`\n"
    )

    write_text(root / BUILD_REL, build_text)
    write_text(root / REPLAY_REL, replay_text)
    write_text(root / FIXTURE_REL, json.dumps(fixture_payload, indent=2) + "\n")
    write_text(root / PARITY_REL, parity_text)
    write_text(root / SCRIPTS_README_REL, scripts_readme)
    write_text(root / TESTS_README_REL, tests_readme)


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        print("PHASE1_HELPER_REPLAY_BUILD_PACKET=fail")
        for issue in issues:
            print(f"PHASE1_HELPER_REPLAY_BUILD_PACKET_ISSUE={issue}")
        return 1
    print("PHASE1_HELPER_REPLAY_BUILD_PACKET=pass")
    print(f"PHASE1_HELPER_REPLAY_BUILD_PACKET_HELPER_COUNT={len(EXPECTED_HELPER_MODULES)}")
    print(f"PHASE1_HELPER_REPLAY_BUILD_PACKET_BUILD_MARKER_COUNT={len(EXPECTED_BUILD_MARKERS)}")
    print(f"PHASE1_HELPER_REPLAY_BUILD_PACKET_SECTION_COUNT={len(EXPECTED_FIXTURE_SECTIONS)}")
    print(f"PHASE1_HELPER_REPLAY_BUILD_PACKET_ROUTE={EXPECTED_FOCUSED_ROUTE}")
    return 0


def run_self_test() -> int:
    import tempfile

    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1_helper_replay_build_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        case_count += 1

        build_sample_root(root)
        write_text(root / TESTS_README_REL, "# zigux/tests\n")
        issues = collect_issues(root)
        assert "tests_readme_focused_route_missing" in issues
        case_count += 1

        build_sample_root(root)
        write_text(
            root / PARITY_REL,
            read_text(root / PARITY_REL).replace(
                '.name = \"phase1-helpers\",',
                '.name = \"phase1-host-tools-smoke\",',
            ),
        )
        issues = collect_issues(root)
        assert any(issue.startswith("parity_build_marker_missing:") for issue in issues)
        case_count += 1

        build_sample_root(root)
        write_text(
            root / BUILD_REL,
            read_text(root / BUILD_REL).replace(
                '    root_module.addImport(\"zalloc\", zalloc_module);\n',
                "",
            ),
        )
        issues = collect_issues(root)
        assert "build_root_import_missing:zalloc" in issues
        case_count += 1

        build_sample_root(root)
        payload = json.loads(read_text(root / FIXTURE_REL))
        payload["slab"]["zero_after_kmalloc"] = False
        write_text(root / FIXTURE_REL, json.dumps(payload, indent=2) + "\n")
        issues = collect_issues(root)
        assert "fixture_slab_zero_after_kmalloc_drift" in issues
        case_count += 1

    print("PHASE1_HELPER_REPLAY_BUILD_PACKET_SELF_TEST=pass")
    print(f"PHASE1_HELPER_REPLAY_BUILD_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the focused Phase 1 helper replay build packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0
    if args.self_test:
        return run_self_test()
    return run_check(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
