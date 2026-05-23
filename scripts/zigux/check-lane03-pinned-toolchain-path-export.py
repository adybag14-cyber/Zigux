#!/usr/bin/env python3
"""Guard the pinned Zig path/export contract for the Lane 03 bootstrap packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
TOOLCHAIN_CHECKER = ROOT / "scripts" / "zigux" / "check-zig-toolchain.py"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"

WORKFLOW_LINE_COUNTS = {
    "mkdir -p .zig-toolchain": 1,
    'archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"': 1,
    'extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"': 1,
    'mirror_file=".zig-toolchain/community-mirrors.txt"': 1,
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"': 1,
    'rm -f "$archive_path" "$mirror_file"': 1,
    'rm -rf "$extract_root"': 1,
    'tar -xJf "$repo_archive_path" -C .zig-toolchain': 1,
    'tar -xJf "$archive_path" -C .zig-toolchain': 1,
    'echo "$extract_root" >> "$GITHUB_PATH"': 1,
    '"$zig_path" version': 1,
}

MAKEFILE_LINE_COUNTS = {
    "ZIG_PINNED_EXTRACT_ROOT := $(ZIGUX_ROOT)/.zig-toolchain/zig-$(ZIG_PINNED_TARGET)-$(ZIG_PINNED_CHANNEL)": 1,
    "ZIG_PINNED_EXECUTABLE := $(firstword $(wildcard $(ZIG_PINNED_EXTRACT_ROOT)/zig $(ZIG_PINNED_EXTRACT_ROOT)/bin/zig))": 1,
    "ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))": 1,
    "ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))": 1,
    "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)": 1,
}

TOOLCHAIN_MARKER_COUNTS = {
    'add_search_root(root / ".zig-toolchain")': 1,
    'add_search_root(root / "toolchains")': 1,
    'add_search_root(root / ".toolchains")': 1,
    'add_search_root(root / "third_party")': 1,
    'add_search_root(root / "agent_files")': 1,
    'add_candidate(base / "zig")': 1,
    'add_candidate(base / "bin" / "zig")': 1,
    'pinned_dirname = f"zig-x86_64-linux-{pinned_channel}"': 1,
    'return which("zig")': 1,
}

EXPECTED_PHASE = "Phase 2"
EXPECTED_TARGET_SCOPE = ["x86_64-linux"]
EXPECTED_REQUIRED_MAKE_ROUTES = ["phase2-toolchain", "phase2-validate", "phase2-cross"]


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


def count_marker_occurrences(text: str, marker: str) -> int:
    return text.count(marker)


def collect_count_issues(
    text: str,
    marker_counts: dict[str, int],
    *,
    counter,
    code: str,
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker, expected_count in marker_counts.items():
        actual_count = counter(text, marker)
        if actual_count != expected_count:
            issues.append((code, f"{marker}:actual={actual_count}:expected={expected_count}"))
    return issues


def validate_policy(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    try:
        payload = json.loads(read_text(resolve_path(root, TOOLCHAIN_POLICY)))
    except json.JSONDecodeError as exc:
        return [("INVALID_POLICY_JSON", exc.msg)]

    if not isinstance(payload, dict):
        return [("INVALID_POLICY", "expected JSON object")]

    if payload.get("phase") != EXPECTED_PHASE:
        issues.append(("INVALID_POLICY", f"phase={payload.get('phase')!r}"))

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        return issues + [("INVALID_POLICY", "upgrade_policy")]

    if upgrade_policy.get("channel_minimum_lockstep") is not True:
        issues.append(("INVALID_POLICY", "channel_minimum_lockstep"))

    if upgrade_policy.get("archive_target_scope") != EXPECTED_TARGET_SCOPE:
        issues.append(("INVALID_POLICY", f"archive_target_scope={upgrade_policy.get('archive_target_scope')!r}"))

    if upgrade_policy.get("required_make_routes") != EXPECTED_REQUIRED_MAKE_ROUTES:
        issues.append(("INVALID_POLICY", f"required_make_routes={upgrade_policy.get('required_make_routes')!r}"))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    makefile_text = read_text(resolve_path(root, MAKEFILE))
    toolchain_checker_text = read_text(resolve_path(root, TOOLCHAIN_CHECKER))

    issues.extend(
        collect_count_issues(
            workflow_text,
            WORKFLOW_LINE_COUNTS,
            counter=count_exact_lines,
            code="WORKFLOW_PATH_EXPORT_DRIFT",
        )
    )
    issues.extend(
        collect_count_issues(
            makefile_text,
            MAKEFILE_LINE_COUNTS,
            counter=count_exact_lines,
            code="MAKEFILE_PATH_EXPORT_DRIFT",
        )
    )
    issues.extend(
        collect_count_issues(
            toolchain_checker_text,
            TOOLCHAIN_MARKER_COUNTS,
            counter=count_marker_occurrences,
            code="TOOLCHAIN_CHECKER_PATH_EXPORT_DRIFT",
        )
    )
    issues.extend(validate_policy(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    print("LANE03_PINNED_TOOLCHAIN_PATH_EXPORT=fail")
    for code, value in issues:
        print(f"{code}:{value}")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_LINE_COUNTS) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINE_COUNTS) + "\n")
    write_text(
        resolve_path(root, TOOLCHAIN_CHECKER),
        "#!/usr/bin/env python3\n" + "\n".join(TOOLCHAIN_MARKER_COUNTS) + "\n",
    )
    write_text(
        resolve_path(root, TOOLCHAIN_POLICY),
        json.dumps(
            {
                "phase": EXPECTED_PHASE,
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": EXPECTED_TARGET_SCOPE,
                    "required_make_routes": EXPECTED_REQUIRED_MAKE_ROUTES,
                },
            },
            indent=2,
        )
        + "\n",
    )


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


def replace_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane03_path_export_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in WORKFLOW_LINE_COUNTS:
            build_sample_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert any(code == "WORKFLOW_PATH_EXPORT_DRIFT" for code, _ in collect_issues(root))
            checks_run += 1

        for marker in WORKFLOW_LINE_COUNTS:
            build_sample_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert any(code == "WORKFLOW_PATH_EXPORT_DRIFT" for code, _ in collect_issues(root))
            checks_run += 1

        for marker in MAKEFILE_LINE_COUNTS:
            build_sample_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert any(code == "MAKEFILE_PATH_EXPORT_DRIFT" for code, _ in collect_issues(root))
            checks_run += 1

        for marker in MAKEFILE_LINE_COUNTS:
            build_sample_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert any(code == "MAKEFILE_PATH_EXPORT_DRIFT" for code, _ in collect_issues(root))
            checks_run += 1

        for marker in TOOLCHAIN_MARKER_COUNTS:
            build_sample_root(root)
            path = resolve_path(root, TOOLCHAIN_CHECKER)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert any(code == "TOOLCHAIN_CHECKER_PATH_EXPORT_DRIFT" for code, _ in collect_issues(root))
            checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["phase"] = "Phase 3"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY", "phase='Phase 3'") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["channel_minimum_lockstep"] = False
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY", "channel_minimum_lockstep") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["aarch64-linux"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY", "archive_target_scope=['aarch64-linux']") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY", "required_make_routes=['phase2-toolchain']") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        path.write_text("{not-json}\n", encoding="utf-8")
        assert any(code == "INVALID_POLICY_JSON" for code, _ in collect_issues(root))
        checks_run += 1

        for path in (WORKFLOW, MAKEFILE, TOOLCHAIN_CHECKER, TOOLCHAIN_POLICY):
            build_sample_root(root)
            resolve_path(root, path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {path}")

    print("LANE03_PINNED_TOOLCHAIN_PATH_EXPORT_SELF_TEST=pass")
    print(f"LANE03_PINNED_TOOLCHAIN_PATH_EXPORT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the pinned Zig path/export contract stays aligned across the Lane 03 bootstrap packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal current-like sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"LANE03_PINNED_TOOLCHAIN_PATH_EXPORT_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("LANE03_PINNED_TOOLCHAIN_PATH_EXPORT=pass")
    print(f"LANE03_PINNED_TOOLCHAIN_PATH_EXPORT_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINE_COUNTS)}")
    print(f"LANE03_PINNED_TOOLCHAIN_PATH_EXPORT_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINE_COUNTS)}")
    print(f"LANE03_PINNED_TOOLCHAIN_PATH_EXPORT_TOOLCHAIN_MARKER_COUNT={len(TOOLCHAIN_MARKER_COUNTS)}")
    print("LANE03_PINNED_TOOLCHAIN_PATH_EXPORT_ARCHIVE_TARGET_SCOPE=" + ",".join(EXPECTED_TARGET_SCOPE))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
