#!/usr/bin/env python3
"""Guard the current Phase 1 review-checklist reminder packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parent

REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
ROUTE_SUMMARY_CHECKER_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")
FIND_BIT_BENCH_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py")
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
SHARED_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
TESTS_BUILD_REL = Path("zigux/tests/build.zig")
SMOKE_TEST_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
MAKEFILE_REL = Path("zigux/Makefile")

REQUIRED_FILES = (
    REVIEW_CHECKLIST_REL,
    PHASE1_CLOSURE_REL,
    LANE_NOTE_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    CLOSURE_VALIDATOR_REL,
    ROUTE_SUMMARY_CHECKER_REL,
    FIND_BIT_BENCH_ANCHOR_CHECKER_REL,
    BENCH_CHECKER_REL,
    SHARED_REMINDER_CHECKER_REL,
    TESTS_BUILD_REL,
    SMOKE_TEST_REL,
    WORKFLOW_REL,
    MANIFEST_REL,
    MAKEFILE_REL,
)

REQUIRED_MARKERS = {
    REVIEW_CHECKLIST_REL: (
        "* if the change touches the shared Phase 1 host-tools closure packet, do `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet, keep `scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `zigux/Makefile` explicit as the adjacent Phase 1 route-summary evidence for the returned Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?",
    ),
    PHASE1_CLOSURE_REL: (
        "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
        "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
        "`PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`",
        "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    ),
    LANE_NOTE_REL: (
        "`PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig`",
    ),
    SCRIPTS_README_REL: (
        "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
        "- `scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `.github/workflows/zigux-bootstrap.yml` keep the adjacent Phase 1 route-summary guard explicit beside the narrower reminder packet, so scripts-root follow-through can verify the returned non-Phase-1 Makefile route inventory without promoting the older Phase 1 wrappers back into shipped proof",
        "- `zigux/Makefile` is current repo evidence again from the scripts root too, because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14, so keep that returned route summary aligned here while the older Phase 1 wrapper names stay historical reminder vocabulary",
    ),
    TESTS_README_REL: (
        "* current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "* current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof",
        "* keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    ),
    CLOSURE_VALIDATOR_REL: (
        'ROUTE_SUMMARY_CHECKER_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")',
        'FIND_BIT_BENCH_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py")',
        'print("PHASE1_CLOSURE_VALIDATION=pass")',
        'print("PHASE1_CLOSURE_SELF_TEST=pass")',
    ),
    ROUTE_SUMMARY_CHECKER_REL: (
        'print("PHASE1_ROUTE_SUMMARY_COUNTS=pass")',
        'print("PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=pass")',
    ),
    FIND_BIT_BENCH_ANCHOR_CHECKER_REL: (
        'print("PHASE1_FIND_BIT_BENCH_ANCHORS=pass")',
        'print("PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST=pass")',
    ),
    BENCH_CHECKER_REL: (
        "RBTREE_REQUIRED_EXACT_CHECKSUMS = {",
        "def run_self_test() -> None:",
    ),
    SHARED_REMINDER_CHECKER_REL: (
        '"""Guard the current shared Phase 1 reminder packet across docs, tests, scripts, and workflow."""',
        'print("PHASE1_SHARED_REMINDER_PACKET=pass")',
        'print("PHASE1_SHARED_REMINDER_PACKET_SELF_TEST=pass")',
    ),
    TESTS_BUILD_REL: (
        '.name = "phase1-host-tools-smoke",',
        'root_module.addImport("slab", slab_module);',
        'root_module.addImport("str_error_r", str_error_r_module);',
        'root_module.addImport("vsprintf", vsprintf_module);',
        'root_module.addImport("zalloc", zalloc_module);',
    ),
    SMOKE_TEST_REL: (
        'const slab = @import("slab");',
        'const str_error_r = @import("str_error_r");',
        'const vsprintf = @import("vsprintf");',
        'const zalloc = @import("zalloc");',
        'try std.testing.expect(@hasDecl(slab, "kmallocBytes"));',
        'try std.testing.expect(@hasDecl(str_error_r, "strErrorR"));',
        'try std.testing.expect(@hasDecl(vsprintf, "scnprintf"));',
        'try std.testing.expect(@hasDecl(zalloc, "zallocBytes"));',
    ),
    WORKFLOW_REL: (
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
    MANIFEST_REL: (
        '"helper_count": 13,',
        '"shared_replay_parked_helpers": [',
        '"direct_anchor_followup_helpers": [',
    ),
    MAKEFILE_REL: (
        "phase1-route-summary:",
        "phase3-validate",
        "phase4-validate",
        "phase6-validate",
        "phase8-validate",
        "phase10-validate",
        "phase12-validate",
        "phase14-validate",
    ),
}

FORBIDDEN_MARKERS = {
    PHASE1_CLOSURE_REL: (
        "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`",
    ),
    MAKEFILE_REL: (
        "phase1-validate:",
        "phase1-test:",
        "phase1-bench:",
        "phase1:",
    ),
}


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{marker}"]


def require_exact_line(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker.strip())
    return [] if count == 1 else [f"{label}:expected_line_once:actual_count={count}:{marker}"]


def require_absent(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 0 else [f"{label}:forbidden:actual_count={count}:{marker}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    for relative_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            if relative_path == WORKFLOW_REL:
                failures.extend(require_exact_line(text, relative_path.as_posix(), marker))
            else:
                failures.extend(
                    require_exact_occurrence(text, relative_path.as_posix(), marker)
                )
        for forbidden in FORBIDDEN_MARKERS.get(relative_path, ()):
            failures.extend(require_absent(text, relative_path.as_posix(), forbidden))

    return failures


def write_text(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        lines = list(REQUIRED_MARKERS.get(relative_path, ()))
        write_text(root, relative_path, "\n".join(lines) + ("\n" if lines else ""))


def remove_marker(root: Path, relative_path: Path, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker + "\n", "", 1).replace(marker, "", 1), encoding="utf-8")


def add_forbidden(root: Path, relative_path: Path, marker: str) -> None:
    path = root / relative_path
    path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [
        ("baseline", None),
        ("missing_review_checklist", lambda root: (root / REVIEW_CHECKLIST_REL).unlink()),
        (
            "missing_review_marker",
            lambda root: remove_marker(root, REVIEW_CHECKLIST_REL, REQUIRED_MARKERS[REVIEW_CHECKLIST_REL][0]),
        ),
        (
            "missing_closure_route_summary_guard",
            lambda root: remove_marker(root, PHASE1_CLOSURE_REL, REQUIRED_MARKERS[PHASE1_CLOSURE_REL][1]),
        ),
        (
            "missing_find_bit_bench_anchor_guard",
            lambda root: remove_marker(root, PHASE1_CLOSURE_REL, REQUIRED_MARKERS[PHASE1_CLOSURE_REL][2]),
        ),
        (
            "missing_scripts_route_summary_line",
            lambda root: remove_marker(root, SCRIPTS_README_REL, REQUIRED_MARKERS[SCRIPTS_README_REL][1]),
        ),
        (
            "missing_tests_smoke_route",
            lambda root: remove_marker(root, TESTS_README_REL, REQUIRED_MARKERS[TESTS_README_REL][0]),
        ),
        (
            "missing_validator_route_summary_constant",
            lambda root: remove_marker(root, CLOSURE_VALIDATOR_REL, REQUIRED_MARKERS[CLOSURE_VALIDATOR_REL][0]),
        ),
        (
            "missing_route_summary_checker_pass",
            lambda root: remove_marker(root, ROUTE_SUMMARY_CHECKER_REL, REQUIRED_MARKERS[ROUTE_SUMMARY_CHECKER_REL][0]),
        ),
        (
            "missing_find_bit_anchor_pass",
            lambda root: remove_marker(root, FIND_BIT_BENCH_ANCHOR_CHECKER_REL, REQUIRED_MARKERS[FIND_BIT_BENCH_ANCHOR_CHECKER_REL][0]),
        ),
        (
            "missing_workflow_route_summary_selftest",
            lambda root: remove_marker(root, WORKFLOW_REL, REQUIRED_MARKERS[WORKFLOW_REL][0]),
        ),
        (
            "missing_makefile_route",
            lambda root: remove_marker(root, MAKEFILE_REL, REQUIRED_MARKERS[MAKEFILE_REL][0]),
        ),
        (
            "forbidden_phase1_validate_route",
            lambda root: add_forbidden(root, MAKEFILE_REL, FORBIDDEN_MARKERS[MAKEFILE_REL][0]),
        ),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-review-checklist-alignment-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-review-checklist-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-review-checklist-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_REVIEW_CHECKLIST_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_REVIEW_CHECKLIST_ALIGNMENT_SELF_TEST_CASE_COUNT={len(cases)}")
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
        print("PHASE1_REVIEW_CHECKLIST_ALIGNMENT=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_REVIEW_CHECKLIST_ALIGNMENT=pass")
    print(f"PHASE1_REVIEW_CHECKLIST_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_REVIEW_CHECKLIST_ALIGNMENT_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
