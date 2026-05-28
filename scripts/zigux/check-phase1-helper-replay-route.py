#!/usr/bin/env python3
"""Guard the focused Phase 1 helper replay route across current reminder surfaces."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
PHASE1_HELPERS_BUILD_REL = Path("zigux/tests/phase1_helpers_build.zig")
PHASE1_HELPERS_REPLAY_REL = Path("zigux/tests/phase1_helpers.zig")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    PHASE1_HELPERS_BUILD_REL,
    PHASE1_HELPERS_REPLAY_REL,
    WORKFLOW_REL,
)

REQUIRED_MARKERS = {
    PHASE1_CLOSURE_REL: (
        "- `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`",
        "Those routes keep a minimal shared import-and-wire smoke check plus a focused fixture-backed helper replay anchor alive for the current helper packet while the dedicated closure validator keeps the restored closure note aligned with the committed helper manifest and the shipped reminder packet on current `master`.",
    ),
    SCRIPTS_README_REL: (
        "- `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_helpers_build.zig`, and `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig` keep a focused fixture-backed helper parity replay anchor on current `master` without widening back into the older validator-first, bench, or installer-backed closure stack",
    ),
    TESTS_README_REL: (
        "  * current focused Phase 1 helper replay route: `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`",
    ),
    PHASE1_HELPERS_BUILD_REL: (
        '.root_source_file = b.path("phase1_helpers.zig"),',
        '.name = "phase1-helpers",',
        'const phase1_helpers = b.step(',
        '"Run the focused Phase 1 helper replay anchor from zigux/tests"',
    ),
    PHASE1_HELPERS_REPLAY_REL: (
        'const fixture_bytes = @embedFile("fixtures/phase1_helpers.json");',
        'test "phase 1 helper ports match committed parity fixture" {',
    ),
    WORKFLOW_REL: (
        "      - name: Run current Phase 1 shared tests-root smoke",
        "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
}

FORBIDDEN_MARKERS = {
    WORKFLOW_REL: (
        "phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig",
        "Run current Phase 1 focused helper replay",
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_absent(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 0 else [f"{label}:expected=0:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    for relative_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            failures.extend(
                require_exact_occurrence(
                    text,
                    f"{relative_path.as_posix()}:{marker}",
                    marker,
                )
            )

    for relative_path, markers in FORBIDDEN_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            failures.extend(
                require_absent(
                    text,
                    f"{relative_path.as_posix()}:{marker}",
                    marker,
                )
            )

    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        write_text(root, relative_path, "\n".join(markers) + "\n")


def run_self_test() -> int:
    cases: list[tuple[str, str | None, str]] = [("baseline", None, "ok")]
    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path.as_posix()}", relative_path.as_posix(), "remove_file"))
    for relative_path, markers in REQUIRED_MARKERS.items():
        for marker in markers:
            cases.append((f"missing_marker:{relative_path.as_posix()}", f"{relative_path.as_posix()}::{marker}", "remove_marker"))
            cases.append((f"duplicate_marker:{relative_path.as_posix()}", f"{relative_path.as_posix()}::{marker}", "duplicate_marker"))
    for relative_path, markers in FORBIDDEN_MARKERS.items():
        for marker in markers:
            cases.append((f"forbidden_marker:{relative_path.as_posix()}", f"{relative_path.as_posix()}::{marker}", "insert_forbidden"))

    for name, payload, mode in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-helper-replay-route-") as tmp_dir:
            root = Path(tmp_dir)
            build_sample_root(root)

            if mode == "remove_file" and payload is not None:
                (root / payload).unlink()
            elif mode in {"remove_marker", "duplicate_marker", "insert_forbidden"} and payload is not None:
                path_text, marker = payload.split("::", 1)
                target = root / path_text
                text = target.read_text(encoding="utf-8")
                if mode == "remove_marker":
                    target.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")
                elif mode == "duplicate_marker":
                    target.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")
                else:
                    target.write_text(text + marker + "\n", encoding="utf-8")

            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-helper-replay-route-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-helper-replay-route-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_HELPER_REPLAY_ROUTE_SELF_TEST=pass")
    print(f"PHASE1_HELPER_REPLAY_ROUTE_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    parser.add_argument(
        "--write-sample-root",
        help="write a sample root for checker replay and exit",
    )
    args = parser.parse_args()

    if args.write_sample_root:
        build_sample_root(Path(args.write_sample_root).resolve())
        return 0

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_HELPER_REPLAY_ROUTE=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_HELPER_REPLAY_ROUTE=pass")
    print(f"PHASE1_HELPER_REPLAY_ROUTE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_HELPER_REPLAY_ROUTE_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    print(
        "PHASE1_HELPER_REPLAY_ROUTE_FORBIDDEN_MARKER_COUNT="
        f"{sum(len(markers) for markers in FORBIDDEN_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
