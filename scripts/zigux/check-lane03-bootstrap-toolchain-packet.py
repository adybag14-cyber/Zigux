#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"
README = "scripts/zigux/README.md"
POLICY = "scripts/zigux/zig-toolchain-policy.json"

REQUIRED_PATHS = (
    WORKFLOW,
    MAKEFILE,
    README,
    POLICY,
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/validate-bootstrap.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
)

README_MARKERS = (
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-validate",
    "make -C zigux phase2-cross",
)

WORKFLOW_EXACT_LINES = (
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
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-cross",
    "run: python3 scripts/zigux/validate-bootstrap.py --self-test",
    "run: python3 scripts/zigux/validate-bootstrap.py",
    "run: make -C zigux phase2-validate",
)

WORKFLOW_FRAGMENT_MARKERS = (
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
    'python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"',
    "failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org",
)

MAKEFILE_MARKERS = (
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
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
)


def read_text(root: Path, rel: str) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


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


def load_policy(root: Path) -> dict[str, object]:
    path = root / POLICY
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid policy JSON: {path}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid policy payload: {path}")
    return payload


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    readme = read_text(root, README)
    workflow = read_text(root, WORKFLOW)
    makefile = read_text(root, MAKEFILE)
    policy = load_policy(root)

    for marker in README_MARKERS:
        if marker not in readme:
            issues.append(("MISSING_README_MARKER", marker))

    for marker in WORKFLOW_EXACT_LINES:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in WORKFLOW_FRAGMENT_MARKERS:
        if marker not in workflow:
            issues.append(("MISSING_WORKFLOW_FRAGMENT", marker))

    for marker in MAKEFILE_MARKERS:
        if marker not in makefile:
            issues.append(("MISSING_MAKEFILE_MARKER", marker))

    route_policy = policy.get("upgrade_policy")
    if not isinstance(route_policy, dict):
        issues.append(("INVALID_POLICY_FIELD", "upgrade_policy"))
        return issues
    required_make_routes = route_policy.get("required_make_routes")
    if not isinstance(required_make_routes, list) or not required_make_routes:
        issues.append(("INVALID_POLICY_FIELD", "upgrade_policy.required_make_routes"))
        return issues

    for route in required_make_routes:
        if not isinstance(route, str) or not route.strip():
            issues.append(("INVALID_POLICY_ROUTE", repr(route)))
            continue
        workflow_marker = f"run: make -C zigux {route}"
        if count_exact_lines(workflow, workflow_marker) != 1:
            issues.append(("POLICY_WORKFLOW_ROUTE_MISMATCH", workflow_marker))
        make_target = f"{route}:"
        if make_target not in makefile:
            issues.append(("POLICY_MAKEFILE_ROUTE_MISSING", make_target))

    archive_targets = route_policy.get("archive_target_scope")
    archive_sha256 = policy.get("archive_sha256")
    if not isinstance(archive_targets, list) or not archive_targets:
        issues.append(("INVALID_POLICY_FIELD", "upgrade_policy.archive_target_scope"))
    if not isinstance(archive_sha256, dict) or not archive_sha256:
        issues.append(("INVALID_POLICY_FIELD", "archive_sha256"))
    if isinstance(archive_targets, list) and isinstance(archive_sha256, dict):
        missing_targets = [target for target in archive_targets if target not in archive_sha256]
        if missing_targets:
            issues.append(("POLICY_TARGET_SHA_MISSING", ",".join(str(target) for target in missing_targets)))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("LANE03_BOOTSTRAP_TOOLCHAIN_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        root,
        README,
        "\n".join(
            (
                "# scripts/zigux",
                "",
                "scripts/zigux/check-zig-toolchain.py",
                "scripts/zigux/install-zig.py",
                "scripts/zigux/check-phase2-toolchain-pinning.py",
                "scripts/zigux/check-phase2-toolchain-pin-scope.py",
                "scripts/zigux/stage-pinned-zig-archive.py",
                "scripts/zigux/check-lane05-stage-helper-contract.py",
                "scripts/zigux/check-lane05-stage-helper-selftest.py",
                "make -C zigux phase2-toolchain",
                "make -C zigux phase2-validate",
                "make -C zigux phase2-cross",
            )
        )
        + "\n",
    )
    write_text(
        root,
        WORKFLOW,
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                '      - name: Setup pinned Zig toolchain',
                "        run: |",
                '          repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
                '          python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
                '          python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"',
                "          echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2",
                *WORKFLOW_EXACT_LINES,
            )
        )
        + "\n",
    )
    write_text(
        root,
        MAKEFILE,
        "\n".join(
            (
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
                "",
                "phase2-cross:",
                "\t@true",
                "",
                "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
                "\t@true",
            )
        )
        + "\n",
    )
    write_text(
        root,
        POLICY,
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {
                    "x86_64-linux": "3" * 64,
                },
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": [
                        "phase2-toolchain",
                        "phase2-validate",
                        "phase2-cross",
                    ],
                },
            },
            indent=2,
        )
        + "\n",
    )
    for rel in REQUIRED_PATHS:
        if rel in {WORKFLOW, MAKEFILE, README, POLICY}:
            continue
        write_text(root, rel, "present\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane03_bootstrap_toolchain_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        write_text(root, README, read_text(root, README).replace(README_MARKERS[4] + "\n", "", 1))
        assert ("MISSING_README_MARKER", README_MARKERS[4]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), WORKFLOW_EXACT_LINES[9], "run: python3 scripts/zigux/other.py"))
        assert ("MISSING_WORKFLOW_LINE", WORKFLOW_EXACT_LINES[9]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), WORKFLOW_EXACT_LINES[15]))
        assert ("DUPLICATE_WORKFLOW_LINE", f"{WORKFLOW_EXACT_LINES[15]}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, read_text(root, WORKFLOW).replace(WORKFLOW_FRAGMENT_MARKERS[0] + "\n", "", 1))
        assert ("MISSING_WORKFLOW_FRAGMENT", WORKFLOW_FRAGMENT_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, MAKEFILE, read_text(root, MAKEFILE).replace(MAKEFILE_MARKERS[10] + "\n", "", 1))
        assert ("MISSING_MAKEFILE_MARKER", MAKEFILE_MARKERS[10]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        policy = load_policy(root)
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate", "phase2-extra"]  # type: ignore[index]
        write_text(root, POLICY, json.dumps(policy, indent=2) + "\n")
        assert ("POLICY_WORKFLOW_ROUTE_MISMATCH", "run: make -C zigux phase2-extra") in collect_issues(root)
        assert ("POLICY_MAKEFILE_ROUTE_MISSING", "phase2-extra:") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        (root / "scripts/zigux/stage-pinned-zig-archive.py").unlink()
        assert ("MISSING_REQUIRED_PATH", "scripts/zigux/stage-pinned-zig-archive.py") in collect_issues(root)
        checks += 1

    print("LANE03_BOOTSTRAP_TOOLCHAIN_PACKET_SELF_TEST=pass")
    print(f"LANE03_BOOTSTRAP_TOOLCHAIN_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that the current Lane 03 bootstrap toolchain packet stays aligned across scripts-root, workflow, Makefile, and policy surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="write a current-like sample root and exit")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("LANE03_BOOTSTRAP_TOOLCHAIN_PACKET=pass")
    print(f"LANE03_BOOTSTRAP_TOOLCHAIN_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"LANE03_BOOTSTRAP_TOOLCHAIN_WORKFLOW_LINE_COUNT={len(WORKFLOW_EXACT_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
