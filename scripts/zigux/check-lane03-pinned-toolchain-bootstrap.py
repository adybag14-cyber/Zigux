#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
POLICY = "scripts/zigux/zig-toolchain-policy.json"
THIRD_PARTY_README = "third_party/README.md"
SCRIPTS_README = "scripts/zigux/README.md"
BOOTSTRAP_NOTES = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
TOOLCHAIN_CHECKER = "scripts/zigux/check-zig-toolchain.py"
STAGE_HELPER = "scripts/zigux/stage-pinned-zig-archive.py"
INSTALL_HELPER = "scripts/zigux/install-zig.py"

ARCHIVE_TARGET = "x86_64-linux"
ARCHIVE_CHANNEL = "0.17.0-dev.87+9b177a7d2"
ARCHIVE_SHA256 = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
ARCHIVE_SIZE = 58_159_088
EXPECTED_SELF_TEST_CASE_COUNT = 14

REQUIRED_PATHS = (
    WORKFLOW,
    POLICY,
    THIRD_PARTY_README,
    SCRIPTS_README,
    BOOTSTRAP_NOTES,
    TOOLCHAIN_CHECKER,
    STAGE_HELPER,
    INSTALL_HELPER,
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
)

WORKFLOW_SETUP_MARKERS = (
    "- name: Setup pinned Zig toolchain",
    'policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    'repo_archive_parts_dir="${repo_archive_path}.parts"',
    'if [ ! -d "$repo_archive_parts_dir" ]; then',
    '--parts-dir "$repo_archive_parts_dir"',
    'if curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
    'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
    'python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"',
)

WORKFLOW_HOOKS = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
)

SCRIPTS_README_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`scripts/zigux/stage-pinned-zig-archive.py`",
)

