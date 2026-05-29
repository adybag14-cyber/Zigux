#!/usr/bin/env python3
"""Fail-close the Phase 3 ABI manifest replay-route packet."""

from __future__ import annotations

import argparse
import ast
import json
import tempfile
from pathlib import Path

VALIDATOR_PATH = Path("scripts/zigux/validate-phase3.py")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
CURRENT_NEXT_SAFE_STEP = (
    "keep the shared Phase 3 policy, export/UAPI, low-level wrapper packet, "
    "and retired generated-packet guard aligned with the dedicated replay routes "
    "and only reopen this manifest if the checker, focused builds, or reminder "
    "surfaces drift again"
)
RETIRED_DUMP = "zigux/tests/phase3_abi_dump.zig"
RETIRED_EXPECTED = "zigux/tests/fixtures/phase3_abi/expected.json"
CURRENT_DUMP = "zigux/tests/phase3_abi_dump_current.zig"
RETIRED_PATHS = [RETIRED_DUMP, RETIRED_EXPECTED]
RETIRED_GUARD_NOTE = (
    "These retired generated paths are historical markers only; the live "
    "export/UAPI-adjacent ABI packet must keep the dump_current replay as its "
    "only generated dump surface."
)
GENERATED_PACKET_NOTE = (
    "The live Phase 3 ABI evidence packet is the dump_current-era manifest "
    "replay; the older generated dump name and expected snapshot fixture are "
    "intentionally retired."
)
REQUIRED_FIELDS = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-abi-packet",
    "status": "shared_abi_and_header_family_binding_surface_present",
    "scope": (
        "shared ABI bindings, directly coupled helper decoding, header-family "
        "follow-through, notifier layouts, export-status layout, and "
        "header-compatibility replay"
    ),
    "next_safe_step": CURRENT_NEXT_SAFE_STEP,
}
SELFTEST_PACKET_FILES = (
    "Documentation/zigux/phase3-abi-slice.md",
    "scripts/zigux/validate-phase3.py",
    CURRENT_DUMP,
    "zigux/tests/fixtures/phase3_abi_manifest.json",
)
SELFTEST_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-abi.py --self-test",
    "python3 scripts/zigux/check-phase3-abi.py",
    "python3 scripts/zigux/validate-phase3.py --self-test",
    "python3 scripts/zigux/validate-phase3.py",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _duplicates(label: str, values: list[object], issues: list[str]) -> None:
    seen: dict[str, int] = {}
    for index, value in enumerate(values):
        key = repr(value)
        if key in seen:
            issues.append(
                f"{label} duplicate entry: {value!r} "
                f"(first index {seen[key]}, duplicate index {index})"
            )
        else:
            seen[key] = index


def _string_tuple(node: ast.AST) -> tuple[str, ...] | None:
    if not isinstance(node, (ast.Tuple, ast.List)):
        return None
    out: list[str] = []
    for element in node.elts:
        if not isinstance(element, ast.Constant) or not isinstance(element.value, str):
            return None
        out.append(element.value)
    return tuple(out)


def _validator_tuple(text: str, name: str, issues: list[str]) -> tuple[str, ...]:
    try:
        module = ast.parse(text, filename=VALIDATOR_PATH.as_posix())
    except SyntaxError as exc:
        issues.append(f"invalid Python in {VALIDATOR_PATH.as_posix()}: {exc}")
        return ()
    for statement in module.body:
        if not isinstance(statement, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == name for target in statement.targets):
            parsed = _string_tuple(statement.value)
            if parsed is not None:
                return parsed
            break
    issues.append(f"validate-phase3.py missing string-tuple constant: {name}")
    return ()


def _check_ordered(name: str, actual: object, expected: tuple[str, ...], issues: list[str]) -> list[object]:
    if not isinstance(actual, list):
        issues.append(f"phase3_abi_manifest.json {name} is not a list")
        return []
    _duplicates(f"phase3_abi_manifest.json {name}", actual, issues)
    singular = name[:-1]
    for entry in expected:
        if entry not in actual:
            issues.append(f"phase3_abi_manifest.json missing {singular} entry: {entry}")
    if tuple(actual) != expected:
        issues.append(
            f"phase3_abi_manifest.json {name} order drifted from "
            f"validate-phase3.py REQUIRED_MANIFEST_{name.upper()}"
        )
    return actual


