#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
POLICY = "scripts/zigux/zig-toolchain-policy.json"
BOOTSTRAP_NOTES = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
SCRIPTS_README = "scripts/zigux/README.md"
MAKEFILE = "zigux/Makefile"
THIRD_PARTY_README = "third_party/README.md"

EXPECTED_PHASE = "Phase 2"
EXPECTED_CHANNEL = "0.17.0-dev.87+9b177a7d2"
EXPECTED_TARGET = "x86_64-linux"
EXPECTED_REQUIRED_ROUTES = ("phase2-toolchain", "phase2-validate", "phase2-cross")

WORKFLOW_SETUP_MARKERS = (
    "- name: Setup pinned Zig toolchain",
    'policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
    'filename = f"zig-{target}-{channel}.tar.xz"',
    'url = f"https://ziglang.org/builds/{filename}"',
    'archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"',
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    'repo_archive_parts_dir="${repo_archive_path}.parts"',
    'python3 scripts/zigux/stage-pinned-zig-archive.py                 --root "$GITHUB_WORKSPACE"                 --parts-dir "$repo_archive_parts_dir" || return 1',
    'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
    'if curl -L --fail "$url" -o "$archive_path"; then',
    'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
    'if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then',
    'if try_download "$ZIGUX_ZIG_URL"; then',
    "echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2",
)

WORKFLOW_HOOK_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: make -C zigux phase2-toolchain",
)

MAKEFILE_MARKERS = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
)

NOTES_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py` is directly readable on current `master` and keeps the pinned-channel probe, repo-local `.zig-toolchain` fallback, and archive-integrity validation surface explicit beside the reminder guards.",
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/stage-pinned-zig-archive.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` are directly readable on current `master` and keep the pinned-channel archive download, staged repo-local archive materialization, archive-verification, helper-contract, helper-selftest, and install-root replay path explicit beside the reminder guards.",
    "`.github/workflows/zigux-bootstrap.yml` also derives `ZIGUX_ZIG_TARGET`, `ZIGUX_ZIG_FILENAME`, and `ZIGUX_ZIG_URL` from `scripts/zigux/zig-toolchain-policy.json`, tries `community-mirrors.txt` before the direct Zig download URL, and reruns `python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"` inside each install attempt so the pinned bootstrap setup path stays reviewable at the same policy-driven boundary as the later reminder hooks.",
)

README_MARKERS = (
    "`.github/workflows/zigux-bootstrap.yml`, `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` keep the shipped pinned Zig toolchain guard explicit in the live bootstrap action path before the surviving Phase 2 bridge and pinning checks",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`, so keep those installer and direct cross-route surfaces explicit beside the shipped toolchain and kbuild reminder packet instead of leaving them in repo-reality-gap wording",
)

