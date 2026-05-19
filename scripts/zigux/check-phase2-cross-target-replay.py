#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import io
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"

EXPECTED_PHASE = "Phase 2"
EXPECTED_STATUS = "active"
EXPECTED_ROUTE = "make -C zigux phase2-cross"
ALLOWED_VALIDATION_MODES = ("archive_required", "route_contract_only")
ZIG_TEST_FILES = (
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
)
DEFAULT_TIMEOUT_SECONDS = 300


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def load_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def resolve_zig(override: str | None) -> str | None:
    if override:
        override_path = Path(override)
        if override_path.is_file():
            return str(override_path)
        return shutil.which(override)
    return shutil.which("zig")


def load_archive_target_scope(root: Path) -> list[str]:
    payload = load_json(root / POLICY)
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid policy payload in required file: {root / POLICY}")

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {root / POLICY}")

    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list) or not archive_target_scope:
        raise SystemExit(f"invalid archive_target_scope in required file: {root / POLICY}")

    normalized: list[str] = []
    for value in archive_target_scope:
        if not is_non_empty_string(value):
            raise SystemExit(f"invalid archive_target_scope entry in required file: {root / POLICY}")
        normalized.append(value.strip())
    return normalized


def collect_fixture_issues(root: Path) -> list[str]:
    payload = load_json(root / FIXTURE)
    issues: list[str] = []

    if not isinstance(payload, dict):
        return [f"fixture:shape:{type(payload).__name__}"]

    if payload.get("phase") != EXPECTED_PHASE:
        issues.append(f"fixture:phase:{payload.get('phase')!r}")
    if payload.get("status") != EXPECTED_STATUS:
        issues.append(f"fixture:status:{payload.get('status')!r}")
    if payload.get("route") != EXPECTED_ROUTE:
        issues.append(f"fixture:route:{payload.get('route')!r}")

    archive_target_scope = load_archive_target_scope(root)
    fixture_scope = payload.get("archive_target_scope")
    if fixture_scope != archive_target_scope:
        issues.append(f"fixture:archive_target_scope:{fixture_scope!r}")

    cross_targets = payload.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        issues.append(f"fixture:cross_targets:{cross_targets!r}")
        return issues

    seen_targets: set[str] = set()
    archive_required_targets: set[str] = set()
    for index, entry in enumerate(cross_targets):
        if not isinstance(entry, dict):
            issues.append(f"fixture:cross_target_entry:{index}:{type(entry).__name__}")
            continue

        target = entry.get("target")
        review_status = entry.get("review_status")
        validation_mode = entry.get("validation_mode")
        route = entry.get("route")

        if not is_non_empty_string(target):
            issues.append(f"fixture:cross_target_target:{index}:{target!r}")
            continue
        target = target.strip()

        if target in seen_targets:
            issues.append(f"fixture:duplicate_target:{target}")
        seen_targets.add(target)

        if route != EXPECTED_ROUTE:
            issues.append(f"fixture:cross_target_route:{target}:{route!r}")
        if not is_non_empty_string(review_status):
            issues.append(f"fixture:cross_target_review_status:{target}:{review_status!r}")
        if validation_mode not in ALLOWED_VALIDATION_MODES:
            issues.append(f"fixture:cross_target_validation_mode:{target}:{validation_mode!r}")
            continue

        if validation_mode == "archive_required":
            archive_required_targets.add(target)
            if target not in archive_target_scope:
                issues.append(f"fixture:archive_required_target_outside_scope:{target}")

    if archive_required_targets != set(archive_target_scope):
        issues.append(
            "fixture:archive_required_target_set_mismatch:"
            f"expected={sorted(archive_target_scope)!r}:actual={sorted(archive_required_targets)!r}"
        )

    return issues


def load_targets(root: Path) -> list[str]:
    payload = load_json(root / FIXTURE)
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid fixture payload in required file: {root / FIXTURE}")

    cross_targets = payload.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        raise SystemExit(f"invalid cross_targets in required file: {root / FIXTURE}")

    targets: list[str] = []
    for entry in cross_targets:
        if not isinstance(entry, dict) or not is_non_empty_string(entry.get("target")):
            raise SystemExit(f"invalid cross target entry in required file: {root / FIXTURE}")
        targets.append(entry["target"].strip())
    return targets


def emit_summary(mode: str, targets: list[str]) -> None:
    print("PHASE2_CROSS_TARGET_REPLAY=pass")
    print(f"PHASE2_CROSS_TARGET_REPLAY_MODE={mode}")
    print(f"PHASE2_CROSS_TARGET_REPLAY_TARGET_COUNT={len(targets)}")
    print(f"PHASE2_CROSS_TARGET_REPLAY_TARGETS={','.join(targets)}")
    print(f"PHASE2_CROSS_TARGET_REPLAY_FILE_COUNT={len(ZIG_TEST_FILES)}")


