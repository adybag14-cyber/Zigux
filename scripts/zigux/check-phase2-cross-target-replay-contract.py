#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import contextlib
import io
import json
import tempfile
from pathlib import Path, PurePosixPath

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent
HELPER = Path("scripts") / "zigux" / "check-phase2-cross-target-replay.py"
FIXTURE = Path("zigux") / "tests" / "fixtures" / "phase2_cross_targets.json"
POLICY = Path("scripts") / "zigux" / "zig-toolchain-policy.json"
EXPECTED_ZIG_TEST_FILES = (
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
)
REQUIRED_CONSTANTS = (
    "FIXTURE",
    "POLICY",
    "EXPECTED_PHASE",
    "EXPECTED_STATUS",
    "EXPECTED_ROUTE",
    "EXPECTED_TARGET_ORDER",
    "EXPECTED_REQUIRED_MAKE_ROUTE",
    "ALLOWED_VALIDATION_MODES",
    "ZIG_TEST_FILES",
)


class DuplicateJsonKeyError(ValueError):
    pass


def reject_duplicate_object_pairs(pairs: list[tuple[object, object]]) -> dict[object, object]:
    payload: dict[object, object] = {}
    for key, value in pairs:
        if key in payload:
            raise DuplicateJsonKeyError(str(key))
        payload[key] = value
    return payload


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


def normalize_pathish(value: object) -> str:
    if isinstance(value, PurePosixPath):
        return value.as_posix()
    if isinstance(value, str):
        return value
    raise TypeError(f"unsupported pathish value: {value!r}")


def normalize_string_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise TypeError(f"expected tuple, got {type(value).__name__}")
    normalized: list[str] = []
    for entry in value:
        if not isinstance(entry, str):
            raise TypeError(f"expected tuple[str], got {type(entry).__name__}")
        normalized.append(entry)
    return tuple(normalized)


def eval_assignment(node: ast.AST) -> object:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Tuple):
        return tuple(eval_assignment(element) for element in node.elts)
    if isinstance(node, ast.List):
        return [eval_assignment(element) for element in node.elts]
    if isinstance(node, ast.Set):
        return {eval_assignment(element) for element in node.elts}
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == "Path" and len(node.args) == 1:
            argument = eval_assignment(node.args[0])
            if not isinstance(argument, str):
                raise TypeError("Path() expects a string literal")
            return PurePosixPath(argument)
        if isinstance(node.func, ast.Name) and node.func.id == "frozenset" and len(node.args) == 1:
            value = eval_assignment(node.args[0])
            if not isinstance(value, (list, tuple, set)):
                raise TypeError("frozenset() expects a literal sequence")
            return frozenset(value)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = normalize_pathish(eval_assignment(node.left))
        right = normalize_pathish(eval_assignment(node.right))
        return PurePosixPath(left) / right
    raise TypeError(f"unsupported literal expression: {ast.dump(node, include_attributes=False)}")


def load_helper_contract(root: Path, helper_relative: Path) -> dict[str, object]:
    helper_path = root / helper_relative
    module = ast.parse(read_text(helper_path), filename=str(helper_path))
    values: dict[str, object] = {}
    for statement in module.body:
        if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
            continue
        target = statement.targets[0]
        if not isinstance(target, ast.Name):
            continue
        if target.id not in REQUIRED_CONSTANTS:
            continue
        values[target.id] = eval_assignment(statement.value)

    missing = sorted(set(REQUIRED_CONSTANTS) - set(values))
    if missing:
        raise SystemExit(f"helper contract is missing required assignments: {', '.join(missing)}")
    return values


