#!/usr/bin/env python3
"""Check that the Phase 3 ABI validator and manifest agree on the current step."""

from __future__ import annotations

import argparse
import ast
import json
import tempfile
from pathlib import Path

VALIDATOR_PATH = Path("scripts/zigux/validate-phase3.py")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
CURRENT_DUMP = "zigux/tests/phase3_abi_dump_current.zig"
RETIRED_DUMP = "zigux/tests/phase3_abi_dump.zig"
RETIRED_EXPECTED = "zigux/tests/fixtures/phase3_abi/expected.json"
RETIRED_PATHS = [RETIRED_DUMP, RETIRED_EXPECTED]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _literal_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _literal_string(node.left)
        right = _literal_string(node.right)
        if left is not None and right is not None:
            return left + right
    if isinstance(node, ast.Tuple):
        parts = [_literal_string(element) for element in node.elts]
        if all(part is not None for part in parts):
            return "".join(part or "" for part in parts)
    return None


def _validator_current_next_safe_step(text: str, issues: list[str]) -> str:
    try:
        module = ast.parse(text, filename=VALIDATOR_PATH.as_posix())
    except SyntaxError as exc:
        issues.append(f"invalid Python in {VALIDATOR_PATH.as_posix()}: {exc}")
        return ""
    for statement in module.body:
        if not isinstance(statement, ast.Assign):
            continue
        if any(
            isinstance(target, ast.Name) and target.id == "CURRENT_NEXT_SAFE_STEP"
            for target in statement.targets
        ):
            value = _literal_string(statement.value)
            if value is not None:
                return value
            issues.append("validate-phase3.py CURRENT_NEXT_SAFE_STEP is not a literal string")
            return ""
    issues.append("validate-phase3.py missing CURRENT_NEXT_SAFE_STEP")
    return ""


def _check_retired_generated_packet(manifest: dict[str, object], issues: list[str]) -> None:
    packet = manifest.get("generated_packet")
    if not isinstance(packet, dict):
        issues.append("phase3_abi_manifest.json generated_packet is not an object")
        return
    if packet.get("current_dump") != CURRENT_DUMP:
        issues.append(
            "phase3_abi_manifest.json generated_packet current_dump does not point at dump_current"
        )
    if packet.get("retired_dump") != RETIRED_DUMP:
        issues.append("phase3_abi_manifest.json generated_packet retired_dump drifted")
    if packet.get("retired_expected_fixture") != RETIRED_EXPECTED:
        issues.append("phase3_abi_manifest.json generated_packet retired_expected_fixture drifted")
    guard = packet.get("retired_generated_guard")
    if not isinstance(guard, dict):
        issues.append("phase3_abi_manifest.json retired_generated_guard is not an object")
        return
    for field in ("must_stay_out_of_packet_files", "must_stay_out_of_replay_routes"):
        if guard.get(field) != RETIRED_PATHS:
            issues.append(f"phase3_abi_manifest.json retired_generated_guard {field} drifted")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    validator_path = repo_root / VALIDATOR_PATH
    manifest_path = repo_root / MANIFEST_PATH
    if not validator_path.is_file():
        return [f"missing repo file: {VALIDATOR_PATH.as_posix()}"]
    if not manifest_path.is_file():
        return [f"missing repo file: {MANIFEST_PATH.as_posix()}"]
    validator_next = _validator_current_next_safe_step(_read(validator_path), issues)
    try:
        manifest = json.loads(_read(manifest_path))
    except json.JSONDecodeError as exc:
        return [f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}"]
    if not isinstance(manifest, dict):
        return ["phase3_abi_manifest.json root is not an object"]
    manifest_next = manifest.get("next_safe_step")
    if manifest_next != validator_next:
        issues.append(
            "phase3_abi_manifest.json next_safe_step does not match "
            "validate-phase3.py CURRENT_NEXT_SAFE_STEP"
        )
    if not isinstance(manifest_next, str) or "retired generated-packet guard" not in manifest_next:
        issues.append("phase3_abi_manifest.json next_safe_step omits retired generated-packet guard")
    if "retired generated-packet guard" not in validator_next:
        issues.append("validate-phase3.py CURRENT_NEXT_SAFE_STEP omits retired generated-packet guard")
    _check_retired_generated_packet(manifest, issues)
    return issues


