#!/usr/bin/env python3
"""Guard the shared Phase 2 bootstrap toolchain reminder packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
DOCS_ROOT = "Documentation/zigux/README.md"
BOOTSTRAP_NOTES = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
REVIEW_CHECKLIST = "Documentation/zigux/review-checklist.md"
SCRIPTS_README = "scripts/zigux/README.md"
TESTS_README = "zigux/tests/README.md"
MAKEFILE = "zigux/Makefile"
THIRD_PARTY_README = "third_party/README.md"
POLICY = "scripts/zigux/zig-toolchain-policy.json"
CHECK_ZIG_TOOLCHAIN = "scripts/zigux/check-zig-toolchain.py"
INSTALL_ZIG = "scripts/zigux/install-zig.py"
STAGE_ARCHIVE = "scripts/zigux/stage-pinned-zig-archive.py"
PIN_SCOPE_CHECKER = "scripts/zigux/check-phase2-toolchain-pin-scope.py"
TOOLCHAIN_PINNING_CHECKER = "scripts/zigux/check-phase2-toolchain-pinning.py"
TESTS_ALIGNMENT_CHECKER = "scripts/zigux/check-phase2-tests-readme-alignment.py"
LOCAL_ARCHIVE_WORKFLOW_CHECKER = "scripts/zigux/check-lane05-local-first-archive-workflow.py"
LOCAL_ARCHIVE_README_CHECKER = "scripts/zigux/check-lane05-local-archive-readme.py"
ARCHIVE_VERIFICATION_CHECKER = "scripts/zigux/check-lane05-install-zig-archive-verification.py"
STAGE_HELPER_CONTRACT_CHECKER = "scripts/zigux/check-lane05-stage-helper-contract.py"
STAGE_HELPER_SELFTEST_CHECKER = "scripts/zigux/check-lane05-stage-helper-selftest.py"

REQUIRED_PATHS = (
    WORKFLOW,
    DOCS_ROOT,
    BOOTSTRAP_NOTES,
    REVIEW_CHECKLIST,
    SCRIPTS_README,
    TESTS_README,
    MAKEFILE,
    THIRD_PARTY_README,
    POLICY,
    CHECK_ZIG_TOOLCHAIN,
    INSTALL_ZIG,
    STAGE_ARCHIVE,
    PIN_SCOPE_CHECKER,
    TOOLCHAIN_PINNING_CHECKER,
    TESTS_ALIGNMENT_CHECKER,
    LOCAL_ARCHIVE_WORKFLOW_CHECKER,
    LOCAL_ARCHIVE_README_CHECKER,
    ARCHIVE_VERIFICATION_CHECKER,
    STAGE_HELPER_CONTRACT_CHECKER,
    STAGE_HELPER_SELFTEST_CHECKER,
)

EXPECTED_POLICY_PHASE = "Phase 2"
EXPECTED_CHANNEL = "0.17.0-dev.87+9b177a7d2"
EXPECTED_TARGET = "x86_64-linux"
EXPECTED_ARCHIVE_SHA256 = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
EXPECTED_REQUIRED_ROUTES = ["phase2-toolchain", "phase2-validate", "phase2-cross"]
EXPECTED_SELF_TEST_CASE_COUNT = 12

WORKFLOW_MARKERS = (
    "- name: Setup pinned Zig toolchain",
    "- name: Self-test current Zig toolchain checker",
    "- name: Check current Zig toolchain policy packet",
    "- name: Check current pinned Zig archive packet",
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
)

MAKEFILE_MARKERS = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
)

THIRD_PARTY_MARKERS = (
    "target: `x86_64-linux`",
    "channel: `0.17.0-dev.87+9b177a7d2`",
    "file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL",
)

BOOTSTRAP_NOTES_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py` is directly readable on current `master` and keeps the pinned-channel probe, repo-local `.zig-toolchain` fallback, and archive-integrity validation surface explicit beside the reminder guards.",
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/stage-pinned-zig-archive.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` are directly readable on current `master`",
    "tries `community-mirrors.txt` before the direct Zig download URL",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2-cross`",
)

DOCS_ROOT_MARKERS = (
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-validate",
    "make -C zigux phase2-cross",
)

REVIEW_CHECKLIST_MARKERS = (
    "if the change touches the shared Phase 2 toolchain packet",
    "third_party/README.md",
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/install-zig.py",
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-validate",
    "make -C zigux phase2-cross",
)

SCRIPTS_README_MARKERS = (
    "`check-zig-toolchain.py`, `install-zig.py`, `validate-phase2.py`, `validate-phase2-closure.py`, `check-phase2-toolchain-pin-scope.py`",
    "`phase2-toolchain`, `phase2-validate`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, and `phase2` route inventory",
    "Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet",
    "`scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
)

TESTS_README_MARKERS = (
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux",
    "python3 scripts/zigux/install-zig.py --self-test",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-validate",
    "make -C zigux phase2-cross",
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


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def load_policy(root: Path) -> dict[str, object]:
    payload = json.loads(read_text(resolve(root, POLICY)))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid toolchain policy payload in {resolve(root, POLICY)}: expected object")
    return payload


def validate_policy(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    payload = load_policy(root)
    if payload.get("phase") != EXPECTED_POLICY_PHASE:
        issues.append(("POLICY_PHASE_MISMATCH", repr(payload.get("phase"))))
    if payload.get("channel") != EXPECTED_CHANNEL:
        issues.append(("POLICY_CHANNEL_MISMATCH", repr(payload.get("channel"))))
    if payload.get("minimum_version") != EXPECTED_CHANNEL:
        issues.append(("POLICY_MINIMUM_VERSION_MISMATCH", repr(payload.get("minimum_version"))))
    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict):
        issues.append(("POLICY_ARCHIVE_SHA_INVALID", repr(archive_sha256)))
    elif archive_sha256.get(EXPECTED_TARGET) != EXPECTED_ARCHIVE_SHA256:
        issues.append(("POLICY_ARCHIVE_SHA_MISMATCH", repr(archive_sha256.get(EXPECTED_TARGET))))
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("POLICY_UPGRADE_POLICY_INVALID", repr(upgrade_policy)))
        return issues
    if upgrade_policy.get("channel_minimum_lockstep") is not True:
        issues.append(("POLICY_LOCKSTEP_MISMATCH", repr(upgrade_policy.get("channel_minimum_lockstep"))))
    if upgrade_policy.get("archive_target_scope") != [EXPECTED_TARGET]:
        issues.append(("POLICY_ARCHIVE_TARGET_SCOPE_MISMATCH", repr(upgrade_policy.get("archive_target_scope"))))
    if upgrade_policy.get("required_make_routes") != EXPECTED_REQUIRED_ROUTES:
        issues.append(("POLICY_REQUIRED_ROUTES_MISMATCH", repr(upgrade_policy.get("required_make_routes"))))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_PATHS:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    issues.extend(validate_policy(root))
    issues.extend(collect_missing_markers(read_text(resolve(root, WORKFLOW)), WORKFLOW_MARKERS, "MISSING_WORKFLOW_MARKER"))
    issues.extend(collect_missing_markers(read_text(resolve(root, MAKEFILE)), MAKEFILE_MARKERS, "MISSING_MAKEFILE_MARKER"))
    issues.extend(collect_missing_markers(read_text(resolve(root, THIRD_PARTY_README)), THIRD_PARTY_MARKERS, "MISSING_THIRD_PARTY_MARKER"))
    issues.extend(collect_missing_markers(read_text(resolve(root, BOOTSTRAP_NOTES)), BOOTSTRAP_NOTES_MARKERS, "MISSING_BOOTSTRAP_NOTES_MARKER"))
    issues.extend(collect_missing_markers(read_text(resolve(root, DOCS_ROOT)), DOCS_ROOT_MARKERS, "MISSING_DOCS_ROOT_MARKER"))
    issues.extend(collect_missing_markers(read_text(resolve(root, REVIEW_CHECKLIST)), REVIEW_CHECKLIST_MARKERS, "MISSING_REVIEW_CHECKLIST_MARKER"))
    issues.extend(collect_missing_markers(read_text(resolve(root, SCRIPTS_README)), SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKER"))
    issues.extend(collect_missing_markers(read_text(resolve(root, TESTS_README)), TESTS_README_MARKERS, "MISSING_TESTS_README_MARKER"))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_BOOTSTRAP_TOOLCHAIN_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    for rel in REQUIRED_PATHS:
        write_text(resolve(root, rel), "placeholder\n")

    write_text(
        resolve(root, POLICY),
        json.dumps(
            {
                "phase": EXPECTED_POLICY_PHASE,
                "channel": EXPECTED_CHANNEL,
                "minimum_version": EXPECTED_CHANNEL,
                "archive_sha256": {EXPECTED_TARGET: EXPECTED_ARCHIVE_SHA256},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": [EXPECTED_TARGET],
                    "required_make_routes": EXPECTED_REQUIRED_ROUTES,
                },
            },
            indent=2,
        )
        + "\n",
    )

    write_text(resolve(root, WORKFLOW), "\n".join(WORKFLOW_MARKERS) + "\n")
    write_text(resolve(root, MAKEFILE), "\n".join(MAKEFILE_MARKERS) + "\n")
    write_text(resolve(root, THIRD_PARTY_README), "\n".join(THIRD_PARTY_MARKERS) + "\n")
    write_text(resolve(root, BOOTSTRAP_NOTES), "# Notes\n\n" + "\n".join(BOOTSTRAP_NOTES_MARKERS) + "\n")
    write_text(resolve(root, DOCS_ROOT), "# Docs Root\n\n" + "\n".join(DOCS_ROOT_MARKERS) + "\n")
    write_text(resolve(root, REVIEW_CHECKLIST), "# Checklist\n\n" + "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(resolve(root, SCRIPTS_README), "# Scripts\n\n" + "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(resolve(root, TESTS_README), "# Tests\n\n" + "\n".join(TESTS_README_MARKERS) + "\n")


def replace_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def replace_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_toolchain_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        workflow_path = resolve(root, WORKFLOW)
        workflow_path.write_text(
            replace_once(workflow_path.read_text(encoding="utf-8"), WORKFLOW_MARKERS[4]),
            encoding="utf-8",
        )
        assert ("MISSING_WORKFLOW_MARKER", WORKFLOW_MARKERS[4]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        makefile_path = resolve(root, MAKEFILE)
        makefile_path.write_text(
            replace_exact_line(makefile_path.read_text(encoding="utf-8"), MAKEFILE_MARKERS[5]),
            encoding="utf-8",
        )
        assert ("MISSING_MAKEFILE_MARKER", MAKEFILE_MARKERS[5]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        readme_path = resolve(root, THIRD_PARTY_README)
        readme_path.write_text(
            replace_once(readme_path.read_text(encoding="utf-8"), THIRD_PARTY_MARKERS[3]),
            encoding="utf-8",
        )
        assert ("MISSING_THIRD_PARTY_MARKER", THIRD_PARTY_MARKERS[3]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        notes_path = resolve(root, BOOTSTRAP_NOTES)
        notes_path.write_text(
            replace_once(notes_path.read_text(encoding="utf-8"), BOOTSTRAP_NOTES_MARKERS[2]),
            encoding="utf-8",
        )
        assert ("MISSING_BOOTSTRAP_NOTES_MARKER", BOOTSTRAP_NOTES_MARKERS[2]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        docs_root_path = resolve(root, DOCS_ROOT)
        docs_root_path.write_text(
            replace_once(docs_root_path.read_text(encoding="utf-8"), DOCS_ROOT_MARKERS[7]),
            encoding="utf-8",
        )
        assert ("MISSING_DOCS_ROOT_MARKER", DOCS_ROOT_MARKERS[7]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        checklist_path = resolve(root, REVIEW_CHECKLIST)
        checklist_path.write_text(
            replace_once(checklist_path.read_text(encoding="utf-8"), REVIEW_CHECKLIST_MARKERS[10]),
            encoding="utf-8",
        )
        assert ("MISSING_REVIEW_CHECKLIST_MARKER", REVIEW_CHECKLIST_MARKERS[10]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        scripts_readme_path = resolve(root, SCRIPTS_README)
        scripts_readme_path.write_text(
            replace_once(scripts_readme_path.read_text(encoding="utf-8"), SCRIPTS_README_MARKERS[2]),
            encoding="utf-8",
        )
        assert ("MISSING_SCRIPTS_README_MARKER", SCRIPTS_README_MARKERS[2]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        tests_readme_path = resolve(root, TESTS_README)
        tests_readme_path.write_text(
            replace_once(tests_readme_path.read_text(encoding="utf-8"), TESTS_README_MARKERS[9]),
            encoding="utf-8",
        )
        assert ("MISSING_TESTS_README_MARKER", TESTS_README_MARKERS[9]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        policy_path = resolve(root, POLICY)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["minimum_version"] = "0.16.0"
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "POLICY_MINIMUM_VERSION_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        policy_path = resolve(root, POLICY)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "POLICY_REQUIRED_ROUTES_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        resolve(root, INSTALL_ZIG).unlink()
        assert ("MISSING_REQUIRED_PATH", INSTALL_ZIG) in collect_issues(root)
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_BOOTSTRAP_TOOLCHAIN_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the shared Phase 2 bootstrap toolchain packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a passing current-like sample root and exit",
    )
    parser.add_argument("--self-test", action="store_true", help="run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print("PHASE2_BOOTSTRAP_TOOLCHAIN_PACKET_SAMPLE_ROOT=pass")
        print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_PACKET_SAMPLE_ROOT_PATH={args.write_sample_root.resolve()}")
        return 0

    root = args.root.resolve()
    issues = collect_issues(root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_TOOLCHAIN_PACKET=pass")
    print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_PACKET_ROOT={root}")
    print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_PACKET_REQUIRED_ROUTE_COUNT={len(EXPECTED_REQUIRED_ROUTES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
