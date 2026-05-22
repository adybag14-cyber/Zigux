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

FIXTURE = Path("zigux") / "tests" / "fixtures" / "phase2_cross_targets.json"
POLICY = Path("scripts") / "zigux" / "zig-toolchain-policy.json"

EXPECTED_PHASE = "Phase 2"
EXPECTED_STATUS = "active"
EXPECTED_ROUTE = "make -C zigux phase2-cross"
EXPECTED_TARGET_ORDER = ("x86_64-linux", "aarch64-linux")
EXPECTED_REQUIRED_MAKE_ROUTE = "phase2-cross"
EXPECTED_FIXTURE_FIELDS = frozenset(
    ("phase", "status", "route", "archive_target_scope", "cross_targets")
)
EXPECTED_CROSS_TARGET_FIELDS = frozenset(
    ("target", "review_status", "validation_mode", "route")
)
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
    if not path.exists():
        raise SystemExit(f"required file missing: {path}")
    if not path.is_file():
        raise SystemExit(f"required path is not a file: {path}")
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"failed to read required file: {path}: {exc}") from exc


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
    return normalized


def load_required_make_routes(root: Path) -> list[str]:
    policy_path = resolve_repo_path(root, POLICY)
    payload = load_json(policy_path)
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid policy payload in required file: {policy_path}")

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {policy_path}")

    required_make_routes = upgrade_policy.get("required_make_routes")
    if not isinstance(required_make_routes, list) or not required_make_routes:
        raise SystemExit(f"invalid required_make_routes in required file: {policy_path}")

    normalized: list[str] = []
    seen_routes: set[str] = set()
    for value in required_make_routes:
        if not is_strict_non_empty_string(value):
            raise SystemExit(f"invalid required_make_routes entry in required file: {policy_path}")
        if value in seen_routes:
            raise SystemExit(f"duplicate required_make_routes entry in required file: {policy_path}: {value}")
        seen_routes.add(value)
        normalized.append(value)
    return normalized


def describe_entry_label(index: int, entry: object) -> str:
    if isinstance(entry, dict):
        target = entry.get("target")
        if isinstance(target, str) and target:
            return target
    return f"index={index}"


def collect_field_set_issues(
    actual_keys: set[str], expected_keys: frozenset[str], prefix: str, label: str
) -> list[str]:
    issues: list[str] = []
    unexpected = sorted(actual_keys - expected_keys)
    missing = sorted(expected_keys - actual_keys)
    if unexpected:
        issues.append(f"{prefix}:unexpected_fields:{label}:{unexpected!r}")
    if missing:
        issues.append(f"{prefix}:missing_fields:{label}:{missing!r}")
    return issues


def collect_fixture_issues(root: Path) -> list[str]:
    fixture_path = resolve_repo_path(root, FIXTURE)
    payload = load_json(fixture_path)
    issues: list[str] = []

    if not isinstance(payload, dict):
        return [f"fixture:shape:{type(payload).__name__}"]

    issues.extend(
        collect_field_set_issues(set(payload.keys()), EXPECTED_FIXTURE_FIELDS, "fixture", "root")
    )

    if payload.get("phase") != EXPECTED_PHASE:
        issues.append(f"fixture:phase:{payload.get('phase')!r}")
    if payload.get("status") != EXPECTED_STATUS:
        issues.append(f"fixture:status:{payload.get('status')!r}")
    if payload.get("route") != EXPECTED_ROUTE:
        issues.append(f"fixture:route:{payload.get('route')!r}")

    archive_target_scope = load_archive_target_scope(root)
    required_make_routes = load_required_make_routes(root)
    if EXPECTED_REQUIRED_MAKE_ROUTE not in required_make_routes:
        issues.append(f"policy:missing_required_make_route:{EXPECTED_REQUIRED_MAKE_ROUTE}")
    fixture_scope = payload.get("archive_target_scope")
    if fixture_scope != archive_target_scope:
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

        entry_label = describe_entry_label(index, entry)
        issues.extend(
            collect_field_set_issues(
                set(entry.keys()), EXPECTED_CROSS_TARGET_FIELDS, "fixture:cross_target", entry_label
            )
        )

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


def replay_target(root: Path, zig: str, target: str, timeout_seconds: int) -> int:
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
                    "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],
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


