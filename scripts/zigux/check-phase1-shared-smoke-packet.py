#!/usr/bin/env python3
"""Guard the current Phase 1 shared-smoke packet and workflow route."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

REQUIRED_FILES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase1-closure.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_host_tools_smoke.zig",
    ".github/workflows/zigux-bootstrap.yml",
)

EXACT_FRAGMENT_MARKERS = {
    "Documentation/zigux/README.md": (
        "keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.",
        "`python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the bounded current reminder checks",
    ),
    "Documentation/zigux/phase1-closure.md": (
        "- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
        "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "The current bootstrap workflow also keeps the adjacent Phase 1 route-summary guard wired beside that same live reminder packet",
    ),
    "scripts/zigux/README.md": (
        "- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live owner-map and string-review guards instead of rebuilding the broader installer-backed closure packet from older missing routes",
        "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
        "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
    ),
    "zigux/tests/README.md": (
        "  * current direct-readback Phase 1 reminder packet:",
        "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    ),
    "zigux/tests/build.zig": (
        '.root_source_file = b.path("phase1_host_tools_smoke.zig"),',
        '.root_source_file = b.path("../../tools/lib/slab.zig"),',
        '.root_source_file = b.path("../../tools/lib/str_error_r.zig"),',
        '.root_source_file = b.path("../../tools/lib/vsprintf.zig"),',
        '.root_source_file = b.path("../../tools/lib/zalloc.zig"),',
        'root_module.addImport("slab", slab_module);',
        'root_module.addImport("str_error_r", str_error_r_module);',
        'root_module.addImport("vsprintf", vsprintf_module);',
        'root_module.addImport("zalloc", zalloc_module);',
        '.name = "phase1-host-tools-smoke",',
        '"Run the shared Phase 1 host-tools smoke anchor from zigux/tests"',
        "smoke_step.dependOn(&phase1_host_tools_smoke.step);",
        "test_step.dependOn(&phase1_host_tools_smoke.step);",
    ),
    "zigux/tests/phase1_host_tools_smoke.zig": (
        'const slab = @import("slab");',
        'const str_error_r = @import("str_error_r");',
        'const vsprintf = @import("vsprintf");',
        'const zalloc = @import("zalloc");',
        'test "phase1 host-tools smoke imports the live helper modules" {',
        'test "phase1 host-tools smoke exercises live helper behavior" {',
        'test "phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned" {',
        'test "phase1 host-tools smoke keeps bitmap alias zero-size and empty-format edges aligned" {',
        'try std.testing.expect(@hasDecl(slab, "kmallocBytes"));',
        'try std.testing.expect(@hasDecl(str_error_r, "strErrorR"));',
        'try std.testing.expect(@hasDecl(vsprintf, "scnprintf"));',
        'try std.testing.expect(@hasDecl(zalloc, "zallocBytes"));',
    ),
}

EXACT_LINE_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": (
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
        "run: python3 scripts/zigux/validate-phase1-closure.py",
        "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
}

FORBIDDEN_EXACT_LINES = {
    ".github/workflows/zigux-bootstrap.yml": (
        "run: zig build test --build-file zigux/tests/build.zig",
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def count_exact_line(text: str, marker: str) -> int:
    want = marker.strip()
    return sum(1 for line in text.splitlines() if line.strip() == want)


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path}")

    if failures:
        return failures

    for relative_path, markers in EXACT_FRAGMENT_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            count = text.count(marker)
            if count != 1:
                failures.append(
                    f"fragment_count:{relative_path}:{marker}:expected=1:actual={count}"
                )

    for relative_path, markers in EXACT_LINE_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            count = count_exact_line(text, marker)
            if count != 1:
                failures.append(
                    f"line_count:{relative_path}:{marker}:expected=1:actual={count}"
                )

    for relative_path, markers in FORBIDDEN_EXACT_LINES.items():
        text = read_text(root, relative_path)
        for marker in markers:
            count = count_exact_line(text, marker)
            if count != 0:
                failures.append(
                    f"forbidden_line:{relative_path}:{marker}:expected=0:actual={count}"
                )

    return failures


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        lines: list[str] = []
        lines.extend(EXACT_FRAGMENT_MARKERS.get(relative_path, ()))
        lines.extend(EXACT_LINE_MARKERS.get(relative_path, ()))
        write_text(root, relative_path, "\n".join(lines) + ("\n" if lines else ""))


def remove_fragment(root: Path, relative_path: str, fragment: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(fragment, "", 1), encoding="utf-8")


def duplicate_fragment(root: Path, relative_path: str, fragment: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(fragment, fragment + "\n" + fragment, 1), encoding="utf-8")


def remove_line(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker.strip():
            del lines[idx]
            path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
            return
    raise ValueError(f"missing marker {marker!r} in {relative_path}")


def duplicate_line(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker.strip():
            lines.insert(idx + 1, line)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(f"missing marker {marker!r} in {relative_path}")


def append_line(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text + marker + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, tuple[str, ...] | None]] = [("success", None)]

    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path}", ("remove_file", relative_path)))
    for relative_path, markers in EXACT_FRAGMENT_MARKERS.items():
        for marker in markers:
            cases.append((f"missing_fragment:{relative_path}", ("remove_fragment", relative_path, marker)))
            cases.append((f"duplicate_fragment:{relative_path}", ("duplicate_fragment", relative_path, marker)))
    for relative_path, markers in EXACT_LINE_MARKERS.items():
        for marker in markers:
            cases.append((f"missing_line:{relative_path}", ("remove_line", relative_path, marker)))
            cases.append((f"duplicate_line:{relative_path}", ("duplicate_line", relative_path, marker)))
    for relative_path, markers in FORBIDDEN_EXACT_LINES.items():
        for marker in markers:
            cases.append((f"forbidden_line:{relative_path}", ("append_line", relative_path, marker)))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-shared-smoke-packet-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutation is not None:
                kind = mutation[0]
                if kind == "remove_file":
                    (root / mutation[1]).unlink()
                elif kind == "remove_fragment":
                    remove_fragment(root, mutation[1], mutation[2])
                elif kind == "duplicate_fragment":
                    duplicate_fragment(root, mutation[1], mutation[2])
                elif kind == "remove_line":
                    remove_line(root, mutation[1], mutation[2])
                elif kind == "duplicate_line":
                    duplicate_line(root, mutation[1], mutation[2])
                elif kind == "append_line":
                    append_line(root, mutation[1], mutation[2])

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("self-test:success:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_SHARED_SMOKE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_SHARED_SMOKE_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a minimal passing sample root and exit",
    )
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        if args.write_sample_root.exists():
            shutil.rmtree(args.write_sample_root)
        build_sample_repo(args.write_sample_root)
        print(f"PHASE1_SHARED_SMOKE_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_SHARED_SMOKE_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_SHARED_SMOKE_PACKET=pass")
    print(f"PHASE1_SHARED_SMOKE_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_SHARED_SMOKE_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in EXACT_FRAGMENT_MARKERS.values()) + sum(len(markers) for markers in EXACT_LINE_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
