#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
POLICY = "scripts/zigux/zig-toolchain-policy.json"
README = "third_party/README.md"

REQUIRED_PATHS = (
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    POLICY,
    README,
    WORKFLOW,
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
)

README_MARKERS = (
    "- target: `x86_64-linux`",
    "- channel: `0.17.0-dev.87+9b177a7d2`",
    "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "- sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`",
    "- do not keep duplicate-suffix copies such as `zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz` in this directory",
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


def load_policy(root: Path) -> dict[str, object]:
    policy_path = root / POLICY
    try:
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {policy_path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {policy_path}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid toolchain policy payload in {policy_path}: expected object")
    return payload


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    workflow = read_text(root, WORKFLOW)
    readme = read_text(root, README)
    try:
        payload = load_policy(root)
    except SystemExit as exc:
        issues.append(("INVALID_POLICY_PAYLOAD", str(exc)))
        return issues

    workflow_positions: list[int] = []
    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
            continue
        if count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))
            continue
        workflow_positions.append(workflow.index(marker))

    if len(workflow_positions) == len(REQUIRED_WORKFLOW_LINES):
        if workflow_positions != sorted(workflow_positions):
            issues.append(
                (
                    "MISORDERED_WORKFLOW_PACKET",
                    f"{REQUIRED_WORKFLOW_LINES[0]} -> {REQUIRED_WORKFLOW_LINES[-1]}",
                )
            )

    for marker in README_MARKERS:
        if marker not in readme:
            issues.append(("MISSING_ARCHIVE_README_MARKER", marker))

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict):
        issues.append(("INVALID_POLICY_FIELD", "archive_sha256"))
    else:
        actual_sha = archive_sha256.get("x86_64-linux")
        if actual_sha != "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77":
            issues.append(("POLICY_MISMATCH", f"archive_sha256.x86_64-linux={actual_sha!r}"))

    channel = payload.get("channel")
    if channel != "0.17.0-dev.87+9b177a7d2":
        issues.append(("POLICY_MISMATCH", f"channel={channel!r}"))

    minimum_version = payload.get("minimum_version")
    if minimum_version != "0.17.0-dev.87+9b177a7d2":
        issues.append(("POLICY_MISMATCH", f"minimum_version={minimum_version!r}"))

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("INVALID_POLICY_FIELD", "upgrade_policy"))
    else:
        archive_target_scope = upgrade_policy.get("archive_target_scope")
        if archive_target_scope != ["x86_64-linux"]:
            issues.append(("POLICY_MISMATCH", f"archive_target_scope={archive_target_scope!r}"))
        required_make_routes = upgrade_policy.get("required_make_routes")
        if required_make_routes != ["phase2-toolchain", "phase2-validate"]:
            issues.append(("POLICY_MISMATCH", f"required_make_routes={required_make_routes!r}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_BOOTSTRAP_ARCHIVE_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(root, "scripts/zigux/check-zig-toolchain.py", "present\n")
    write_text(root, "scripts/zigux/check-lane05-local-first-archive-workflow.py", "present\n")
    write_text(root, "scripts/zigux/check-lane05-local-archive-readme.py", "present\n")
    write_text(
        root,
        POLICY,
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {
                    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
                },
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
        root,
        README,
        "\n".join(
            (
                "# Zigux third-party archives",
                "",
                "## Current pinned Zig archive contract",
                "",
                "- target: `x86_64-linux`",
                "- channel: `0.17.0-dev.87+9b177a7d2`",
                "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
                "- sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`",
                "",
                "## Rules",
                "- do not keep duplicate-suffix copies such as `zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz` in this directory",
            )
        )
        + "\n",
    )
    write_text(root, WORKFLOW, "name: zigux-bootstrap\n" + "\n".join(REQUIRED_WORKFLOW_LINES) + "\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_archive_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        write_text(root, README, read_text(root, README).replace(README_MARKERS[4] + "\n", "", 1))
        assert ("MISSING_ARCHIVE_README_MARKER", README_MARKERS[4]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), REQUIRED_WORKFLOW_LINES[1], "run: python3 scripts/zigux/other.py"))
        assert ("MISSING_WORKFLOW_LINE", REQUIRED_WORKFLOW_LINES[1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            WORKFLOW,
            "\n".join(
                (
                    "name: zigux-bootstrap",
                    REQUIRED_WORKFLOW_LINES[1],
                    REQUIRED_WORKFLOW_LINES[0],
                    *REQUIRED_WORKFLOW_LINES[2:],
                )
            )
            + "\n",
        )
        assert (
            "MISORDERED_WORKFLOW_PACKET",
            f"{REQUIRED_WORKFLOW_LINES[0]} -> {REQUIRED_WORKFLOW_LINES[-1]}",
        ) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        payload = load_policy(root)
        payload["archive_sha256"]["x86_64-linux"] = "0" * 64
        write_text(root, POLICY, json.dumps(payload, indent=2) + "\n")
        assert ("POLICY_MISMATCH", "archive_sha256.x86_64-linux='0000000000000000000000000000000000000000000000000000000000000000'") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        (root / "scripts/zigux/check-lane05-local-first-archive-workflow.py").unlink()
        assert ("MISSING_REQUIRED_PATH", "scripts/zigux/check-lane05-local-first-archive-workflow.py") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, POLICY, "{not-json}\n")
        issues = collect_issues(root)
        assert ("INVALID_POLICY_PAYLOAD", f"invalid JSON in {root / POLICY}: Expecting property name enclosed in double quotes") in issues
        checks += 1

    print("PHASE2_BOOTSTRAP_ARCHIVE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_ARCHIVE_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the live Zigux bootstrap archive packet stays aligned across workflow, toolchain policy, and pinned-archive notes."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--write-sample-root", type=Path, help="write a passing sample root for replay checks")
    parser.add_argument("--self-test", action="store_true", help="run built-in contract checks")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_ARCHIVE_PACKET=pass")
    print(f"PHASE2_BOOTSTRAP_ARCHIVE_PACKET_WORKFLOW_STEP_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_BOOTSTRAP_ARCHIVE_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