def fail_with_note(note: str) -> int:
    print("PHASE2_CROSS_TARGET_REPLAY=fail")
    print(f"PHASE2_CROSS_TARGET_REPLAY_NOTE={note}")
    return 1


def run_checked(root: Path, zig: str | None, target: str | None, all_targets: bool, timeout_seconds: int) -> int:
    try:
        timeout_seconds = normalize_timeout_seconds(timeout_seconds)

        issues = collect_fixture_issues(root)
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

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["cross_targets"][1]["review_status"] = " route contract only "
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert (
            "fixture:cross_target_review_status:aarch64-linux:' route contract only '"
            in collect_fixture_issues(root)
        )
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert f"policy:missing_required_make_route:{EXPECTED_REQUIRED_MAKE_ROUTE}" in collect_fixture_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = [" x86_64-linux "]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            collect_fixture_issues(root)
        except SystemExit as exc:
            assert "invalid archive_target_scope entry" in str(exc)
        else:
            raise AssertionError("expected whitespace-padded archive_target_scope entry to fail closed")
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["x86_64-linux", "x86_64-linux"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            collect_fixture_issues(root)
        except SystemExit as exc:
            assert "duplicate archive_target_scope entry" in str(exc)
        else:
            raise AssertionError("expected duplicate archive_target_scope entry to fail closed")
        checks_run += 1

        build_self_test_root(root)
        policy_path.write_text(
            """{
  \"phase\": \"Phase 2\",
  \"phase\": \"Phase 2\",
  \"channel\": \"0.17.0-dev.87+9b177a7d2\",
  \"minimum_version\": \"0.17.0-dev.87+9b177a7d2\",
  \"archive_sha256\": {
    \"x86_64-linux\": \"3333333333333333333333333333333333333333333333333333333333333333\"
  },
  \"upgrade_policy\": {
    \"channel_minimum_lockstep\": true,
    \"archive_target_scope\": [
      \"x86_64-linux\"
    ],
    \"required_make_routes\": [
      \"phase2-toolchain\",
      \"phase2-validate\"
    ]
  }
}
""",
            encoding="utf-8",
        )
        try:
            collect_fixture_issues(root)
        except SystemExit as exc:
            assert "duplicate json key" in str(exc)
        else:
            raise AssertionError("expected duplicate policy json key to fail closed")
        checks_run += 1

        build_self_test_root(root)
        fixture_path.write_text(
            """{
  \"phase\": \"Phase 2\",
  \"status\": \"active\",
  \"route\": \"make -C zigux phase2-cross\",
  \"archive_target_scope\": [
    \"x86_64-linux\"
  ],
  \"cross_targets\": [
    {
      \"target\": \"x86_64-linux\",
      \"review_status\": \"pinned bootstrap archive\",
      \"validation_mode\": \"archive_required\",
      \"validation_mode\": \"archive_required\",
      \"route\": \"make -C zigux phase2-cross\"
    },
    {
      \"target\": \"aarch64-linux\",
      \"review_status\": \"route contract only\",
      \"validation_mode\": \"route_contract_only\",
      \"route\": \"make -C zigux phase2-cross\"
    }
  ]
}
""",
            encoding="utf-8",
        )
        try:
            collect_fixture_issues(root)
        except SystemExit as exc:
            assert "duplicate json key" in str(exc)
        else:
            raise AssertionError("expected duplicate fixture json key to fail closed")
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["unexpected"] = True
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert (
            "fixture:cross_target:unexpected_fields:x86_64-linux:['unexpected']"
            in collect_fixture_issues(root)
        )
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["extra_root"] = True
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert "fixture:unexpected_fields:root:['extra_root']" in collect_fixture_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["cross_targets"][0].pop("route")
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_fixture_issues(root)
        assert "fixture:cross_target:missing_fields:x86_64-linux:['route']" in issues
        assert "fixture:cross_target_route:x86_64-linux:None" in issues
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["target"] = "riscv64-linux"
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_fixture_issues(root)
        assert "fixture:unexpected_target:riscv64-linux" in issues
        assert (
            "fixture:target_set_mismatch:expected=['x86_64-linux', 'aarch64-linux']:actual=['riscv64-linux', 'aarch64-linux']"
            in issues
        )
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
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["cross_targets"] = {}
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert "fixture:cross_targets:{}" in collect_fixture_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["cross_targets"][0] = "broken"
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert "fixture:cross_target_entry:0:str" in collect_fixture_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["cross_targets"] = [payload["cross_targets"][1], payload["cross_targets"][0]]
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_fixture_issues(root)
        assert (
            "fixture:target_order_mismatch:expected=['x86_64-linux', 'aarch64-linux']:actual=['aarch64-linux', 'x86_64-linux']"
            in issues
        )
        assert (
            "fixture:target_set_mismatch:expected=['x86_64-linux', 'aarch64-linux']:actual=['aarch64-linux', 'x86_64-linux']"
            not in issues
        )
        checks_run += 1

        build_self_test_root(root)
        result, output = capture_stdout(run_checked, root, None, None, False, 60)
        assert result == 0
        assert "PHASE2_CROSS_TARGET_REPLAY_MODE=summary" in output
        assert "PHASE2_CROSS_TARGET_REPLAY_TARGET_COUNT=2" in output
        checks_run += 1

        build_self_test_root(root)
        result, output = capture_stdout(run_checked, root, None, None, False, 0)
        assert result == 1
        assert "PHASE2_CROSS_TARGET_REPLAY=fail" in output
        assert "--timeout-seconds must be a positive integer" in output
        checks_run += 1

        build_self_test_root(root)
        result, output = capture_stdout(run_checked, root, None, "x86_64-linux", False, 60)
        assert result == 1
        assert "PHASE2_CROSS_TARGET_REPLAY=fail" in output
        assert "zig not found on PATH" in output
        checks_run += 1

        build_self_test_root(root)
        result, output = capture_stdout(run_checked, root, None, None, True, 60)
        assert result == 1
        assert "PHASE2_CROSS_TARGET_REPLAY=fail" in output
        assert "zig not found on PATH" in output
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

        build_self_test_root(root)
        fixture_path.unlink()
        result, output = capture_stdout(run_checked, root, "zig", None, False, 60)
        assert result == 1
        assert "PHASE2_CROSS_TARGET_REPLAY=fail" in output
        assert "required file missing" in output
        checks_run += 1

        build_self_test_root(root)
        fixture_path.unlink()
        fixture_path.mkdir()
        result, output = capture_stdout(run_checked, root, "zig", None, False, 60)
        assert result == 1
        assert "PHASE2_CROSS_TARGET_REPLAY=fail" in output
        assert "required path is not a file" in output
        checks_run += 1
        fixture_path.rmdir()

        build_self_test_root(root)
        policy_path.unlink()
        result, output = capture_stdout(run_checked, root, "zig", None, False, 60)
        assert result == 1
        assert "PHASE2_CROSS_TARGET_REPLAY=fail" in output
        assert "required file missing" in output
        checks_run += 1

        build_self_test_root(root)
        policy_path.unlink()
        policy_path.mkdir()
        result, output = capture_stdout(run_checked, root, "zig", None, False, 60)
        assert result == 1
        assert "PHASE2_CROSS_TARGET_REPLAY=fail" in output
        assert "required path is not a file" in output
        checks_run += 1
        policy_path.rmdir()

        build_self_test_root(root)
        fixture_path.write_text("{\n", encoding="utf-8")
        result, output = capture_stdout(run_checked, root, "zig", None, False, 60)
        assert result == 1
        assert "PHASE2_CROSS_TARGET_REPLAY=fail" in output
        assert "invalid json in required file" in output
        checks_run += 1

        build_self_test_root(root)
        fake_zig = root / "fake-zig"
        log_path = root / "fake-zig.log"
        if log_path.exists():
            log_path.unlink()
        build_fake_zig(fake_zig, log_path)
        result, output = capture_stdout(run_checked, root, str(fake_zig), "x86_64-linux", True, 60)
        assert result == 1
        assert "PHASE2_CROSS_TARGET_REPLAY=fail" in output
        assert "--target and --all-targets are mutually exclusive" in output
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

    zig = resolve_zig(args.zig)
    return run_checked(root, zig, args.target, args.all_targets, args.timeout_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
