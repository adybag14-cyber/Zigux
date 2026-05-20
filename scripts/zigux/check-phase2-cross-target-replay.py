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
ROOT = SELF_PATH.parents[2] if len(Path(__file__).resolve().parents) >= 3 else SELF_PATH.parent

FIXTURE = Path("zigux") / "tests" / "fixtures" / "phase2_cross_targets.json"
POLICY = Path("scripts") / "zigux" / "zig-toolchain-policy.json"

EXPECTED_PHASE = "Phase 2"
EXPECTED_STATUS = "active"
EXPECTED_ROUTE = "make -C zigux phase2-cross"
EXPECTED_TARGET_ORDER = ("x86_64-linux", "aarch64-linux")
ALLOWED_VALIDATION_MODES = ("archive_required", "route_contract_only")
ZIG_TEST_FILES = (
    Path("scripts") / "zigux" / "kconfig" / "conf_bridge.zig",
    Path("scripts") / "zigux" / "kconfig" / "confdata_bridge.zig",
)
DEFAULT_TIMEOUT_SECONDS = 300


class DuplicateJsonKeyError(ValueError):
    pass


def reject_duplicate_object_pairs(pairs: list[tuple[object, object]]) -> dict[object, object]:
    payload: dict[object, object] = {}
    for key, value in pairs:
        if key in payload:
            raise DuplicateJsonKeyError(str(key))
        payload[key] = value
    return payload


def resolve_repo_path(root: Path, relative_path: Path) -> Path:
    return root / relative_path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def load_json(path: Path) -> object:
    try:
        return json.loads(read_text(path), object_pairs_hook=reject_duplicate_object_pairs)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    except DuplicateJsonKeyError as exc:
        raise SystemExit(f"duplicate json key in required file: {path}: {exc}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def is_strict_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value) and value == value.strip()


def resolve_zig(override: str | None) -> str | None:
    if override:
        override_path = Path(override)
        if override_path.is_file():
            return str(override_path)
        return shutil.which(override)
    return shutil.which("zig")


def normalize_timeout_seconds(value: int) -> int:
    if value <= 0:
        raise SystemExit("--timeout-seconds must be a positive integer")
    return value


def load_archive_target_scope(root: Path) -> list[str]:
    policy_path = resolve_repo_path(root, POLICY)
    payload = load_json(policy_path)
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid policy payload in required file: {policy_path}")

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {policy_path}")

    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list) or not archive_target_scope:
        raise SystemExit(f"invalid archive_target_scope in required file: {policy_path}")

    normalized: list[str] = []
    seen_targets: set[str] = set()
    for value in archive_target_scope:
        if not is_strict_non_empty_string(value):
            raise SystemExit(f"invalid archive_target_scope entry in required file: {policy_path}")
        if value in seen_targets:
            raise SystemExit(f"duplicate archive_target_scope entry in required file: {policy_path}: {value}")
        seen_targets.add(value)
        normalized.append(value)

    unsupported_targets = [value for value in normalized if value not in EXPECTED_TARGET_ORDER]
    if unsupported_targets:
        raise SystemExit(
            "unsupported archive_target_scope target in required file: "
            f"{policy_path}: {', '.join(unsupported_targets)}"
        )
    return normalized


def collect_fixture_archive_target_scope_issues(fixture_scope: object) -> list[str]:
    issues: list[str] = []
    if not isinstance(fixture_scope, list) or not fixture_scope:
        return [f"fixture:archive_target_scope:{fixture_scope!r}"]

    seen_targets: set[str] = set()
    for index, value in enumerate(fixture_scope):
        if not is_strict_non_empty_string(value):
            issues.append(f"fixture:archive_target_scope_entry:{index}:{value!r}")
            continue
        if value in seen_targets:
            issues.append(f"fixture:duplicate_archive_target_scope:{value}")
            continue
        seen_targets.add(value)
    return issues


