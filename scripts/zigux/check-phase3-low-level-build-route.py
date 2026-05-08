#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


FILE_PATH = Path(__file__).resolve()
ROOT = FILE_PATH.parents[2] if len(FILE_PATH.parents) >= 3 else FILE_PATH.parent

BUILD_REL = "zigux/tests/build.zig"
ABI_TEST_REL = "zigux/tests/phase3_abi.zig"
LOW_LEVEL_TEST_REL = "zigux/tests/phase3_low_level_wrappers.zig"

BUILD_REQUIRED_MARKERS = (
    'const phase3_root_module = b.createModule(.{',
    '.root_source_file = b.path("phase3_abi.zig"),',
    'phase3_root_module.addImport("atomic_helpers", atomic_helpers_module);',
    'phase3_root_module.addImport("barrier_helpers", barrier_helpers_module);',
    'phase3_root_module.addImport("mmio_helpers", mmio_helpers_module);',
    'phase3_root_module.addImport("narrow_unsafe", narrow_unsafe_module);',
    'const phase3_step = b.step("phase3-test", "Run Phase 3 ABI and interop substrate tests");',
)

ABI_REQUIRED_MARKERS = (
    'const atomic = @import("atomic_helpers");',
    'const barrier = @import("barrier_helpers");',
    'const mmio = @import("mmio_helpers");',
    'const narrow = @import("narrow_unsafe");',
)

LOW_LEVEL_REQUIRED_MARKERS = (
    'const atomic = @import("atomic_helpers");',
    'const barrier = @import("barrier_helpers");',
    'const mmio = @import("mmio_helpers");',
    'const narrow = @import("narrow_unsafe");',
    'test "phase3 low-level wrappers cover the shipped helper surface directly"',
)

SELF_TEST_CASE_COUNT = 4


def require_tokens(issues: list[str], rel: str, text: str, tokens: tuple[str, ...]) -> None:
    for token in tokens:
        if token not in text:
            issues.append(f"missing_token:{rel}:{token}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for rel, tokens in (
        (BUILD_REL, BUILD_REQUIRED_MARKERS),
        (ABI_TEST_REL, ABI_REQUIRED_MARKERS),
        (LOW_LEVEL_TEST_REL, LOW_LEVEL_REQUIRED_MARKERS),
    ):
        path = root / rel
        if not path.exists():
            issues.append(f"missing_file:{rel}")
            continue
        require_tokens(issues, rel, path.read_text(encoding="utf-8"), tokens)
    return issues


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def build_valid_workspace(root: Path) -> None:
    write(
        root / BUILD_REL,
        "\n".join(
            (
                "const phase3_root_module = b.createModule(.{",
                '    .root_source_file = b.path("phase3_abi.zig"),',
                "});",
                'phase3_root_module.addImport("atomic_helpers", atomic_helpers_module);',
                'phase3_root_module.addImport("barrier_helpers", barrier_helpers_module);',
                'phase3_root_module.addImport("mmio_helpers", mmio_helpers_module);',
                'phase3_root_module.addImport("narrow_unsafe", narrow_unsafe_module);',
                'const phase3_step = b.step("phase3-test", "Run Phase 3 ABI and interop substrate tests");',
            )
        )
        + "\n",
    )
    write(
        root / ABI_TEST_REL,
        "\n".join(ABI_REQUIRED_MARKERS) + "\n",
    )
    write(
        root / LOW_LEVEL_TEST_REL,
        "\n".join(LOW_LEVEL_REQUIRED_MARKERS) + "\n",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_low_level_build_route_") as tmp_dir:
        root = Path(tmp_dir)
        build_valid_workspace(root)
        assert validate(root) == [], validate(root)

        write(root / BUILD_REL, (root / BUILD_REL).read_text(encoding="utf-8").replace(
            'phase3_root_module.addImport("mmio_helpers", mmio_helpers_module);\n', "", 1
        ))
        issues = validate(root)
        assert (
            'missing_token:zigux/tests/build.zig:phase3_root_module.addImport("mmio_helpers", mmio_helpers_module);'
            in issues
        ), issues

        build_valid_workspace(root)
        write(root / ABI_TEST_REL, (root / ABI_TEST_REL).read_text(encoding="utf-8").replace(
            'const narrow = @import("narrow_unsafe");\n', "", 1
        ))
        issues = validate(root)
        assert 'missing_token:zigux/tests/phase3_abi.zig:const narrow = @import("narrow_unsafe");' in issues, issues

        build_valid_workspace(root)
        write(root / LOW_LEVEL_TEST_REL, (root / LOW_LEVEL_TEST_REL).read_text(encoding="utf-8").replace(
            'test "phase3 low-level wrappers cover the shipped helper surface directly"\n', "", 1
        ))
        issues = validate(root)
        assert (
            'missing_token:zigux/tests/phase3_low_level_wrappers.zig:test "phase3 low-level wrappers cover the shipped helper surface directly"'
            in issues
        ), issues

    print("PHASE3_LOW_LEVEL_BUILD_ROUTE_SELF_TEST=pass")
    print(f"PHASE3_LOW_LEVEL_BUILD_ROUTE_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the shared Phase 3 build route keeps the bounded low-level wrapper packet wired."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker coverage.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(ROOT)
    if issues:
        print("PHASE3_LOW_LEVEL_BUILD_ROUTE=fail")
        print("PHASE3_LOW_LEVEL_BUILD_ROUTE_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE3_LOW_LEVEL_BUILD_ROUTE_ISSUES_END")
        return 1

    print("PHASE3_LOW_LEVEL_BUILD_ROUTE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