def _sample_validator(next_step: str) -> str:
    return "CURRENT_NEXT_SAFE_STEP = (\n    " + repr(next_step) + "\n)\n"


def _sample_manifest(next_step: str) -> str:
    return json.dumps(
        {
            "next_safe_step": next_step,
            "generated_packet": {
                "current_dump": CURRENT_DUMP,
                "retired_dump": RETIRED_DUMP,
                "retired_expected_fixture": RETIRED_EXPECTED,
                "retired_generated_guard": {
                    "must_stay_out_of_packet_files": RETIRED_PATHS,
                    "must_stay_out_of_replay_routes": RETIRED_PATHS,
                },
            },
        },
        indent=2,
    ) + "\n"


def _populate(root: Path, validator_step: str, manifest_step: str) -> None:
    _write(root / VALIDATOR_PATH, _sample_validator(validator_step))
    _write(root / MANIFEST_PATH, _sample_manifest(manifest_step))


def run_self_test() -> int:
    current_step = (
        "keep the shared Phase 3 policy, export/UAPI, low-level wrapper packet, "
        "and retired generated-packet guard aligned with the dedicated replay routes "
        "and only reopen this manifest if the checker, focused builds, or reminder "
        "surfaces drift again"
    )
    stale_step = current_step.replace("and retired generated-packet guard ", "")
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_next_step_") as temp_dir:
        root = Path(temp_dir)
        _populate(root, current_step, current_step)
        issues = validate_repo(root)
        if issues:
            print("PHASE3_ABI_VALIDATOR_NEXT_STEP_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        _populate(root, stale_step, current_step)
        issues = validate_repo(root)
        expected = "validate-phase3.py CURRENT_NEXT_SAFE_STEP omits retired generated-packet guard"
        if expected not in issues:
            print("PHASE3_ABI_VALIDATOR_NEXT_STEP_SELF_TEST=fail")
            print("expected stale validator next-step issue was not reported")
            print("\n".join(issues))
            return 1

        _populate(root, current_step, stale_step)
        issues = validate_repo(root)
        expected = "phase3_abi_manifest.json next_safe_step omits retired generated-packet guard"
        if expected not in issues:
            print("PHASE3_ABI_VALIDATOR_NEXT_STEP_SELF_TEST=fail")
            print("expected stale manifest next-step issue was not reported")
            print("\n".join(issues))
            return 1

        _populate(root, current_step, current_step)
        manifest_path = root / MANIFEST_PATH
        manifest = json.loads(_read(manifest_path))
        manifest["generated_packet"]["retired_generated_guard"]["must_stay_out_of_packet_files"] = []
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = "phase3_abi_manifest.json retired_generated_guard must_stay_out_of_packet_files drifted"
        if expected not in issues:
            print("PHASE3_ABI_VALIDATOR_NEXT_STEP_SELF_TEST=fail")
            print("expected retired guard drift issue was not reported")
            print("\n".join(issues))
            return 1

    print("PHASE3_ABI_VALIDATOR_NEXT_STEP_SELF_TEST=pass")
    print("PHASE3_ABI_VALIDATOR_NEXT_STEP_SELF_TEST_CASES=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Phase 3 ABI validator/manifest current-step alignment."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = validate_repo(args.repo_root.resolve())
    if issues:
        print("PHASE3_ABI_VALIDATOR_NEXT_STEP=fail")
        print("\n".join(issues))
        return 1
    print("PHASE3_ABI_VALIDATOR_NEXT_STEP=pass")
    print("validated Phase 3 ABI validator and manifest current-step alignment")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
