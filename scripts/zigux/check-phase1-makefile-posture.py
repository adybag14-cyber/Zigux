#!/usr/bin/env python3
"""Guard the current Phase 1 Makefile posture across closure-validation surfaces."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

REQUIRED_FILES = (
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/README.md",
    "zigux/tests/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase1-closure.py",
    "scripts/zigux/check-phase1-route-summary-counts.py",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
)

EXACT_MARKERS = {
    "Documentation/zigux/phase1-closure.md": (
        "Current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane non-Phase-1 routes across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14. It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`, so treat the returned file as current repo evidence while those older Phase 1 wrapper names remain historical packet members rather than active closure proof.",
        "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
    ),
    "Documentation/zigux/README.md": (
        "* repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/phase1_helpers_c_harness.c`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence, while `zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14.",
        "* `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.",
    ),
    "zigux/tests/README.md": (
        "  * current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof",
        "  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    ),
    "scripts/zigux/README.md": (
        "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, bench, and C-harness routes as historical packet members that need fresh re-materialization before they are reused here as direct current-`master` reminder evidence",
        "- `zigux/Makefile` is current repo evidence again from the scripts root too, because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded returned `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so keep that returned route summary aligned here while the older Phase 1 wrapper names stay historical reminder vocabulary",
        "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
    ),
    "scripts/zigux/validate-phase1-closure.py": (
        'EXPECTED_MAKEFILE_MARKERS = (',
        '"phase14-validate:",',
        'FORBIDDEN_MAKEFILE_MARKERS = (',
        '"phase1-validate:",',
        '"phase1-test:",',
        '"phase1-bench:",',
        '"phase1:",',
    ),
    "scripts/zigux/check-phase1-route-summary-counts.py": (
        '"zigux/Makefile": (',
        '"phase1-route-summary:",',
        '"phase1-validate:",',
        '"phase1-test:",',
        '"phase1-bench:",',
        '"phase1:",',
        'print("PHASE1_ROUTE_SUMMARY_COUNTS=pass")',
    ),
    "zigux/Makefile": (
        "phase1-route-summary:",
        "phase2-toolchain:",
        "phase12: phase12-validate phase12-smoke phase12-test",
        "phase14-validate:",
    ),
    ".github/workflows/zigux-bootstrap.yml": (
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    ),
}

FORBIDDEN_MARKERS = {
    "zigux/Makefile": (
        "phase1-validate:",
        "phase1-test:",
        "phase1-bench:",
        "phase1:",
    ),
}

EXACT_LINE_FILES = {
    ".github/workflows/zigux-bootstrap.yml",
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_marker(text: str, label: str, marker: str, exact_line: bool) -> list[str]:
    if exact_line:
        count = sum(1 for line in text.splitlines() if line.strip() == marker.strip())
    else:
        count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_absent_marker(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker.strip())
    return [] if count == 0 else [f"{label}:expected=0:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path}" for path in REQUIRED_FILES if not (root / path).exists()]
    if failures:
        return failures

    for relative_path, markers in EXACT_MARKERS.items():
        text = read_text(root, relative_path)
        exact_line = relative_path in EXACT_LINE_FILES
        for marker in markers:
            failures.extend(require_exact_marker(text, f"{relative_path}:{marker}", marker, exact_line))

    for relative_path, markers in FORBIDDEN_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            failures.extend(require_absent_marker(text, f"{relative_path}:{marker}", marker))

    return failures


def write_text(root: Path, relative_path: str, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        lines = list(EXACT_MARKERS.get(relative_path, ()))
        if relative_path in FORBIDDEN_MARKERS:
            lines.append("# forbidden markers intentionally absent")
        write_text(root, relative_path, "\n".join(lines) + ("\n" if lines else ""))


def remove_marker(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def duplicate_marker(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def add_forbidden(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, tuple[str, ...] | None]] = [("success", None)]
    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path}", ("missing_file", relative_path)))
    for relative_path, markers in EXACT_MARKERS.items():
        for marker in markers:
            marker_id = str(abs(hash((relative_path, marker))))
            cases.append((f"missing_marker:{relative_path}:{marker_id}", ("remove", relative_path, marker)))
            cases.append((f"duplicate_marker:{relative_path}:{marker_id}", ("duplicate", relative_path, marker)))
    for relative_path, markers in FORBIDDEN_MARKERS.items():
        for marker in markers:
            cases.append((f"forbidden_marker:{relative_path}:{marker}", ("forbidden", relative_path, marker)))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-makefile-posture-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutation is not None:
                kind = mutation[0]
                if kind == "missing_file":
                    (root / mutation[1]).unlink()
                elif kind == "remove":
                    remove_marker(root, mutation[1], mutation[2])
                elif kind == "duplicate":
                    duplicate_marker(root, mutation[1], mutation[2])
                elif kind == "forbidden":
                    add_forbidden(root, mutation[1], mutation[2])

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

    print("PHASE1_MAKEFILE_POSTURE_SELF_TEST=pass")
    print(f"PHASE1_MAKEFILE_POSTURE_SELF_TEST_CASE_COUNT={len(cases)}")
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
        print("PHASE1_MAKEFILE_POSTURE=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_MAKEFILE_POSTURE=pass")
    print(f"PHASE1_MAKEFILE_POSTURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_MAKEFILE_POSTURE_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in EXACT_MARKERS.values())}"
    )
    print(
        "PHASE1_MAKEFILE_POSTURE_FORBIDDEN_MARKER_COUNT="
        f"{sum(len(markers) for markers in FORBIDDEN_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
