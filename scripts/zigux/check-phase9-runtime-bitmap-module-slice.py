#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()

MODULE_SLICE_PATH = "Documentation/zigux/phase9-runtime-bitmap-module-slice.md"
SURVEY_PATH = "Documentation/zigux/phase9-runtime-bitmap-survey.md"
MANIFEST_PATH = "zigux/tests/runtime_bitmap_manifest.json"
BUILD_PATH = "zigux/tests/phase9_build.zig"
SAMPLES_README_PATH = "samples/zigux/README.md"


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


MODULE_SLICE_REQUIRED_MARKERS = [
    '`PHASE9_SLICE=runtime-bitmap-partial-slice`',
    "scope: partial runtime bitmap reminder packet, direct sample proof, direct loader proof, manifest-backed ownership packet, top-bit companion proof, bounded build-bundle vocabulary, and no broader shared runtime-loader claim",
    "## Current visible slice",
    "`zigux/tests/runtime_bitmap_manifest.json`",
    "## Repo-reality gaps inside the bitmap family",
    "`zigux/tests/runtime_bitmap_module.zig`",
    "`zigux/tests/runtime_bitmap_diff.zig`",
    "## Adjacent shared-owner evidence outside this bitmap reminder packet",
    "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
    "`zigux/kernel/runtime_loader.zig`",
    "`zigux/kernel/runtime_loader_contract.zig`",
    "`zigux/kernel/runtime_loader_command_env_boundary_guard.zig`",
    "the bounded `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` routes inside `zigux/tests/phase9_build.zig`",
    "The current visible packet includes the direct bitmap sample, direct loader companion, focused top-bit companion, manifest-backed ownership packet, survey note, module-slice note, survey gate, and bounded build bundle.",
    "The shared `zigux/tests/phase9_build.zig` bundle reruns the direct sample, loader, survey gate, and top-bit companion;",
    "The module and diff legs are still absent on the trusted read path, and the older wider-family loader-gap survey and manifest vocabulary still does not return there either, so this slice must stay bitmap-local while keeping that narrower returned shared loader packet distinct from the still-missing wider-family loader backlog.",
    "the blocked follow-through remains `bitmap module-and-diff parity plus broader shared runtime-loader family completion`",
]

SURVEY_REQUIRED_MARKERS = [
    "the current runtime bitmap reminder packet is still `partial_packet_without_module_and_diff_follow_through`",
    "manifest-backed ownership packet",
    "keep `zigux/tests/runtime_bitmap_module.zig` and `zigux/tests/runtime_bitmap_diff.zig` framed as same-lane repo-reality gaps until the trusted current-tree read path returns them directly again",
]

MANIFEST_REQUIRED_MARKERS = [
    '"lane_key": "P9-L08"',
    '"loader_reinit_and_re_selftest_guards"',
    '"loader_loaded_summary_stability"',
    '"shared_build_route_visibility"',
]

BUILD_REQUIRED_MARKERS = [
    '"phase9-runtime-bitmap-sample-tests"',
    '"phase9-runtime-bitmap-loader-tests"',
    '"phase9-runtime-bitmap-survey-tests"',
    '"phase9-runtime-bitmap-top-bit-tests"',
    '"phase9-runtime-bitmap-tests"',
]

BUILD_FORBIDDEN_MARKERS = [
    '"phase9-runtime-bitmap-module-tests"',
    '"phase9-runtime-bitmap-diff-tests"',
]

