#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
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
RELEASE_COORDINATION_PATH = "Documentation/zigux/phase12-release-coordination-matrix.md"
RELEASE_CLOSURE_PATH = "Documentation/zigux/phase12-release-closure-checklist.md"
LIBBPF_LANE_PATH = "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md"
RAW_FALLBACK_PATH = "Documentation/zigux/phase12-raw-github-coverage-survey.md"
BUILD_ONLY_CHECKER_PATH = "scripts/zigux/check-build-only-phase12-surface.py"
READINESS_CHECKER_PATH = "scripts/zigux/check-phase12-release-readiness-packet.py"
VALIDATE_PATH = "scripts/zigux/validate-phase12.py"

REQUIRED_FILES = [
    MAKEFILE_PATH,
    RELEASE_SEQUENCING_PATH,
    RELEASE_READINESS_PATH,
    RELEASE_COORDINATION_PATH,
    RELEASE_CLOSURE_PATH,
    LIBBPF_LANE_PATH,
    RAW_FALLBACK_PATH,
    BUILD_ONLY_CHECKER_PATH,
    READINESS_CHECKER_PATH,
    VALIDATE_PATH,
]

MAKEFILE_REQUIRED_MARKERS = [
    ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-validate phase2 phase3-validate phase3 phase3-export-uapi-layout-test phase6-base64-test phase6-base64-perf phase6-bsearch-test phase6-checksum-test phase6-checksum-perf phase6-hexdump-review phase6-hexdump-test phase6-hexdump-perf phase8-validate phase8-exec-cmd-test phase8-libbpf-segments-test phase8-file-path-handle-bridge-test phase8-perf-buffer-poll-test phase8-test phase8 phase10-validate phase10-test phase10 phase12-smoke phase12-test phase12",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-smoke phase12-test",
]

MAKEFILE_FORBIDDEN_MARKERS = [
    "phase12-validate:",
]

RELEASE_SEQUENCING_MARKERS = [
    "reminder-only wrapper vocabulary until it returns: `make -C zigux phase12-validate`",
    "shipped wrapper evidence on current `master`: `make -C zigux phase12-smoke`",
    "shipped wrapper evidence on current `master`: `make -C zigux phase12-test`",
    "shipped wrapper evidence on current `master`: `make -C zigux phase12`",
    "it now exposes shared `phase12-smoke`, `phase12-test`, and `phase12` wrappers again",
    "the directly readable rerun surfaces `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `scripts/zigux/validate-phase12.py`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`",
]

RELEASE_READINESS_MARKERS = [
    "current `zigux/Makefile` now exposes `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again even though `make -C zigux phase12-validate` is still absent.",
    "That means the PMO release notes can treat `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-`master` evidence again, while `make -C zigux phase12-validate` must stay reminder-only text until same-lane work rematerializes that wrapper.",
    "keep the intended shared-tree anchor pair `zigux/tests/phase12_build.zig` and `scripts/zigux/check-build-only-phase12-surface.py` explicit, treat `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-route proof again, and keep only `make -C zigux phase12-validate` framed as reminder-only text while `zigux/Makefile` still omits that wrapper on current `master`.",
]

RELEASE_COORDINATION_MARKERS = [
    "validator-first support bundle: `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and the reminder-only wrapper name `make -C zigux phase12-validate`",
    "`zigux/Makefile` remains directly readable repo evidence and now exposes `phase12-smoke`, `phase12-test`, and `phase12` on `master` while still omitting `phase12-validate`",
    "Current repo-reality override: `zigux/Makefile` now exposes `phase12-smoke`, `phase12-test`, and `phase12` on current `master`, while `phase12-validate` remains reminder-only vocabulary until same-lane work rematerializes that wrapper.",
]

RELEASE_CLOSURE_MARKERS = [
    "The directly readable validator-first support bundle still reruns as `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `python3 scripts/zigux/validate-phase12.py`; keep `make -C zigux phase12-validate` here only as reminder-only wrapper vocabulary until `zigux/Makefile` rematerializes that route on current `master`.",
    "The shared build-and-make replay path stays visible through `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`, while current `zigux/Makefile` now keeps `phase12-smoke`, `phase12-test`, and `phase12` explicit as shipped wrapper evidence and still omits `phase12-validate`.",
    "The shared smoke-first replay packet still stays wired through `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all` and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`; treat `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped wrapper evidence again, while `make -C zigux phase12-validate` stays reminder-only vocabulary until that wrapper returns.",
]

