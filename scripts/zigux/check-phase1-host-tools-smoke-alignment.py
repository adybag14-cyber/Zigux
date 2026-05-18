#!/usr/bin/env python3
"""Check that the current Phase 1 host-tools smoke route stays aligned."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
TESTS_BUILD_REL = Path("zigux/tests/build.zig")
PHASE1_SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    TESTS_BUILD_REL,
    PHASE1_SMOKE_REL,
    MANIFEST_REL,
)

EXPECTED_HELPERS = [
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
]

EXPECTED_CLOSURE_MARKERS = [
    "The current shared tests-root closure route is narrow on purpose:",
    "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    (
        "That route keeps a minimal shared import-and-wire smoke check alive for the current "
        "helper packet while the dedicated closure validator keeps the restored closure note "
        "aligned with the committed helper manifest and the shipped reminder packet on current "
        "`master`."
    ),
]

EXPECTED_BUILD_MARKERS = [
    "fn addPhase1HostToolsSmoke(",
    '.root_source_file = b.path("phase1_host_tools_smoke.zig"),',
    'const phase1_host_tools_smoke = addPhase1HostToolsSmoke(b, target, optimize);',
    '\"phase1-host-tools-smoke\",',
    '\"Run the shared Phase 1 host-tools smoke anchor from zigux/tests\",',
    "phase1_step.dependOn(&phase1_host_tools_smoke.step);",
    "smoke_step.dependOn(&phase1_host_tools_smoke.step);",
    "test_step.dependOn(&phase1_host_tools_smoke.step);",
]

EXPECTED_BUILD_HELPER_LINES = [
    '.root_source_file = b.path("../../tools/lib/argv_split.zig"),',
    '.root_source_file = b.path("../../tools/lib/cmdline.zig"),',
    '.root_source_file = b.path("../../tools/lib/find_bit.zig"),',
    '.root_source_file = b.path("../../tools/lib/bitmap.zig"),',
    '.root_source_file = b.path("../../tools/lib/ctype.zig"),',
    '.root_source_file = b.path("../../tools/lib/hweight.zig"),',
    '.root_source_file = b.path("../../tools/lib/list_sort.zig"),',
    '.root_source_file = b.path("../../tools/lib/rbtree.zig"),',
    '.root_source_file = b.path("../../tools/lib/string.zig"),',
    '.root_source_file = b.path("../../tools/lib/slab.zig"),',
    '.root_source_file = b.path("../../tools/lib/str_error_r.zig"),',
    '.root_source_file = b.path("../../tools/lib/vsprintf.zig"),',
    '.root_source_file = b.path("../../tools/lib/zalloc.zig"),',
    'root_module.addImport("argv_split", argv_split_module);',
    'root_module.addImport("cmdline", cmdline_module);',
    'root_module.addImport("find_bit", find_bit_module);',
    'root_module.addImport("bitmap", bitmap_module);',
    'root_module.addImport("ctype", ctype_module);',
    'root_module.addImport("hweight", hweight_module);',
    'root_module.addImport("list_sort", list_sort_module);',
    'root_module.addImport("rbtree", rbtree_module);',
    'root_module.addImport("string", string_module);',
    'root_module.addImport("slab", slab_module);',
    'root_module.addImport("str_error_r", str_error_r_module);',
    'root_module.addImport("vsprintf", vsprintf_module);',
    'root_module.addImport("zalloc", zalloc_module);',
]

EXPECTED_SMOKE_IMPORTS = [
    'const argv_split = @import("argv_split");',
    'const cmdline = @import("cmdline");',
    'pub const find_bit = @import("find_bit");',
    'const bitmap = @import("bitmap");',
    'const ctype = @import("ctype");',
    'const hweight = @import("hweight");',
    'const list_sort = @import("list_sort");',
    'const rbtree = @import("rbtree");',
    'const string = @import("string");',
    'const slab = @import("slab");',
    'const str_error_r = @import("str_error_r");',
    'const vsprintf = @import("vsprintf");',
    'const zalloc = @import("zalloc");',
]

EXPECTED_SMOKE_TEST_ANCHORS = [
    'test "phase1 host-tools smoke imports the live helper modules" {',
    'test "phase1 host-tools smoke exercises live helper behavior" {',
    'test "phase1 host-tools smoke keeps bitmap alias zero-size and empty-format edges aligned" {',
]

EXPECTED_SMOKE_DECL_CHECKS = [
    'try std.testing.expect(@hasDecl(argv_split, "argvSplit"));',
    'try std.testing.expect(@hasDecl(cmdline, "memparse"));',
    'try std.testing.expect(@hasDecl(find_bit, "findFirstBit"));',
    'try std.testing.expect(@hasDecl(bitmap, "setRange"));',
    'try std.testing.expect(@hasDecl(ctype, "isalpha"));',
    'try std.testing.expect(@hasDecl(hweight, "swHweight64"));',
    'try std.testing.expect(@hasDecl(list_sort, "listSort"));',
    'try std.testing.expect(@hasDecl(rbtree, "find"));',
    'try std.testing.expect(@hasDecl(rbtree, "matchIterator"));',
    'try std.testing.expect(@hasDecl(string, "strtobool"));',
    'try std.testing.expect(@hasDecl(slab, "kmallocBytes"));',
    'try std.testing.expect(@hasDecl(str_error_r, "strErrorR"));',
    'try std.testing.expect(@hasDecl(vsprintf, "scnprintf"));',
    'try std.testing.expect(@hasDecl(zalloc, "zallocBytes"));',
]

EXPECTED_SMOKE_BEHAVIOR_MARKERS = [
    'const parsed = cmdline.memparse("64K tail");',
    'const signed = cmdline.memparse("-2K tail");',
    'const saturated = cmdline.memparse("+9223372036854775808");',
    'const rendered_len = vsprintf.scnprintf(&render_buffer, "{s}:{d}", .{ "zigux", 9 });',
    'const padded_len = vsprintf.scnprintfPad(&padded_render, 10, "id={d}", .{7});',
    "var tree_root = rbtree.Root.init();",
    "var cached_root = rbtree.RootCached.init();",
    "bitmap.bitmap_copy_clear_tail(alias_clear[0..0], src[0..0], 0);",
    "bitmap.bitmap_copy_and_extend(alias_extend[0..0], src[0..0], 0, 0);",
    "const sysfs = [_][]const u8{ \"disabled\", \"auto\\n\", \"manual\" };",
]


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{needle}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    closure_text = load_text(root, PHASE1_CLOSURE_REL)
    for marker in EXPECTED_CLOSURE_MARKERS:
        failures.extend(
            require_exact_occurrence(
                closure_text,
                f"{PHASE1_CLOSURE_REL.as_posix()}:closure_marker",
                marker,
            )
        )

    build_text = load_text(root, TESTS_BUILD_REL)
    for marker in EXPECTED_BUILD_MARKERS + EXPECTED_BUILD_HELPER_LINES:
        failures.extend(
            require_exact_occurrence(
                build_text,
                f"{TESTS_BUILD_REL.as_posix()}:build_marker",
                marker,
            )
        )

    smoke_text = load_text(root, PHASE1_SMOKE_REL)
    for marker in EXPECTED_SMOKE_IMPORTS + EXPECTED_SMOKE_TEST_ANCHORS + EXPECTED_SMOKE_DECL_CHECKS + EXPECTED_SMOKE_BEHAVIOR_MARKERS:
        failures.extend(
            require_exact_occurrence(
                smoke_text,
                f"{PHASE1_SMOKE_REL.as_posix()}:smoke_marker",
                marker,
            )
        )

    manifest = json.loads(load_text(root, MANIFEST_REL))
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]
    failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:phase", manifest.get("phase"), "Phase 1"))
    failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:status", manifest.get("status"), "closed"))
    failures.extend(
        require_exact_value(f"{MANIFEST_REL.as_posix()}:helper_count", manifest.get("helper_count"), len(EXPECTED_HELPERS))
    )
    failures.extend(require_exact_value(f"{MANIFEST_REL.as_posix()}:helpers", manifest.get("helpers"), EXPECTED_HELPERS))
    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing expected marker: {old}")
    return text.replace(old, new, 1)


def make_fixture_tree(root: Path) -> None:
    write_text(
        root / PHASE1_CLOSURE_REL,
        "# Phase 1 Closure\n\n" + "\n".join(EXPECTED_CLOSURE_MARKERS) + "\n",
    )
    write_text(
        root / TESTS_BUILD_REL,
        "\n".join(EXPECTED_BUILD_MARKERS + EXPECTED_BUILD_HELPER_LINES) + "\n",
    )
    write_text(
        root / PHASE1_SMOKE_REL,
        "\n".join(
            EXPECTED_SMOKE_IMPORTS
            + EXPECTED_SMOKE_TEST_ANCHORS
            + EXPECTED_SMOKE_DECL_CHECKS
            + EXPECTED_SMOKE_BEHAVIOR_MARKERS
        )
        + "\n",
    )
    write_text(
        root / MANIFEST_REL,
        json.dumps(
            {
                "phase": "Phase 1",
                "status": "closed",
                "helper_count": len(EXPECTED_HELPERS),
                "helpers": EXPECTED_HELPERS,
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    cases = [
        ("baseline", None),
        (
            "missing_closure_route_marker",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                replace_once(load_text(root, PHASE1_CLOSURE_REL), EXPECTED_CLOSURE_MARKERS[1] + "\n", ""),
            ),
        ),
        (
            "missing_build_step_marker",
            lambda root: write_text(
                root / TESTS_BUILD_REL,
                replace_once(load_text(root, TESTS_BUILD_REL), EXPECTED_BUILD_MARKERS[5] + "\n", ""),
            ),
        ),
        (
            "missing_build_helper_import",
            lambda root: write_text(
                root / TESTS_BUILD_REL,
                replace_once(load_text(root, TESTS_BUILD_REL), EXPECTED_BUILD_HELPER_LINES[-1] + "\n", ""),
            ),
        ),
        (
            "missing_smoke_decl_check",
            lambda root: write_text(
                root / PHASE1_SMOKE_REL,
                replace_once(load_text(root, PHASE1_SMOKE_REL), EXPECTED_SMOKE_DECL_CHECKS[9] + "\n", ""),
            ),
        ),
        (
            "wrong_helper_count",
            lambda root: write_text(
                root / MANIFEST_REL,
                json.dumps(
                    {
                        "phase": "Phase 1",
                        "status": "closed",
                        "helper_count": len(EXPECTED_HELPERS) - 1,
                        "helpers": EXPECTED_HELPERS,
                    },
                    indent=2,
                )
                + "\n",
            ),
        ),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-host-tools-smoke-") as tmp:
            root = Path(tmp)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-host-tools-smoke-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-host-tools-smoke-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_HOST_TOOLS_SMOKE_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_HOST_TOOLS_SMOKE_ALIGNMENT_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_HOST_TOOLS_SMOKE_ALIGNMENT=pass")
    print(f"PHASE1_HOST_TOOLS_SMOKE_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_HOST_TOOLS_SMOKE_ALIGNMENT_REQUIRED_MARKER_COUNT="
        f"{len(EXPECTED_CLOSURE_MARKERS) + len(EXPECTED_BUILD_MARKERS) + len(EXPECTED_BUILD_HELPER_LINES) + len(EXPECTED_SMOKE_IMPORTS) + len(EXPECTED_SMOKE_TEST_ANCHORS) + len(EXPECTED_SMOKE_DECL_CHECKS) + len(EXPECTED_SMOKE_BEHAVIOR_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())