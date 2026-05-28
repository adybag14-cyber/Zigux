#!/usr/bin/env python3
"""Guard the current Phase 1 closure-authority packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

REQUIRED_FILES = (
    "Documentation/zigux/phase1-closure.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "scripts/zigux/validate-phase1-closure.py",
    "scripts/zigux/check-phase1-route-summary-counts.py",
    "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_host_tools_smoke.zig",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
)

TEXT_MARKERS = {
    "Documentation/zigux/phase1-closure.md": (
        "- current authority: the committed helper manifest, this closure note, the narrow closure validator, the direct-anchor manifest gate, the shipped bench checker, the shipped shared reminder checker, the live owner-map reminders, and the shared tests-root smoke route remain the trustworthy current-master sources for the closed helper tranche, while the route-summary checker stays an adjacent workflow and Makefile guard.",
        "- `PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-direct-anchor-manifest-gate.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_helpers_build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`",
        "- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
        "- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
        "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "- `PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py exact-checks the current direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string and then reruns the dedicated rbtree direct-anchor checker`",
        "Current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane non-Phase-1 routes across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14.",
    ),
    "scripts/zigux/README.md": (
        "- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live owner-map and string-review guards instead of rebuilding the broader installer-backed closure packet from older missing routes",
        "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
        "- `scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `.github/workflows/zigux-bootstrap.yml` keep the adjacent Phase 1 route-summary guard explicit beside the narrower reminder packet, so scripts-root follow-through can verify the returned non-Phase-1 Makefile route inventory without promoting the older Phase 1 wrappers back into shipped proof",
        "- `zigux/Makefile` is current repo evidence again from the scripts root too, because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded returned `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so keep that returned route summary aligned here while the older Phase 1 wrapper names stay historical reminder vocabulary",
        "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
    ),
    "zigux/tests/README.md": (
        "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "  * current focused Phase 1 helper replay route: `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`",
        "  * current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof",
        "  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    ),
    "scripts/zigux/validate-phase1-closure.py": (
        'DIRECT_ANCHOR_MANIFEST_GATE_REL = Path("scripts/zigux/check-phase1-direct-anchor-manifest-gate.py")',
        'ROUTE_SUMMARY_CHECKER_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")',
        '"direct_anchor_manifest_gate": "`PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py exact-checks the current direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string and then reruns the dedicated rbtree direct-anchor checker`",',
        '"route_summary_guard": "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",',
        '(DIRECT_ANCHOR_MANIFEST_GATE_REL, "phase1-direct-anchor-manifest-gate"),',
        '(ROUTE_SUMMARY_CHECKER_REL, "phase1-route-summary-counts"),',
        "PHASE1_CLOSURE_VALIDATION=pass",
        "PHASE1_CLOSURE_SELF_TEST=pass",
    ),
    "scripts/zigux/check-phase1-route-summary-counts.py": (
        '"""Guard the current Phase 1 route-summary packet across closure, Makefile, and workflow."""',
        'print("PHASE1_ROUTE_SUMMARY_COUNTS=pass")',
        'print("PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=pass")',
    ),
    "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py": (
        'description="Validate the Phase 1 direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string."',
        'print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=pass")',
        'print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST=pass")',
    ),
    "scripts/zigux/check-phase1-bench.py": (
        "RBTREE_REQUIRED_EXACT_CHECKSUMS = {",
        'print("PHASE1_BENCH_CHECK=pass")',
    ),
    "scripts/zigux/check-phase1-shared-reminder-packet.py": (
        '"""Guard the current shared Phase 1 reminder packet across docs, tests, scripts, and workflow."""',
        'print("PHASE1_SHARED_REMINDER_PACKET=pass")',
        'print("PHASE1_SHARED_REMINDER_PACKET_SELF_TEST=pass")',
    ),
    "zigux/tests/fixtures/phase1_helper_manifest.json": (
        '"rule_summary": "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.",',
        '"direct_anchor_followup_helpers": [',
        '"tools/lib/bitmap.zig"',
        '"tools/lib/find_bit.zig"',
        '"tools/lib/rbtree.zig"',
        '"tools/lib/string.zig"',
    ),
}

EXACT_LINE_MARKERS = {
    "zigux/tests/build.zig": (
        '.name = "phase1-host-tools-smoke",',
    ),
    "zigux/tests/phase1_host_tools_smoke.zig": (
        'const slab = @import("slab");',
        'const str_error_r = @import("str_error_r");',
        'const vsprintf = @import("vsprintf");',
        'const zalloc = @import("zalloc");',
    ),
    ".github/workflows/zigux-bootstrap.yml": (
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
    "zigux/Makefile": (
        "phase1-route-summary:",
    ),
}

FORBIDDEN_TEXT_MARKERS = {
    "Documentation/zigux/phase1-closure.md": (
        "- current authority: the committed helper manifest and this closure note remain the only trustworthy current-master sources for the closed helper tranche.",
        "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`",
    ),
}

FORBIDDEN_EXACT_LINE_MARKERS = {
    "zigux/Makefile": (
        "phase1-validate:",
        "phase1-test:",
        "phase1-bench:",
        "phase1:",
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def count_exact_line(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker.strip())


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path}")
    if failures:
        return failures

    for relative_path, markers in TEXT_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            count = text.count(marker)
            if count != 1:
                failures.append(
                    f"{relative_path}:expected_once:actual_count={count}:{marker}"
                )

    for relative_path, markers in EXACT_LINE_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            count = count_exact_line(text, marker)
            if count != 1:
                failures.append(
                    f"{relative_path}:expected_line_once:actual_count={count}:{marker}"
                )

    for relative_path, markers in FORBIDDEN_TEXT_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            count = text.count(marker)
            if count != 0:
                failures.append(
                    f"{relative_path}:forbidden_text:actual_count={count}:{marker}"
                )

    for relative_path, markers in FORBIDDEN_EXACT_LINE_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            count = count_exact_line(text, marker)
            if count != 0:
                failures.append(
                    f"{relative_path}:forbidden_line:actual_count={count}:{marker}"
                )

    return failures


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        lines: list[str] = []
        lines.extend(TEXT_MARKERS.get(relative_path, ()))
        lines.extend(EXACT_LINE_MARKERS.get(relative_path, ()))
        write_text(root, relative_path, "\n".join(lines) + ("\n" if lines else ""))


def remove_marker(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    if marker + "\n" in text:
        text = text.replace(marker + "\n", "", 1)
    else:
        text = text.replace(marker, "", 1)
    path.write_text(text, encoding="utf-8")


def duplicate_marker(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def add_marker(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text + marker + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [("success", None)]

    for relative_path in REQUIRED_FILES:
        cases.append(
            (
                f"missing_file:{relative_path}",
                lambda root, relative_path=relative_path: (root / relative_path).unlink(),
            )
        )

    for relative_path, markers in TEXT_MARKERS.items():
        for marker in markers:
            marker_id = abs(hash((relative_path, marker)))
            cases.append(
                (
                    f"missing_text:{relative_path}:{marker_id}",
                    lambda root, relative_path=relative_path, marker=marker: remove_marker(
                        root, relative_path, marker
                    ),
                )
            )
            cases.append(
                (
                    f"duplicate_text:{relative_path}:{marker_id}",
                    lambda root, relative_path=relative_path, marker=marker: duplicate_marker(
                        root, relative_path, marker
                    ),
                )
            )

    for relative_path, markers in EXACT_LINE_MARKERS.items():
        for marker in markers:
            marker_id = abs(hash((relative_path, marker)))
            cases.append(
                (
                    f"missing_line:{relative_path}:{marker_id}",
                    lambda root, relative_path=relative_path, marker=marker: remove_marker(
                        root, relative_path, marker
                    ),
                )
            )
            cases.append(
                (
                    f"duplicate_line:{relative_path}:{marker_id}",
                    lambda root, relative_path=relative_path, marker=marker: duplicate_marker(
                        root, relative_path, marker
                    ),
                )
            )

    for relative_path, markers in FORBIDDEN_TEXT_MARKERS.items():
        for marker in markers:
            marker_id = abs(hash((relative_path, marker)))
            cases.append(
                (
                    f"forbidden_text:{relative_path}:{marker_id}",
                    lambda root, relative_path=relative_path, marker=marker: add_marker(
                        root, relative_path, marker
                    ),
                )
            )

    for relative_path, markers in FORBIDDEN_EXACT_LINE_MARKERS.items():
        for marker in markers:
            marker_id = abs(hash((relative_path, marker)))
            cases.append(
                (
                    f"forbidden_line:{relative_path}:{marker_id}",
                    lambda root, relative_path=relative_path, marker=marker: add_marker(
                        root, relative_path, marker
                    ),
                )
            )

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-authority-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutate is not None:
                mutate(root)
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

    print("PHASE1_CLOSURE_AUTHORITY_PACKET_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_AUTHORITY_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_CLOSURE_AUTHORITY_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_AUTHORITY_PACKET=pass")
    print(f"PHASE1_CLOSURE_AUTHORITY_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_CLOSURE_AUTHORITY_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in TEXT_MARKERS.values()) + sum(len(markers) for markers in EXACT_LINE_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