LIBBPF_LANE_MARKERS = [
    "Current repo-reality override: `zigux/Makefile` now rematerializes `phase12-smoke`, `phase12-test`, and `phase12` on current `master` while still omitting `phase12-validate`, so keep only `make -C zigux phase12-validate` here as reminder vocabulary and keep the directly readable support bundle explicit through `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `scripts/zigux/validate-phase12.py` beside the returned smoke-and-test wrappers.",
    "If `zig` is unavailable on `PATH`, keep that same validator-first then smoke-first order documented with the reminder-only `make -C zigux phase12-validate` vocabulary ahead of the shipped attached-toolchain reruns `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of inventing a focused libbpf-only fallback entrypoint.",
]

RAW_FALLBACK_MARKERS = [
    "the directly readable `zigux/Makefile` blob",
    "now exposes shared `phase12-smoke`, `phase12-test`, and `phase12` again while still omitting `phase12-validate`",
    "keep the current validator-first then smoke-first order explicit through the reminder-only `make -C zigux phase12-validate` vocabulary, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, the shipped wrapper evidence `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, the shipped wrapper evidence `make -C zigux phase12-test`, and the shipped wrapper evidence `make -C zigux phase12`",
    "keep the same reminder-only validator route plus shipped wrapper reruns explicit as `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>`",
]


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")

    if failures:
        return failures

    marker_groups = [
        ("release_sequencing", RELEASE_SEQUENCING_PATH, RELEASE_SEQUENCING_MARKERS),
        ("release_readiness", RELEASE_READINESS_PATH, RELEASE_READINESS_MARKERS),
        ("release_coordination", RELEASE_COORDINATION_PATH, RELEASE_COORDINATION_MARKERS),
        ("release_closure", RELEASE_CLOSURE_PATH, RELEASE_CLOSURE_MARKERS),
        ("libbpf_lane", LIBBPF_LANE_PATH, LIBBPF_LANE_MARKERS),
        ("raw_fallback", RAW_FALLBACK_PATH, RAW_FALLBACK_MARKERS),
    ]

    for label, rel_path, markers in marker_groups:
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                failures.append(f"{label}:{marker}")

    makefile_text = (root / MAKEFILE_PATH).read_text(encoding="utf-8")
    for marker in MAKEFILE_REQUIRED_MARKERS:
        if marker not in makefile_text:
            failures.append(f"makefile:{marker}")
    for forbidden in MAKEFILE_FORBIDDEN_MARKERS:
        if forbidden in makefile_text:
            failures.append(f"makefile_forbidden:{forbidden}")

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def minimal_join(title: str, markers: list[str]) -> str:
    return title + "\n\n" + "\n".join(f"- {marker}" for marker in markers) + "\n"