SAMPLES_README_REQUIRED_MARKERS = [
    "Keep that bitmap packet framed as a separate Phase 9 runtime reminder rather than as proof that the broader shared runtime-loader packet returned or as evidence that a fifth approved Phase 5 sample family landed here.",
    "Keep `samples/zigux/runtime_bitmap_loader.zig` explicit as the returned loader-input companion proof for the same runtime bitmap starter.",
    "Keep `zigux/tests/runtime_bitmap_manifest.json` explicit as the manifest-backed ownership packet for the same runtime bitmap reminder family.",
]


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in [
        MODULE_SLICE_PATH,
        SURVEY_PATH,
        MANIFEST_PATH,
        BUILD_PATH,
        SAMPLES_README_PATH,
    ]:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    module_slice = read_text(root, MODULE_SLICE_PATH)
    for marker in MODULE_SLICE_REQUIRED_MARKERS:
        if marker not in module_slice:
            failures.append(f"missing_marker:{MODULE_SLICE_PATH}:{marker}")

    survey = read_text(root, SURVEY_PATH)
    for marker in SURVEY_REQUIRED_MARKERS:
        if marker not in survey:
            failures.append(f"missing_marker:{SURVEY_PATH}:{marker}")

    manifest = read_text(root, MANIFEST_PATH)
    for marker in MANIFEST_REQUIRED_MARKERS:
        if marker not in manifest:
            failures.append(f"missing_marker:{MANIFEST_PATH}:{marker}")

    build = read_text(root, BUILD_PATH)
    for marker in BUILD_REQUIRED_MARKERS:
        if marker not in build:
            failures.append(f"missing_marker:{BUILD_PATH}:{marker}")
    for marker in BUILD_FORBIDDEN_MARKERS:
        if marker in build:
            failures.append(f"unexpected_marker:{BUILD_PATH}:{marker}")

    samples_readme = read_text(root, SAMPLES_README_PATH)
    for marker in SAMPLES_README_REQUIRED_MARKERS:
        if marker not in samples_readme:
            failures.append(f"missing_marker:{SAMPLES_README_PATH}:{marker}")

    return failures


def build_module_slice_fixture_text() -> str:
    return """# Phase 9 Runtime Bitmap Module Slice

- `PHASE9_SLICE=runtime-bitmap-partial-slice`
- scope: partial runtime bitmap reminder packet, direct sample proof, direct loader proof, manifest-backed ownership packet, top-bit companion proof, bounded build-bundle vocabulary, and no broader shared runtime-loader claim

## Current visible slice
- `zigux/tests/runtime_bitmap_manifest.json`

## Repo-reality gaps inside the bitmap family
- `zigux/tests/runtime_bitmap_module.zig`
- `zigux/tests/runtime_bitmap_diff.zig`

## Adjacent shared-owner evidence outside this bitmap reminder packet
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`
- the bounded `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` routes inside `zigux/tests/phase9_build.zig`

The current visible packet includes the direct bitmap sample, direct loader companion, focused top-bit companion, manifest-backed ownership packet, survey note, module-slice note, survey gate, and bounded build bundle.
The shared `zigux/tests/phase9_build.zig` bundle reruns the direct sample, loader, survey gate, and top-bit companion; the neighboring shared loader packet also survives through allocator/init-flow, command/environment boundary guard, and bounded loader-shared routes, but those adjacent shared-owner surfaces still do not prove that the broader runtime bitmap module or diff packet returned.
The module and diff legs are still absent on the trusted read path, and the older wider-family loader-gap survey and manifest vocabulary still does not return there either, so this slice must stay bitmap-local while keeping that narrower returned shared loader packet distinct from the still-missing wider-family loader backlog.
- the blocked follow-through remains `bitmap module-and-diff parity plus broader shared runtime-loader family completion`
"""


def build_survey_fixture_text() -> str:
    return """# Phase 9 Runtime Bitmap Survey

- the current runtime bitmap reminder packet is still `partial_packet_without_module_and_diff_follow_through`
- manifest-backed ownership packet
- keep `zigux/tests/runtime_bitmap_module.zig` and `zigux/tests/runtime_bitmap_diff.zig` framed as same-lane repo-reality gaps until the trusted current-tree read path returns them directly again
"""


def build_manifest_fixture_text() -> str:
    return """{
  "lane_key": "P9-L08",
  "exact_checks": [
    "loader_reinit_and_re_selftest_guards",
    "loader_loaded_summary_stability",
    "shared_build_route_visibility"
  ]
}
"""


def build_build_fixture_text() -> str:
    return """const phase9 = .{
    "phase9-runtime-bitmap-sample-tests",
    "phase9-runtime-bitmap-loader-tests",
    "phase9-runtime-bitmap-survey-tests",
    "phase9-runtime-bitmap-top-bit-tests",
    "phase9-runtime-bitmap-tests",
};
"""


def build_samples_readme_fixture_text() -> str:
    return """# samples/zigux

Keep that bitmap packet framed as a separate Phase 9 runtime reminder rather than as proof that the broader shared runtime-loader packet returned or as evidence that a fifth approved Phase 5 sample family landed here.
Keep `samples/zigux/runtime_bitmap_loader.zig` explicit as the returned loader-input companion proof for the same runtime bitmap starter.
Keep `zigux/tests/runtime_bitmap_manifest.json` explicit as the manifest-backed ownership packet for the same runtime bitmap reminder family.
"""


