#!/usr/bin/env python3
"""Guard the current Phase 1 closure-route cluster across docs, workflow, Makefile, and tests."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

REQUIRED_FILES = (
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/build.zig",
    ".github/workflows/zigux-bootstrap.yml",
)

TEXT_MARKERS = {
    "Documentation/zigux/phase1-closure.md": (
        "- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
        "- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
        "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "The current bootstrap workflow also keeps the adjacent Phase 1 route-summary guard wired beside that same live reminder packet:",
    ),
    "Documentation/zigux/review-checklist.md": (
        "`scripts/zigux/check-phase1-direct-owner-markers.py`",
        "`scripts/zigux/check-phase1-bench.py`",
        "`scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "`zigux/tests/build.zig`",
        "`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet",
    ),
    "scripts/zigux/README.md": (
        "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
        "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
    ),
    "zigux/tests/README.md": (
        "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "  * current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof",
    ),
    "zigux/tests/build.zig": (
        '.name = "phase1-host-tools-smoke",',
        '"Run the shared Phase 1 host-tools smoke anchor from zigux/tests"',
        "phase1_step.dependOn(&phase1_host_tools_smoke.step);",
        "smoke_step.dependOn(&phase1_host_tools_smoke.step);",
        "test_step.dependOn(&phase1_host_tools_smoke.step);",
    ),
}

LINE_MARKERS = {
    "zigux/Makefile": (
        "phase1-route-summary:",
        "phase2-toolchain:",
        "phase3-validate:",
        "phase4-validate:",
        "phase6-validate:",
        "phase8-validate:",
        "phase10-validate:",
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-smoke phase12-test",
        "phase14-validate:",
    ),
    ".github/workflows/zigux-bootstrap.yml": (
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
        "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
        "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
        "run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
        "run: python3 scripts/zigux/check-phase1-string-review-packet.py",
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
        "run: python3 scripts/zigux/validate-phase1-closure.py",
        "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
}

FORBIDDEN_LINES = {
    "zigux/Makefile": (
        "phase1-validate:",
        "phase1-test:",
        "phase1-bench:",
        "phase1:",
    ),
    ".github/workflows/zigux-bootstrap.yml": (
        "run: python3 scripts/zigux/validate-phase1.py --self-test",
        "run: python3 scripts/zigux/validate-phase1.py",
        "run: python3 scripts/zigux/check-phase1-parity.py --self-test",
        "run: python3 scripts/zigux/check-phase1-parity.py",
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def count_exact_line(text: str, marker: str) -> int:
    want = marker.strip()
    return sum(1 for line in text.splitlines() if line.strip() == want)


def require_once(text: str, label: str, marker: str, *, exact_line: bool) -> list[str]:
    count = count_exact_line(text, marker) if exact_line else text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_absent(text: str, label: str, marker: str, *, exact_line: bool) -> list[str]:
    count = count_exact_line(text, marker) if exact_line else text.count(marker)
    return [] if count == 0 else [f"{label}:expected=0:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path}")
    if failures:
        return failures

    for relative_path, markers in TEXT_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            failures.extend(require_once(text, f"{relative_path}:{marker}", marker, exact_line=False))

    for relative_path, markers in LINE_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            failures.extend(require_once(text, f"{relative_path}:{marker}", marker, exact_line=True))

    for relative_path, markers in FORBIDDEN_LINES.items():
        text = read_text(root, relative_path)
        for marker in markers:
            failures.extend(require_absent(text, f"{relative_path}:{marker}", marker, exact_line=True))

    return failures


def write_text(root: Path, relative_path: str, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        chunks: list[str] = []
        chunks.extend(TEXT_MARKERS.get(relative_path, ()))
        chunks.extend(LINE_MARKERS.get(relative_path, ()))
        write_text(root, relative_path, "\n".join(chunks) + ("\n" if chunks else ""))


def remove_marker(root: Path, relative_path: str, marker: str, *, exact_line: bool) -> None:
    path = root / relative_path
    if exact_line:
        lines = path.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(lines):
            if line.strip() == marker.strip():
                del lines[idx]
                path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
                return
        raise ValueError(f"missing marker: {relative_path}: {marker}")

    text = path.read_text(encoding="utf-8")
    replacement = marker + "\n"
    if replacement in text:
        path.write_text(text.replace(replacement, "", 1), encoding="utf-8")
        return
    if marker in text:
        path.write_text(text.replace(marker, "", 1), encoding="utf-8")
        return
    raise ValueError(f"missing marker: {relative_path}: {marker}")


def duplicate_marker(root: Path, relative_path: str, marker: str, *, exact_line: bool) -> None:
    path = root / relative_path
    if exact_line:
        lines = path.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(lines):
            if line.strip() == marker.strip():
                lines.insert(idx + 1, line)
                path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                return
        raise ValueError(f"missing marker: {relative_path}: {marker}")

    text = path.read_text(encoding="utf-8")
    if marker not in text:
        raise ValueError(f"missing marker: {relative_path}: {marker}")
    path.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def add_forbidden(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text + marker + "\n", encoding="utf-8")


def write_sample_root(destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)
    build_sample_repo(destination)


def run_self_test() -> int:
    cases: list[tuple[str, tuple[str, str, bool] | tuple[str, str] | None]] = [("success", None)]

    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path}", ("missing_file", relative_path)))
    for relative_path, markers in TEXT_MARKERS.items():
        for marker in markers:
            cases.append((f"missing_marker:{relative_path}", ("remove_text", relative_path, marker, False)))
            cases.append((f"duplicate_marker:{relative_path}", ("duplicate_text", relative_path, marker, False)))
    for relative_path, markers in LINE_MARKERS.items():
        for marker in markers:
            cases.append((f"missing_line:{relative_path}", ("remove_line", relative_path, marker, True)))
            cases.append((f"duplicate_line:{relative_path}", ("duplicate_line", relative_path, marker, True)))
    for relative_path, markers in FORBIDDEN_LINES.items():
        for marker in markers:
            cases.append((f"forbidden_line:{relative_path}", ("forbidden", relative_path, marker)))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-route-cluster-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutation:
                kind = mutation[0]
                if kind == "missing_file":
                    (root / mutation[1]).unlink()
                elif kind == "remove_text":
                    remove_marker(root, mutation[1], mutation[2], exact_line=False)
                elif kind == "duplicate_text":
                    duplicate_marker(root, mutation[1], mutation[2], exact_line=False)
                elif kind == "remove_line":
                    remove_marker(root, mutation[1], mutation[2], exact_line=True)
                elif kind == "duplicate_line":
                    duplicate_marker(root, mutation[1], mutation[2], exact_line=True)
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

    print("PHASE1_CLOSURE_ROUTE_CLUSTER_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_ROUTE_CLUSTER_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    parser.add_argument("--write-sample-root", help="write a sample current-like root for validation")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        destination = Path(args.write_sample_root).resolve()
        write_sample_root(destination)
        print(f"phase1-closure-route-cluster:sample-root-written:{destination}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_CLOSURE_ROUTE_CLUSTER=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_ROUTE_CLUSTER=pass")
    print(f"PHASE1_CLOSURE_ROUTE_CLUSTER_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_CLOSURE_ROUTE_CLUSTER_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in TEXT_MARKERS.values()) + sum(len(markers) for markers in LINE_MARKERS.values())}"
    )
    print(
        "PHASE1_CLOSURE_ROUTE_CLUSTER_FORBIDDEN_MARKER_COUNT="
        f"{sum(len(markers) for markers in FORBIDDEN_LINES.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
