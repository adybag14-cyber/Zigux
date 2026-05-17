#!/usr/bin/env python3
"""Fail closed when the current shared Phase 10 harness packet drifts."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = (
    Path(__file__).resolve().parents[2]
    if len(Path(__file__).resolve().parents) > 2
    else Path(__file__).resolve().parent
)

FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "drivers/virtio/virtio_input_registration_preflight.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "drivers/virtio/virtio_mmio.zig",
    "zigux/tests/phase10_build.zig",
]

DOCS_ROOT_MARKERS = [
    "scripts/zigux/check-phase10-harness-coverage.py",
    "zigux/tests/phase10_build.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "drivers/virtio/virtio_mmio.zig",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
]

REVIEW_CHECKLIST_MARKERS = [
    "scripts/zigux/check-phase10-harness-coverage.py",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_closure_manifest.json",
    "make -C zigux phase10-validate",
]

COMPANION_MARKERS = [
    "scripts/zigux/check-phase10-harness-coverage.py",
    "zigux/tests/phase10_build.zig",
    "drivers/virtio/virtio_input_registration_preflight.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "drivers/virtio/virtio_mmio.zig",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
]

BUILD_MARKERS = [
    "virtio_input_verify_module",
    "virtio_mmio_module",
    "phase10_virtio_input_module",
    "phase10_virtio_input_probe_preflight_module",
    "phase10_virtio_input_queue_callback_preflight_module",
    "phase10_virtio_input_registration_preflight_module",
    "phase10_virtio_input_status_drain_module",
    "phase10_virtio_input_teardown_observation_module",
    '"phase10-virtio-input-tests"',
    '"phase10-virtio-input-probe-preflight-tests"',
    '"phase10-virtio-input-queue-callback-preflight-tests"',
    '"phase10-virtio-input-registration-preflight-tests"',
    '"phase10-virtio-input-status-drain-tests"',
    '"phase10-virtio-input-teardown-observation-tests"',
    '"phase10-virtio-input-verify-tests"',
    '"phase10-virtio-mmio-tests"',
    'Run the live Phase 10 virtio input, verify, and MMIO lab validation tests',
]

REGISTRATION_HELPER_MARKERS = [
    "pub const RegistrationPreflightSummary = virtio_input.RegistrationPreflightSummary;",
    "pub const RegistrationBlocker = virtio_input.RegistrationBlocker;",
    "pub fn summarize(device: *const virtio_input.VirtioInputLab) RegistrationPreflightSummary {",
    "pub fn blockerTag(blocker: RegistrationBlocker) []const u8 {",
]

VERIFY_MARKERS = [
    'test "phase10 virtio input verify keeps wrapper-facing queue preflight ordering explicit" {',
    'test "phase10 virtio input verify keeps wrapper prerequisites ahead of registration claims" {',
]

MMIO_MARKERS = [
    'test "phase10 virtio mmio config-generation bumps clear stale planned config writes" {',
    'test "phase10 virtio mmio restaging config bytes clears stale planned config writes" {',
    'test "phase10 virtio mmio legacy probe preflight requires guest-page-size programming" {',
    'test "phase10 virtio mmio disposition reports byte-level deltas without mutating config bytes" {',
]

EXPECTED_COUNTS = {
    "Documentation/zigux/README.md::scripts/zigux/check-phase10-harness-coverage.py": 1,
    "Documentation/zigux/review-checklist.md::scripts/zigux/check-phase10-harness-coverage.py": 1,
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md::scripts/zigux/check-phase10-harness-coverage.py": 1,
    "zigux/tests/phase10_build.zig::virtio_input_verify_module": 1,
    "zigux/tests/phase10_build.zig::virtio_mmio_module": 1,
    'zigux/tests/phase10_build.zig::"phase10-virtio-input-verify-tests"': 1,
    'zigux/tests/phase10_build.zig::"phase10-virtio-mmio-tests"': 1,
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def check_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def check_counts(missing: list[str], rel_path: str, text: str) -> None:
    prefix = f"{rel_path}::"
    for key, expected in EXPECTED_COUNTS.items():
        if not key.startswith(prefix):
            continue
        marker = key[len(prefix) :]
        actual = text.count(marker)
        if actual != expected:
            missing.append(f"{rel_path}:count:{marker}:{actual}!={expected}")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []

    docs_root = read_text(root, "Documentation/zigux/README.md")
    review_checklist = read_text(root, "Documentation/zigux/review-checklist.md")
    companion = read_text(
        root, "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"
    )
    build = read_text(root, "zigux/tests/phase10_build.zig")
    registration_helper = read_text(root, "drivers/virtio/virtio_input_registration_preflight.zig")
    verify = read_text(root, "drivers/virtio/virtio_input_verify.zig")
    mmio = read_text(root, "drivers/virtio/virtio_mmio.zig")

    check_markers(missing_markers, "docs_root", docs_root, DOCS_ROOT_MARKERS)
    check_markers(
        missing_markers,
        "review_checklist",
        review_checklist,
        REVIEW_CHECKLIST_MARKERS,
    )
    check_markers(missing_markers, "tests_root_companion", companion, COMPANION_MARKERS)
    check_markers(missing_markers, "phase10_build", build, BUILD_MARKERS)
    check_markers(
        missing_markers,
        "virtio_input_registration_preflight",
        registration_helper,
        REGISTRATION_HELPER_MARKERS,
    )
    check_markers(missing_markers, "virtio_input_verify", verify, VERIFY_MARKERS)
    check_markers(missing_markers, "virtio_mmio", mmio, MMIO_MARKERS)

    check_counts(missing_markers, "Documentation/zigux/README.md", docs_root)
    check_counts(
        missing_markers, "Documentation/zigux/review-checklist.md", review_checklist
    )
    check_counts(
        missing_markers,
        "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
        companion,
    )
    check_counts(missing_markers, "zigux/tests/phase10_build.zig", build)

    return [], missing_markers


def write_fixture(root: Path) -> None:
    fixture_contents = {
        "Documentation/zigux/README.md": "\n".join(DOCS_ROOT_MARKERS) + "\n",
        "Documentation/zigux/review-checklist.md": "\n".join(REVIEW_CHECKLIST_MARKERS)
        + "\n",
        "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": "\n".join(
            COMPANION_MARKERS
        )
        + "\n",
        "zigux/tests/phase10_build.zig": "\n".join(BUILD_MARKERS) + "\n",
        "drivers/virtio/virtio_input_registration_preflight.zig": "\n".join(
            REGISTRATION_HELPER_MARKERS
        )
        + "\n",
        "drivers/virtio/virtio_input_verify.zig": "\n".join(VERIFY_MARKERS) + "\n",
        "drivers/virtio/virtio_mmio.zig": "\n".join(MMIO_MARKERS) + "\n",
    }

    for rel_path, content in fixture_contents.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def expect_missing_marker(root: Path, expected: str, label: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(f"{label}:unexpected_missing_files:{','.join(missing_files)}")
    if expected not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def expect_missing_file(root: Path, expected: str, label: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_markers:
        raise SystemExit(f"{label}:unexpected_missing_markers:{','.join(missing_markers)}")
    if expected not in missing_files:
        actual = ",".join(missing_files) if missing_files else "none"
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_harness_coverage_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-harness-coverage-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        case_count = 0

        docs_root_path = root / "Documentation/zigux/README.md"
        original_docs_root = docs_root_path.read_text(encoding="utf-8")
        docs_root_path.writeText(
            original_docs_root.replace(
                "scripts/zigux/check-phase10-harness-coverage.py",
                "scripts/zigux/check-phase10-harness-coverage-missing.py",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            "docs_root:scripts/zigux/check-phase10-harness-coverage.py",
            "phase10-harness-coverage-self-test:docs_root_checker_path",
        )
        docs_root_path.write_text(original_docs_root, encoding="utf-8")
        case_count += 1

        review_path = root / "Documentation/zigux/review-checklist.md"
        original_review = review_path.read_text(encoding="utf-8")
        review_path.write_text(
            original_review.replace(
                "zigux/tests/phase10_closure_manifest.json",
                "zigux/tests/phase10_closure_manifest_missing.json",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            "review_checklist:zigux/tests/phase10_closure_manifest.json",
            "phase10-harness-coverage-self-test:review_manifest",
        )
        review_path.write_text(original_review, encoding="utf-8")
        case_count += 1

        companion_path = (
            root / "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"
        )
        original_companion = companion_path.read_text(encoding="utf-8")
        companion_path.write_text(
            original_companion.replace(
                "drivers/virtio/virtio_input_registration_preflight.zig",
                "drivers/virtio/virtio_input_registration_preflight_missing.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            "tests_root_companion:drivers/virtio/virtio_input_registration_preflight.zig",
            "phase10-harness-coverage-self-test:companion_registration_helper_path",
        )
        companion_path.write_text(original_companion, encoding="utf-8")
        case_count += 1

        build_path = root / "zigux/tests/phase10_build.zig"
        original_build = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            original_build.replace(
                '"phase10-virtio-mmio-tests"',
                '"phase10-virtio-mmio-drift"',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            'phase10_build:"phase10-virtio-mmio-tests"',
            "phase10-harness-coverage-self-test:build_mmio_test_name",
        )
        build_path.write_text(original_build, encoding="utf-8")
        case_count += 1

        registration_helper_path = root / "drivers/virtio/virtio_input_registration_preflight.zig"
        original_registration_helper = registration_helper_path.read_text(encoding="utf-8")
        registration_helper_path.write_text(
            original_registration_helper.replace(
                "pub const RegistrationBlocker = virtio_input.RegistrationBlocker;",
                "pub const RegistrationGate = virtio_input.RegistrationBlocker;",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            "virtio_input_registration_preflight:pub const RegistrationBlocker = virtio_input.RegistrationBlocker;",
            "phase10-harness-coverage-self-test:registration_helper_blocker_alias",
        )
        registration_helper_path.write_text(original_registration_helper, encoding="utf-8")
        case_count += 1

        verify_path = root / "drivers/virtio/virtio_input_verify.zig"
        original_verify = verify_path.read_text(encoding="utf-8")
        verify_path.write_text(
            original_verify.replace(
                'test "phase10 virtio input verify keeps wrapper prerequisites ahead of registration claims" {',
                'test "phase10 virtio input verify drift" {',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            'virtio_input_verify:test "phase10 virtio input verify keeps wrapper prerequisites ahead of registration claims" {',
            "phase10-harness-coverage-self-test:verify_helper_test_title",
        )
        verify_path.write_text(original_verify, encoding="utf-8")
        case_count += 1

        mmio_path = root / "drivers/virtio/virtio_mmio.zig"
        original_mmio = mmio_path.read_text(encoding="utf-8")
        mmio_path.write_text(
            original_mmio.replace(
                'test "phase10 virtio mmio legacy probe preflight requires guest-page-size programming" {',
                'test "phase10 virtio mmio drift" {',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            'virtio_mmio:test "phase10 virtio mmio legacy probe preflight requires guest-page-size programming" {',
            "phase10-harness-coverage-self-test:mmio_probe_test_title",
        )
        mmio_path.write_text(original_mmio, encoding="utf-8")
        case_count += 1

        docs_root_path.write_text(
            original_docs_root
            + "scripts/zigux/check-phase10-harness-coverage.py\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            "Documentation/zigux/README.md:count:scripts/zigux/check-phase10-harness-coverage.py:2!=1",
            "phase10-harness-coverage-self-test:docs_root_duplicate_checker_path",
        )
        docs_root_path.write_text(original_docs_root, encoding="utf-8")
        case_count += 1

        (root / "drivers/virtio/virtio_mmio.zig").unlink()
        expect_missing_file(
            root,
            "drivers/virtio/virtio_mmio.zig",
            "phase10-harness-coverage-self-test:missing_mmio_helper",
        )
        case_count += 1

    print("PHASE10_HARNESS_COVERAGE_SELF_TEST=pass")
    print(f"PHASE10_HARNESS_COVERAGE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 10 harness-coverage reminder packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the checker's built-in synthetic drift tests",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE10_HARNESS_COVERAGE=fail")
        print("MISSING_PHASE10_HARNESS_COVERAGE_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_HARNESS_COVERAGE_FILES_END")
        return 1

    if missing_markers:
        print("PHASE10_HARNESS_COVERAGE=fail")
        print("MISSING_PHASE10_HARNESS_COVERAGE_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_HARNESS_COVERAGE_MARKERS_END")
        return 1

    print("PHASE10_HARNESS_COVERAGE=pass")
    print(f"PHASE10_HARNESS_COVERAGE_REQUIRED_FILE_COUNT={len(FILES)}")
    print(
        "PHASE10_HARNESS_COVERAGE_REQUIRED_MARKER_COUNT="
        f"{len(DOCS_ROOT_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(COMPANION_MARKERS) + len(BUILD_MARKERS) + len(REGISTRATION_HELPER_MARKERS) + len(VERIFY_MARKERS) + len(MMIO_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