def seed_fixture_tree(base: Path) -> None:
    write_text(base / MODULE_SLICE_PATH, build_module_slice_fixture_text())
    write_text(base / SURVEY_PATH, build_survey_fixture_text())
    write_text(base / MANIFEST_PATH, build_manifest_fixture_text())
    write_text(base / BUILD_PATH, build_build_fixture_text())
    write_text(base / SAMPLES_README_PATH, build_samples_readme_fixture_text())


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-runtime-bitmap-module-slice-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for marker in MODULE_SLICE_REQUIRED_MARKERS:
            seed_fixture_tree(base)
            current = read_text(base, MODULE_SLICE_PATH)
            if current.count(marker) != 1:
                continue
            write_text(base / MODULE_SLICE_PATH, current.replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{MODULE_SLICE_PATH}:{marker}")

        for marker in SURVEY_REQUIRED_MARKERS:
            seed_fixture_tree(base)
            current = read_text(base, SURVEY_PATH)
            if current.count(marker) != 1:
                continue
            write_text(base / SURVEY_PATH, current.replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{SURVEY_PATH}:{marker}")

        for marker in MANIFEST_REQUIRED_MARKERS:
            seed_fixture_tree(base)
            current = read_text(base, MANIFEST_PATH)
            if current.count(marker) != 1:
                continue
            write_text(base / MANIFEST_PATH, current.replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{MANIFEST_PATH}:{marker}")

        for marker in BUILD_REQUIRED_MARKERS:
            seed_fixture_tree(base)
            current = read_text(base, BUILD_PATH)
            if current.count(marker) != 1:
                continue
            write_text(base / BUILD_PATH, current.replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{BUILD_PATH}:{marker}")

        for marker in BUILD_FORBIDDEN_MARKERS:
            seed_fixture_tree(base)
            current = read_text(base, BUILD_PATH)
            write_text(base / BUILD_PATH, current + marker + "\n")
            expect_failure(base, f"unexpected_marker:{BUILD_PATH}:{marker}")

        for marker in SAMPLES_README_REQUIRED_MARKERS:
            seed_fixture_tree(base)
            current = read_text(base, SAMPLES_README_PATH)
            if current.count(marker) != 1:
                continue
            write_text(base / SAMPLES_README_PATH, current.replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{SAMPLES_README_PATH}:{marker}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_RUNTIME_BITMAP_MODULE_SLICE_SELF_TEST=pass")
    print("PHASE9_RUNTIME_BITMAP_MODULE_SLICE_FILE_COUNT=5")
    print(
        "PHASE9_RUNTIME_BITMAP_MODULE_SLICE_REQUIRED_MARKER_COUNT="
        f"{len(MODULE_SLICE_REQUIRED_MARKERS) + len(SURVEY_REQUIRED_MARKERS) + len(MANIFEST_REQUIRED_MARKERS) + len(BUILD_REQUIRED_MARKERS) + len(SAMPLES_README_REQUIRED_MARKERS)}"
    )
    print(
        "PHASE9_RUNTIME_BITMAP_MODULE_SLICE_FORBIDDEN_MARKER_COUNT="
        f"{len(BUILD_FORBIDDEN_MARKERS)}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the current Phase 9 runtime bitmap module-slice reminder "
            "stays aligned with the partial bitmap packet, the neighboring shared "
            "runtime-loader boundaries, and the still-missing module and diff legs."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=SELF_PATH.parent, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE9_RUNTIME_BITMAP_MODULE_SLICE_ERROR={failure}")
        return 1

    print("PHASE9_RUNTIME_BITMAP_MODULE_SLICE_FILE_COUNT=5")
    print(
        "PHASE9_RUNTIME_BITMAP_MODULE_SLICE_REQUIRED_MARKER_COUNT="
        f"{len(MODULE_SLICE_REQUIRED_MARKERS) + len(SURVEY_REQUIRED_MARKERS) + len(MANIFEST_REQUIRED_MARKERS) + len(BUILD_REQUIRED_MARKERS) + len(SAMPLES_README_REQUIRED_MARKERS)}"
    )
    print(
        "PHASE9_RUNTIME_BITMAP_MODULE_SLICE_FORBIDDEN_MARKER_COUNT="
        f"{len(BUILD_FORBIDDEN_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