def collect_contract_issues(root: Path, helper_relative: Path) -> list[str]:
    helper_path = root / helper_relative
    helper_contract = load_helper_contract(root, helper_relative)
    fixture_path = root / FIXTURE
    policy_path = root / POLICY

    issues: list[str] = []
    if normalize_pathish(helper_contract["FIXTURE"]) != FIXTURE.as_posix():
        issues.append(
            f"helper:fixture_path:{normalize_pathish(helper_contract['FIXTURE'])!r}"
        )
    if normalize_pathish(helper_contract["POLICY"]) != POLICY.as_posix():
        issues.append(
            f"helper:policy_path:{normalize_pathish(helper_contract['POLICY'])!r}"
        )

    helper_zig_files = tuple(normalize_pathish(path) for path in helper_contract["ZIG_TEST_FILES"])
    if helper_zig_files != EXPECTED_ZIG_TEST_FILES:
        issues.append(f"helper:zig_test_files:{helper_zig_files!r}")

    for path_text in helper_zig_files:
        if not (root / path_text).is_file():
            issues.append(f"helper:missing_referenced_zig_file:{path_text}")

    fixture_payload = load_json(fixture_path)
    if not isinstance(fixture_payload, dict):
        return [f"fixture:shape:{type(fixture_payload).__name__}"]

    cross_targets = fixture_payload.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        return [f"fixture:cross_targets:{cross_targets!r}"]

    actual_targets: list[str] = []
    actual_validation_modes: list[str] = []
    seen_modes: set[str] = set()
    archive_required_targets: list[str] = []
    for index, entry in enumerate(cross_targets):
        if not isinstance(entry, dict):
            issues.append(f"fixture:cross_target_entry:{index}:{type(entry).__name__}")
            continue
        target = entry.get("target")
        validation_mode = entry.get("validation_mode")
        if not isinstance(target, str):
            issues.append(f"fixture:target:{index}:{target!r}")
        else:
            actual_targets.append(target)
        if not isinstance(validation_mode, str):
            issues.append(f"fixture:validation_mode:{index}:{validation_mode!r}")
        else:
            if validation_mode not in seen_modes:
                seen_modes.add(validation_mode)
                actual_validation_modes.append(validation_mode)
            if validation_mode == "archive_required" and isinstance(target, str):
                archive_required_targets.append(target)

    if helper_contract["EXPECTED_PHASE"] != fixture_payload.get("phase"):
        issues.append(f"helper:expected_phase:{helper_contract['EXPECTED_PHASE']!r}")
    if helper_contract["EXPECTED_STATUS"] != fixture_payload.get("status"):
        issues.append(f"helper:expected_status:{helper_contract['EXPECTED_STATUS']!r}")
    if helper_contract["EXPECTED_ROUTE"] != fixture_payload.get("route"):
        issues.append(f"helper:expected_route:{helper_contract['EXPECTED_ROUTE']!r}")

    helper_targets = normalize_string_tuple(helper_contract["EXPECTED_TARGET_ORDER"])
    if helper_targets != tuple(actual_targets):
        issues.append(f"helper:expected_target_order:{helper_targets!r}")

    helper_modes = normalize_string_tuple(helper_contract["ALLOWED_VALIDATION_MODES"])
    if helper_modes != tuple(actual_validation_modes):
        issues.append(f"helper:allowed_validation_modes:{helper_modes!r}")

    policy_payload = load_json(policy_path)
    if not isinstance(policy_payload, dict):
        return [f"policy:shape:{type(policy_payload).__name__}"]

    upgrade_policy = policy_payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        return [f"policy:upgrade_policy:{type(upgrade_policy).__name__}"]

    archive_target_scope = upgrade_policy.get("archive_target_scope")
    required_make_routes = upgrade_policy.get("required_make_routes")
    if not isinstance(archive_target_scope, list):
        issues.append(f"policy:archive_target_scope:{archive_target_scope!r}")
    else:
        normalized_scope = tuple(value for value in archive_target_scope if isinstance(value, str))
        if tuple(archive_required_targets) != normalized_scope:
            issues.append(f"helper:archive_target_scope:{tuple(archive_required_targets)!r}")

    if not isinstance(required_make_routes, list):
        issues.append(f"policy:required_make_routes:{required_make_routes!r}")
    else:
        required_route = helper_contract["EXPECTED_REQUIRED_MAKE_ROUTE"]
        if required_route not in required_make_routes:
            issues.append(f"helper:missing_required_make_route:{required_route}")

    if not helper_path.is_file():
        issues.append(f"helper:missing_helper_file:{helper_relative.as_posix()}")

    return issues


