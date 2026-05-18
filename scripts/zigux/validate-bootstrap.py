#!/usr/bin/env python3
"""Guard the current bootstrap validation and toolchain packet."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
SCRIPTS_README = "scripts/zigux/README.md"
TOOLCHAIN_CHECKER = "scripts/zigux/check-zig-toolchain.py"
PINNING_CHECKER = "scripts/zigux/check-phase2-toolchain-pinning.py"
PIN_SCOPE_CHECKER = "scripts/zigux/check-phase2-toolchain-pin-scope.py"
REQUIRED_MAKE_ROUTES_CHECKER = "scripts/zigux/check-phase2-required-make-routes.py"
TOOLCHAIN_POLICY = "scripts/zigux/zig-toolchain-policy.json"
SELF_PATH = "scripts/zigux/validate-bootstrap.py"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
POLICY_KEYS = {
    "phase",
    "channel",
    "minimum_version",
    "archive_sha256",
    "upgrade_policy",
}
UPGRADE_POLICY_KEYS = {
    "channel_minimum_lockstep",
    "archive_target_scope",
    "required_make_routes",
}

REQUIRED_PATHS = (
    SCRIPTS_README,
    TOOLCHAIN_CHECKER,
    PINNING_CHECKER,
    PIN_SCOPE_CHECKER,
    REQUIRED_MAKE_ROUTES_CHECKER,
    TOOLCHAIN_POLICY,
    WORKFLOW,
    SELF_PATH,
)

WORKFLOW_SUBSTRING_MARKERS = (
    "- name: Setup pinned Zig toolchain",
    'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
    'python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"',
)

WORKFLOW_LINE_MARKERS = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/validate-bootstrap.py --self-test",
    "run: python3 scripts/zigux/validate-bootstrap.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
)

# Keep the bootstrap validator steps anchored inside the live Lane 03 packet
# instead of drifting later into unrelated Phase 2 or Phase 3 workflow sections.
WORKFLOW_ORDER_MARKERS = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/validate-bootstrap.py --self-test",
    "run: python3 scripts/zigux/validate-bootstrap.py",
    "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
)

README_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/zig-toolchain-policy.json`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "repeated authenticated reads on current `master` still return missing for",
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
)

TOOLCHAIN_CHECKER_MARKERS = (
    'TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"',
    "def load_policy(",
    "def load_pinned_channel(",
    "def iter_repo_local_zig_candidates(",
    "def resolve_zig_executable(",
    "def resolve_policy_archive(",
    'parser.add_argument("--policy-only"',
    'parser.add_argument("--archive-only"',
    'parser.add_argument("--allow-missing"',
)

EXPECTED_POLICY = {
    "phase": "Phase 2",
    "archive_target_scope": ["x86_64-linux"],
    "required_make_routes": ["phase2-toolchain", "phase2-validate"],
    "channel_minimum_lockstep": True,
}

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(WORKFLOW_SUBSTRING_MARKERS)
    + len(WORKFLOW_SUBSTRING_MARKERS)
    + len(WORKFLOW_LINE_MARKERS)
    + len(WORKFLOW_LINE_MARKERS)
    + len(README_MARKERS)
    + len(TOOLCHAIN_CHECKER_MARKERS)
    + (len(REQUIRED_PATHS) - 1)
    + 13
)


def path_under(root: Path, rel: str) -> Path:
    return root / rel


def read_text(root: Path, rel: str) -> str:
    path = path_under(root, rel)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: str, content: str) -> None:
    path = path_under(root, rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def duplicate_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, marker + "\n" + marker, 1)


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
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


def swap_exact_lines(text: str, first: str, second: str) -> str:
    lines = text.splitlines()
    first_index = None
    second_index = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == first and first_index is None:
            first_index = index
        if stripped == second and second_index is None:
            second_index = index
    if first_index is None or second_index is None:
        raise AssertionError(f"unable to swap workflow lines: {first!r}, {second!r}")
    lines[first_index], lines[second_index] = lines[second_index], lines[first_index]
    return "\n".join(lines) + "\n"


def collect_workflow_order_issues(workflow_text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    positions: list[tuple[str, int]] = []
    workflow_lines = [line.strip() for line in workflow_text.splitlines()]
    for marker in WORKFLOW_ORDER_MARKERS:
        count = count_exact_lines(workflow_text, marker)
        if count == 1:
            positions.append((marker, workflow_lines.index(marker)))
    for (previous_marker, previous_index), (current_marker, current_index) in zip(
        positions,
        positions[1:],
    ):
        if previous_index >= current_index:
            issues.append(
                (
                    "OUT_OF_ORDER_WORKFLOW_MARKER",
                    f"{previous_marker} -> {current_marker}",
                )
            )
    return issues


def collect_policy_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    try:
        payload = json.loads(read_text(root, TOOLCHAIN_POLICY))
    except json.JSONDecodeError as exc:
        return [("INVALID_POLICY_JSON", exc.msg)]

    if not isinstance(payload, dict):
        return [("INVALID_POLICY", "expected JSON object")]

    unexpected_policy_keys = sorted(set(payload) - POLICY_KEYS)
    if unexpected_policy_keys:
        issues.append(("INVALID_POLICY", f"unexpected_policy_keys={unexpected_policy_keys!r}"))

    if payload.get("phase") != EXPECTED_POLICY["phase"]:
        issues.append(("INVALID_POLICY", f"phase={payload.get('phase')!r}"))

    channel = payload.get("channel")
    minimum_version = payload.get("minimum_version")
    if not isinstance(channel, str) or not channel:
        issues.append(("INVALID_POLICY", "channel"))
    if not isinstance(minimum_version, str) or not minimum_version:
        issues.append(("INVALID_POLICY", "minimum_version"))
    if isinstance(channel, str) and isinstance(minimum_version, str) and channel != minimum_version:
        issues.append(("INVALID_POLICY", "channel_minimum_version_mismatch"))

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict):
        issues.append(("INVALID_POLICY", "archive_sha256"))
    else:
        if list(archive_sha256.keys()) != EXPECTED_POLICY["archive_target_scope"]:
            issues.append(("INVALID_POLICY", f"archive_sha256_keys={list(archive_sha256.keys())!r}"))
        for target, digest in archive_sha256.items():
            if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
                issues.append(("INVALID_POLICY", f"archive_sha256[{target}]"))

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("INVALID_POLICY", "upgrade_policy"))
    else:
        unexpected_upgrade_policy_keys = sorted(set(upgrade_policy) - UPGRADE_POLICY_KEYS)
        if unexpected_upgrade_policy_keys:
            issues.append(
                ("INVALID_POLICY", f"unexpected_upgrade_policy_keys={unexpected_upgrade_policy_keys!r}")
            )
        if upgrade_policy.get("channel_minimum_lockstep") is not EXPECTED_POLICY["channel_minimum_lockstep"]:
            issues.append(("INVALID_POLICY", "channel_minimum_lockstep"))
        if upgrade_policy.get("archive_target_scope") != EXPECTED_POLICY["archive_target_scope"]:
            issues.append(("INVALID_POLICY", "archive_target_scope"))
        if upgrade_policy.get("required_make_routes") != EXPECTED_POLICY["required_make_routes"]:
            issues.append(("INVALID_POLICY", "required_make_routes"))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    existing_paths: set[str] = set()

    for rel in REQUIRED_PATHS:
        if path_under(root, rel).exists():
            existing_paths.add(rel)
        else:
            issues.append(("MISSING_REQUIRED_PATH", rel))

    if WORKFLOW in existing_paths:
        workflow_text = read_text(root, WORKFLOW)
        for marker in WORKFLOW_SUBSTRING_MARKERS:
            count = workflow_text.count(marker)
            if count == 0:
                issues.append(("MISSING_WORKFLOW_MARKER", marker))
            elif count != 1:
                issues.append(("DUPLICATE_WORKFLOW_MARKER", f"{marker}:count={count}"))

        for marker in WORKFLOW_LINE_MARKERS:
            count = count_exact_lines(workflow_text, marker)
            if count == 0:
                issues.append(("MISSING_WORKFLOW_MARKER", marker))
            elif count != 1:
                issues.append(("DUPLICATE_WORKFLOW_MARKER", f"{marker}:count={count}"))

        issues.extend(collect_workflow_order_issues(workflow_text))

    if SCRIPTS_README in existing_paths:
        readme_text = read_text(root, SCRIPTS_README)
        for marker in README_MARKERS:
            if marker not in readme_text:
                issues.append(("MISSING_README_MARKER", marker))

    if TOOLCHAIN_CHECKER in existing_paths:
        checker_text = read_text(root, TOOLCHAIN_CHECKER)
        for marker in TOOLCHAIN_CHECKER_MARKERS:
            if marker not in checker_text:
                issues.append(("MISSING_TOOLCHAIN_CHECKER_MARKER", marker))

    if TOOLCHAIN_POLICY in existing_paths:
        issues.extend(collect_policy_issues(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("BOOTSTRAP_VALIDATION=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        root,
        WORKFLOW,
        "\n".join(
            (
                "name: zigux-bootstrap",
                *WORKFLOW_SUBSTRING_MARKERS,
                *WORKFLOW_LINE_MARKERS,
                'run: python3 scripts/zigux/check-kconfig-bridge.py --self-test',
            )
        )
        + "\n",
    )
    write_text(root, SCRIPTS_README, "# scripts/zigux\n\n" + "\n".join(f"- {marker}" for marker in README_MARKERS) + "\n")
    write_text(
        root,
        TOOLCHAIN_CHECKER,
        "\n".join(
            (
                "#!/usr/bin/env python3",
                *TOOLCHAIN_CHECKER_MARKERS,
            )
        )
        + "\n",
    )
    for rel in (PINNING_CHECKER, PIN_SCOPE_CHECKER, REQUIRED_MAKE_ROUTES_CHECKER):
        write_text(root, rel, "# present\n")
    write_text(
        root,
        TOOLCHAIN_POLICY,
        json.dumps(
            {
                "phase": EXPECTED_POLICY["phase"],
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": EXPECTED_POLICY["channel_minimum_lockstep"],
                    "archive_target_scope": EXPECTED_POLICY["archive_target_scope"],
                    "required_make_routes": EXPECTED_POLICY["required_make_routes"],
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(root, SELF_PATH, "# present\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_validate_bootstrap_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in WORKFLOW_SUBSTRING_MARKERS:
            build_self_test_root(root)
            workflow_path = path_under(root, WORKFLOW)
            workflow_path.write_text(
                replace_once(workflow_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_WORKFLOW_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_SUBSTRING_MARKERS:
            build_self_test_root(root)
            workflow_path = path_under(root, WORKFLOW)
            workflow_path.write_text(
                duplicate_once(workflow_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("DUPLICATE_WORKFLOW_MARKER", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_LINE_MARKERS:
            build_self_test_root(root)
            workflow_path = path_under(root, WORKFLOW)
            workflow_path.write_text(
                replace_exact_line(workflow_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_WORKFLOW_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_LINE_MARKERS:
            build_self_test_root(root)
            workflow_path = path_under(root, WORKFLOW)
            workflow_path.write_text(
                duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("DUPLICATE_WORKFLOW_MARKER", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        workflow_path = path_under(root, WORKFLOW)
        workflow_path.write_text(
            swap_exact_lines(
                workflow_path.read_text(encoding="utf-8"),
                "run: python3 scripts/zigux/validate-bootstrap.py",
                'run: python3 scripts/zigux/check-kconfig-bridge.py --self-test',
            ),
            encoding="utf-8",
        )
        assert (
            "OUT_OF_ORDER_WORKFLOW_MARKER",
            "run: python3 scripts/zigux/validate-bootstrap.py -> run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        workflow_path = path_under(root, WORKFLOW)
        workflow_path.write_text(
            swap_exact_lines(
                workflow_path.read_text(encoding="utf-8"),
                "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
                "run: python3 scripts/zigux/validate-bootstrap.py --self-test",
            ),
            encoding="utf-8",
        )
        assert (
            "OUT_OF_ORDER_WORKFLOW_MARKER",
            "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing -> run: python3 scripts/zigux/validate-bootstrap.py --self-test",
        ) in collect_issues(root)
        checks_run += 1

        for marker in README_MARKERS:
            build_self_test_root(root)
            readme_path = path_under(root, SCRIPTS_README)
            readme_path.write_text(
                replace_once(readme_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_README_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in TOOLCHAIN_CHECKER_MARKERS:
            build_self_test_root(root)
            checker_path = path_under(root, TOOLCHAIN_CHECKER)
            checker_path.write_text(
                replace_once(checker_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_TOOLCHAIN_CHECKER_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for rel in REQUIRED_PATHS:
            if rel == SELF_PATH:
                continue
            build_self_test_root(root)
            path_under(root, rel).unlink()
            assert ("MISSING_REQUIRED_PATH", rel) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        policy_path = path_under(root, TOOLCHAIN_POLICY)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["phase"] = "Phase 1"
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY", "phase='Phase 1'") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        policy_path = path_under(root, TOOLCHAIN_POLICY)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["channel"] = ""
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY", "channel") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        policy_path = path_under(root, TOOLCHAIN_POLICY)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["minimum_version"] = "0.16.0"
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY", "channel_minimum_version_mismatch") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        policy_path = path_under(root, TOOLCHAIN_POLICY)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain"]
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY", "required_make_routes") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        policy_path = path_under(root, TOOLCHAIN_POLICY)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["archive_target_scope"] = ["aarch64-linux"]
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY", "archive_target_scope") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        policy_path = path_under(root, TOOLCHAIN_POLICY)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["channel_minimum_lockstep"] = False
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY", "channel_minimum_lockstep") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        policy_path = path_under(root, TOOLCHAIN_POLICY)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["archive_sha256"] = {"x86_64-linux": "g" * 64}
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY", "archive_sha256[x86_64-linux]") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        policy_path = path_under(root, TOOLCHAIN_POLICY)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["archive_sha256"] = {"aarch64-linux": "3" * 64}
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        assert (
            "INVALID_POLICY",
            "archive_sha256_keys=['aarch64-linux']",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        policy_path = path_under(root, TOOLCHAIN_POLICY)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"] = "invalid"
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY", "upgrade_policy") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        policy_path = path_under(root, TOOLCHAIN_POLICY)
        policy_path.write_text("{invalid json\n", encoding="utf-8")
        assert any(code == "INVALID_POLICY_JSON" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        assert path_under(root, SELF_PATH).exists()
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT, (checks_run, EXPECTED_SELF_TEST_CASE_COUNT)
    print("BOOTSTRAP_VALIDATION_SELF_TEST=pass")
    print(f"BOOTSTRAP_VALIDATION_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run validator self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("BOOTSTRAP_VALIDATION=pass")
    print("BOOTSTRAP_VALIDATION_SCOPE=lane03_bootstrap_toolchain_packet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
