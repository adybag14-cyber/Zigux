#!/usr/bin/env python3
"""Guard the current Phase 1 historical-companion packet across reminder surfaces."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

REQUIRED_FILES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase1-closure.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "zigux/tests/README.md",
    "zigux/Makefile",
)

EXACT_LINE_MARKERS = {
    "Documentation/zigux/README.md": (
        "* repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence, while `zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14.",
        "* the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces.",
        "* keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.",
    ),
    "Documentation/zigux/phase1-closure.md": (
        "- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
        "- `PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`",
    ),
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md": (
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_GAPS=the shared reminder packet now keeps scripts/zigux/check-phase1-bench.py explicit across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md, while the older installer-backed, validator-first, bench-route, and replay names stay historical packet members until they reread cleanly on current master`",
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ROUTE_SPLIT=Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md now all carry the shipped bench-checker wording, while Documentation/zigux/phase1-closure.md plus scripts/zigux/validate-phase1-closure.py keep the restored closure-side packet explicit and the broader installer-backed, validator-first, bench-route, and replay names remain historical packet members until direct current-master rereads restore them`",
    ),
    "Documentation/zigux/review-checklist.md": (
        "  * if the change touches the shared Phase 1 host-tools closure packet, do `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?",
    ),
    "scripts/zigux/README.md": (
        "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence",
        "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
    ),
    "zigux/tests/README.md": (
        "  * broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
        "  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    ),
}

FORBIDDEN_EXACT_LINES = {
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


def require_exact_line(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker.strip())
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_absent_line(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker.strip())
    return [] if count == 0 else [f"{label}:expected=0:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path}")
    if failures:
        return failures

    for relative_path, markers in EXACT_LINE_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            failures.extend(require_exact_line(text, f"{relative_path}:{marker}", marker))

    for relative_path, markers in FORBIDDEN_EXACT_LINES.items():
        text = read_text(root, relative_path)
        for marker in markers:
            failures.extend(require_absent_line(text, f"{relative_path}:{marker}", marker))

    return failures


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        markers = list(EXACT_LINE_MARKERS.get(relative_path, ()))
        content = "\n".join(markers)
        if content:
            content += "\n"
        write_text(root, relative_path, content)


def remove_marker(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker.strip():
            del lines[idx]
            path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
            return
    raise ValueError(f"missing marker: {relative_path}: {marker}")


def duplicate_marker(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker.strip():
            lines.insert(idx + 1, line)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(f"missing marker: {relative_path}: {marker}")


def add_forbidden(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text + marker + "\n", encoding="utf-8")


def write_sample_root(root: Path) -> None:
    build_sample_repo(root)


def run_self_test() -> int:
    cases = [("success", None)]
    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path}", ("missing_file", relative_path)))
    for relative_path, markers in EXACT_LINE_MARKERS.items():
        for marker in markers:
            cases.append((f"missing_marker:{relative_path}", ("remove", relative_path, marker)))
            cases.append((f"duplicate_marker:{relative_path}", ("duplicate", relative_path, marker)))
    for relative_path, markers in FORBIDDEN_EXACT_LINES.items():
        for marker in markers:
            cases.append((f"forbidden_marker:{relative_path}", ("forbidden", relative_path, marker)))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-historical-companion-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutation:
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

    print("PHASE1_HISTORICAL_COMPANION_PACKET_SELF_TEST=pass")
    print(f"PHASE1_HISTORICAL_COMPANION_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in self-test",
    )
    parser.add_argument(
        "--write-sample-root",
        help="write a minimal current-like sample root",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_HISTORICAL_COMPANION_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_HISTORICAL_COMPANION_PACKET=pass")
    print(f"PHASE1_HISTORICAL_COMPANION_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_HISTORICAL_COMPANION_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in EXACT_LINE_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