THIRD_PARTY_MARKERS = (
    "`third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "duplicate-copy boundary",
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


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_policy_issues(root: Path) -> list[tuple[str, str]]:
    payload = json.loads(read_text(resolve(root, POLICY)))
    if not isinstance(payload, dict):
        return [("INVALID_POLICY_PAYLOAD", type(payload).__name__)]

    issues: list[tuple[str, str]] = []
    if payload.get("phase") != EXPECTED_PHASE:
        issues.append(("POLICY_PHASE_MISMATCH", repr(payload.get("phase"))))
    if payload.get("channel") != EXPECTED_CHANNEL:
        issues.append(("POLICY_CHANNEL_MISMATCH", repr(payload.get("channel"))))
    if payload.get("minimum_version") != EXPECTED_CHANNEL:
        issues.append(("POLICY_MINIMUM_VERSION_MISMATCH", repr(payload.get("minimum_version"))))

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict) or list(archive_sha256.keys()) != [EXPECTED_TARGET]:
        issues.append(("POLICY_ARCHIVE_SCOPE_MISMATCH", repr(archive_sha256)))

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("INVALID_UPGRADE_POLICY", type(upgrade_policy).__name__))
        return issues

    if upgrade_policy.get("channel_minimum_lockstep") is not True:
        issues.append(("POLICY_LOCKSTEP_MISMATCH", repr(upgrade_policy.get("channel_minimum_lockstep"))))
    if upgrade_policy.get("archive_target_scope") != [EXPECTED_TARGET]:
        issues.append(("POLICY_ARCHIVE_TARGET_SCOPE_MISMATCH", repr(upgrade_policy.get("archive_target_scope"))))
    if tuple(upgrade_policy.get("required_make_routes", ())) != EXPECTED_REQUIRED_ROUTES:
        issues.append(("POLICY_REQUIRED_MAKE_ROUTES_MISMATCH", repr(upgrade_policy.get("required_make_routes"))))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    workflow = read_text(resolve(root, WORKFLOW))
    makefile = read_text(resolve(root, MAKEFILE))
    notes = read_text(resolve(root, BOOTSTRAP_NOTES))
    scripts_readme = read_text(resolve(root, SCRIPTS_README))
    third_party = read_text(resolve(root, THIRD_PARTY_README))

    issues.extend(collect_missing_markers(workflow, WORKFLOW_SETUP_MARKERS, "MISSING_WORKFLOW_SETUP_MARKERS"))
    for marker in WORKFLOW_HOOK_LINES:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOK_LINES", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOK_LINES", f"{marker}:count={count}"))

    for marker in MAKEFILE_MARKERS:
        count = count_exact_lines(makefile, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_MARKERS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_MARKERS", f"{marker}:count={count}"))

    issues.extend(collect_missing_markers(notes, NOTES_MARKERS, "MISSING_BOOTSTRAP_NOTES_MARKERS"))
    issues.extend(collect_missing_markers(scripts_readme, README_MARKERS, "MISSING_SCRIPTS_README_MARKERS"))
    issues.extend(collect_missing_markers(third_party, THIRD_PARTY_MARKERS, "MISSING_THIRD_PARTY_MARKERS"))
    issues.extend(collect_policy_issues(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_BOOTSTRAP_TOOLCHAIN_SETUP_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(resolve(root, WORKFLOW), "\n".join((*WORKFLOW_SETUP_MARKERS, *WORKFLOW_HOOK_LINES)) + "\n")
    write_text(resolve(root, MAKEFILE), "\n".join(MAKEFILE_MARKERS) + "\n")
    write_text(resolve(root, BOOTSTRAP_NOTES), "\n".join(NOTES_MARKERS) + "\n")
    write_text(resolve(root, SCRIPTS_README), "\n".join(README_MARKERS) + "\n")
    write_text(resolve(root, THIRD_PARTY_README), "\n".join(THIRD_PARTY_MARKERS) + "\n")
    write_text(
        resolve(root, POLICY),
        json.dumps(
            {
                "phase": EXPECTED_PHASE,
                "channel": EXPECTED_CHANNEL,
                "minimum_version": EXPECTED_CHANNEL,
                "archive_sha256": {EXPECTED_TARGET: "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": [EXPECTED_TARGET],
                    "required_make_routes": list(EXPECTED_REQUIRED_ROUTES),
                },
            },
            indent=2,
        )
        + "\n",
    )


def replace_once(text: str, marker: str, replacement: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks = 0
    expected = 10

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_toolchain_setup_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_self_test_root(root)
        path = resolve(root, WORKFLOW)
        path.write_text(replace_once(path.read_text(encoding="utf-8"), WORKFLOW_SETUP_MARKERS[7], ""), encoding="utf-8")
        assert ("MISSING_WORKFLOW_SETUP_MARKERS", WORKFLOW_SETUP_MARKERS[7]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        path = resolve(root, WORKFLOW)
        marker = WORKFLOW_HOOK_LINES[0]
        path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
        assert ("DUPLICATE_WORKFLOW_HOOK_LINES", f"{marker}:count=2") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        path = resolve(root, MAKEFILE)
        path.write_text(replace_once(path.read_text(encoding="utf-8"), MAKEFILE_MARKERS[8], ""), encoding="utf-8")
        assert ("MISSING_MAKEFILE_MARKERS", MAKEFILE_MARKERS[8]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        path = resolve(root, BOOTSTRAP_NOTES)
        path.write_text(replace_once(path.read_text(encoding="utf-8"), NOTES_MARKERS[2], ""), encoding="utf-8")
        assert ("MISSING_BOOTSTRAP_NOTES_MARKERS", NOTES_MARKERS[2]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        path = resolve(root, SCRIPTS_README)
        path.write_text(replace_once(path.read_text(encoding="utf-8"), README_MARKERS[0], ""), encoding="utf-8")
        assert ("MISSING_SCRIPTS_README_MARKERS", README_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        path = resolve(root, THIRD_PARTY_README)
        path.write_text(replace_once(path.read_text(encoding="utf-8"), THIRD_PARTY_MARKERS[1], ""), encoding="utf-8")
        assert ("MISSING_THIRD_PARTY_MARKERS", THIRD_PARTY_MARKERS[1]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        path = resolve(root, POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "POLICY_REQUIRED_MAKE_ROUTES_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        path = resolve(root, POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["minimum_version"] = "0.16.0"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "POLICY_MINIMUM_VERSION_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        resolve(root, WORKFLOW).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks += 1
        else:
            raise AssertionError("missing workflow did not abort")

    assert checks == expected
    print("PHASE2_BOOTSTRAP_TOOLCHAIN_SETUP_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_SETUP_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the pinned bootstrap toolchain setup packet stays aligned across workflow, policy, and reminder surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_TOOLCHAIN_SETUP_PACKET=pass")
    print("PHASE2_BOOTSTRAP_TOOLCHAIN_SETUP_REQUIRED_ROUTE_LIST=" + ",".join(EXPECTED_REQUIRED_ROUTES))
    print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_SETUP_WORKFLOW_HOOK_COUNT={len(WORKFLOW_HOOK_LINES)}")
    print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_SETUP_MARKER_COUNT={len(WORKFLOW_SETUP_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
