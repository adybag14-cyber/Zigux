#!/usr/bin/env python3
"""Guard the focused Phase 1 helper replay route and its live companion files."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parent

SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
HELPERS_BUILD_REL = Path("zigux/tests/phase1_helpers_build.zig")
HELPERS_TEST_REL = Path("zigux/tests/phase1_helpers.zig")

REQUIRED_FILES = (
    SCRIPTS_README_REL,
    TESTS_README_REL,
    HELPERS_BUILD_REL,
    HELPERS_TEST_REL,
)

REQUIRED_MARKERS = {
    SCRIPTS_README_REL: (
        "`zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_helpers_build.zig`, and `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig` restore a focused fixture-backed helper replay anchor on current `master` without widening back into the older validator-first or bench-route stack",
    ),
    TESTS_README_REL: (
        "* current focused Phase 1 helper replay route: `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`",
    ),
    HELPERS_BUILD_REL: (
        '.name = "phase1-helpers",',
        'root_source_file = b.path("phase1_helpers.zig"),',
    ),
    HELPERS_TEST_REL: (
        'const fixture_bytes = @embedFile("fixtures/phase1_helpers.json");',
        'test "phase 1 helper ports match committed parity fixture" {',
    ),
}


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT.resolve()


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        path = root / relative_path
        if not path.exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
            continue

        text = path.read_text(encoding="utf-8")
        for marker in REQUIRED_MARKERS[relative_path]:
            count = text.count(marker)
            if count != 1:
                failures.append(
                    f"{relative_path.as_posix()}:marker:{marker}:expected=1:actual={count}"
                )

    return failures


def write_text(root: Path, relative_path: Path, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write_text(
        root,
        SCRIPTS_README_REL,
        "\n".join(REQUIRED_MARKERS[SCRIPTS_README_REL]) + "\n",
    )
    write_text(
        root,
        TESTS_README_REL,
        "\n".join(REQUIRED_MARKERS[TESTS_README_REL]) + "\n",
    )
    write_text(
        root,
        HELPERS_BUILD_REL,
        "\n".join(REQUIRED_MARKERS[HELPERS_BUILD_REL]) + "\n",
    )
    write_text(
        root,
        HELPERS_TEST_REL,
        "\n".join(REQUIRED_MARKERS[HELPERS_TEST_REL]) + "\n",
    )


def mutate_remove_marker(root: Path, relative_path: Path, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def mutate_duplicate_marker(root: Path, relative_path: Path, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [("success", None)]

    for relative_path in REQUIRED_FILES:
        cases.append(
            (
                f"missing_file:{relative_path.as_posix()}",
                lambda root, relative_path=relative_path: (root / relative_path).unlink(),
            )
        )
        for marker in REQUIRED_MARKERS[relative_path]:
            cases.append(
                (
                    f"remove_marker:{relative_path.as_posix()}:{abs(hash(marker))}",
                    lambda root, relative_path=relative_path, marker=marker: mutate_remove_marker(
                        root, relative_path, marker
                    ),
                )
            )
            cases.append(
                (
                    f"duplicate_marker:{relative_path.as_posix()}:{abs(hash(marker))}",
                    lambda root, relative_path=relative_path, marker=marker: mutate_duplicate_marker(
                        root, relative_path, marker
                    ),
                )
            )

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-helper-replay-route-") as tmpdir:
            root = Path(tmpdir)
            build_sample_root(root)
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

    print("PHASE1_HELPER_REPLAY_ROUTE_SELF_TEST=pass")
    print(f"PHASE1_HELPER_REPLAY_ROUTE_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root used for checks")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_HELPER_REPLAY_ROUTE=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_HELPER_REPLAY_ROUTE=pass")
    print("PHASE1_HELPER_REPLAY_ROUTE_SHARED_DOCS=2")
    print("PHASE1_HELPER_REPLAY_ROUTE_LIVE_COMPANIONS=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