def collect_fixture_issues(root: Path) -> list[str]:
    fixture_path = resolve_repo_path(root, FIXTURE)
    payload = load_json(fixture_path)
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
    fixture_scope_issues = collect_fixture_archive_target_scope_issues(fixture_scope)
    issues.extend(fixture_scope_issues)
    if not fixture_scope_issues and fixture_scope != archive_target_scope:
        issues.append(f"fixture:archive_target_scope:{fixture_scope!r}")

    cross_targets = payload.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        issues.append(f"fixture:cross_targets:{cross_targets!r}")
        return issues

    seen_targets: set[str] = set()
    target_order: list[str] = []
    archive_required_targets: set[str] = set()
    for index, entry in enumerate(cross_targets):
        if not isinstance(entry, dict):
            issues.append(f"fixture:cross_target_entry:{index}:{type(entry).__name__}")
            continue

        target = entry.get("target")
        review_status = entry.get("review_status")
        validation_mode = entry.get("validation_mode")
        route = entry.get("route")

        if not is_strict_non_empty_string(target):
            issues.append(f"fixture:cross_target_target:{index}:{target!r}")
            continue

        if target in seen_targets:
            issues.append(f"fixture:duplicate_target:{target}")
        seen_targets.add(target)
        target_order.append(target)

        if target not in EXPECTED_TARGET_ORDER:
            issues.append(f"fixture:unexpected_target:{target}")

        if route != EXPECTED_ROUTE:
            issues.append(f"fixture:cross_target_route:{target}:{route!r}")
        if not is_strict_non_empty_string(review_status):
            issues.append(f"fixture:cross_target_review_status:{target}:{review_status!r}")
        if validation_mode not in ALLOWED_VALIDATION_MODES:
            issues.append(f"fixture:cross_target_validation_mode:{target}:{validation_mode!r}")
            continue

        if validation_mode == "archive_required":
            archive_required_targets.add(target)
            if target not in archive_target_scope:
                issues.append(f"fixture:archive_required_target_outside_scope:{target}")

    if seen_targets != set(EXPECTED_TARGET_ORDER):
        issues.append(
            "fixture:target_set_mismatch:"
            f"expected={list(EXPECTED_TARGET_ORDER)!r}:actual={target_order!r}"
        )
    if target_order != list(EXPECTED_TARGET_ORDER):
        issues.append(
            "fixture:target_order_mismatch:"
            f"expected={list(EXPECTED_TARGET_ORDER)!r}:actual={target_order!r}"
        )

    if archive_required_targets != set(archive_target_scope):
        issues.append(
            "fixture:archive_required_target_set_mismatch:"
            f"expected={sorted(archive_target_scope)!r}:actual={sorted(archive_required_targets)!r}"
        )

    return issues


def collect_replay_file_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path in ZIG_TEST_FILES:
        path = resolve_repo_path(root, rel_path)
        if not path.is_file():
            issues.append(f"replay:file_missing:{rel_path.as_posix()}")
    return issues


def load_targets(root: Path) -> list[str]:
    fixture_path = resolve_repo_path(root, FIXTURE)
    payload = load_json(fixture_path)
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid fixture payload in required file: {fixture_path}")

    cross_targets = payload.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        raise SystemExit(f"invalid cross_targets in required file: {fixture_path}")

    targets: list[str] = []
    for entry in cross_targets:
        if not isinstance(entry, dict) or not is_strict_non_empty_string(entry.get("target")):
            raise SystemExit(f"invalid cross target entry in required file: {fixture_path}")
        targets.append(entry["target"])
    return targets


def emit_summary(mode: str, targets: list[str]) -> None:
    print("PHASE2_CROSS_TARGET_REPLAY=pass")
    print(f"PHASE2_CROSS_TARGET_REPLAY_MODE={mode}")
    print(f"PHASE2_CROSS_TARGET_REPLAY_TARGET_COUNT={len(targets)}")
    print(f"PHASE2_CROSS_TARGET_REPLAY_TARGETS={','.join(targets)}")
    print(f"PHASE2_CROSS_TARGET_REPLAY_FILE_COUNT={len(ZIG_TEST_FILES)}")


def emit_completed_targets(mode: str, completed_targets: list[str]) -> None:
    print(f"PHASE2_CROSS_TARGET_REPLAY_MODE={mode}")
    print(f"PHASE2_CROSS_TARGET_REPLAY_COMPLETED_TARGET_COUNT={len(completed_targets)}")
    print(f"PHASE2_CROSS_TARGET_REPLAY_COMPLETED_TARGETS={','.join(completed_targets)}")


