#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()
SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"

REQUIRED_MARKERS = [
    "shared runtime-loader allocator/init-flow packet has returned",
    "`zigux/tests/phase9_build.zig` now names `runtime_loader_allocator_init_flow.zig` through the dedicated `phase9-runtime-loader-allocator-init-flow-tests` test and keeps that replay inside the shared `phase9-runtime-bitmap-tests` bundle",
    "`scripts/zigux/README.md` still keeps the narrower trace-events-only Phase 9 summary and therefore remains the smallest stale shared reminder surface in this lane",
    "`scripts/zigux/check-phase9-build-only-surface.py` is part of the current shared packet and already guards the review-first allocator/init-flow bundle rather than a removed wider-family reminder",
    "keep the bounded `zigux/tests/phase9_build.zig` bundle explicit without treating it as proof that every deeper runtime-publication surface is complete",
    "do not treat the partial runtime bitmap reminder packet as full sample-family return",
]

FORBIDDEN_MARKERS = [
    "the broader runtime-loader packet is absent",
    "does not currently expose the broader shared runtime-loader packet",
]


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / SEQUENCING_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_fixture_text() -> str:
    return "# fixture\n\n" + "\n".join(REQUIRED_MARKERS) + "\n"


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    target = root / SEQUENCING_PATH
    if not target.exists():
        return [f"missing_file:{SEQUENCING_PATH}"]

    text = read_text(root, SEQUENCING_PATH)
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"missing_marker:{SEQUENCING_PATH}:{marker}")
    for marker in FORBIDDEN_MARKERS:
        if marker in text:
            failures.append(f"forbidden_marker:{SEQUENCING_PATH}:{marker}")
    return failures


def seed_fixture_tree(base: Path) -> None:
    write_text(base / SEQUENCING_PATH, build_fixture_text())


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-trace-events-sequencing-loader-boundary-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for marker in REQUIRED_MARKERS:
            seed_fixture_tree(base)
            current = read_text(base, SEQUENCING_PATH)
            write_text(base / SEQUENCING_PATH, current.replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{SEQUENCING_PATH}:{marker}")

        for marker in FORBIDDEN_MARKERS:
            seed_fixture_tree(base)
            current = read_text(base, SEQUENCING_PATH)
            write_text(base / SEQUENCING_PATH, current + f"\n{marker}\n")
            expect_failure(base, f"forbidden_marker:{SEQUENCING_PATH}:{marker}")

        seed_fixture_tree(base)
        (base / SEQUENCING_PATH).unlink()
        expect_failure(base, f"missing_file:{SEQUENCING_PATH}")

        print("PHASE9_TRACE_EVENTS_SEQUENCING_LOADER_BOUNDARY_SELF_TEST=pass")
        print(f"PHASE9_TRACE_EVENTS_SEQUENCING_LOADER_BOUNDARY_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
        print(f"PHASE9_TRACE_EVENTS_SEQUENCING_LOADER_BOUNDARY_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_MARKERS)}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE9_TRACE_EVENTS_SEQUENCING_LOADER_BOUNDARY=pass")
    print(f"PHASE9_TRACE_EVENTS_SEQUENCING_LOADER_BOUNDARY_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE9_TRACE_EVENTS_SEQUENCING_LOADER_BOUNDARY_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