def _check_generated_packet(manifest: dict[str, object], packet_files: list[object], replay_routes: list[object], issues: list[str]) -> None:
    packet = manifest.get("generated_packet")
    if not isinstance(packet, dict):
        issues.append("phase3_abi_manifest.json generated_packet is not an object")
        return
    expected_fields = {
        "current_dump": CURRENT_DUMP,
        "retired_dump": RETIRED_DUMP,
        "retired_expected_fixture": RETIRED_EXPECTED,
        "note": GENERATED_PACKET_NOTE,
    }
    for field, expected in expected_fields.items():
        actual = packet.get(field)
        if actual != expected:
            issues.append(f"phase3_abi_manifest.json generated_packet wrong {field}: {actual!r} != {expected!r}")
    guard = packet.get("retired_generated_guard")
    if not isinstance(guard, dict):
        issues.append("phase3_abi_manifest.json generated_packet.retired_generated_guard is not an object")
        return
    for field in ("must_stay_out_of_packet_files", "must_stay_out_of_replay_routes"):
        actual = guard.get(field)
        if actual != RETIRED_PATHS:
            issues.append(f"phase3_abi_manifest.json retired_generated_guard wrong {field}: {actual!r} != {RETIRED_PATHS!r}")
    if guard.get("note") != RETIRED_GUARD_NOTE:
        issues.append(f"phase3_abi_manifest.json retired_generated_guard wrong note: {guard.get('note')!r} != {RETIRED_GUARD_NOTE!r}")
    if CURRENT_DUMP not in packet_files:
        issues.append(f"phase3_abi_manifest.json packet_files missing live dump_current entry: {CURRENT_DUMP}")
    for retired_path in RETIRED_PATHS:
        if retired_path in packet_files:
            issues.append(f"phase3_abi_manifest.json packet_files includes retired generated entry: {retired_path}")
        if retired_path in replay_routes:
            issues.append(f"phase3_abi_manifest.json replay_routes includes retired generated entry: {retired_path}")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    validator_path = repo_root / VALIDATOR_PATH
    manifest_path = repo_root / MANIFEST_PATH
    if not validator_path.is_file():
        return [f"missing repo file: {VALIDATOR_PATH.as_posix()}"]
    if not manifest_path.is_file():
        return [f"missing repo file: {MANIFEST_PATH.as_posix()}"]
    validator_text = _read(validator_path)
    expected_packet_files = _validator_tuple(validator_text, "REQUIRED_MANIFEST_PACKET_FILES", issues)
    expected_replay_routes = _validator_tuple(validator_text, "REQUIRED_MANIFEST_REPLAY_ROUTES", issues)
    try:
        manifest = json.loads(_read(manifest_path))
    except json.JSONDecodeError as exc:
        return [f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}"]
    if not isinstance(manifest, dict):
        return ["phase3_abi_manifest.json root is not an object"]
    for field, expected in REQUIRED_FIELDS.items():
        actual = manifest.get(field)
        if actual != expected:
            issues.append(f"phase3_abi_manifest.json wrong {field}: {actual!r} != {expected!r}")
    packet_files = _check_ordered("packet_files", manifest.get("packet_files"), expected_packet_files, issues)
    replay_routes = _check_ordered("replay_routes", manifest.get("replay_routes"), expected_replay_routes, issues)
    gaps = manifest.get("repo_reality_gaps")
    if not isinstance(gaps, list):
        issues.append("phase3_abi_manifest.json repo_reality_gaps is not a list")
    elif gaps:
        issues.append("phase3_abi_manifest.json repo_reality_gaps drifted from the current shared packet expectation")
    _check_generated_packet(manifest, packet_files, replay_routes, issues)
    return issues


def _sample_validator() -> str:
    body = ["#!/usr/bin/env python3", "REQUIRED_MANIFEST_PACKET_FILES = ("]
    body.extend(f"    {entry!r}," for entry in SELFTEST_PACKET_FILES)
    body.extend([")", "", "REQUIRED_MANIFEST_REPLAY_ROUTES = ("])
    body.extend(f"    {route!r}," for route in SELFTEST_REPLAY_ROUTES)
    body.extend([")", ""])
    return "\n".join(body)