def emit_summary(helper_relative: Path) -> None:
    print("PHASE2_CROSS_TARGET_REPLAY_CONTRACT=pass")
    print(f"PHASE2_CROSS_TARGET_REPLAY_CONTRACT_HELPER={helper_relative.as_posix()}")


def run_checked(root: Path, helper_relative: Path) -> int:
    try:
        issues = collect_contract_issues(root, helper_relative)
    except SystemExit as exc:
        print("PHASE2_CROSS_TARGET_REPLAY_CONTRACT=fail")
        print(f"PHASE2_CROSS_TARGET_REPLAY_CONTRACT_NOTE={exc}")
        return 1

    if issues:
        print("PHASE2_CROSS_TARGET_REPLAY_CONTRACT=fail")
        for issue in issues:
            print(issue)
        return 1

    emit_summary(helper_relative)
    return 0


def build_helper_source(
    *,
    fixture_path: str = FIXTURE.as_posix(),
    policy_path: str = POLICY.as_posix(),
    phase: str = "Phase 2",
    status: str = "active",
    route: str = "make -C zigux phase2-cross",
    target_order: tuple[str, ...] = ("x86_64-linux", "aarch64-linux"),
    required_route: str = "phase2-cross",
    validation_modes: tuple[str, ...] = ("archive_required", "route_contract_only"),
    zig_test_files: tuple[str, ...] = EXPECTED_ZIG_TEST_FILES,
) -> str:
    zig_file_lines = ",\n".join(
        f'    Path("{path.split("/", 1)[0]}") / "{path.split("/", 1)[1]}"'
        for path in zig_test_files
    )
    if len(zig_test_files) == 1:
        zig_file_lines += ","

    target_lines = ", ".join(repr(value) for value in target_order)
    if len(target_order) == 1:
        target_lines += ","

    mode_lines = ", ".join(repr(value) for value in validation_modes)
    if len(validation_modes) == 1:
        mode_lines += ","
    return "\n".join(
        (
            "#!/usr/bin/env python3",
            "from pathlib import Path",
            f'FIXTURE = Path("{fixture_path.split("/", 1)[0]}") / "{fixture_path.split("/", 1)[1]}"',
            f'POLICY = Path("{policy_path.split("/", 1)[0]}") / "{policy_path.split("/", 1)[1]}"',
            f"EXPECTED_PHASE = {phase!r}",
            f"EXPECTED_STATUS = {status!r}",
            f"EXPECTED_ROUTE = {route!r}",
            f"EXPECTED_TARGET_ORDER = ({target_lines})",
            f"EXPECTED_REQUIRED_MAKE_ROUTE = {required_route!r}",
            f"ALLOWED_VALIDATION_MODES = ({mode_lines})",
            "ZIG_TEST_FILES = (",
            zig_file_lines,
            ")",
            "",
        )
    )


def build_fixture_payload() -> dict[str, object]:
    return {
        "phase": "Phase 2",
        "status": "active",
        "route": "make -C zigux phase2-cross",
        "archive_target_scope": ["x86_64-linux"],
        "cross_targets": [
            {
                "target": "x86_64-linux",
                "review_status": "pinned bootstrap archive",
                "validation_mode": "archive_required",
                "route": "make -C zigux phase2-cross",
            },
            {
                "target": "aarch64-linux",
                "review_status": "route contract only",
                "validation_mode": "route_contract_only",
                "route": "make -C zigux phase2-cross",
            },
        ],
    }


def build_policy_payload() -> dict[str, object]:
    return {
        "phase": "Phase 2",
        "channel": "0.17.0-dev.87+9b177a7d2",
        "minimum_version": "0.17.0-dev.87+9b177a7d2",
        "archive_sha256": {"x86_64-linux": "3" * 64},
        "upgrade_policy": {
            "channel_minimum_lockstep": True,
            "archive_target_scope": ["x86_64-linux"],
            "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],
        },
    }


def build_self_test_root(root: Path, helper_source: str | None = None) -> None:
    write_text(root / HELPER, helper_source or build_helper_source())
    write_text(root / FIXTURE, json.dumps(build_fixture_payload(), indent=2) + "\n")
    write_text(root / POLICY, json.dumps(build_policy_payload(), indent=2) + "\n")
    for path_text in EXPECTED_ZIG_TEST_FILES:
        write_text(root / path_text, "test {\n    try @import(\"std\").testing.expect(true);\n}\n")