def replay_target(root: Path, zig: str, target: str, timeout_seconds: int) -> int:
    for rel_path in ZIG_TEST_FILES:
        try:
            completed = subprocess.run(
                [zig, "test", rel_path, "-target", target, "--test-no-exec"],
                cwd=root,
                check=False,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            print("PHASE2_CROSS_TARGET_REPLAY=fail")
            print("PHASE2_CROSS_TARGET_REPLAY_MODE=single-target")
            print(f"PHASE2_CROSS_TARGET_REPLAY_TARGET={target}")
            print(f"PHASE2_CROSS_TARGET_REPLAY_FAILED_FILE={rel_path}")
            print(f"PHASE2_CROSS_TARGET_REPLAY_NOTE=zig timed out: {exc}")
            return 1
        except OSError as exc:
            print("PHASE2_CROSS_TARGET_REPLAY=fail")
            print("PHASE2_CROSS_TARGET_REPLAY_MODE=single-target")
            print(f"PHASE2_CROSS_TARGET_REPLAY_TARGET={target}")
            print(f"PHASE2_CROSS_TARGET_REPLAY_FAILED_FILE={rel_path}")
            print(f"PHASE2_CROSS_TARGET_REPLAY_NOTE=failed to execute zig: {exc}")
            return 1

        if completed.returncode != 0:
            print("PHASE2_CROSS_TARGET_REPLAY=fail")
            print("PHASE2_CROSS_TARGET_REPLAY_MODE=single-target")
            print(f"PHASE2_CROSS_TARGET_REPLAY_TARGET={target}")
            print(f"PHASE2_CROSS_TARGET_REPLAY_FAILED_FILE={rel_path}")
            return completed.returncode

    emit_summary("single-target", [target])
    return 0


def run_single_target(root: Path, zig: str, target: str, timeout_seconds: int) -> int:
    targets = load_targets(root)
    if target not in targets:
        print("PHASE2_CROSS_TARGET_REPLAY=fail")
        print("PHASE2_CROSS_TARGET_REPLAY_MODE=single-target")
        print(f"PHASE2_CROSS_TARGET_REPLAY_TARGET={target}")
        print("PHASE2_CROSS_TARGET_REPLAY_NOTE=target not listed in fixture")
        return 1
    return replay_target(root, zig, target, timeout_seconds)


def run_all_targets(root: Path, zig: str, timeout_seconds: int) -> int:
    targets = load_targets(root)
    for target in targets:
        result = replay_target(root, zig, target, timeout_seconds)
        if result != 0:
            print("PHASE2_CROSS_TARGET_REPLAY_MODE=all-targets")
            return result

    emit_summary("all-targets", targets)
    return 0


def build_self_test_root(root: Path) -> None:
    write_text(
        root / POLICY,
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": ["phase2-toolchain", "phase2-validate"],
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / FIXTURE,
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "route": EXPECTED_ROUTE,
                "archive_target_scope": ["x86_64-linux"],
                "cross_targets": [
                    {
                        "target": "x86_64-linux",
                        "review_status": "pinned bootstrap archive",
                        "validation_mode": "archive_required",
                        "route": EXPECTED_ROUTE,
                    },
                    {
                        "target": "aarch64-linux",
                        "review_status": "route contract only",
                        "validation_mode": "route_contract_only",
                        "route": EXPECTED_ROUTE,
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )
    for rel_path in ZIG_TEST_FILES:
        write_text(root / rel_path, "test {\n    try @import(\"std\").testing.expect(true);\n}\n")


def build_fake_zig(path: Path, log_path: Path) -> None:
    write_text(
        path,
        "\n".join(
            (
                "#!/usr/bin/env python3",
                "import pathlib, sys",
                f"log_path = pathlib.Path({str(log_path)!r})",
                "log_path.parent.mkdir(parents=True, exist_ok=True)",
                "with log_path.open('a', encoding='utf-8') as handle:",
                "    handle.write(' '.join(sys.argv[1:]) + '\\n')",
                "raise SystemExit(0)",
            )
        )
        + "\n",
    )
    path.chmod(0o755)


def capture_stdout(callable_obj, *args) -> tuple[int, str]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        result = callable_obj(*args)
    return result, buffer.getvalue()


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_target_replay_") as tmp_dir:
        root = Path(tmp_dir)
        fixture_path = root / FIXTURE
        policy_path = root / POLICY

        build_self_test_root(root)
        assert collect_fixture_issues(root) == []
        checks_run += 1

        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["status"] = "blocked"
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert "fixture:status:'blocked'" in collect_fixture_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["validation_mode"] = "unexpected_mode"
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_fixture_issues(root)
        assert "fixture:cross_target_validation_mode:x86_64-linux:'unexpected_mode'" in issues
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["cross_targets"].append(dict(payload["cross_targets"][0]))
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert "fixture:duplicate_target:x86_64-linux" in collect_fixture_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["target"] = "riscv64-linux"
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_fixture_issues(root)
        assert "fixture:archive_required_target_outside_scope:riscv64-linux" in issues
        assert any(issue.startswith("fixture:archive_required_target_set_mismatch:") for issue in issues)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["x86_64-linux", "riscv64-linux"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_fixture_issues(root)
        assert "fixture:archive_target_scope:['x86_64-linux']" in issues
        assert any(issue.startswith("fixture:archive_required_target_set_mismatch:") for issue in issues)
        checks_run += 1

        build_self_test_root(root)
        fake_zig = root / "fake-zig"
        log_path = root / "fake-zig.log"
        if log_path.exists():
            log_path.unlink()
        build_fake_zig(fake_zig, log_path)
        result, output = capture_stdout(run_single_target, root, str(fake_zig), "x86_64-linux", 60)
        assert result == 0
        log_lines = log_path.read_text(encoding="utf-8").splitlines()
        assert len(log_lines) == len(ZIG_TEST_FILES)
        assert "PHASE2_CROSS_TARGET_REPLAY_MODE=single-target" in output
        assert "PHASE2_CROSS_TARGET_REPLAY_TARGETS=x86_64-linux" in output
        assert log_lines[0] == "test scripts/zigux/kconfig/conf_bridge.zig -target x86_64-linux --test-no-exec"
        assert log_lines[1] == "test scripts/zigux/kconfig/confdata_bridge.zig -target x86_64-linux --test-no-exec"
        checks_run += 1

        build_self_test_root(root)
        fake_zig = root / "fake-zig"
        log_path = root / "fake-zig.log"
        if log_path.exists():
            log_path.unlink()
        build_fake_zig(fake_zig, log_path)
        result, output = capture_stdout(run_all_targets, root, str(fake_zig), 60)
        assert result == 0
        log_lines = log_path.read_text(encoding="utf-8").splitlines()
        assert len(log_lines) == len(ZIG_TEST_FILES) * 2
        assert "PHASE2_CROSS_TARGET_REPLAY_MODE=all-targets" in output
        assert "PHASE2_CROSS_TARGET_REPLAY_TARGET_COUNT=2" in output
        assert "PHASE2_CROSS_TARGET_REPLAY_TARGETS=x86_64-linux,aarch64-linux" in output
        checks_run += 1

        build_self_test_root(root)
        result, output = capture_stdout(run_single_target, root, "/definitely-missing-zig", "x86_64-linux", 60)
        assert result == 1
        assert "failed to execute zig" in output
        checks_run += 1

        build_self_test_root(root)
        fake_zig = root / "fake-zig"
        log_path = root / "fake-zig.log"
        if log_path.exists():
            log_path.unlink()
        build_fake_zig(fake_zig, log_path)
        result, output = capture_stdout(run_single_target, root, str(fake_zig), "riscv64-linux", 60)
        assert result == 1
        assert "target not listed in fixture" in output
        checks_run += 1

    print("PHASE2_CROSS_TARGET_REPLAY_SELF_TEST=pass")
    print(f"PHASE2_CROSS_TARGET_REPLAY_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compile-check the current Phase 2 cross-target fixture against the live bridge Zig files."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--zig", help="Path to the Zig binary to use")
    parser.add_argument("--target", help="Single target from phase2_cross_targets.json to replay")
    parser.add_argument("--all-targets", action="store_true", help="Replay every target from the fixture")
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    root = args.root.resolve()
    if args.self_test:
        return run_self_test()

    issues = collect_fixture_issues(root)
    if issues:
        print("PHASE2_CROSS_TARGET_REPLAY=fail")
        for issue in issues:
            print(issue)
        return 1

    zig = resolve_zig(args.zig)
    if zig is None:
        print("PHASE2_CROSS_TARGET_REPLAY=fail")
        print("PHASE2_CROSS_TARGET_REPLAY_NOTE=zig not found on PATH")
        return 1

    if args.target and args.all_targets:
        raise SystemExit("--target and --all-targets are mutually exclusive")

    if args.all_targets:
        return run_all_targets(root, zig, args.timeout_seconds)
    if args.target:
        return run_single_target(root, zig, args.target, args.timeout_seconds)

    emit_summary("summary", load_targets(root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())