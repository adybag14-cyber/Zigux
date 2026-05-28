#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"

REQUIRED_PATHS = (
    ROOT / "scripts" / "zigux" / "check-zig-toolchain.py",
    ROOT / "scripts" / "zigux" / "install-zig.py",
    ROOT / "scripts" / "zigux" / "stage-pinned-zig-archive.py",
    ROOT / "scripts" / "zigux" / "check-lane05-local-first-archive-workflow.py",
    ROOT / "scripts" / "zigux" / "check-lane05-local-archive-readme.py",
    ROOT / "scripts" / "zigux" / "check-lane05-install-zig-archive-verification.py",
    ROOT / "scripts" / "zigux" / "check-lane05-stage-helper-contract.py",
    ROOT / "scripts" / "zigux" / "check-lane05-stage-helper-selftest.py",
    ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pinning.py",
    ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py",
    WORKFLOW,
    MAKEFILE,
    PHASE2_NOTES,
    SCRIPTS_README,
    TOOLCHAIN_POLICY,
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: make -C zigux phase2-toolchain",
)

MAKEFILE_LINES = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-archive-readme.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-archive-readme.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
)

PHASE2_NOTES_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-lane05-install-zig-archive-verification.py`",
    "`scripts/zigux/stage-pinned-zig-archive.py`",
    "`scripts/zigux/check-lane05-stage-helper-contract.py`",
    "`scripts/zigux/check-lane05-stage-helper-selftest.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`make -C zigux phase2-toolchain`",
)

SCRIPTS_README_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`",
    "`third_party/README.md`, `scripts/zigux/stage-pinned-zig-archive.py`, `python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py`",
    "`make -C zigux phase2-toolchain`",
)

EXPECTED_CHANNEL = "0.17.0-dev.87+9b177a7d2"
EXPECTED_TARGET_SCOPE = ("x86_64-linux",)
EXPECTED_REQUIRED_MAKE_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
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


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_exact_line_issues(
    text: str,
    markers: tuple[str, ...],
    missing_code: str,
    duplicate_code: str,
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def load_policy(root: Path) -> dict[str, object]:
    path = resolve_path(root, TOOLCHAIN_POLICY)
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid policy payload in required file: {path}")
    return payload


def collect_policy_issues(root: Path) -> list[tuple[str, str]]:
    payload = load_policy(root)
    issues: list[tuple[str, str]] = []
    channel = payload.get("channel")
    minimum_version = payload.get("minimum_version")
    if channel != EXPECTED_CHANNEL:
        issues.append(("INVALID_POLICY_FIELD", f"channel:{channel!r}"))
    if minimum_version != EXPECTED_CHANNEL:
        issues.append(("INVALID_POLICY_FIELD", f"minimum_version:{minimum_version!r}"))

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("INVALID_POLICY_FIELD", "upgrade_policy"))
        return issues

    if upgrade_policy.get("channel_minimum_lockstep") is not True:
        issues.append(("INVALID_POLICY_FIELD", "channel_minimum_lockstep"))

    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if archive_target_scope != list(EXPECTED_TARGET_SCOPE):
        issues.append(("INVALID_POLICY_FIELD", f"archive_target_scope:{archive_target_scope!r}"))

    required_make_routes = upgrade_policy.get("required_make_routes")
    if required_make_routes != list(EXPECTED_REQUIRED_MAKE_ROUTES):
        issues.append(("INVALID_POLICY_FIELD", f"required_make_routes:{required_make_routes!r}"))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for path in REQUIRED_PATHS:
        if not resolve_path(root, path).exists():
            issues.append(("MISSING_REQUIRED_PATH", path.relative_to(ROOT).as_posix()))

    if issues:
        return issues

    workflow_text = read_text(resolve_path(root, WORKFLOW))
    makefile_text = read_text(resolve_path(root, MAKEFILE))
    notes_text = read_text(resolve_path(root, PHASE2_NOTES))
    readme_text = read_text(resolve_path(root, SCRIPTS_README))

    issues.extend(
        collect_exact_line_issues(
            workflow_text,
            WORKFLOW_LINES,
            "MISSING_WORKFLOW_LINE",
            "DUPLICATE_WORKFLOW_LINE",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            makefile_text,
            MAKEFILE_LINES,
            "MISSING_MAKEFILE_LINE",
            "DUPLICATE_MAKEFILE_LINE",
        )
    )
    issues.extend(collect_missing_markers(notes_text, PHASE2_NOTES_MARKERS, "MISSING_PHASE2_NOTES_MARKER"))
    issues.extend(collect_missing_markers(readme_text, SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKER"))
    issues.extend(collect_policy_issues(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_TOOLCHAIN_SELFTEST_ALIGNMENT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    for path in REQUIRED_PATHS:
        if path in (WORKFLOW, MAKEFILE, PHASE2_NOTES, SCRIPTS_README, TOOLCHAIN_POLICY):
            continue
        write_text(resolve_path(root, path), "present\n")

    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    write_text(resolve_path(root, PHASE2_NOTES), "\n".join(PHASE2_NOTES_MARKERS) + "\n")
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(
        resolve_path(root, TOOLCHAIN_POLICY),
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": EXPECTED_CHANNEL,
                "minimum_version": EXPECTED_CHANNEL,
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": list(EXPECTED_TARGET_SCOPE),
                    "required_make_routes": list(EXPECTED_REQUIRED_MAKE_ROUTES),
                },
            },
            indent=2,
        )
        + "\n",
    )


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def remove_marker(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def run_self_test() -> int:
    checks = 0
    expected = (
        1
        + len(WORKFLOW_LINES)
        + len(WORKFLOW_LINES)
        + len(MAKEFILE_LINES)
        + len(PHASE2_NOTES_MARKERS)
        + len(SCRIPTS_README_MARKERS)
        + 4
        + len(REQUIRED_PATHS)
    )

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_selftest_alignment_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "run: python3 broken.py"),
                encoding="utf-8",
            )
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2") in collect_issues(root)
            checks += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "$(PYTHON) broken.py"),
                encoding="utf-8",
            )
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks += 1

        for marker in PHASE2_NOTES_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, PHASE2_NOTES)
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_PHASE2_NOTES_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in SCRIPTS_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, SCRIPTS_README)
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_SCRIPTS_README_MARKER", marker) in collect_issues(root)
            checks += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["channel"] = "0.17.0"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY_FIELD", "channel:'0.17.0'") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["aarch64-linux"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert (
            "INVALID_POLICY_FIELD",
            "archive_target_scope:['aarch64-linux']",
        ) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "INVALID_POLICY_FIELD" and value.startswith("required_make_routes:") for code, value in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["channel_minimum_lockstep"] = False
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY_FIELD", "channel_minimum_lockstep") in collect_issues(root)
        checks += 1

        for missing_path in REQUIRED_PATHS:
            build_self_test_root(root)
            resolve_path(root, missing_path).unlink()
            assert ("MISSING_REQUIRED_PATH", missing_path.relative_to(ROOT).as_posix()) in collect_issues(root)
            checks += 1

    assert checks == expected
    print("PHASE2_TOOLCHAIN_SELFTEST_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current Phase 2 toolchain self-test packet stays aligned across workflow, make-wrapper, and reminder surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLCHAIN_SELFTEST_ALIGNMENT=pass")
    print(f"PHASE2_TOOLCHAIN_SELFTEST_ALIGNMENT_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_TOOLCHAIN_SELFTEST_ALIGNMENT_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    print(f"PHASE2_TOOLCHAIN_SELFTEST_ALIGNMENT_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())