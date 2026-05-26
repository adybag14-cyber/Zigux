#!/usr/bin/env python3
"""Guard the restored Phase 1 helper-replay packet against reminder drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
PHASE1_HELPERS_BUILD_REL = Path("zigux/tests/phase1_helpers_build.zig")
PHASE1_HELPERS_REL = Path("zigux/tests/phase1_helpers.zig")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    PHASE1_HELPERS_BUILD_REL,
    PHASE1_HELPERS_REL,
)

MARKERS = {
    PHASE1_CLOSURE_REL: (
        "- `zigux/tests/phase1_helpers.zig`",
        "- `zigux/tests/phase1_helpers_build.zig`",
        "- `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`",
    ),
    SCRIPTS_README_REL: (
        "- `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_helpers_build.zig`, and `zigux/tests/phase1_host_tools_smoke.zig` remain the current reminder-surface companions for that packet",
        "- `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_helpers_build.zig`, and `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig` restore a focused fixture-backed helper replay anchor on current `master` without widening back into the older validator-first or bench-route stack",
    ),
    TESTS_README_REL: (
        "- `zigux/tests/phase1_helpers.zig`",
        "- `zigux/tests/phase1_helpers_build.zig`",
        "* current focused Phase 1 helper replay route: `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`",
    ),
    PHASE1_HELPERS_BUILD_REL: (
        '.root_source_file = b.path("phase1_helpers.zig"),',
        '.name = "phase1-helpers",',
        'root_module.addImport("bitmap", bitmap_module);',
        'root_module.addImport("find_bit", find_bit_module);',
        'root_module.addImport("rbtree", rbtree_module);',
        'root_module.addImport("string", string_module);',
    ),
    PHASE1_HELPERS_REL: (
        'const fixture_bytes = @embedFile("fixtures/phase1_helpers.json");',
        'const bitmap = @import("bitmap");',
        'const find_bit = @import("find_bit");',
        'const rbtree = @import("rbtree");',
        'const string = @import("string");',
        'test "phase 1 helper ports match committed parity fixture" {',
    ),
}


def repo_root(root_arg: str | None) -> Path:
    return Path(root_arg).resolve() if root_arg else DEFAULT_ROOT.resolve()


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        path = root / relative_path
        if not path.is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in MARKERS[relative_path]:
            count = text.count(marker)
            if count != 1:
                failures.append(
                    f"{relative_path.as_posix()}:expected=1:actual={count}:{marker}"
                )
    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path, markers in MARKERS.items():
        write_text(root, relative_path, "\n".join(markers) + "\n")


def remove_marker(root: Path, relative_path: Path, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def duplicate_marker(root: Path, relative_path: Path, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [("success", None)]

    for relative_path in REQUIRED_FILES:
        cases.append(
            (
                f"missing_file:{relative_path.as_posix()}",
                lambda root, relative_path=relative_path: (root / relative_path).unlink(),
            )
        )

    for relative_path, markers in MARKERS.items():
        for marker in markers:
            cases.append(
                (
                    f"remove:{relative_path.as_posix()}",
                    lambda root, relative_path=relative_path, marker=marker: remove_marker(
                        root, relative_path, marker
                    ),
                )
            )
            cases.append(
                (
                    f"duplicate:{relative_path.as_posix()}",
                    lambda root, relative_path=relative_path, marker=marker: duplicate_marker(
                        root, relative_path, marker
                    ),
                )
            )

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-helper-replay-packet-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutation is not None:
                mutation(root)
            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("PHASE1_HELPER_REPLAY_PACKET_SELF_TEST=fail")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_HELPER_REPLAY_PACKET_SELF_TEST=pass")
    print(f"PHASE1_HELPER_REPLAY_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run embedded self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_HELPER_REPLAY_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_HELPER_REPLAY_PACKET=pass")
    print(f"PHASE1_HELPER_REPLAY_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
