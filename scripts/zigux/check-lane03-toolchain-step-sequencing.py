#!/usr/bin/env python3
"""Guard the current pinned-toolchain bootstrap step sequence."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"

EXPECTED_REQUIRED_MAKE_ROUTES = ["phase2-toolchain", "phase2-validate", "phase2-cross"]
EXPECTED_ARCHIVE_TARGET_SCOPE = ["x86_64-linux"]

WORKFLOW_SEQUENCE = (
    "      - name: Compile current scripts",
    "      - name: Self-test current Zig toolchain checker",
    "      - name: Check current Zig toolchain policy packet",
    "      - name: Check current pinned Zig archive packet",
    "      - name: Self-test current Lane 05 local-first archive checker",
    "      - name: Check current Lane 05 local-first archive packet",
    "      - name: Self-test current Lane 05 local archive README checker",
    "      - name: Check current Lane 05 local archive README packet",
    "      - name: Self-test current Lane 05 install-zig archive verification checker",
    "      - name: Check current Lane 05 install-zig archive verification packet",
    "      - name: Self-test current Zig installer helper",
    "      - name: Self-test current staged pinned Zig archive helper",
    "      - name: Self-test current Lane 05 stage helper contract checker",
    "      - name: Check current Lane 05 stage helper contract packet",
    "      - name: Self-test current Lane 05 stage helper selftest checker",
    "      - name: Check current Lane 05 stage helper selftest packet",
    "      - name: Self-test current Phase 2 toolchain pinning checker",
    "      - name: Check current Phase 2 toolchain pinning packet",
    "      - name: Self-test current Phase 2 toolchain pin-scope checker",
    "      - name: Check current Phase 2 toolchain pin-scope packet",
    "      - name: Run current Phase 2 toolchain make route",
    "      - name: Run current Phase 2 cross make route",
    "      - name: Run current Phase 2 validate make route",
)

MAKEFILE_SEQUENCE = (
    "phase2-toolchain:",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-archive-readme.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-archive-readme.py",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line == marker:
            if replacement:
                lines[index] = replacement
            else:
                del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line == marker)


def collect_sequence_issues(
    text: str,
    sequence: tuple[str, ...],
    missing_code: str,
    duplicate_code: str,
    order_code: str,
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    positions: list[int] = []
    lines = text.splitlines()

    for marker in sequence:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
            continue
        if count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
            continue
        positions.append(lines.index(marker))

    for index in range(1, len(positions)):
        if positions[index] <= positions[index - 1]:
            issues.append((order_code, f"{sequence[index - 1]} -> {sequence[index]}"))

    return issues


def collect_policy_issues(policy_path: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    try:
        payload = json.loads(read_text(policy_path))
    except json.JSONDecodeError as exc:
        return [("INVALID_TOOLCHAIN_POLICY_JSON", exc.msg)]

    if not isinstance(payload, dict):
        return [("INVALID_TOOLCHAIN_POLICY", "expected JSON object")]

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        return [("INVALID_TOOLCHAIN_POLICY", "upgrade_policy")]

    required_routes = upgrade_policy.get("required_make_routes")
    if required_routes != EXPECTED_REQUIRED_MAKE_ROUTES:
        issues.append(("INVALID_REQUIRED_MAKE_ROUTES", repr(required_routes)))

    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if archive_target_scope != EXPECTED_ARCHIVE_TARGET_SCOPE:
        issues.append(("INVALID_ARCHIVE_TARGET_SCOPE", repr(archive_target_scope)))

    if upgrade_policy.get("channel_minimum_lockstep") is not True:
        issues.append(("INVALID_CHANNEL_MINIMUM_LOCKSTEP", repr(upgrade_policy.get("channel_minimum_lockstep"))))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    makefile_text = read_text(resolve_path(root, MAKEFILE))
    policy_path = resolve_path(root, TOOLCHAIN_POLICY)

    issues: list[tuple[str, str]] = []
    issues.extend(
        collect_sequence_issues(
            workflow_text,
            WORKFLOW_SEQUENCE,
            "MISSING_WORKFLOW_SEQUENCE",
            "DUPLICATE_WORKFLOW_SEQUENCE",
            "MISORDERED_WORKFLOW_SEQUENCE",
        )
    )
    issues.extend(
        collect_sequence_issues(
            makefile_text,
            MAKEFILE_SEQUENCE,
            "MISSING_MAKEFILE_SEQUENCE",
            "DUPLICATE_MAKEFILE_SEQUENCE",
            "MISORDERED_MAKEFILE_SEQUENCE",
        )
    )
    issues.extend(collect_policy_issues(policy_path))
    return issues


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, WORKFLOW), "\n".join(("name: zigux-bootstrap", *WORKFLOW_SEQUENCE)) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_SEQUENCE) + "\n")
    write_text(
        resolve_path(root, TOOLCHAIN_POLICY),
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {
                    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
                },
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": EXPECTED_ARCHIVE_TARGET_SCOPE,
                    "required_make_routes": EXPECTED_REQUIRED_MAKE_ROUTES,
                },
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane03_toolchain_step_sequence_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in WORKFLOW_SEQUENCE:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_WORKFLOW_SEQUENCE", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_SEQUENCE:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_WORKFLOW_SEQUENCE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, WORKFLOW)
        workflow_text = path.read_text(encoding="utf-8")
        later = WORKFLOW_SEQUENCE[3]
        earlier = WORKFLOW_SEQUENCE[2]
        workflow_text = replace_exact_line(workflow_text, later)
        workflow_text = replace_exact_line(workflow_text, earlier)
        workflow_text += f"{later}\n{earlier}\n"
        path.write_text(workflow_text, encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISORDERED_WORKFLOW_SEQUENCE", f"{WORKFLOW_SEQUENCE[2]} -> {WORKFLOW_SEQUENCE[3]}") in issues
        checks_run += 1

        for marker in MAKEFILE_SEQUENCE:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_MAKEFILE_SEQUENCE", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_SEQUENCE:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_MAKEFILE_SEQUENCE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, MAKEFILE)
        makefile_text = path.read_text(encoding="utf-8")
        later = MAKEFILE_SEQUENCE[3]
        earlier = MAKEFILE_SEQUENCE[2]
        makefile_text = replace_exact_line(makefile_text, later)
        makefile_text = replace_exact_line(makefile_text, earlier)
        makefile_text += f"{later}\n{earlier}\n"
        path.write_text(makefile_text, encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISORDERED_MAKEFILE_SEQUENCE", f"{MAKEFILE_SEQUENCE[2]} -> {MAKEFILE_SEQUENCE[3]}") in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_REQUIRED_MAKE_ROUTES", "['phase2-toolchain']") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["aarch64-linux"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_ARCHIVE_TARGET_SCOPE", "['aarch64-linux']") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["channel_minimum_lockstep"] = False
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CHANNEL_MINIMUM_LOCKSTEP", "False") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        path.write_text("{not-json}\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(code == "INVALID_TOOLCHAIN_POLICY_JSON" for code, _ in issues)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        path.write_text("[]\n", encoding="utf-8")
        assert ("INVALID_TOOLCHAIN_POLICY", "expected JSON object") in collect_issues(root)
        checks_run += 1

        for path in (WORKFLOW, MAKEFILE, TOOLCHAIN_POLICY):
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {path}")

    print("LANE03_TOOLCHAIN_STEP_SEQUENCE_SELF_TEST=pass")
    print(f"LANE03_TOOLCHAIN_STEP_SEQUENCE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current pinned-toolchain bootstrap step packet stays ordered and unique."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        print("LANE03_TOOLCHAIN_STEP_SEQUENCE=fail")
        for code, value in issues:
            print(f"{code}:{value}")
        return 1

    print("LANE03_TOOLCHAIN_STEP_SEQUENCE=pass")
    print(f"LANE03_TOOLCHAIN_WORKFLOW_STEP_COUNT={len(WORKFLOW_SEQUENCE)}")
    print(f"LANE03_TOOLCHAIN_MAKEFILE_STEP_COUNT={len(MAKEFILE_SEQUENCE)}")
    print("LANE03_TOOLCHAIN_REQUIRED_MAKE_ROUTES=" + ",".join(EXPECTED_REQUIRED_MAKE_ROUTES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
