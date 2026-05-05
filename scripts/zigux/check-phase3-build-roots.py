#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys
import tempfile


SCRIPT_PATH = Path(__file__).resolve()
BUILD_FILE_REL = "zigux/tests/build.zig"
ROOT_SOURCE_FILE_RE = re.compile(r'\.root_source_file\s*=\s*b\.path\("([^"]+)"\)')


def derive_root(script_path: Path) -> Path:
    resolved = script_path.resolve()
    if resolved.parent.name == "zigux" and resolved.parent.parent.name == "scripts":
        return resolved.parents[2]
    return resolved.parent


ROOT = derive_root(SCRIPT_PATH)


def _build_path(root: Path) -> Path:
    return root / BUILD_FILE_REL


def discover_root_source_files(root: Path) -> list[tuple[str, str]]:
    build_path = _build_path(root)
    text = build_path.read_text(encoding="utf-8")
    resolved: list[tuple[str, str]] = []
    seen: set[str] = set()
    for rel_path in ROOT_SOURCE_FILE_RE.findall(text):
        candidate = (build_path.parent / rel_path).resolve()
        try:
            normalized = candidate.relative_to(root).as_posix()
        except ValueError:
            normalized = candidate.as_posix()
        if normalized in seen:
            continue
        seen.add(normalized)
        resolved.append((rel_path, normalized))
    return resolved


def validate(root: Path) -> tuple[list[str], int]:
    build_path = _build_path(root)
    if not build_path.exists():
        return ([f"missing_build_file:{BUILD_FILE_REL}"], 0)

    references = discover_root_source_files(root)
    missing = [
        f"missing_root_source_file:{rel_path}:{normalized}"
        for rel_path, normalized in references
        if not (root / normalized).exists()
    ]
    return missing, len(references)


def write_fixture(root: Path) -> None:
    build_path = _build_path(root)
    build_path.parent.mkdir(parents=True, exist_ok=True)
    build_path.write_text(
        "\n".join(
            (
                'const std = @import("std");',
                "",
                "pub fn build(b: *std.Build) void {",
                "    const existing = b.createModule(.{",
                '        .root_source_file = b.path("../helpers/existing_plan.zig"),',
                "    });",
                "    _ = existing;",
                "    const duplicate = b.createModule(.{",
                '        .root_source_file = b.path("../helpers/existing_plan.zig"),',
                "    });",
                "    _ = duplicate;",
                "}",
                "",
            )
        ),
        encoding="utf-8",
        newline="\n",
    )
    helper_path = root / "zigux/helpers/existing_plan.zig"
    helper_path.parent.mkdir(parents=True, exist_ok=True)
    helper_path.write_text("pub fn noop() void {}\n", encoding="utf-8", newline="\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_build_roots_") as tmp_dir:
        root = Path(tmp_dir) / "repo"
        write_fixture(root)

        if derive_root(root / "scripts/zigux/check-phase3-build-roots.py") != root:
            raise SystemExit("phase3-build-roots-self-test:derive_root_nested_failed")
        if derive_root(root / "check-phase3-build-roots.py") != root:
            raise SystemExit("phase3-build-roots-self-test:derive_root_shallow_failed")

        missing, reference_count = validate(root)
        if missing:
            raise SystemExit(
                "phase3-build-roots-self-test:baseline_failed:"
                f"missing={','.join(missing)}"
            )
        if reference_count != 1:
            raise SystemExit(
                "phase3-build-roots-self-test:dedupe_failed:"
                f"count={reference_count}"
            )

        build_path = _build_path(root)
        build_text = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            build_text.replace(
                '../helpers/existing_plan.zig',
                '../helpers/missing_plan.zig',
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        missing, reference_count = validate(root)
        expected = "missing_root_source_file:../helpers/missing_plan.zig:zigux/helpers/missing_plan.zig"
        if missing != [expected]:
            raise SystemExit(
                "phase3-build-roots-self-test:missing_guard_failed:"
                f"actual={','.join(missing) if missing else 'none'}"
            )
        if reference_count != 2:
            raise SystemExit(
                "phase3-build-roots-self-test:count_failed:"
                f"count={reference_count}"
            )

    print("PHASE3_BUILD_ROOTS_SELF_TEST=pass")
    print("PHASE3_BUILD_ROOTS_SELF_TEST_CASE_COUNT=4")
    return 0


if "--self-test" in sys.argv[1:]:
    raise SystemExit(run_self_test())

missing, reference_count = validate(ROOT)
if missing:
    print("PHASE3_BUILD_ROOTS=fail")
    print(f"PHASE3_BUILD_ROOT_REFERENCE_COUNT={reference_count}")
    for issue in missing:
        print(issue)
    raise SystemExit(1)

print("PHASE3_BUILD_ROOTS=pass")
print(f"PHASE3_BUILD_ROOT_REFERENCE_COUNT={reference_count}")
