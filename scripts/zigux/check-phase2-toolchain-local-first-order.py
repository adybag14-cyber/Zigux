#!/usr/bin/env python3
"""Guard the local-first Phase 2 toolchain fallback order."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else Path.cwd()

WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
THIRD_PARTY_README = Path("third_party/README.md")
POLICY = Path("scripts/zigux/zig-toolchain-policy.json")

REQUIRED_FILES = (
    WORKFLOW,
    BOOTSTRAP_NOTES,
    THIRD_PARTY_README,
    POLICY,
)

WORKFLOW_MARKERS = (
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    'mirror_file=".zig-toolchain/community-mirrors.txt"',
    'rm -f "$archive_path" "$mirror_file"',
    'rm -rf "$extract_root"',
    "try_local_archive() {",
    'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
    "if try_local_archive; then",
    'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
    'if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then',
    'if try_download "$ZIGUX_ZIG_URL"; then',
)

BOOTSTRAP_NOTE_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py`",
    "`third_party/README.md`",
    "repo-local `.zig-toolchain` fallback",
    "tries `community-mirrors.txt` before the direct Zig download URL",
    "reruns `python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"`",
)

THIRD_PARTY_README_MARKERS = (
    "Lane 05 bootstrap first reuses and validates",
    "Before retrying the mirror or direct-download path",
    "falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
)

POLICY_TARGET_SCOPE = ("x86_64-linux",)
POLICY_PHASE = "Phase 2"


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def exact_line_index(text: str, marker: str) -> int | None:
    for index, line in enumerate(text.splitlines()):
        if line.strip() == marker:
            return index
    return None


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def collect_marker_issues(
    text: str,
    markers: tuple[str, ...],
    code: str,
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        if marker not in text:
            issues.append((code, marker))
    return issues


def collect_workflow_order_issues(text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    order_markers = (
        'rm -f "$archive_path" "$mirror_file"',
        'rm -rf "$extract_root"',
        "try_local_archive() {",
        "if try_local_archive; then",
        'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
        'if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then',
        'if try_download "$ZIGUX_ZIG_URL"; then',
    )
    indices: list[int] = []
    for marker in order_markers:
        index = exact_line_index(text, marker)
        if index is None:
            return issues
        indices.append(index)
    if indices != sorted(indices):
        issues.append(("WORKFLOW_ORDER_MISMATCH", "local-archive -> mirrors -> direct-download"))
    return issues


def collect_policy_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    payload = read_json(resolve(root, POLICY))
    if not isinstance(payload, dict):
        return [("INVALID_POLICY_PAYLOAD", type(payload).__name__)]
    if payload.get("phase") != POLICY_PHASE:
        issues.append(("POLICY_PHASE_MISMATCH", repr(payload.get("phase"))))
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        return issues + [("INVALID_UPGRADE_POLICY", type(upgrade_policy).__name__)]
    target_scope = upgrade_policy.get("archive_target_scope")
    if target_scope != list(POLICY_TARGET_SCOPE):
        issues.append(("POLICY_TARGET_SCOPE_MISMATCH", repr(target_scope)))
    channel = payload.get("channel")
    if not isinstance(channel, str) or not channel.strip():
        issues.append(("INVALID_POLICY_CHANNEL", repr(channel)))
        return issues

    expected_archive = f"third_party/zig-{POLICY_TARGET_SCOPE[0]}-{channel.strip()}.tar.xz"
    bootstrap_notes_text = read_text(resolve(root, BOOTSTRAP_NOTES))
    third_party_readme_text = read_text(resolve(root, THIRD_PARTY_README))
    if f"`{expected_archive}`" not in bootstrap_notes_text:
        issues.append(("MISSING_BOOTSTRAP_ARCHIVE_MARKER", expected_archive))
    if f"`{expected_archive}`" not in third_party_readme_text:
        issues.append(("MISSING_THIRD_PARTY_ARCHIVE_MARKER", expected_archive))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_FILES:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    workflow_text = read_text(resolve(root, WORKFLOW))
    bootstrap_notes_text = read_text(resolve(root, BOOTSTRAP_NOTES))
    third_party_readme_text = read_text(resolve(root, THIRD_PARTY_README))

    issues.extend(collect_marker_issues(workflow_text, WORKFLOW_MARKERS, "MISSING_WORKFLOW_MARKER"))
    issues.extend(collect_workflow_order_issues(workflow_text))
    issues.extend(
        collect_marker_issues(
            bootstrap_notes_text,
            BOOTSTRAP_NOTE_MARKERS,
            "MISSING_BOOTSTRAP_NOTE_MARKER",
        )
    )
    issues.extend(
        collect_marker_issues(
            third_party_readme_text,
            THIRD_PARTY_README_MARKERS,
            "MISSING_THIRD_PARTY_README_MARKER",
        )
    )
    issues.extend(collect_policy_issues(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_TOOLCHAIN_LOCAL_FIRST_ORDER=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    workflow_text = "\n".join(
        (
            "name: zigux-bootstrap",
            'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
            'mirror_file=".zig-toolchain/community-mirrors.txt"',
            'rm -f "$archive_path" "$mirror_file"',
            'rm -rf "$extract_root"',
            "try_local_archive() {",
            'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
            "}",
            "if try_local_archive; then",
            'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
            'if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then',
            "fi",
            'if try_download "$ZIGUX_ZIG_URL"; then',
        )
    )
    write_text(resolve(root, WORKFLOW), workflow_text + "\n")

    channel = "0.17.0-dev.87+9b177a7d2"
    archive_marker = f"`third_party/zig-{POLICY_TARGET_SCOPE[0]}-{channel}.tar.xz`"
    bootstrap_notes = "\n".join(
        (
            "# Phase 2 Toolchain Bootstrap Notes",
            *BOOTSTRAP_NOTE_MARKERS,
            archive_marker,
        )
    )
    write_text(resolve(root, BOOTSTRAP_NOTES), bootstrap_notes + "\n")

    third_party_readme = "\n".join(
        (
            "# Zigux third-party archives",
            *THIRD_PARTY_README_MARKERS,
            archive_marker,
        )
    )
    write_text(resolve(root, THIRD_PARTY_README), third_party_readme + "\n")

    policy = {
        "phase": POLICY_PHASE,
        "channel": channel,
        "minimum_version": channel,
        "archive_sha256": {POLICY_TARGET_SCOPE[0]: "3" * 64},
        "upgrade_policy": {
            "channel_minimum_lockstep": True,
            "archive_target_scope": list(POLICY_TARGET_SCOPE),
            "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],
        },
    }
    write_text(resolve(root, POLICY), json.dumps(policy, indent=2) + "\n")


def run_self_test() -> int:
    expected_case_count = (
        1
        + len(WORKFLOW_MARKERS)
        + 1
        + len(BOOTSTRAP_NOTE_MARKERS)
        + len(THIRD_PARTY_README_MARKERS)
        + 4
        + len(REQUIRED_FILES)
        + 1
    )
    cases_run = 0

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_local_first_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        cases_run += 1

        for marker in WORKFLOW_MARKERS:
            case_root = root / f"workflow-marker-{cases_run}"
            build_sample_root(case_root)
            workflow_path = resolve(case_root, WORKFLOW)
            workflow_path.write_text(
                replace_once(workflow_path.read_text(encoding="utf-8"), marker).rstrip() + "\n",
                encoding="utf-8",
            )
            assert ("MISSING_WORKFLOW_MARKER", marker) in collect_issues(case_root)
            cases_run += 1

        case_root = root / "workflow-order"
        build_sample_root(case_root)
        workflow_path = resolve(case_root, WORKFLOW)
        swapped = workflow_path.read_text(encoding="utf-8").replace(
            'if try_download "$ZIGUX_ZIG_URL"; then\n',
            'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then\n',
            1,
        ).replace(
            'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then\n',
            'if try_download "$ZIGUX_ZIG_URL"; then\n',
            1,
        )
        workflow_path.write_text(swapped, encoding="utf-8")
        assert (
            "WORKFLOW_ORDER_MISMATCH",
            "local-archive -> mirrors -> direct-download",
        ) in collect_issues(case_root)
        cases_run += 1

        for marker in BOOTSTRAP_NOTE_MARKERS:
            case_root = root / f"bootstrap-{cases_run}"
            build_sample_root(case_root)
            path = resolve(case_root, BOOTSTRAP_NOTES)
            path.write_text(
                replace_once(path.read_text(encoding="utf-8"), marker).rstrip() + "\n",
                encoding="utf-8",
            )
            assert ("MISSING_BOOTSTRAP_NOTE_MARKER", marker) in collect_issues(case_root)
            cases_run += 1

        for marker in THIRD_PARTY_README_MARKERS:
            case_root = root / f"third-party-{cases_run}"
            build_sample_root(case_root)
            path = resolve(case_root, THIRD_PARTY_README)
            path.write_text(
                replace_once(path.read_text(encoding="utf-8"), marker).rstrip() + "\n",
                encoding="utf-8",
            )
            assert ("MISSING_THIRD_PARTY_README_MARKER", marker) in collect_issues(case_root)
            cases_run += 1

        case_root = root / "policy-phase"
        build_sample_root(case_root)
        path = resolve(case_root, POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["phase"] = "Phase 3"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("POLICY_PHASE_MISMATCH", repr("Phase 3")) in collect_issues(case_root)
        cases_run += 1

        case_root = root / "policy-scope"
        build_sample_root(case_root)
        path = resolve(case_root, POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["aarch64-linux"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("POLICY_TARGET_SCOPE_MISMATCH", repr(["aarch64-linux"])) in collect_issues(case_root)
        cases_run += 1

        case_root = root / "bootstrap-archive"
        build_sample_root(case_root)
        path = resolve(case_root, BOOTSTRAP_NOTES)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz").rstrip() + "\n",
            encoding="utf-8",
        )
        assert (
            "MISSING_BOOTSTRAP_ARCHIVE_MARKER",
            "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
        ) in collect_issues(case_root)
        cases_run += 1

        case_root = root / "third-party-archive"
        build_sample_root(case_root)
        path = resolve(case_root, THIRD_PARTY_README)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz").rstrip() + "\n",
            encoding="utf-8",
        )
        assert (
            "MISSING_THIRD_PARTY_ARCHIVE_MARKER",
            "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
        ) in collect_issues(case_root)
        cases_run += 1

        for rel in REQUIRED_FILES:
            case_root = root / f"missing-file-{cases_run}"
            build_sample_root(case_root)
            resolve(case_root, rel).unlink()
            assert ("MISSING_REQUIRED_FILE", rel.as_posix()) in collect_issues(case_root)
            cases_run += 1

        case_root = root / "invalid-json"
        build_sample_root(case_root)
        resolve(case_root, POLICY).write_text("{not-json}\n", encoding="utf-8")
        try:
            collect_issues(case_root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
            cases_run += 1
        else:
            raise AssertionError("invalid policy JSON did not abort")

    assert cases_run == expected_case_count, (cases_run, expected_case_count)
    print("PHASE2_TOOLCHAIN_LOCAL_FIRST_ORDER_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_LOCAL_FIRST_ORDER_SELF_TEST_CASE_COUNT={cases_run}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="Write a minimal passing sample root and exit",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-tests")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0

    root = args.root.resolve()
    issues = collect_issues(root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLCHAIN_LOCAL_FIRST_ORDER=pass")
    print(f"PHASE2_TOOLCHAIN_LOCAL_FIRST_ORDER_WORKFLOW_MARKER_COUNT={len(WORKFLOW_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_LOCAL_FIRST_ORDER_BOOTSTRAP_MARKER_COUNT={len(BOOTSTRAP_NOTE_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_LOCAL_FIRST_ORDER_THIRD_PARTY_MARKER_COUNT={len(THIRD_PARTY_README_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_LOCAL_FIRST_ORDER_TARGET_SCOPE_COUNT={len(POLICY_TARGET_SCOPE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
