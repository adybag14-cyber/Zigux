#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "zigux/Makefile").exists() and (
            candidate / "Documentation/zigux/phase12-release-sequencing.md"
        ).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

MAKEFILE_PATH = "zigux/Makefile"
RELEASE_SEQUENCING_PATH = "Documentation/zigux/phase12-release-sequencing.md"
RELEASE_READINESS_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"

MAKEFILE_FALLBACK_MARKERS = [
    "ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))",
    "ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))",
    "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)",
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
]

RELEASE_SEQUENCING_MARKERS = [
    "shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`",
    "If `zig` is unavailable on `PATH`, keep that same validator-first then smoke-first order and first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`; if that local fallback is also absent, keep the shipped `make -C zigux phase12-validate` wrapper explicit ahead of the attached-Zig reruns `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of inventing a focused libbpf-only route, a cross-build route, or another unshipped Phase 12 replay surface.",
    "Current workflow-side fallback recovery evidence: `.github/workflows/zigux-bootstrap.yml` now rebuilds the repo-local `.zig-toolchain` path by first trying the pinned `third_party` archive, then the Zig community-mirror list, and finally `ziglang.org`, so this sequencing note should treat the local Makefile fallback as a restorable local-first path before attached-`ZIG=<attached-zig-path>` reruns rather than as a one-shot cache hit.",
]

RELEASE_READINESS_MARKERS = [
    "current `zigux/Makefile` now exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again.",
    "That means the PMO release notes can treat `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-`master` evidence again, while still keeping the validator-first support packet distinct from deeper driver-delivery claims.",
]

REQUIRED_FILES = [
    MAKEFILE_PATH,
    RELEASE_SEQUENCING_PATH,
    RELEASE_READINESS_PATH,
]

REQUIRED_MARKERS = {
    MAKEFILE_PATH: MAKEFILE_FALLBACK_MARKERS,
    RELEASE_SEQUENCING_PATH: RELEASE_SEQUENCING_MARKERS,
    RELEASE_READINESS_PATH: RELEASE_READINESS_MARKERS,
}

FORBIDDEN_MARKERS = {
    RELEASE_SEQUENCING_PATH: ["reminder-only `make -C zigux phase12-validate`"],
    RELEASE_READINESS_PATH: ["reminder-only `make -C zigux phase12-validate`"],
}


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")

    for rel_path, markers in FORBIDDEN_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker in text:
                failures.append(f"forbidden_marker:{rel_path}:{marker}")

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def marker_fixture(title: str, markers: list[str]) -> str:
    return f"{title}\n\n" + "\n".join(f"- {marker}" for marker in markers) + "\n"


def fixture_text(rel_path: str) -> str:
    if rel_path == MAKEFILE_PATH:
        return "\n".join(MAKEFILE_FALLBACK_MARKERS) + "\n"
    if rel_path == RELEASE_SEQUENCING_PATH:
        return marker_fixture("# Phase 12 Release Sequencing", RELEASE_SEQUENCING_MARKERS)
    if rel_path == RELEASE_READINESS_PATH:
        return marker_fixture("# Phase 12 Release Readiness Survey", RELEASE_READINESS_MARKERS)
    raise ValueError(rel_path)


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, fixture_text(rel_path))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def remove_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(f"- {marker}\n", "", 1)
    if updated == text:
        updated = text.replace(f"{marker}\n", "", 1)
    if updated == text:
        updated = text.replace(marker, "", 1)
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-validate-route-return-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path in REQUIRED_FILES:
            write_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        marker_cases = [
            (rel_path, marker)
            for rel_path, markers in REQUIRED_MARKERS.items()
            for marker in markers
        ]
        for rel_path, marker in marker_cases:
            write_fixture_tree(base)
            remove_marker(base / rel_path, marker)
            expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        forbidden_cases = [
            (rel_path, marker)
            for rel_path, markers in FORBIDDEN_MARKERS.items()
            for marker in markers
        ]
        for rel_path, marker in forbidden_cases:
            write_fixture_tree(base)
            write_text(
                base / rel_path,
                (base / rel_path).read_text(encoding="utf-8") + f"{marker}\n",
            )
            expect_failure(base, f"forbidden_marker:{rel_path}:{marker}")

        case_count = len(REQUIRED_FILES) + len(marker_cases) + len(forbidden_cases)
        print("PHASE12_VALIDATE_ROUTE_RETURN_SELF_TEST=pass")
        print(f"PHASE12_VALIDATE_ROUTE_RETURN_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate that the current Phase 12 shared fallback packet still treats "
            "the repo-local `.zig-toolchain` as the first degraded rerun path and "
            "the returned `phase12-validate` wrapper as shipped current-master evidence."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the inferred repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(f"PHASE12_VALIDATE_ROUTE_RETURN=fail:{failure}")
        return 1

    print("PHASE12_VALIDATE_ROUTE_RETURN=pass")
    print(f"PHASE12_VALIDATE_ROUTE_RETURN_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
