#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "zigux/tests/fixtures/phase12_cross_targets.json"
CROSS_BUILD = ROOT / "zigux/tests/phase12_cross_build.zig"

EXPECTED_TARGETS = [
    "x86_64-linux-musl",
    "aarch64-linux-musl",
    "riscv64-linux-musl",
]

REQUIRED_FILES = [
    "zigux/tests/phase12_cross_build.zig",
    "zigux/tests/fixtures/phase12_cross_targets.json",
    "drivers/net/virtio_net_transmit_recycle.zig",
    "drivers/net/virtio_net_queue_resume.zig",
    "drivers/scsi/virtio_scsi.zig",
    "zigux/tests/phase12_virtio_net_transmit_recycle.zig",
    "zigux/tests/phase12_virtio_net_queue_resume.zig",
    "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig",
]

REQUIRED_BUILD_MARKERS = [
    "../../drivers/net/virtio_net_transmit_recycle.zig",
    "../../drivers/net/virtio_net_queue_resume.zig",
    '"phase12_virtio_net_transmit_recycle.zig"',
    '"phase12_virtio_net_queue_resume.zig"',
    '"phase12_virtio_scsi_repeated_rollback_gate.zig"',
    '.name = "phase12-cross-virtio-net-transmit-recycle-tests"',
    '.name = "phase12-cross-virtio-net-queue-resume-tests"',
    '.name = "phase12-cross-virtio-scsi-repeated-rollback-gate-tests"',
    "cross_step.dependOn(&phase12_virtio_net_transmit_recycle_tests.step);",
    "cross_step.dependOn(&phase12_virtio_net_queue_resume_tests.step);",
    "cross_step.dependOn(&phase12_virtio_scsi_repeated_rollback_tests.step);",
]

EXPECTED_SELF_TEST_CASE_COUNT = 21


