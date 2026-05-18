#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
FIXTURE_PATH = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
POLICY_PATH = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
MAKEFILE_PATH = ROOT / "zigux" / "Makefile"
ALIGNMENT_CHECKER_PATH = ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"

EXPECTED_PHASE = "Phase 2"
EXPECTED_STATUS = "seeded"
EXPECTED_SCOPE = "bounded direct-cross target matrix for the phase2-cross route"
EXPECTED_TARGETS = [
    {
        "zig_target": "x86_64-linux",
        "coverage": "pinned-archive-bootstrap",
        "route": "phase2-toolchain",
        "notes": "current bootstrap archive target pinned by scripts/zigux/zig-toolchain-policy.json",
    },
    {
        "zig_target": "aarch64-linux",
        "coverage": "direct-cross-route-planned",
        "route": "phase2-cross",
        "notes": "bounded direct-cross target row pending workflow and make-route integration",
    },
    {
        "zig_target": "riscv64-linux",
        "coverage": "direct-cross-route-planned",
        "route": "phase2-cross",
        "notes": "bounded direct-cross target row pending workflow and make-route integration",
    },
]
EXPECTED_NOTES = [
    "The direct phase2-cross checker is now materialized as a fixture-backed packet even though current master still keeps the shared route itself aligned through scripts/zigux/check-phase2-cross-selftest-alignment.py.",
    "Keep the pinned x86_64-linux archive row anchored to scripts/zigux/zig-toolchain-policy.json so the direct-cross matrix does not drift away from the live toolchain packet.",
    "Treat aarch64-linux and riscv64-linux as bounded planned rows until the workflow and make-wrapper packet explicitly replays this checker on current master.",
]
MAKEFILE_MARKERS = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def load_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in {path}: {exc.msg}") from exc


def collect_fixture_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    fixture_path = resolve_path(root, FIXTURE_PATH)
    payload = load_json(fixture_path)
    if not isinstance(payload, dict):
        return [("INVALID_FIXTURE_PAYLOAD", type(payload).__name__)]

    if payload.get("phase") != EXPECTED_PHASE:
        issues.append(("FIXTURE_FIELD_MISMATCH", f"phase:actual={payload.get('phase')!r}:expected={EXPECTED_PHASE!r}"))
    if payload.get("status") != EXPECTED_STATUS:
        issues.append(("FIXTURE_FIELD_MISMATCH", f"status:actual={payload.get('status')!r}:expected={EXPECTED_STATUS!r}"))
    if payload.get("scope") != EXPECTED_SCOPE:
        issues.append(("FIXTURE_FIELD_MISMATCH", f"scope:actual={payload.get('scope')!r}:expected={EXPECTED_SCOPE!r}"))
    if payload.get("targets") != EXPECTED_TARGETS:
        issues.append(("FIXTURE_TARGETS_MISMATCH", f"actual={payload.get('targets')!r}:expected={EXPECTED_TARGETS!r}"))
    if payload.get("notes") != EXPECTED_NOTES:
        issues.append(("FIXTURE_NOTES_MISMATCH", f"actual={payload.get('notes')!r}:expected={EXPECTED_NOTES!r}"))
    return issues


def collect_policy_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    payload = load_json(resolve_path(root, POLICY_PATH))
    if not isinstance(payload, dict):
        return [("INVALID_POLICY_PAYLOAD", type(payload).__name__)]

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        return [("INVALID_UPGRADE_POLICY", type(upgrade_policy).__name__)]

    archive_target_scope = upgrade_policy.get("archive_target_scope")
    expected_scope = [EXPECTED_TARGETS[0]["zig_target"]]
    if archive_target_scope != expected_scope:
        issues.append(("POLICY_ARCHIVE_TARGET_SCOPE_MISMATCH", f"actual={archive_target_scope!r}:expected={expected_scope!r}"))
    return issues


def collect_makefile_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    makefile_text = read_text(resolve_path(root, MAKEFILE_PATH))
    for marker in MAKEFILE_MARKERS:
        if marker not in makefile_text:
            issues.append(("MISSING_MAKEFILE_MARKERS", marker))
    return issues


def collect_required_path_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for path in (FIXTURE_PATH, POLICY_PATH, MAKEFILE_PATH, ALIGNMENT_CHECKER_PATH):
        if not resolve_path(root, path).exists():
            issues.append(("MISSING_REQUIRED_PATH", path.relative_to(ROOT).as_posix()))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(collect_required_path_issues(root))
    if issues:
        return issues
    issues.extend(collect_fixture_issues(root))
    issues.extend(collect_policy_issues(root))
    issues.extend(collect_makefile_issues(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(
        resolve_path(root, FIXTURE_PATH),
        json.dumps(
            {
                "phase": EXPECTED_PHASE,
                "status": EXPECTED_STATUS,
                "scope": EXPECTED_SCOPE,
                "targets": EXPECTED_TARGETS,
                "notes": EXPECTED_NOTES,
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve_path(root, POLICY_PATH),
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
        resolve_path(root, MAKEFILE_PATH),
        "\n".join(
            (
                "phase2-cross:",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
            )
        )
        + "\n",
    )
    write_text(resolve_path(root, ALIGNMENT_CHECKER_PATH), "present\n")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 13
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        fixture_path = resolve_path(root, FIXTURE_PATH)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["phase"] = "Phase 3"
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "FIXTURE_FIELD_MISMATCH" and value.startswith("phase:") for code, value in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        fixture_path = resolve_path(root, FIXTURE_PATH)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["status"] = "active"
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "FIXTURE_FIELD_MISMATCH" and value.startswith("status:") for code, value in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        fixture_path = resolve_path(root, FIXTURE_PATH)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["scope"] = "broadened matrix"
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "FIXTURE_FIELD_MISMATCH" and value.startswith("scope:") for code, value in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        fixture_path = resolve_path(root, FIXTURE_PATH)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["targets"] = payload["targets"][:-1]
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "FIXTURE_TARGETS_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        fixture_path = resolve_path(root, FIXTURE_PATH)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["notes"] = []
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "FIXTURE_NOTES_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        policy_path = resolve_path(root, POLICY_PATH)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["aarch64-linux"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "POLICY_ARCHIVE_TARGET_SCOPE_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        for marker in MAKEFILE_MARKERS:
            build_self_test_root(root)
            makefile_path = resolve_path(root, MAKEFILE_PATH)
            makefile_path.write_text(makefile_path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert ("MISSING_MAKEFILE_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for path in (FIXTURE_PATH, POLICY_PATH, MAKEFILE_PATH, ALIGNMENT_CHECKER_PATH):
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            assert ("MISSING_REQUIRED_PATH", path.relative_to(ROOT).as_posix()) in collect_issues(root)
            checks_run += 1

    assert checks_run == expected_case_count
    print("PHASE2_CROSS_SELF_TEST=pass")
    print(f"PHASE2_CROSS_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the bounded direct-cross Phase 2 target matrix packet.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS=pass")
    print(f"PHASE2_CROSS_TARGET_COUNT={len(EXPECTED_TARGETS)}")
    print(f"PHASE2_CROSS_NOTE_COUNT={len(EXPECTED_NOTES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
