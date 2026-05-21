#!/usr/bin/env python3
"""Guard the live Phase 1 host-tools smoke packet for Lane 17."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
REVIEW_REL = Path("Documentation/zigux/review-checklist.md")
TESTS_README_REL = Path("zigux/tests/README.md")
TESTS_BUILD_REL = Path("zigux/tests/build.zig")
SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
CHECKER_REL = Path("scripts/zigux/check-phase1-host-tools-smoke-packet.py")

REQUIRED_FILES = (
    WORKFLOW_REL,
    CLOSURE_REL,
    REVIEW_REL,
    TESTS_README_REL,
    TESTS_BUILD_REL,
    SMOKE_REL,
    MANIFEST_REL,
    CHECKER_REL,
)

MARKERS = {
    WORKFLOW_REL: (
        "      - name: Run current Phase 1 shared tests-root smoke",
        "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
    CLOSURE_REL: (
        "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "the shared tests-root smoke route remain the trustworthy current-master sources for the closed helper tranche",
    ),
    REVIEW_REL: (
        "`zigux/tests/phase1_host_tools_smoke.zig`",
        "`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet",
    ),
    TESTS_README_REL: (
        "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest",
    ),
    TESTS_BUILD_REL: (
        "root_source_file = b.path(\"phase1_host_tools_smoke.zig\"),",
        "\"phase1-host-tools-smoke\"",
        "\"Run the shared Phase 1 host-tools smoke anchor from zigux/tests\"",
        "phase1_step.dependOn(&phase1_host_tools_smoke.step);",
        "root_module.addImport(\"slab\", slab_module);",
        "root_module.addImport(\"str_error_r\", str_error_r_module);",
        "root_module.addImport(\"vsprintf\", vsprintf_module);",
        "root_module.addImport(\"zalloc\", zalloc_module);",
    ),
    SMOKE_REL: (
        "test \"phase1 host-tools smoke imports the live helper modules\" {",
        "test \"phase1 host-tools smoke exercises live helper behavior\" {",
        "test \"phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned\" {",
        "test \"phase1 host-tools smoke keeps bitmap alias zero-size and empty-format edges aligned\" {",
        "try std.testing.expect(@hasDecl(slab, \"kmallocBytes\"));",
        "try std.testing.expect(@hasDecl(str_error_r, \"strErrorR\"));",
        "try std.testing.expect(@hasDecl(vsprintf, \"scnprintf\"));",
        "try std.testing.expect(@hasDecl(zalloc, \"zallocBytes\"));",
        "try std.testing.expectEqual(@as(usize, 3), split.argc());",
        "try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, duplicate_serials[0..duplicate_count]);",
    ),
    MANIFEST_REL: (
        "\"helper_count\": 13,",
        "\"tools/lib/slab.zig\"",
        "\"tools/lib/str_error_r.zig\"",
        "\"tools/lib/vsprintf.zig\"",
        "\"tools/lib/zalloc.zig\"",
        "\"direct_anchor_followup_helpers\": [",
        "\"rule_summary\": \"Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.\"",
    ),
}

FORBIDDEN = {
    WORKFLOW_REL: (
        "make -C zigux phase1-validate",
        "make -C zigux phase1-test",
        "make -C zigux phase1-bench",
    ),
    TESTS_README_REL: (
        "active tests-root proof",
    ),
}


def load_text(root: Path, relative: Path) -> str:
    return (root / relative).read_text(encoding="utf-8")


def write_text(root: Path, relative: Path, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_once(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_absent(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 0 else [f"{label}:expected=0:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.exists():
            failures.append(f"missing_file:{relative.as_posix()}")
        elif not path.is_file():
            failures.append(f"non_file_path:{relative.as_posix()}")
    if failures:
        return failures

    for relative, markers in MARKERS.items():
        text = load_text(root, relative)
        for marker in markers:
            failures.extend(require_once(text, f"{relative.as_posix()}:{marker}", marker))

    for relative, markers in FORBIDDEN.items():
        text = load_text(root, relative)
        for marker in markers:
            failures.extend(require_absent(text, f"{relative.as_posix()}:{marker}", marker))

    return failures


def sample_text(relative: Path) -> str:
    markers = list(MARKERS.get(relative, ()))
    if relative == TESTS_BUILD_REL:
        return "const std = @import(\"std\");\n\n" + "\n".join(markers) + "\n"
    if relative == SMOKE_REL:
        return "const std = @import(\"std\");\n\n" + "\n".join(markers) + "\n"
    return "\n".join(markers) + ("\n" if markers else "")


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    for relative in REQUIRED_FILES:
        write_text(root, relative, sample_text(relative))


def rewrite_once(text: str, old: str, new: str = "") -> str:
    if old not in text:
        raise AssertionError(f"missing sample text: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-host-tools-smoke-packet-") as tmpdir:
        root = Path(tmpdir)

        write_sample_root(root)
        if collect_failures(root):
            print("self-test:baseline_failed")
            return 1
        case_count += 1

        sample_root = root / "sample-root"
        write_sample_root(sample_root)
        if collect_failures(sample_root):
            print("self-test:written_sample_failed")
            return 1
        case_count += 1

        broken_root = root / "missing_checker"
        write_sample_root(broken_root)
        (broken_root / CHECKER_REL).unlink()
        failures = collect_failures(broken_root)
        if f"missing_file:{CHECKER_REL.as_posix()}" not in failures:
            print("self-test:missing_checker_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing_workflow_marker"
        write_sample_root(broken_root)
        workflow_text = load_text(broken_root, WORKFLOW_REL)
        write_text(
            broken_root,
            WORKFLOW_REL,
            rewrite_once(workflow_text, MARKERS[WORKFLOW_REL][1] + "\n"),
        )
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{WORKFLOW_REL.as_posix()}:{MARKERS[WORKFLOW_REL][1]}") for item in failures):
            print("self-test:missing_workflow_marker_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing_closure_marker"
        write_sample_root(broken_root)
        closure_text = load_text(broken_root, CLOSURE_REL)
        write_text(
            broken_root,
            CLOSURE_REL,
            rewrite_once(closure_text, MARKERS[CLOSURE_REL][0] + "\n"),
        )
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{CLOSURE_REL.as_posix()}:{MARKERS[CLOSURE_REL][0]}") for item in failures):
            print("self-test:missing_closure_marker_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing_build_marker"
        write_sample_root(broken_root)
        build_text = load_text(broken_root, TESTS_BUILD_REL)
        write_text(
            broken_root,
            TESTS_BUILD_REL,
            rewrite_once(build_text, MARKERS[TESTS_BUILD_REL][3] + "\n"),
        )
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{TESTS_BUILD_REL.as_posix()}:{MARKERS[TESTS_BUILD_REL][3]}") for item in failures):
            print("self-test:missing_build_marker_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing_smoke_marker"
        write_sample_root(broken_root)
        smoke_text = load_text(broken_root, SMOKE_REL)
        write_text(
            broken_root,
            SMOKE_REL,
            rewrite_once(smoke_text, MARKERS[SMOKE_REL][2] + "\n"),
        )
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{SMOKE_REL.as_posix()}:{MARKERS[SMOKE_REL][2]}") for item in failures):
            print("self-test:missing_smoke_marker_not_detected")
            return 1
        case_count += 1

        broken_root = root / "duplicate_smoke_marker"
        write_sample_root(broken_root)
        smoke_text = load_text(broken_root, SMOKE_REL)
        duplicated = smoke_text.replace(MARKERS[SMOKE_REL][4], MARKERS[SMOKE_REL][4] + "\n" + MARKERS[SMOKE_REL][4], 1)
        write_text(broken_root, SMOKE_REL, duplicated)
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{SMOKE_REL.as_posix()}:{MARKERS[SMOKE_REL][4]}") for item in failures):
            print("self-test:duplicate_smoke_marker_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing_manifest_marker"
        write_sample_root(broken_root)
        manifest_text = load_text(broken_root, MANIFEST_REL)
        write_text(
            broken_root,
            MANIFEST_REL,
            rewrite_once(manifest_text, MARKERS[MANIFEST_REL][0] + "\n"),
        )
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{MANIFEST_REL.as_posix()}:{MARKERS[MANIFEST_REL][0]}") for item in failures):
            print("self-test:missing_manifest_marker_not_detected")
            return 1
        case_count += 1

        broken_root = root / "forbidden_workflow"
        write_sample_root(broken_root)
        workflow_text = load_text(broken_root, WORKFLOW_REL)
        write_text(
            broken_root,
            WORKFLOW_REL,
            workflow_text + FORBIDDEN[WORKFLOW_REL][0] + "\n",
        )
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{WORKFLOW_REL.as_posix()}:{FORBIDDEN[WORKFLOW_REL][0]}") for item in failures):
            print("self-test:forbidden_workflow_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing_tests_readme"
        write_sample_root(broken_root)
        tests_text = load_text(broken_root, TESTS_README_REL)
        write_text(
            broken_root,
            TESTS_README_REL,
            rewrite_once(tests_text, MARKERS[TESTS_README_REL][0] + "\n"),
        )
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{TESTS_README_REL.as_posix()}:{MARKERS[TESTS_README_REL][0]}") for item in failures):
            print("self-test:missing_tests_readme_not_detected")
            return 1
        case_count += 1

    print("PHASE1_HOST_TOOLS_SMOKE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_HOST_TOOLS_SMOKE_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"phase1-host-tools-smoke-packet:sample-root-written:{args.write_sample_root}")
        return 0

    failures = collect_failures(args.root.resolve())
    if failures:
        print("PHASE1_HOST_TOOLS_SMOKE_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_HOST_TOOLS_SMOKE_PACKET=pass")
    print(f"PHASE1_HOST_TOOLS_SMOKE_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_HOST_TOOLS_SMOKE_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