def _sample_manifest() -> str:
    return json.dumps({
        "phase": "Phase 3",
        "lane": "abi-runtime",
        "slug": "phase3-abi-packet",
        "status": REQUIRED_FIELDS["status"],
        "scope": REQUIRED_FIELDS["scope"],
        "generated_packet": {
            "current_dump": CURRENT_DUMP,
            "retired_dump": RETIRED_DUMP,
            "retired_expected_fixture": RETIRED_EXPECTED,
            "retired_generated_guard": {
                "must_stay_out_of_packet_files": RETIRED_PATHS,
                "must_stay_out_of_replay_routes": RETIRED_PATHS,
                "note": RETIRED_GUARD_NOTE,
            },
            "note": GENERATED_PACKET_NOTE,
        },
        "packet_files": list(SELFTEST_PACKET_FILES),
        "replay_routes": list(SELFTEST_REPLAY_ROUTES),
        "repo_reality_gaps": [],
        "next_safe_step": CURRENT_NEXT_SAFE_STEP,
    }, indent=2) + "\n"


def _populate(root: Path) -> None:
    _write(root / VALIDATOR_PATH, _sample_validator())
    _write(root / MANIFEST_PATH, _sample_manifest())


def _require(issues: list[str], expected: str) -> None:
    if expected not in issues:
        print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
        print(f"missing expected issue: {expected}")
        print("\n".join(issues))
        raise SystemExit(1)


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_manifest_routes_") as temp_dir:
        root = Path(temp_dir)
        validator = root / VALIDATOR_PATH
        manifest_path = root / MANIFEST_PATH
        _populate(root)
        issues = validate_repo(root)
        if issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        checks = [
            (lambda m: m["packet_files"].remove(SELFTEST_PACKET_FILES[0]), f"phase3_abi_manifest.json missing packet_file entry: {SELFTEST_PACKET_FILES[0]}"),
            (lambda m: m["replay_routes"].remove(SELFTEST_REPLAY_ROUTES[0]), f"phase3_abi_manifest.json missing replay_route entry: {SELFTEST_REPLAY_ROUTES[0]}"),
            (lambda m: m.update(next_safe_step="stale"), "phase3_abi_manifest.json wrong next_safe_step: 'stale' != " + repr(CURRENT_NEXT_SAFE_STEP)),
            (lambda m: m.update(repo_reality_gaps=["stale"]), "phase3_abi_manifest.json repo_reality_gaps drifted from the current shared packet expectation"),
            (lambda m: m["generated_packet"].update(current_dump=RETIRED_DUMP), f"phase3_abi_manifest.json generated_packet wrong current_dump: {RETIRED_DUMP!r} != {CURRENT_DUMP!r}"),
            (lambda m: m["generated_packet"]["retired_generated_guard"].update(must_stay_out_of_packet_files=[]), f"phase3_abi_manifest.json retired_generated_guard wrong must_stay_out_of_packet_files: [] != {RETIRED_PATHS!r}"),
            (lambda m: m["packet_files"].append(RETIRED_DUMP), f"phase3_abi_manifest.json packet_files includes retired generated entry: {RETIRED_DUMP}"),
            (lambda m: m["replay_routes"].append(RETIRED_EXPECTED), f"phase3_abi_manifest.json replay_routes includes retired generated entry: {RETIRED_EXPECTED}"),
        ]
        for mutate, expected in checks:
            _populate(root)
            manifest = json.loads(_read(manifest_path))
            mutate(manifest)
            _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
            _require(validate_repo(root), expected)
            cases += 1
        _populate(root)
        manifest = json.loads(_read(manifest_path))
        manifest["packet_files"][0], manifest["packet_files"][1] = manifest["packet_files"][1], manifest["packet_files"][0]
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        _require(validate_repo(root), "phase3_abi_manifest.json packet_files order drifted from validate-phase3.py REQUIRED_MANIFEST_PACKET_FILES")
        cases += 1
        _populate(root)
        manifest = json.loads(_read(manifest_path))
        manifest["replay_routes"].append(manifest["replay_routes"][-1])
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expected = f"phase3_abi_manifest.json replay_routes duplicate entry: {SELFTEST_REPLAY_ROUTES[-1]!r} (first index 3, duplicate index 4)"
        _require(validate_repo(root), expected)
        cases += 1
        _populate(root)
        _write(validator, _sample_validator().replace("REQUIRED_MANIFEST_PACKET_FILES = (", "REQUIRED_MANIFEST_PACKET_FILES = {", 1))
        _require(validate_repo(root), "invalid Python in scripts/zigux/validate-phase3.py: closing parenthesis ')' does not match opening parenthesis '{' on line 2 (validate-phase3.py, line 7)")
        cases += 1
    print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=pass")
    print(f"PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Phase 3 ABI manifest's shared replay routes.")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="repository root")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES=fail")
        print("\n".join(issues))
        return 1
    print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