def capture_stdout(callable_obj, *args) -> tuple[int, str]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        result = callable_obj(*args)
    return result, buffer.getvalue()


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_target_replay_contract_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        result, output = capture_stdout(run_checked, root, HELPER)
        assert result == 0
        assert "PHASE2_CROSS_TARGET_REPLAY_CONTRACT=pass" in output
        checks_run += 1

        build_self_test_root(root, build_helper_source(phase="Phase X"))
        result, output = capture_stdout(run_checked, root, HELPER)
        assert result == 1
        assert "helper:expected_phase:'Phase X'" in output
        checks_run += 1

        build_self_test_root(root, build_helper_source(status="paused"))
        result, output = capture_stdout(run_checked, root, HELPER)
        assert result == 1
        assert "helper:expected_status:'paused'" in output
        checks_run += 1

        build_self_test_root(root, build_helper_source(route="make -C zigux phase2"))
        result, output = capture_stdout(run_checked, root, HELPER)
        assert result == 1
        assert "helper:expected_route:'make -C zigux phase2'" in output
        checks_run += 1

        build_self_test_root(root, build_helper_source(target_order=("aarch64-linux", "x86_64-linux")))
        result, output = capture_stdout(run_checked, root, HELPER)
        assert result == 1
        assert "helper:expected_target_order:('aarch64-linux', 'x86_64-linux')" in output
        checks_run += 1

        build_self_test_root(root, build_helper_source(validation_modes=("route_contract_only", "archive_required")))
        result, output = capture_stdout(run_checked, root, HELPER)
        assert result == 1
        assert "helper:allowed_validation_modes:('route_contract_only', 'archive_required')" in output
        checks_run += 1

        build_self_test_root(root, build_helper_source(required_route="phase2"))
        result, output = capture_stdout(run_checked, root, HELPER)
        assert result == 1
        assert "helper:missing_required_make_route:phase2" in output
        checks_run += 1

        build_self_test_root(root)
        (root / EXPECTED_ZIG_TEST_FILES[0]).unlink()
        result, output = capture_stdout(run_checked, root, HELPER)
        assert result == 1
        assert f"helper:missing_referenced_zig_file:{EXPECTED_ZIG_TEST_FILES[0]}" in output
        checks_run += 1

        build_self_test_root(root, build_helper_source(zig_test_files=("scripts/zigux/kconfig/conf_bridge.zig",)))
        result, output = capture_stdout(run_checked, root, HELPER)
        assert result == 1
        assert "helper:zig_test_files:('scripts/zigux/kconfig/conf_bridge.zig',)" in output
        checks_run += 1

        build_self_test_root(root)
        policy_payload = build_policy_payload()
        policy_payload["upgrade_policy"]["archive_target_scope"] = ["aarch64-linux"]
        write_text(root / POLICY, json.dumps(policy_payload, indent=2) + "\n")
        result, output = capture_stdout(run_checked, root, HELPER)
        assert result == 1
        assert "helper:archive_target_scope:('x86_64-linux',)" in output
        checks_run += 1

        build_self_test_root(root)
        (root / HELPER).write_text("#!/usr/bin/env python3\n", encoding="utf-8")
        result, output = capture_stdout(run_checked, root, HELPER)
        assert result == 1
        assert "helper contract is missing required assignments" in output
        checks_run += 1

        build_self_test_root(root)
        (root / FIXTURE).write_text("{\n", encoding="utf-8")
        result, output = capture_stdout(run_checked, root, HELPER)
        assert result == 1
        assert "invalid json in required file" in output
        checks_run += 1

    print("PHASE2_CROSS_TARGET_REPLAY_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_TARGET_REPLAY_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the replay helper's hard-coded Phase 2 cross-target contract still matches the live fixture and policy surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--helper-path",
        type=Path,
        default=HELPER,
        help="Relative path to the replay helper to inspect",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    return run_checked(args.root.resolve(), args.helper_path)


if __name__ == "__main__":
    raise SystemExit(main())