def fixture_makefile() -> str:
    return "\n".join(
        [
            "PYTHON ?= python3",
            "ZIG ?= zig",
            "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
            "PHASE3_SCRIPT_ROOT := ../scripts/zigux",
            "PHASE8_SCRIPT_ROOT := ../scripts/zigux",
            "ZIGUX_ROOT := ..",
            "",
            ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-validate phase2 phase3-validate phase3 phase3-export-uapi-layout-test phase6-base64-test phase6-base64-perf phase6-bsearch-test phase6-checksum-test phase6-checksum-perf phase6-hexdump-review phase6-hexdump-test phase6-hexdump-perf phase8-validate phase8-exec-cmd-test phase8-libbpf-segments-test phase8-file-path-handle-bridge-test phase8-perf-buffer-poll-test phase8-test phase8 phase10-validate phase10-test phase10 phase12-smoke phase12-test phase12",
            "",
            "phase12-smoke:",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) build smoke --build-file zigux/tests/phase12_build.zig --summary all",
            "",
            "phase12-test:",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all",
            "",
            "phase12: phase12-smoke phase12-test",
            "",
        ]
    )


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)

    write_text(root / MAKEFILE_PATH, fixture_makefile())
    write_text(
        root / RELEASE_SEQUENCING_PATH,
        minimal_join("# Phase 12 Release Sequencing", RELEASE_SEQUENCING_MARKERS),
    )
    write_text(
        root / RELEASE_READINESS_PATH,
        minimal_join("# Phase 12 Release Readiness Survey", RELEASE_READINESS_MARKERS),
    )
    write_text(
        root / RELEASE_COORDINATION_PATH,
        minimal_join("# Phase 12 Release Coordination Matrix", RELEASE_COORDINATION_MARKERS),
    )
    write_text(
        root / RELEASE_CLOSURE_PATH,
        minimal_join("# Phase 12 Release Closure Checklist", RELEASE_CLOSURE_MARKERS),
    )
    write_text(
        root / LIBBPF_LANE_PATH,
        minimal_join(
            "# Phase 12 Libbpf Heavy-Consumer Lane Sequencing",
            LIBBPF_LANE_MARKERS,
        ),
    )
    write_text(
        root / RAW_FALLBACK_PATH,
        minimal_join("# Phase 12 Raw GitHub Coverage Survey", RAW_FALLBACK_MARKERS),
    )
    write_text(root / BUILD_ONLY_CHECKER_PATH, "# placeholder\n")
    write_text(root / READINESS_CHECKER_PATH, "# placeholder\n")
    write_text(root / VALIDATE_PATH, "# placeholder\n")


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def remove_marker_line(path: Path, marker: str) -> None:
    path.write_text(
        path.read_text(encoding="utf-8").replace(f"- {marker}\n", "", 1),
        encoding="utf-8",
    )


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-release-route-split-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        write_fixture_tree(base)
        makefile_path = base / MAKEFILE_PATH
        makefile_path.write_text(
            makefile_path.read_text(encoding="utf-8").replace("phase12-test:\n", "", 1),
            encoding="utf-8",
        )
        expect_failure(base, "makefile:phase12-test:")

        write_fixture_tree(base)
        makefile_path = base / MAKEFILE_PATH
        makefile_path.write_text(
            makefile_path.read_text(encoding="utf-8") + "phase12-validate:\n",
            encoding="utf-8",
        )
        expect_failure(base, "makefile_forbidden:phase12-validate:")

        write_fixture_tree(base)
        sequencing_path = base / RELEASE_SEQUENCING_PATH
        remove_marker_line(sequencing_path, RELEASE_SEQUENCING_MARKERS[2])
        expect_failure(base, f"release_sequencing:{RELEASE_SEQUENCING_MARKERS[2]}")

        write_fixture_tree(base)
        readiness_path = base / RELEASE_READINESS_PATH
        remove_marker_line(readiness_path, RELEASE_READINESS_MARKERS[0])
        expect_failure(base, f"release_readiness:{RELEASE_READINESS_MARKERS[0]}")

        write_fixture_tree(base)
        coordination_path = base / RELEASE_COORDINATION_PATH
        remove_marker_line(coordination_path, RELEASE_COORDINATION_MARKERS[2])
        expect_failure(base, f"release_coordination:{RELEASE_COORDINATION_MARKERS[2]}")

        write_fixture_tree(base)
        closure_path = base / RELEASE_CLOSURE_PATH
        remove_marker_line(closure_path, RELEASE_CLOSURE_MARKERS[1])
        expect_failure(base, f"release_closure:{RELEASE_CLOSURE_MARKERS[1]}")

        write_fixture_tree(base)
        libbpf_lane_path = base / LIBBPF_LANE_PATH
        remove_marker_line(libbpf_lane_path, LIBBPF_LANE_MARKERS[0])
        expect_failure(base, f"libbpf_lane:{LIBBPF_LANE_MARKERS[0]}")

        write_fixture_tree(base)
        raw_fallback_path = base / RAW_FALLBACK_PATH
        remove_marker_line(raw_fallback_path, RAW_FALLBACK_MARKERS[2])
        expect_failure(base, f"raw_fallback:{RAW_FALLBACK_MARKERS[2]}")

        write_fixture_tree(base)
        (base / VALIDATE_PATH).unlink()
        expect_failure(base, f"missing_file:{VALIDATE_PATH}")

        print("PHASE12_RELEASE_ROUTE_SPLIT_SELF_TEST=pass")
        print("PHASE12_RELEASE_ROUTE_SPLIT_SELF_TEST_CASE_COUNT=9")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate that the current Phase 12 PMO release packet keeps the returned "
            "phase12 smoke/test routes explicit while leaving phase12-validate as "
            "reminder-only vocabulary until that wrapper returns."
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
            print(f"PHASE12_RELEASE_ROUTE_SPLIT=fail:{failure}", file=sys.stderr)
        return 1

    print("PHASE12_RELEASE_ROUTE_SPLIT=pass")
    print(f"PHASE12_RELEASE_ROUTE_SPLIT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE12_RELEASE_ROUTE_SPLIT_REQUIRED_DOC_MARKER_COUNT="
        f"{len(RELEASE_SEQUENCING_MARKERS) + len(RELEASE_READINESS_MARKERS) + len(RELEASE_COORDINATION_MARKERS) + len(RELEASE_CLOSURE_MARKERS) + len(LIBBPF_LANE_MARKERS) + len(RAW_FALLBACK_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