THIRD_PARTY_MARKERS = (
    f"`third_party/zig-{ARCHIVE_TARGET}-{ARCHIVE_CHANNEL}.tar.xz`",
    f"`{ARCHIVE_SHA256}`",
    f"`{ARCHIVE_SIZE}`",
    "duplicate-copy boundary",
    "community-mirrors.txt",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-stage-helper-contract.py`",
)

BOOTSTRAP_NOTES_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py` is directly readable on current `master`",
    "`third_party/README.md` is directly readable on current `master`",
    "tries `community-mirrors.txt` before the direct Zig download URL",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`",
)

TOOLCHAIN_CHECKER_MARKERS = (
    'TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"',
    'add_search_root(root / "third_party")',
    'add_search_root(root / "agent_files")',
    'def expected_archive_metadata(',
    '--policy-only',
    '--archive-only',
    '--archive-target',
    '--allow-missing',
)

STAGE_HELPER_MARKERS = (
    'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
    'THIRD_PARTY_DIR = Path("third_party")',
    'EXPECTED_ARCHIVE_SIZES = {',
    'duplicate-suffix archive copies',
    '--parts-dir',
    'STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass',
)


def resolve(root: Path, rel: str) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(text: str, needle: str, replacement: str = "") -> str:
    if needle not in text:
        raise AssertionError(f"marker not found: {needle}")
    return text.replace(needle, replacement, 1)


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_policy_issues(root: Path) -> list[tuple[str, str]]:
    payload = json.loads(read_text(resolve(root, POLICY)))
    issues: list[tuple[str, str]] = []
    if payload.get("phase") != "Phase 2":
        issues.append(("POLICY_FIELD_MISMATCH", "phase"))
    if payload.get("channel") != ARCHIVE_CHANNEL:
        issues.append(("POLICY_FIELD_MISMATCH", "channel"))
    if payload.get("minimum_version") != ARCHIVE_CHANNEL:
        issues.append(("POLICY_FIELD_MISMATCH", "minimum_version"))

    archive_sha256 = payload.get("archive_sha256")
    if archive_sha256 != {ARCHIVE_TARGET: ARCHIVE_SHA256}:
        issues.append(("POLICY_FIELD_MISMATCH", "archive_sha256"))

    upgrade_policy = payload.get("upgrade_policy")
    expected_routes = [
        "phase2-toolchain",
        "phase2-tools",
        "phase2-kconfig",
        "phase2-cross",
        "phase2-genksyms",
        "phase2-fixdep",
        "phase2-validate",
    ]
    if not isinstance(upgrade_policy, dict):
        return issues + [("POLICY_FIELD_MISMATCH", "upgrade_policy")]
    if upgrade_policy.get("channel_minimum_lockstep") is not True:
        issues.append(("POLICY_FIELD_MISMATCH", "channel_minimum_lockstep"))
    if upgrade_policy.get("archive_target_scope") != [ARCHIVE_TARGET]:
        issues.append(("POLICY_FIELD_MISMATCH", "archive_target_scope"))
    if upgrade_policy.get("required_make_routes") != expected_routes:
        issues.append(("POLICY_FIELD_MISMATCH", "required_make_routes"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_PATHS:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    workflow = read_text(resolve(root, WORKFLOW))
    issues.extend(collect_missing_markers(workflow, WORKFLOW_SETUP_MARKERS, "MISSING_WORKFLOW_SETUP_MARKER"))
    for marker in WORKFLOW_HOOKS:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOK", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOK", f"{marker}:count={count}"))

    issues.extend(
        collect_missing_markers(
            read_text(resolve(root, SCRIPTS_README)),
            SCRIPTS_README_MARKERS,
            "MISSING_SCRIPTS_README_MARKER",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve(root, THIRD_PARTY_README)),
            THIRD_PARTY_MARKERS,
            "MISSING_THIRD_PARTY_MARKER",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve(root, BOOTSTRAP_NOTES)),
            BOOTSTRAP_NOTES_MARKERS,
            "MISSING_BOOTSTRAP_NOTE_MARKER",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve(root, TOOLCHAIN_CHECKER)),
            TOOLCHAIN_CHECKER_MARKERS,
            "MISSING_TOOLCHAIN_CHECKER_MARKER",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve(root, STAGE_HELPER)),
            STAGE_HELPER_MARKERS,
            "MISSING_STAGE_HELPER_MARKER",
        )
    )
    issues.extend(collect_policy_issues(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("LANE03_PINNED_TOOLCHAIN_BOOTSTRAP=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    workflow_lines = [
        "name: zigux-bootstrap",
        "",
        *WORKFLOW_SETUP_MARKERS,
        "",
        *WORKFLOW_HOOKS,
        "",
    ]
    write_text(resolve(root, WORKFLOW), "\n".join(workflow_lines))
    write_text(resolve(root, SCRIPTS_README), "\n".join(("# scripts/zigux", "", *SCRIPTS_README_MARKERS, "")))
    write_text(resolve(root, THIRD_PARTY_README), "\n".join(("# third_party", "", *THIRD_PARTY_MARKERS, "")))
    write_text(resolve(root, BOOTSTRAP_NOTES), "\n".join(("# notes", "", *BOOTSTRAP_NOTES_MARKERS, "")))
    write_text(resolve(root, TOOLCHAIN_CHECKER), "\n".join(("#!/usr/bin/env python3", "", *TOOLCHAIN_CHECKER_MARKERS, "")))
    write_text(resolve(root, STAGE_HELPER), "\n".join(("#!/usr/bin/env python3", "", *STAGE_HELPER_MARKERS, "")))
    write_text(resolve(root, INSTALL_HELPER), "present\n")
    for rel in REQUIRED_PATHS:
        if rel in {WORKFLOW, SCRIPTS_README, THIRD_PARTY_README, BOOTSTRAP_NOTES, TOOLCHAIN_CHECKER, STAGE_HELPER, INSTALL_HELPER, POLICY}:
            continue
        write_text(resolve(root, rel), "present\n")
    write_text(
        resolve(root, POLICY),
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": ARCHIVE_CHANNEL,
                "minimum_version": ARCHIVE_CHANNEL,
                "archive_sha256": {ARCHIVE_TARGET: ARCHIVE_SHA256},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": [ARCHIVE_TARGET],
                    "required_make_routes": [
                        "phase2-toolchain",
                        "phase2-tools",
                        "phase2-kconfig",
                        "phase2-cross",
                        "phase2-genksyms",
                        "phase2-fixdep",
                        "phase2-validate",
                    ],
                },
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane03_pinned_toolchain_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_self_test_root(root)
        path = resolve(root, WORKFLOW)
        write_text(path, replace_once(read_text(path), WORKFLOW_SETUP_MARKERS[4]))
        assert ("MISSING_WORKFLOW_SETUP_MARKER", WORKFLOW_SETUP_MARKERS[4]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        path = resolve(root, WORKFLOW)
        write_text(path, replace_once(read_text(path), WORKFLOW_HOOKS[2]))
        assert ("MISSING_WORKFLOW_HOOK", WORKFLOW_HOOKS[2]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        path = resolve(root, WORKFLOW)
        write_text(path, replace_once(read_text(path), WORKFLOW_HOOKS[0], WORKFLOW_HOOKS[0] + "\n" + WORKFLOW_HOOKS[0]))
        assert ("DUPLICATE_WORKFLOW_HOOK", f"{WORKFLOW_HOOKS[0]}:count=2") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        path = resolve(root, SCRIPTS_README)
        write_text(path, replace_once(read_text(path), SCRIPTS_README_MARKERS[2]))
        assert ("MISSING_SCRIPTS_README_MARKER", SCRIPTS_README_MARKERS[2]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        path = resolve(root, THIRD_PARTY_README)
        write_text(path, replace_once(read_text(path), THIRD_PARTY_MARKERS[3]))
        assert ("MISSING_THIRD_PARTY_MARKER", THIRD_PARTY_MARKERS[3]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        path = resolve(root, BOOTSTRAP_NOTES)
        write_text(path, replace_once(read_text(path), BOOTSTRAP_NOTES_MARKERS[2]))
        assert ("MISSING_BOOTSTRAP_NOTE_MARKER", BOOTSTRAP_NOTES_MARKERS[2]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        path = resolve(root, TOOLCHAIN_CHECKER)
        write_text(path, replace_once(read_text(path), TOOLCHAIN_CHECKER_MARKERS[6]))
        assert ("MISSING_TOOLCHAIN_CHECKER_MARKER", TOOLCHAIN_CHECKER_MARKERS[6]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        path = resolve(root, STAGE_HELPER)
        write_text(path, replace_once(read_text(path), STAGE_HELPER_MARKERS[4]))
        assert ("MISSING_STAGE_HELPER_MARKER", STAGE_HELPER_MARKERS[4]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        policy_path = resolve(root, POLICY)
        payload = json.loads(read_text(policy_path))
        payload["minimum_version"] = "0.16.0"
        write_text(policy_path, json.dumps(payload, indent=2) + "\n")
        assert ("POLICY_FIELD_MISMATCH", "minimum_version") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        policy_path = resolve(root, POLICY)
        payload = json.loads(read_text(policy_path))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain"]
        write_text(policy_path, json.dumps(payload, indent=2) + "\n")
        assert ("POLICY_FIELD_MISMATCH", "required_make_routes") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        resolve(root, "scripts/zigux/check-lane05-stage-helper-contract.py").unlink()
        assert ("MISSING_REQUIRED_PATH", "scripts/zigux/check-lane05-stage-helper-contract.py") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        resolve(root, INSTALL_HELPER).unlink()
        assert ("MISSING_REQUIRED_PATH", INSTALL_HELPER) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        policy_path = resolve(root, POLICY)
        payload = json.loads(read_text(policy_path))
        payload["archive_sha256"] = {"aarch64-linux": ARCHIVE_SHA256}
        write_text(policy_path, json.dumps(payload, indent=2) + "\n")
        assert ("POLICY_FIELD_MISMATCH", "archive_sha256") in collect_issues(root)
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("LANE03_PINNED_TOOLCHAIN_BOOTSTRAP_SELF_TEST=pass")
    print(f"LANE03_PINNED_TOOLCHAIN_BOOTSTRAP_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the current Lane 03 pinned Zig bootstrap packet aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)
    print("LANE03_PINNED_TOOLCHAIN_BOOTSTRAP=pass")
    print(f"LANE03_PINNED_TOOLCHAIN_BOOTSTRAP_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"LANE03_PINNED_TOOLCHAIN_BOOTSTRAP_WORKFLOW_HOOK_COUNT={len(WORKFLOW_HOOKS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
