#!/usr/bin/env python3
"""Fail closed when the shared Phase 10 reminder packet drifts."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

REQUIRED_FILES = (
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase10_closure_manifest.json",
)

REQUIRED_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": (
        "Self-test current Phase 10 bootstrap route checker",
        "Check current Phase 10 bootstrap route",
        "Validate Phase 10 checker-backed review packet",
        "make -C zigux phase10-validate",
        "Run Phase 10 helper tests",
        "make -C zigux phase10-test",
    ),
    "Documentation/zigux/phase10-closure-evidence.md": (
        "`PHASE10_STATUS=active`",
        "`PHASE10_RISKY_TRANSPORT_POSTURE=blocked_on_risky_transport`",
        "scripts/zigux/check-phase10-harness-coverage.py",
        "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
        "scripts/zigux/check-phase10-closure-manifest-counts.py",
        "zigux/tests/phase10_closure_manifest.json",
        "scripts/zigux/validate-phase10.py",
        "scripts/zigux/validate-phase10-closure.py",
        "make -C zigux phase10-validate",
        "make -C zigux phase10-test",
        "phase10-virtio-input-registration-lifecycle",
        "phase10-mmio-lifecycle-and-irq-paths",
    ),
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": (
        "scripts/zigux/check-phase10-harness-coverage.py",
        "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
        "scripts/zigux/check-phase10-closure-manifest-counts.py",
        "scripts/zigux/validate-phase10.py",
        "scripts/zigux/validate-phase10-closure.py",
        "make -C zigux phase10-validate",
        "make -C zigux phase10-test",
        "make -C zigux phase10",
        "phase10-virtio-input-registration-lifecycle",
        "phase10-mmio-lifecycle-and-irq-paths",
        "P10-L22",
        "P10-L11",
    ),
    "Documentation/zigux/review-checklist.md": (
        "scripts/zigux/check-phase10-harness-coverage.py",
        "Documentation/zigux/phase10-closure-evidence.md",
        "zigux/tests/phase10_closure_manifest.json",
        "make -C zigux phase10-test",
        "make -C zigux phase10",
    ),
    "zigux/Makefile": (
        "phase10-validate:",
        "scripts/zigux/check-phase10-bootstrap-route.py",
        "scripts/zigux/check-phase10-shared-freeze-boundary.py",
        "scripts/zigux/check-phase10-ring-packet.py",
        "scripts/zigux/check-phase10-input-packet.py",
        "scripts/zigux/check-phase10-mmio-packet.py",
        "scripts/zigux/check-phase10-harness-coverage.py",
        "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
        "scripts/zigux/check-phase10-closure-manifest-counts.py",
        "scripts/zigux/validate-phase10.py",
        "scripts/zigux/validate-phase10-closure.py",
        "phase10-test:",
        "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
        "phase10: phase10-validate phase10-test",
    ),
    "zigux/tests/README.md": (
        "Documentation/zigux/phase10-closure-evidence.md",
        "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
        "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
        "scripts/zigux/check-phase10-harness-coverage.py",
        "scripts/zigux/validate-phase10-closure.py",
        "zigux/tests/phase10_closure_manifest.json",
        "zigux/tests/phase10_build.zig",
        "make -C zigux phase10-validate",
        "make -C zigux phase10-test",
        "make -C zigux phase10",
        "phase10_virtio_input_queue_callback_preflight.zig",
        "phase10_virtio_input_registration_preflight.zig",
        "phase10_virtio_input_status_drain.zig",
        "phase10_virtio_input_teardown_observation.zig",
        "phase10_virtio_mmio_apply_observation_replay.zig",
        "build.phase10_virtio_mmio_apply_observation_replay.zig",
    ),
    "zigux/tests/phase10_closure_manifest.json": (
        '"phase": "Phase 10"',
        '"status": "active"',
        '"tranche": "virtio-lab-bundle"',
        '"risky_transport_posture": "blocked_on_risky_transport"',
        '"core": "P10-L01"',
        '"ring": "P10-L10"',
        '"input": "P10-L22"',
        '"mmio": "P10-L11"',
        '"zigux/tests/phase10_virtio_input_manifest.json": "phase10-virtio-input-registration-lifecycle"',
        '"zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-lifecycle-and-irq-paths"',
        '"scripts/zigux/check-phase10-harness-coverage.py"',
        '"scripts/zigux/check-phase10-tests-readme-core-surfaces.py"',
        '"scripts/zigux/check-phase10-closure-manifest-counts.py"',
    ),
}


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(f"missing_required_file:{rel}")

    for rel, markers in REQUIRED_MARKERS.items():
        path = root / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                issues.append(f"missing_marker:{rel}:{marker}")

    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        print("PHASE10_SHARED_REMINDER_PACKET=fail")
        print("PHASE10_SHARED_REMINDER_PACKET_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE10_SHARED_REMINDER_PACKET_ISSUES_END")
        return 1

    print("PHASE10_SHARED_REMINDER_PACKET=pass")
    print(f"PHASE10_SHARED_REMINDER_PACKET_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE10_SHARED_REMINDER_PACKET_BLOCKED_FOLLOWUPS="
        "phase10-virtio-input-registration-lifecycle,"
        "phase10-mmio-lifecycle-and-irq-paths"
    )
    return 0


def build_fixture(root: Path) -> None:
    for rel, markers in REQUIRED_MARKERS.items():
        write_text(root / rel, "\n".join(markers) + "\n")


def expect_issue(issues: list[str], expected: str, label: str) -> None:
    if expected not in issues:
        joined = ",".join(issues) if issues else "none"
        raise SystemExit(f"{label}:expected={expected}:actual={joined}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase10_shared_reminder_") as tmp_dir:
        root = Path(tmp_dir)
        build_fixture(root)
        baseline = collect_issues(root)
        if baseline:
            raise SystemExit("phase10-shared-reminder-self-test:baseline_failed:" + ",".join(baseline))

        cases = 1

        missing_workflow = root / ".github/workflows/zigux-bootstrap.yml"
        missing_workflow.unlink()
        expect_issue(
            collect_issues(root),
            "missing_required_file:.github/workflows/zigux-bootstrap.yml",
            "phase10-shared-reminder-self-test",
        )
        cases += 1
        build_fixture(root)

        closure_note = root / "Documentation/zigux/phase10-closure-evidence.md"
        closure_note.write_text(
            closure_note.read_text(encoding="utf-8").replace(
                "phase10-mmio-lifecycle-and-irq-paths",
                "phase10-mmio-lifecycle-blocked",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(root),
            "missing_marker:Documentation/zigux/phase10-closure-evidence.md:phase10-mmio-lifecycle-and-irq-paths",
            "phase10-shared-reminder-self-test",
        )
        cases += 1
        build_fixture(root)

        lane_note = root / "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md"
        lane_note.write_text(
            lane_note.read_text(encoding="utf-8").replace("P10-L22", "P10-L21", 1),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(root),
            "missing_marker:Documentation/zigux/phase10-virtio-driver-lane-sequencing.md:P10-L22",
            "phase10-shared-reminder-self-test",
        )
        cases += 1
        build_fixture(root)

        review = root / "Documentation/zigux/review-checklist.md"
        review.write_text(
            review.read_text(encoding="utf-8").replace("make -C zigux phase10-test", "make -C zigux phase10-smoke", 1),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(root),
            "missing_marker:Documentation/zigux/review-checklist.md:make -C zigux phase10-test",
            "phase10-shared-reminder-self-test",
        )
        cases += 1
        build_fixture(root)

        makefile = root / "zigux/Makefile"
        makefile.write_text(
            makefile.read_text(encoding="utf-8").replace(
                "scripts/zigux/check-phase10-harness-coverage.py",
                "scripts/zigux/check-phase10-missing.py",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(root),
            "missing_marker:zigux/Makefile:scripts/zigux/check-phase10-harness-coverage.py",
            "phase10-shared-reminder-self-test",
        )
        cases += 1
        build_fixture(root)

        tests_readme = root / "zigux/tests/README.md"
        tests_readme.write_text(
            tests_readme.read_text(encoding="utf-8").replace(
                "phase10_virtio_mmio_apply_observation_replay.zig",
                "phase10_virtio_mmio_missing_apply_replay.zig",
                2,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(root),
            "missing_marker:zigux/tests/README.md:phase10_virtio_mmio_apply_observation_replay.zig",
            "phase10-shared-reminder-self-test",
        )
        cases += 1
        build_fixture(root)

        manifest = root / "zigux/tests/phase10_closure_manifest.json"
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace(
                '"zigux/tests/phase10_virtio_input_manifest.json": "phase10-virtio-input-registration-lifecycle"',
                '"zigux/tests/phase10_virtio_input_manifest.json": "phase10-input-lifecycle-missing"',
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(root),
            'missing_marker:zigux/tests/phase10_closure_manifest.json:"zigux/tests/phase10_virtio_input_manifest.json": "phase10-virtio-input-registration-lifecycle"',
            "phase10-shared-reminder-self-test",
        )
        cases += 1

    print("PHASE10_SHARED_REMINDER_PACKET_SELF_TEST=pass")
    print(f"PHASE10_SHARED_REMINDER_PACKET_SELF_TEST_CASES={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the shared Phase 10 reminder packet matches current repo reality."
    )
    parser.add_argument("--root", help="Repository root to inspect.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = Path(args.root).resolve() if args.root else ROOT.resolve()
    return run_check(root)


if __name__ == "__main__":
    raise SystemExit(main())