def load_fixture(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("fixture must be a JSON object")
    return payload


def require_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def validate_fixture(payload: dict[str, object]) -> list[str]:
    issues: list[str] = []
    if payload.get("phase") != "Phase 12":
        issues.append(f"fixture:phase:{payload.get('phase')!r}")
    if payload.get("lane_key") != "P12-L02":
        issues.append(f"fixture:lane_key:{payload.get('lane_key')!r}")
    if payload.get("build_file") != "zigux/tests/phase12_cross_build.zig":
        issues.append(f"fixture:build_file:{payload.get('build_file')!r}")
    if payload.get("build_step") != "cross":
        issues.append(f"fixture:build_step:{payload.get('build_step')!r}")
    if payload.get("target_count") != len(EXPECTED_TARGETS):
        issues.append(f"fixture:target_count:{payload.get('target_count')!r}")
    if payload.get("targets") != EXPECTED_TARGETS:
        issues.append(f"fixture:targets:{payload.get('targets')!r}")
    return issues


def validate_cross_build(text: str) -> list[str]:
    issues: list[str] = []
    for marker in REQUIRED_BUILD_MARKERS:
        if marker not in text:
            issues.append(f"cross_build:{marker}")
    return issues


def resolve_zig(explicit_zig: str | None) -> str | None:
    if explicit_zig:
        return explicit_zig
    return shutil.which("zig")


def run_cross_target(
    root: Path,
    target: str,
    *,
    zig_executable: str | None,
    runner=subprocess.run,
) -> int:
    zig = resolve_zig(zig_executable)
    if zig is None:
        print("PHASE12_CROSS=fail")
        print("PHASE12_CROSS_NOTE=zig not found on PATH; pass --zig to replay a target")
        return 1

    payload = load_fixture(root / "zigux/tests/fixtures/phase12_cross_targets.json")
    configured_targets = payload.get("targets")
    if not isinstance(configured_targets, list) or target not in configured_targets:
        print("PHASE12_CROSS=fail")
        print(f"PHASE12_CROSS_TARGET={target}")
        print("PHASE12_CROSS_NOTE=target not listed in phase12 cross fixture")
        return 1

    completed = runner(
        [
            zig,
            "build",
            "cross",
            "--build-file",
            "zigux/tests/phase12_cross_build.zig",
            f"-Dtarget={target}",
            "--summary",
            "all",
        ],
        cwd=root,
        check=False,
    )
    if completed.returncode != 0:
        print("PHASE12_CROSS=fail")
        print(f"PHASE12_CROSS_TARGET={target}")
        return completed.returncode

    print("PHASE12_CROSS=pass")
    print(f"PHASE12_CROSS_TARGET={target}")
    return 0


def run_all_targets(root: Path, *, zig_executable: str | None, runner=subprocess.run) -> int:
    payload = load_fixture(root / "zigux/tests/fixtures/phase12_cross_targets.json")
    configured_targets = payload.get("targets")
    if not isinstance(configured_targets, list):
        print("PHASE12_CROSS=fail")
        print("PHASE12_CROSS_NOTE=fixture targets list is invalid")
        return 1

    for target in configured_targets:
        rc = run_cross_target(
            root,
            target,
            zig_executable=zig_executable,
            runner=runner,
        )
        if rc != 0:
            return rc

    print(f"PHASE12_CROSS_TARGET_COUNT={len(configured_targets)}")
    return 0


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_tree(root: Path) -> None:
    write_text(
        root / "zigux/tests/fixtures/phase12_cross_targets.json",
        json.dumps(
            {
                "phase": "Phase 12",
                "lane_key": "P12-L02",
                "build_file": "zigux/tests/phase12_cross_build.zig",
                "build_step": "cross",
                "target_count": len(EXPECTED_TARGETS),
                "targets": EXPECTED_TARGETS,
            },
            indent=2,
        )
        + "\n",
    )
    write_text(root / "zigux/tests/phase12_cross_build.zig", "\n".join(REQUIRED_BUILD_MARKERS) + "\n")
    for rel_path in REQUIRED_FILES[2:]:
        write_text(root / rel_path, "// fixture\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="phase12_cross_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_tree(root)
        assert require_files(root) == []
        assert validate_fixture(load_fixture(root / "zigux/tests/fixtures/phase12_cross_targets.json")) == []
        assert validate_cross_build((root / "zigux/tests/phase12_cross_build.zig").read_text(encoding="utf-8")) == []
        checks_run += 1

        build_self_test_tree(root)
        payload = load_fixture(root / "zigux/tests/fixtures/phase12_cross_targets.json")
        payload["phase"] = "Phase 11"
        write_text(root / "zigux/tests/fixtures/phase12_cross_targets.json", json.dumps(payload) + "\n")
        assert "fixture:phase:'Phase 11'" in validate_fixture(load_fixture(root / "zigux/tests/fixtures/phase12_cross_targets.json"))
        checks_run += 1

        build_self_test_tree(root)
        payload = load_fixture(root / "zigux/tests/fixtures/phase12_cross_targets.json")
        payload["lane_key"] = "P12-L99"
        write_text(root / "zigux/tests/fixtures/phase12_cross_targets.json", json.dumps(payload) + "\n")
        assert "fixture:lane_key:'P12-L99'" in validate_fixture(load_fixture(root / "zigux/tests/fixtures/phase12_cross_targets.json"))
        checks_run += 1

        build_self_test_tree(root)
        payload = load_fixture(root / "zigux/tests/fixtures/phase12_cross_targets.json")
        payload["build_file"] = "zigux/tests/phase12_cross_build_missing.zig"
        write_text(root / "zigux/tests/fixtures/phase12_cross_targets.json", json.dumps(payload) + "\n")
        assert "fixture:build_file:'zigux/tests/phase12_cross_build_missing.zig'" in validate_fixture(
            load_fixture(root / "zigux/tests/fixtures/phase12_cross_targets.json")
        )
        checks_run += 1

        build_self_test_tree(root)
        payload = load_fixture(root / "zigux/tests/fixtures/phase12_cross_targets.json")
        payload["build_step"] = "test"
        write_text(root / "zigux/tests/fixtures/phase12_cross_targets.json", json.dumps(payload) + "\n")
        assert "fixture:build_step:'test'" in validate_fixture(
            load_fixture(root / "zigux/tests/fixtures/phase12_cross_targets.json")
        )
        checks_run += 1

        build_self_test_tree(root)
        payload = load_fixture(root / "zigux/tests/fixtures/phase12_cross_targets.json")
        payload["targets"] = EXPECTED_TARGETS[:-1]
        payload["target_count"] = len(EXPECTED_TARGETS) - 1
        write_text(root / "zigux/tests/fixtures/phase12_cross_targets.json", json.dumps(payload) + "\n")
        issues = validate_fixture(load_fixture(root / "zigux/tests/fixtures/phase12_cross_targets.json"))
        assert "fixture:targets:['x86_64-linux-musl', 'aarch64-linux-musl']" in issues
        assert "fixture:target_count:2" in issues
        checks_run += 1

        build_self_test_tree(root)
        cross_build_path = root / "zigux/tests/phase12_cross_build.zig"
        cross_build_path.write_text(
            cross_build_path.read_text(encoding="utf-8").replace(REQUIRED_BUILD_MARKERS[0], "", 1),
            encoding="utf-8",
        )
        assert f"cross_build:{REQUIRED_BUILD_MARKERS[0]}" in validate_cross_build(
            cross_build_path.read_text(encoding="utf-8")
        )
        checks_run += 1

        for rel_path in REQUIRED_FILES:
            build_self_test_tree(root)
            (root / rel_path).unlink()
            assert rel_path in require_files(root)
            checks_run += 1

        build_self_test_tree(root)
        assert resolve_zig("/custom/zig") == "/custom/zig"
        checks_run += 1

        build_self_test_tree(root)
        calls: list[list[str]] = []

        def success_runner(command, cwd, check=False):
            calls.append(command)
            return subprocess.CompletedProcess(command, 0)

        assert run_cross_target(root, EXPECTED_TARGETS[0], zig_executable="/custom/zig", runner=success_runner) == 0
        assert calls == [[
            "/custom/zig",
            "build",
            "cross",
            "--build-file",
            "zigux/tests/phase12_cross_build.zig",
            f"-Dtarget={EXPECTED_TARGETS[0]}",
            "--summary",
            "all",
        ]]
        checks_run += 1

        build_self_test_tree(root)
        calls = []
        assert run_all_targets(root, zig_executable="/custom/zig", runner=success_runner) == 0
        assert calls == [
            [
                "/custom/zig",
                "build",
                "cross",
                "--build-file",
                "zigux/tests/phase12_cross_build.zig",
                f"-Dtarget={target}",
                "--summary",
                "all",
            ]
            for target in EXPECTED_TARGETS
        ]
        checks_run += 1

        build_self_test_tree(root)

        def failing_runner(command, cwd, check=False):
            return subprocess.CompletedProcess(command, 7)

        assert run_cross_target(root, EXPECTED_TARGETS[1], zig_executable="/custom/zig", runner=failing_runner) == 7
        checks_run += 1

        build_self_test_tree(root)
        payload = load_fixture(root / "zigux/tests/fixtures/phase12_cross_targets.json")
        payload["targets"] = "not-a-list"
        write_text(root / "zigux/tests/fixtures/phase12_cross_targets.json", json.dumps(payload) + "\n")
        assert run_all_targets(
            root,
            zig_executable="/custom/zig",
            runner=lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("runner should not be used")),
        ) == 1
        checks_run += 1

        build_self_test_tree(root)
        assert run_cross_target(
            root,
            "powerpc-linux-musl",
            zig_executable="/custom/zig",
            runner=lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("runner should not be used")),
        ) == 1
        checks_run += 1

    if checks_run != EXPECTED_SELF_TEST_CASE_COUNT:
        raise SystemExit(
            f"phase12-cross:self-test:case_count:actual={checks_run}:expected={EXPECTED_SELF_TEST_CASE_COUNT}"
        )

    print("PHASE12_CROSS_SELF_TEST=pass")
    print(f"PHASE12_CROSS_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Phase 12 cross-target compile packet and optionally replay one or all configured targets."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage.")
    parser.add_argument("--target", help="Replay one configured target from the Phase 12 cross fixture.")
    parser.add_argument("--all-targets", action="store_true", help="Replay every configured target from the Phase 12 cross fixture.")
    parser.add_argument("--zig", help="Explicit zig executable path.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = require_files(ROOT)
    if missing:
        print("PHASE12_CROSS=fail")
        print("PHASE12_CROSS_MISSING_FILES_START")
        for rel_path in missing:
            print(rel_path)
        print("PHASE12_CROSS_MISSING_FILES_END")
        return 1

    try:
        issues = validate_fixture(load_fixture(FIXTURE))
    except json.JSONDecodeError as exc:
        print("PHASE12_CROSS=fail")
        print(f"PHASE12_CROSS_NOTE=invalid fixture JSON: {exc.msg}")
        return 1
    except ValueError as exc:
        print("PHASE12_CROSS=fail")
        print(f"PHASE12_CROSS_NOTE={exc}")
        return 1

    issues.extend(validate_cross_build(CROSS_BUILD.read_text(encoding="utf-8")))
    if issues:
        print("PHASE12_CROSS=fail")
        print("PHASE12_CROSS_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE12_CROSS_ISSUES_END")
        return 1

    if args.target:
        return run_cross_target(ROOT, args.target, zig_executable=args.zig)
    if args.all_targets:
        return run_all_targets(ROOT, zig_executable=args.zig)

    payload = load_fixture(FIXTURE)
    targets = payload["targets"]
    print("PHASE12_CROSS=pass")
    print(f"PHASE12_CROSS_TARGET_COUNT={len(targets)}")
    print(f"PHASE12_CROSS_TARGETS={','.join(targets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())