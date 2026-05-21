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
    "scripts/zigux/validate-phase1-closure.py",
    "scripts/zigux/check-phase1-route-summary-counts.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "scripts/zigux/check-phase1-string-review-packet.py",
    "scripts/zigux/check-phase1-direct-owner-markers.py",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_host_tools_smoke.zig",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
)

EXACT_MARKERS = {
    "Documentation/zigux/phase1-closure.md": (
        "- current authority: the committed helper manifest, this closure note, the narrow closure validator, the shipped bench checker, the shipped shared reminder checker, the live owner-map reminders, and the shared tests-root smoke route remain the trustworthy current-master sources for the closed helper tranche, while the route-summary checker stays an adjacent workflow and Makefile guard.",
        "- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
        "- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
        "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "The current bootstrap workflow also keeps the adjacent Phase 1 route-summary guard wired beside that same live reminder packet: `.github/workflows/zigux-bootstrap.yml` self-tests the directly readable Phase 1 direct-owner, string-review, route-summary, bench, shared-reminder, and closure-validator checks, replays the route-summary, direct-owner, string-review, shared-reminder, closure-validator, and shared tests-root smoke steps on current `master`, and currently keeps the bench checker at self-test coverage only.",
    ),
    "scripts/zigux/validate-phase1-closure.py": (
        'ROUTE_SUMMARY_CHECKER_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")',
        '"route_summary_guard": "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",',
        '(ROUTE_SUMMARY_CHECKER_REL, "phase1-route-summary-counts"),',
    ),
    "scripts/zigux/check-phase1-route-summary-counts.py": (
        '"""Guard the current Phase 1 route-summary packet across closure, Makefile, and workflow."""',
        '"run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",',
        '"run: python3 scripts/zigux/check-phase1-route-summary-counts.py",',
        '"phase1-route-summary:",',
        'print("PHASE1_ROUTE_SUMMARY_COUNTS=pass")',
    ),
    "scripts/zigux/check-phase1-bench.py": (
        "def run_self_test() -> None:",
        'print("phase1-bench:ok")',
    ),
    "scripts/zigux/check-phase1-shared-reminder-packet.py": (
        '"""Guard the current shared Phase 1 reminder packet across docs, tests, scripts, and workflow."""',
        'print("PHASE1_SHARED_REMINDER_PACKET=pass")',
    ),
    "scripts/zigux/check-phase1-string-review-packet.py": (
        'print("phase1-string-review-packet:ok")',
    ),
    "scripts/zigux/check-phase1-direct-owner-markers.py": (
        'print("phase1-direct-owner-markers:ok")',
    ),
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
        "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
    "zigux/Makefile": (
        "phase1-route-summary:",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py",
    ),
    "zigux/tests/fixtures/phase1_helper_manifest.json": (
        '"rule_summary": "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.",',
        '"direct_anchor_followup_helpers": [',
    ),
}

ORDERED_LINE_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": (
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
        "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
        "run: python3 scripts/zigux/validate-phase1-closure.py",
        "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
    "zigux/Makefile": (
        "phase1-route-summary:",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py",
    ),
}

FORBIDDEN_MARKERS = {
    "Documentation/zigux/phase1-closure.md": (
        "- current authority: the committed helper manifest and this closure note remain the only trustworthy current-master sources for the closed helper tranche.",
    ),
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


def require_ordered_lines(relative_path: str, text: str, markers: tuple[str, ...]) -> list[str]:
    lines = [line.strip() for line in text.splitlines()]
    start = 0
    failures: list[str] = []

    for marker in markers:
        try:
            next_index = lines.index(marker.strip(), start)
        except ValueError:
            failures.append(f"{relative_path}:ordered_marker_missing:{marker}")
            return failures
        start = next_index + 1

    return failures


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path}")
    if failures:
        return failures

    for relative_path, markers in EXACT_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            count = text.count(marker)
            if relative_path.endswith((".yml", "Makefile", ".zig")):
                count = count_exact_line(text, marker)
            if count != 1:
                failures.append(f"{relative_path}:expected_once:actual_count={count}:{marker}")

    for relative_path, markers in ORDERED_LINE_MARKERS.items():
        failures.extend(require_ordered_lines(relative_path, read_text(root, relative_path), markers))

    for relative_path, markers in FORBIDDEN_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            count = text.count(marker)
            if relative_path.endswith((".yml", "Makefile", ".zig")):
                count = count_exact_line(text, marker)
            if count != 0:
                failures.append(f"{relative_path}:forbidden_marker:actual_count={count}:{marker}")

    return failures


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        lines: list[str] = []
        for marker in ORDERED_LINE_MARKERS.get(relative_path, ()):
            if marker not in lines:
                lines.append(marker)
        for marker in EXACT_MARKERS.get(relative_path, ()):
            if marker not in lines:
                lines.append(marker)
        write_text(root, relative_path, "\n".join(lines) + ("\n" if lines else ""))


def remove_marker(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    replacement = ""
    if marker + "\n" in text:
        replacement = text.replace(marker + "\n", "", 1)
    else:
        replacement = text.replace(marker, "", 1)
    path.write_text(replacement, encoding="utf-8")


def duplicate_marker(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def add_forbidden(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text + marker + "\n", encoding="utf-8")


def reorder_markers(root: Path, relative_path: str, first: str, second: str) -> None:
    path = root / relative_path
    lines = path.read_text(encoding="utf-8").splitlines()
    first_index = next(i for i, line in enumerate(lines) if line.strip() == first.strip())
    second_index = next(i for i, line in enumerate(lines) if line.strip() == second.strip())
    lines[first_index], lines[second_index] = lines[second_index], lines[first_index]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [("success", None)]
    for relative_path in REQUIRED_FILES:
        cases.append(
            (
                f"missing_file:{relative_path}",
                lambda root, relative_path=relative_path: (root / relative_path).unlink(),
            )
        )
    for relative_path, markers in EXACT_MARKERS.items():
        for marker in markers:
            cases.append(
                (
                    f"missing_marker:{relative_path}:{abs(hash(marker))}",
                    lambda root, relative_path=relative_path, marker=marker: remove_marker(
                        root, relative_path, marker
                    ),
                )
            )
            cases.append(
                (
                    f"duplicate_marker:{relative_path}:{abs(hash(marker))}",
                    lambda root, relative_path=relative_path, marker=marker: duplicate_marker(
                        root, relative_path, marker
                    ),
                )
            )
    for relative_path, markers in ORDERED_LINE_MARKERS.items():
        if len(markers) >= 2:
            cases.append(
                (
                    f"reordered_markers:{relative_path}",
                    lambda root, relative_path=relative_path, first=markers[0], second=markers[1]: reorder_markers(
                        root, relative_path, first, second
                    ),
                )
            )
    for relative_path, markers in FORBIDDEN_MARKERS.items():
        for marker in markers:
            cases.append(
                (
                    f"forbidden_marker:{relative_path}:{abs(hash(marker))}",
                    lambda root, relative_path=relative_path, marker=marker: add_forbidden(
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
        f"{sum(len(markers) for markers in EXACT_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