def replay_target(
    root: Path,
    zig: str,
    target: str,
    timeout_seconds: int,
    *,
    emit_pass_summary: bool = True,
) -> int:
    for rel_path in ZIG_TEST_FILES:
        rel_path_text = rel_path.as_posix()
        try:
            completed = subprocess.run(
                [zig, "test", rel_path_text, "-target", target, "--test-no-exec"],
                cwd=root,
                check=False,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            print("PHASE2_CROSS_TARGET_REPLAY=fail")
            print("PHASE2_CROSS_TARGET_REPLAY_MODE=single-target")
            print(f"PHASE2_CROSS_TARGET_REPLAY_TARGET={target}")
            print(f"PHASE2_CROSS_TARGET_REPLAY_FAILED_FILE={rel_path_text}")
            print(f"PHASE2_CROSS_TARGET_REPLAY_NOTE=zig timed out: {exc}")
            return 1
        except OSError as exc:
            print("PHASE2_CROSS_TARGET_REPLAY=fail")
            print("PHASE2_CROSS_TARGET_REPLAY_MODE=single-target")
            print(f"PHASE2_CROSS_TARGET_REPLAY_TARGET={target}")
            print(f"PHASE2_CROSS_TARGET_REPLAY_FAILED_FILE={rel_path_text}")
            print(f"PHASE2_CROSS_TARGET_REPLAY_NOTE=failed to execute zig: {exc}")
            return 1

        if completed.returncode != 0:
            print("PHASE2_CROSS_TARGET_REPLAY=fail")
            print("PHASE2_CROSS_TARGET_REPLAY_MODE=single-target")
            print(f"PHASE2_CROSS_TARGET_REPLAY_TARGET={target}")
            print(f"PHASE2_CROSS_TARGET_REPLAY_FAILED_FILE={rel_path_text}")
            return completed.returncode

    if emit_pass_summary:
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
    completed_targets: list[str] = []
    for target in targets:
        result = replay_target(root, zig, target, timeout_seconds, emit_pass_summary=False)
        if result != 0:
            emit_completed_targets("all-targets", completed_targets)
            return result
        completed_targets.append(target)

    emit_summary("all-targets", targets)
    return 0


def build_self_test_root(root: Path) -> None:
    write_text(
        resolve_repo_path(root, POLICY),
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
        resolve_repo_path(root, FIXTURE),
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
        write_text(resolve_repo_path(root, rel_path), 'test {\n    try @import("std").testing.expect(true);\n}\n')


def build_fake_zig(path: Path, log_path: Path, *, fail_target: str | None = None) -> None:
    fail_condition = "False"
    if fail_target is not None:
        fail_condition = repr(fail_target) + " in sys.argv"
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
                f"if {fail_condition}:",
                "    raise SystemExit(9)",
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


def fail_with_note(note: str) -> int:
    print("PHASE2_CROSS_TARGET_REPLAY=fail")
    print(f"PHASE2_CROSS_TARGET_REPLAY_NOTE={note}")
    return 1


def run_checked(root: Path, zig: str | None, target: str | None, all_targets: bool, timeout_seconds: int) -> int:
    try:
        timeout_seconds = normalize_timeout_seconds(timeout_seconds)

        issues = collect_fixture_issues(root)
        issues.extend(collect_replay_file_issues(root))
        if issues:
            print("PHASE2_CROSS_TARGET_REPLAY=fail")
            for issue in issues:
                print(issue)
            return 1

        if target and all_targets:
            raise SystemExit("--target and --all-targets are mutually exclusive")

        if all_targets or target:
            if zig is None:
                return fail_with_note("zig not found on PATH")

        if all_targets:
            return run_all_targets(root, zig, timeout_seconds)
        if target:
            return run_single_target(root, zig, target, timeout_seconds)

        emit_summary("summary", load_targets(root))
        return 0
    except SystemExit as exc:
        if isinstance(exc.code, str):
            return fail_with_note(exc.code)
        raise


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_target_replay_") as tmp_dir:
        root = Path(tmp_dir)
        fixture_path = resolve_repo_path(root, FIXTURE)
        policy_path = resolve_repo_path(root, POLICY)

        assert policy_path == root / "scripts" / "zigux" / "zig-toolchain-policy.json"
        assert fixture_path == root / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
        assert ZIG_TEST_FILES[0] == Path("scripts") / "zigux" / "kconfig" / "conf_bridge.zig"
        checks_run += 1

        build_self_test_root(root)
        assert collect_fixture_issues(root) == []
        assert collect_replay_file_issues(root) == []
        checks_run += 1

        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["phase"] = "Phase X"
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert "fixture:phase:'Phase X'" in collect_fixture_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["status"] = "blocked"
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert "fixture:status:'blocked'" in collect_fixture_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["route"] = "make -C zigux phase2"
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert "fixture:route:'make -C zigux phase2'" in collect_fixture_issues(root)
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
        payload["cross_targets"][0]["target"] = " x86_64-linux "
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert "fixture:cross_target_target:0:' x86_64-linux '" in collect_fixture_issues(root)
        checks_run += 1

        build_selfTestRoot(root)
