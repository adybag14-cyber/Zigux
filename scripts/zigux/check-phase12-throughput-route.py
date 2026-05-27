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
            candidate / "zigux/tests/phase12_build.zig"
        ).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

MAKEFILE_PATH = "zigux/Makefile"
BUILD_PATH = "zigux/tests/phase12_build.zig"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_FILES = [MAKEFILE_PATH, BUILD_PATH, WORKFLOW_PATH]

REQUIRED_MARKERS = {
    MAKEFILE_PATH: [
        "phase12-virtio-net-throughput-parity-test:",
        "cd $(ZIGUX_ROOT) && $(ZIG) build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all",
    ],
    BUILD_PATH: [
        '"phase12_virtio_net_throughput_parity.zig"',
        '"phase12-virtio-net-throughput-parity-tests"',
        '"phase12-virtio-net-throughput-parity"',
        "smoke_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
        "test_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
        "throughput_parity_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
        "throughput-parity, and survey-gate smoke tests",
        "throughput-parity, and survey-gate tests",
        "throughput-parity replay in isolation",
    ],
    WORKFLOW_PATH: [
        "- name: Run current Phase 12 throughput-parity anchor",
        "run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig",
        "- name: Run current Phase 12 aggregate route",
        "run: make -C zigux phase12",
    ],
}

FORBIDDEN_MARKERS = {
    BUILD_PATH: [
        '"phase12_virtio_net.zig"',
        '"phase12_virtio_net_syntax_lab.zig"',
        '"phase12-virtio-net-tests"',
        '"phase12-virtio-net-syntax-lab-tests"',
    ],
}


def normalize_exact_line(text: str) -> str:
    normalized = text.lstrip()
    if normalized.startswith("- "):
        return normalized[2:]
    return normalized


def has_marker(rel_path: str, text: str, marker: str) -> bool:
    if rel_path == WORKFLOW_PATH:
        normalized_marker = normalize_exact_line(marker)
        return normalized_marker in [
            normalize_exact_line(line) for line in text.splitlines()
        ]
    return marker in text


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
            if not has_marker(rel_path, text, marker):
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


def make_fixture_root(root: Path) -> None:
    write_text(
        root / MAKEFILE_PATH,
        "\n".join(
            [
                "phase12-virtio-net-throughput-parity-test:",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all",
                "",
            ]
        ),
    )
    write_text(
        root / BUILD_PATH,
        "\n".join(
            [
                'const virtio_net_throughput_parity_root_module = b.createModule(.{ .root_source_file = b.path("phase12_virtio_net_throughput_parity.zig"), });',
                'const phase12_virtio_net_throughput_parity_tests = b.addTest(.{ .name = "phase12-virtio-net-throughput-parity-tests", .root_module = virtio_net_throughput_parity_root_module, });',
                'const smoke_step = b.step("smoke", "Run the Phase 12 virtio_net queue-resume, transmit-recycle, receive-refill replay, post-reset replay, throughput-parity, and survey-gate smoke tests");',
                "smoke_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
                'const test_step = b.step("test", "Run the Phase 12 virtio_net queue-resume, transmit-recycle, receive-refill replay, post-reset replay, throughput-parity, and survey-gate tests");',
                "test_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
                'const throughput_parity_step = b.step("phase12-virtio-net-throughput-parity", "Run the Phase 12 virtio_net throughput-parity replay in isolation");',
                "throughput_parity_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
                "",
            ]
        ),
    )
    write_text(
        root / WORKFLOW_PATH,
        "\n".join(
            [
                "- name: Run current Phase 12 aggregate route",
                "  run: make -C zigux phase12",
                "- name: Run current Phase 12 throughput-parity anchor",
                "  run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig",
                "",
            ]
        ),
    )


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-throughput-route-"))
    try:
        make_fixture_root(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture root should pass but failed: {failures!r}")

        for rel_path in REQUIRED_FILES:
            make_fixture_root(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        marker_cases = [
            (rel_path, marker)
            for rel_path, markers in REQUIRED_MARKERS.items()
            for marker in markers
        ]
        for rel_path, marker in marker_cases:
            make_fixture_root(base)
            target = base / rel_path
            text = target.read_text(encoding="utf-8")
            updated = text.replace(marker, "", 1)
            if updated == text:
                raise SystemExit(f"marker not removable: {marker}")
            target.write_text(updated, encoding="utf-8")
            expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        forbidden_cases = [
            (rel_path, marker)
            for rel_path, markers in FORBIDDEN_MARKERS.items()
            for marker in markers
        ]
        for rel_path, marker in forbidden_cases:
            make_fixture_root(base)
            target = base / rel_path
            target.write_text(target.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            expect_failure(base, f"forbidden_marker:{rel_path}:{marker}")

        print("PHASE12_THROUGHPUT_ROUTE_SELF_TEST=pass")
        print(
            "PHASE12_THROUGHPUT_ROUTE_SELF_TEST_CASE_COUNT="
            f"{1 + len(REQUIRED_FILES) + len(marker_cases) + len(forbidden_cases)}"
        )
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate that the bounded Phase 12 virtio_net throughput-parity route "
            "stays readable in the shared build file, the dedicated make route, "
            "and the bootstrap workflow."
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
            print(f"PHASE12_THROUGHPUT_ROUTE=fail:{failure}")
        return 1

    print("PHASE12_THROUGHPUT_ROUTE=pass")
    print(f"PHASE12_THROUGHPUT_ROUTE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
