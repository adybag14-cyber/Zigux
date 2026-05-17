#!/usr/bin/env python3
"""Guard the current shared Phase 1 reminder packet across docs, tests, scripts, and workflow."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase1-bench.py",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_host_tools_smoke.zig",
    ".github/workflows/zigux-bootstrap.yml",
]

DOCS_ROOT_MARKERS = [
    "  * the current docs-root Phase 1 reminder packet should stay parked on the live owner-map and string-review guards: `scripts/zigux/check-phase1-string-review-packet.py` and `scripts/zigux/check-phase1-direct-owner-markers.py` are the shipped direct checks, while `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around them.",
    "  * repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, closure-side, validator-first, bench, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence.",
    "  * current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so the remaining shared reminder follow-through is limited to keeping the broader docs-root, checklist, and tests-root bench wording truthful instead of treating the bench checker itself as a repo-reality gap.",
    "  * keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.",
    "  * `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test` and `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.",
]

SCRIPTS_README_MARKERS = [
    "- `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test` and `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test` replay the shipped bounded Phase 1 reminder checks",
    "- `scripts/zigux/check-phase1-string-review-packet.py` and `scripts/zigux/check-phase1-direct-owner-markers.py` keep the shipped string-review and direct-owner marker packet explicit from the scripts root",
    "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
]

TESTS_README_MARKERS = [
    "  * current direct-readback Phase 1 reminder packet: `scripts/zigux/check-phase1-string-review-packet.py` and `scripts/zigux/check-phase1-direct-owner-markers.py`",
    "  * repo-reality warning for the broader Phase 1 installer-backed closure-and-replay packet: repeated authenticated contents reads on current `master` now return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    "  * keep current Phase 1 follow-through tied to the live owner-map plus string-review reminder packet instead of reconstructing the broader installer-backed closure-and-replay packet from those older missing installer, closure-side, and replay files and routes alone",
]

REVIEW_CHECKLIST_MARKERS = [
    "  * if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `scripts/zigux/check-phase1-string-review-packet.py`, and `scripts/zigux/check-phase1-direct-owner-markers.py` still agree on the same bounded current-`master` reminder packet: the thirteen-helper owner map, the parked shared-replay-versus-direct-anchor split, the live string-review and direct-owner guards, and the repo-reality warning that older installer-backed, closure-side, validator-first, make-route, bench, and replay paths such as `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` stay framed as historical packet members rather than direct current evidence unless a fresh reread materializes them again, without widening Phase 1 beyond the bounded host-side helper packet?",
    "  * if the change touches that same Phase 1 reminder packet, does the checklist still say clearly that `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test` and `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test` replay the bounded live reminder checks while `scripts/zigux/check-phase1-string-review-packet.py` and `scripts/zigux/check-phase1-direct-owner-markers.py` guard the shipped current-`master` Phase 1 reminder packet, and that the older installer-companion self-test-versus-live route wording stays historical until `scripts/zigux/check-phase1-installer-companion-checks.py` is directly readable again?",
]

WORKFLOW_MARKERS = [
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
]

BUILD_ZIG_MARKERS = [
    'root_source_file = b.path("phase1_host_tools_smoke.zig"),',
    '.name = "phase1-host-tools-smoke",',
    '"Run the shared Phase 1 host-tools smoke anchor from zigux/tests",',
    "smoke_step.dependOn(&phase1_host_tools_smoke.step);",
    "test_step.dependOn(&phase1_host_tools_smoke.step);",
]

SMOKE_ZIG_MARKERS = [
    'const argv_split = @import("argv_split");',
    'const cmdline = @import("cmdline");',
    'pub const find_bit = @import("find_bit");',
    'const bitmap = @import("bitmap");',
    'try std.testing.expect(@hasDecl(bitmap, "setRange"));',
]

EXPECTED_SELF_TEST_CASE_COUNT = 20


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [relative_path for relative_path in REQUIRED_FILES if not (root / relative_path).exists()]


def collect_exact_count_markers(text: str, label: str, markers: list[str]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            missing.append(f"{label}:{marker}:expected=1:actual={count}")
    return missing


def collect_stripped_line_markers(text: str, label: str, markers: list[str]) -> list[str]:
    lines = text.splitlines()
    missing: list[str] = []
    for marker in markers:
        count = sum(1 for line in lines if line.strip() == marker)
        if count != 1:
            missing.append(f"{label}:{marker}:expected=1:actual={count}")
    return missing


def collect_missing_markers(root: Path) -> list[str]:
    missing = [f"missing_file:{relative_path}" for relative_path in collect_missing_files(root)]
    if missing:
        return missing

    docs_root = read_text(root, "Documentation/zigux/README.md")
    review_checklist = read_text(root, "Documentation/zigux/review-checklist.md")
    scripts_readme = read_text(root, "scripts/zigux/README.md")
    tests_readme = read_text(root, "zigux/tests/README.md")
    build_zig = read_text(root, "zigux/tests/build.zig")
    smoke_zig = read_text(root, "zigux/tests/phase1_host_tools_smoke.zig")
    workflow = read_text(root, ".github/workflows/zigux-bootstrap.yml")

    missing.extend(collect_exact_count_markers(docs_root, "docs_root", DOCS_ROOT_MARKERS))
    missing.extend(collect_exact_count_markers(scripts_readme, "scripts_readme", SCRIPTS_README_MARKERS))
    missing.extend(collect_exact_count_markers(tests_readme, "tests_readme", TESTS_README_MARKERS))
    missing.extend(
        collect_exact_count_markers(
            review_checklist,
            "review_checklist",
            REVIEW_CHECKLIST_MARKERS,
        )
    )
    missing.extend(collect_exact_count_markers(build_zig, "build_zig", BUILD_ZIG_MARKERS))
    missing.extend(collect_exact_count_markers(smoke_zig, "smoke_zig", SMOKE_ZIG_MARKERS))
    missing.extend(collect_stripped_line_markers(workflow, "workflow", WORKFLOW_MARKERS))
    return missing


def write_text(root: Path, relative_path: str, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root, relative_path, "")

    write_text(root, "Documentation/zigux/README.md", "\n".join(DOCS_ROOT_MARKERS) + "\n")
    write_text(root, "Documentation/zigux/review-checklist.md", "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(root, "scripts/zigux/README.md", "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(root, "scripts/zigux/check-phase1-bench.py", "# placeholder\n")
    write_text(root, "zigux/tests/README.md", "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(
        root,
        "zigux/tests/build.zig",
        "\n".join(BUILD_ZIG_MARKERS) + "\n",
    )
    write_text(
        root,
        "zigux/tests/phase1_host_tools_smoke.zig",
        "\n".join(SMOKE_ZIG_MARKERS) + "\n",
    )
    write_text(
        root,
        ".github/workflows/zigux-bootstrap.yml",
        "\n".join(
            [
                "      - name: Self-test current Phase 1 bench checker",
                "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
                "      - name: Self-test current Phase 1 shared reminder checker",
                "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
                "      - name: Check current Phase 1 shared reminder packet",
                "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
            ]
        )
        + "\n",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-shared-reminder-success-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        missing = collect_missing_markers(root)
        if missing:
            print("self-test:success:unexpected_failures")
            for item in missing:
                print(item)
            return 1

    cases = [
        ("missing_file", "Documentation/zigux/README.md", "remove_file"),
        ("missing_docs_marker", "Documentation/zigux/README.md", "remove_marker"),
        ("duplicate_docs_marker", "Documentation/zigux/README.md", "duplicate_marker"),
        ("missing_docs_historical_warning", "Documentation/zigux/README.md", "remove_docs_historical_warning"),
        ("missing_docs_bench_marker", "Documentation/zigux/README.md", "remove_docs_bench_marker"),
        ("missing_docs_selftest_marker", "Documentation/zigux/README.md", "remove_docs_selftest_marker"),
        ("missing_scripts_marker", "scripts/zigux/README.md", "remove_marker"),
        ("missing_scripts_bench_marker", "scripts/zigux/README.md", "remove_scripts_bench_marker"),
        ("missing_bench_checker", "scripts/zigux/check-phase1-bench.py", "remove_file"),
        ("missing_tests_marker", "zigux/tests/README.md", "remove_marker"),
        ("missing_tests_historical_warning", "zigux/tests/README.md", "remove_tests_historical_warning"),
        ("missing_phase1_build", "zigux/tests/build.zig", "remove_file"),
        ("missing_phase1_host_tools_smoke", "zigux/tests/phase1_host_tools_smoke.zig", "remove_file"),
        ("missing_checklist_marker", "Documentation/zigux/review-checklist.md", "remove_marker"),
        ("missing_checklist_packet_alignment", "Documentation/zigux/review-checklist.md", "remove_checklist_packet_alignment"),
        ("missing_build_marker", "zigux/tests/build.zig", "remove_build_marker"),
        ("missing_smoke_marker", "zigux/tests/phase1_host_tools_smoke.zig", "remove_smoke_marker"),
        ("missing_workflow_bench_selftest", ".github/workflows/zigux-bootstrap.yml", "remove_bench_selftest"),
        ("missing_workflow_selftest", ".github/workflows/zigux-bootstrap.yml", "remove_selftest"),
        ("missing_workflow_live", ".github/workflows/zigux-bootstrap.yml", "remove_live"),
    ]
    if len(cases) != EXPECTED_SELF_TEST_CASE_COUNT:
        print(
            "self-test:case-count-mismatch:"
            f"expected={EXPECTED_SELF_TEST_CASE_COUNT}:actual={len(cases)}"
        )
        return 1

    first_docs_marker = DOCS_ROOT_MARKERS[0]
    docs_historical_warning_marker = DOCS_ROOT_MARKERS[1]
    docs_bench_marker = DOCS_ROOT_MARKERS[2]
    docs_selftest_marker = DOCS_ROOT_MARKERS[4]
    first_scripts_marker = SCRIPTS_README_MARKERS[0]
    bench_scripts_marker = SCRIPTS_README_MARKERS[2]
    first_tests_marker = TESTS_README_MARKERS[0]
    tests_historical_warning_marker = TESTS_README_MARKERS[1]
    first_checklist_marker = REVIEW_CHECKLIST_MARKERS[0]
    checklist_packet_alignment_marker = REVIEW_CHECKLIST_MARKERS[1]
    first_build_marker = BUILD_ZIG_MARKERS[0]
    first_smoke_marker = SMOKE_ZIG_MARKERS[0]

    for name, relative_path, operation in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-shared-reminder-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            target = root / relative_path
            text = target.read_text(encoding="utf-8")

            if operation == "remove_file":
                target.unlink()
            elif operation == "remove_marker":
                if relative_path == "Documentation/zigux/README.md":
                    target.write_text(text.replace(first_docs_marker + "\n", "", 1), encoding="utf-8")
                elif relative_path == "scripts/zigux/README.md":
                    target.writeText(text.replace(first_scripts_marker + "\n", "", 1), encoding="utf-8")
                elif relative_path == "zigux/tests/README.md":
                    target.write_text(text.replace(first_tests_marker + "\n", "", 1), encoding="utf-8")
                else:
                    target.write_text(text.replace(first_checklist_marker + "\n", "", 1), encoding="utf-8")
            elif operation == "remove_docs_historical_warning":
                target.write_text(
                    text.replace(docs_historical_warning_marker + "\n", "", 1),
                    encoding="utf-8",
                )
            elif operation == "remove_docs_bench_marker":
                target.write_text(
                    text.replace(docs_bench_marker + "\n", "", 1),
                    encoding="utf-8",
                )
            elif operation == "remove_docs_selftest_marker":
                target.write_text(
                    text.replace(docs_selftest_marker + "\n", "", 1),
                    encoding="utf-8",
                )
            elif operation == "remove_scripts_bench_marker":
                target.write_text(text.replace(bench_scripts_marker + "\n", "", 1), encoding="utf-8")
            elif operation == "remove_tests_historical_warning":
                target.write_text(
                    text.replace(tests_historical_warning_marker + "\n", "", 1),
                    encoding="utf-8",
                )
            elif operation == "duplicate_marker":
                target.write_text(text.replace(first_docs_marker, first_docs_marker + "\n" + first_docs_marker, 1), encoding="utf-8")
            elif operation == "remove_checklist_packet_alignment":
                target.write_text(
                    text.replace(checklist_packet_alignment_marker + "\n", "", 1),
                    encoding="utf-8",
                )
            elif operation == "remove_build_marker":
                target.write_text(text.replace(first_build_marker + "\n", "", 1), encoding="utf-8")
            elif operation == "remove_smoke_marker":
                target.write_text(text.replace(first_smoke_marker + "\n", "", 1), encoding="utf-8")
            elif operation == "remove_bench_selftest":
                target.write_text(
                    text.replace("        run: python3 scripts/zigux/check-phase1-bench.py --self-test\n", "", 1),
                    encoding="utf-8",
                )
            elif operation == "remove_selftest":
                target.write_text(
                    text.replace("        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test\n", "", 1),
                    encoding="utf-8",
                )
            elif operation == "remove_live":
                target.write_text(
                    text.replace("        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\n", "", 1),
                    encoding="utf-8",
                )

            missing = collect_missing_markers(root)
            if not missing:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_SHARED_REMINDER_PACKET_SELF_TEST=pass")
    print(f"PHASE1_SHARED_REMINDER_PACKET_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASE_COUNT}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_missing_markers(repo_root(args.root))
    if missing:
        print("PHASE1_SHARED_REMINDER_PACKET=fail")
        for item in missing:
            print(item)
        return 1

    print("PHASE1_SHARED_REMINDER_PACKET=pass")
    print(f"PHASE1_SHARED_REMINDER_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_SHARED_REMINDER_PACKET_REQUIRED_MARKER_COUNT="
        f"{len(DOCS_ROOT_MARKERS) + len(SCRIPTS_README_MARKERS) + len(TESTS_README_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(BUILD_ZIG_MARKERS) + len(SMOKE_ZIG_MARKERS) + len(WORKFLOW_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
