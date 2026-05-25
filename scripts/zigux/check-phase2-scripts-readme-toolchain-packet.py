#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
README_PATH = Path("scripts/zigux/README.md")
POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")
CHECK_ZIG_TOOLCHAIN_PATH = Path("scripts/zigux/check-zig-toolchain.py")
INSTALL_ZIG_PATH = Path("scripts/zigux/install-zig.py")
STAGE_HELPER_PATH = Path("scripts/zigux/stage-pinned-zig-archive.py")
THIRD_PARTY_README_PATH = Path("third_party/README.md")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_PATH = Path("zigux/Makefile")

EXPECTED_ARCHIVE_SIZES = {
    "x86_64-linux": 58_159_088,
}

README_MARKERS = (
    "## Phase 2",
    "the live toolchain checker, installer helper, direct cross-route packet",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`third_party/README.md`, `scripts/zigux/stage-pinned-zig-archive.py`, `python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py`",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    "`Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, `make -C zigux phase2`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
)

CHECK_ZIG_TOOLCHAIN_MARKERS = (
    'parser.add_argument("--policy-only"',
    'parser.add_argument("--archive-only"',
    "def resolve_policy_archive(",
    "def iter_archive_search_roots(",
    'print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing")',
    'print("ZIG_TOOLCHAIN_STATUS=missing")',
)

INSTALL_ZIG_MARKERS = (
    "def load_policy_archive_sha256(",
    "def verify_archive_sha256(",
    "copy_url_to_file(tarball_url, archive_path)",
    "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
)

STAGE_HELPER_MARKERS = (
    'THIRD_PARTY_DIR = Path("third_party")',
    "EXPECTED_ARCHIVE_SIZES = {",
    'parser.add_argument("--parts-dir"',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}")',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_STATUS={status}")',
    'print("STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: make -C zigux phase2-toolchain",
)

MAKEFILE_LINES = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
)


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: Path, content: str) -> None:
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
    raise AssertionError(f"line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"line not found: {marker}")


def load_policy_contract(root: Path) -> dict[str, object]:
    policy_path = root / POLICY_PATH
    try:
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {policy_path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {policy_path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise SystemExit(f"invalid policy payload in required file: {policy_path}")

    channel = payload.get("channel")
    minimum_version = payload.get("minimum_version")
    archive_sha256 = payload.get("archive_sha256")
    upgrade_policy = payload.get("upgrade_policy")

    issues: list[tuple[str, str]] = []
    if not isinstance(channel, str) or not channel.strip():
        issues.append(("INVALID_POLICY_FIELD", "channel"))
    if not isinstance(minimum_version, str) or not minimum_version.strip():
        issues.append(("INVALID_POLICY_FIELD", "minimum_version"))
    if isinstance(channel, str) and isinstance(minimum_version, str) and channel.strip() != minimum_version.strip():
        issues.append(("POLICY_CHANNEL_MINIMUM_MISMATCH", f"{channel.strip()} != {minimum_version.strip()}"))
    if not isinstance(archive_sha256, dict) or not archive_sha256:
        issues.append(("INVALID_POLICY_FIELD", "archive_sha256"))
        raise SystemExit(json.dumps(issues))
    if not isinstance(upgrade_policy, dict):
        issues.append(("INVALID_POLICY_FIELD", "upgrade_policy"))
        raise SystemExit(json.dumps(issues))

    archive_targets = upgrade_policy.get("archive_target_scope")
    required_make_routes = upgrade_policy.get("required_make_routes")
    if not isinstance(archive_targets, list) or not archive_targets:
        issues.append(("INVALID_POLICY_FIELD", "archive_target_scope"))
    if not isinstance(required_make_routes, list) or not required_make_routes:
        issues.append(("INVALID_POLICY_FIELD", "required_make_routes"))
    if issues:
        raise SystemExit(json.dumps(issues))

    if len(archive_targets) != 1:
        raise SystemExit(json.dumps([("UNEXPECTED_ARCHIVE_TARGET_COUNT", str(len(archive_targets)))]))
    target = archive_targets[0]
    if not isinstance(target, str) or not target.strip():
        raise SystemExit(json.dumps([("INVALID_ARCHIVE_TARGET", "index=0")]))
    target = target.strip()
    digest = archive_sha256.get(target)
    if not isinstance(digest, str) or len(digest.strip()) != 64:
        raise SystemExit(json.dumps([("INVALID_ARCHIVE_SHA256", target)]))
    if target not in EXPECTED_ARCHIVE_SIZES:
        raise SystemExit(json.dumps([("MISSING_EXPECTED_ARCHIVE_SIZE", target)]))

    routes = [route.strip() for route in required_make_routes if isinstance(route, str) and route.strip()]
    if len(routes) != len(required_make_routes):
        raise SystemExit(json.dumps([("INVALID_POLICY_FIELD", "required_make_routes")]))

    return {
        "channel": channel.strip(),
        "target": target,
        "sha256": digest.strip(),
        "size": EXPECTED_ARCHIVE_SIZES[target],
        "filename": f"zig-{target}-{channel.strip()}.tar.xz",
        "required_make_routes": routes,
    }


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    try:
        contract = load_policy_contract(root)
    except SystemExit as exc:
        detail = str(exc)
        if detail.startswith("["):
            try:
                decoded = json.loads(detail)
                return [(code, value) for code, value in decoded]
            except json.JSONDecodeError:
                pass
        raise

    readme = read_text(root, README_PATH)
    check_zig_toolchain = read_text(root, CHECK_ZIG_TOOLCHAIN_PATH)
    install_zig = read_text(root, INSTALL_ZIG_PATH)
    stage_helper = read_text(root, STAGE_HELPER_PATH)
    workflow = read_text(root, WORKFLOW_PATH)
    makefile = read_text(root, MAKEFILE_PATH)
    third_party_readme = read_text(root, THIRD_PARTY_README_PATH)

    for marker in README_MARKERS:
        if marker not in readme:
            issues.append(("MISSING_README_MARKER", marker))

    for marker in CHECK_ZIG_TOOLCHAIN_MARKERS:
        if marker not in check_zig_toolchain:
            issues.append(("MISSING_CHECK_ZIG_TOOLCHAIN_MARKER", marker))

    for marker in INSTALL_ZIG_MARKERS:
        if marker not in install_zig:
            issues.append(("MISSING_INSTALL_ZIG_MARKER", marker))

    for marker in STAGE_HELPER_MARKERS:
        if marker not in stage_helper:
            issues.append(("MISSING_STAGE_HELPER_MARKER", marker))

    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif marker != "phase2-toolchain:" and count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    third_party_markers = (
        f"`{contract['target']}`",
        f"`{contract['channel']}`",
        f"`third_party/{contract['filename']}`",
        f"`{contract['sha256']}`",
        f"`{contract['size']}` bytes",
        f"--archive third_party/{contract['filename']} --archive-target {contract['target']}",
    )
    for marker in third_party_markers:
        if marker not in third_party_readme:
            issues.append(("MISSING_THIRD_PARTY_README_MARKER", marker))

    route_list = ",".join(contract["required_make_routes"])
    if route_list != "phase2-toolchain,phase2-tools,phase2-kconfig,phase2-cross,phase2-genksyms,phase2-fixdep,phase2-validate":
        issues.append(("UNEXPECTED_REQUIRED_MAKE_ROUTE_PACKET", route_list))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_SCRIPTS_README_TOOLCHAIN_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        root,
        POLICY_PATH,
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
    write_text(
        root,
        README_PATH,
        "\n".join(
            (
                "# scripts/zigux",
                "",
                "## Phase 2",
                "",
                "- Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet, `conf_bridge` and `confdata_bridge` helper surfaces, the restored closure-side validator packet, the manifest-backed kconfig fixture roster, the shipped make-wrapper packet, and the surviving Phase 2 alignment guards instead of replaying older missing-route assumptions inside that now-rematerialized toolchain packet",
                "- `.github/workflows/zigux-bootstrap.yml`, `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` keep the shipped pinned Zig toolchain guard explicit in the live bootstrap action path before the surviving Phase 2 bridge and pinning checks",
                "- `third_party/README.md`, `scripts/zigux/stage-pinned-zig-archive.py`, `python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` keep the staged repo-local archive helper, contract, and self-test packet explicit from the scripts root beside that same shipped Lane 05 local-first archive path",
                "- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, `make -C zigux phase2`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set",
                "- `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`, so keep those installer and direct cross-route surfaces explicit beside the shipped toolchain and kbuild reminder packet instead of leaving them in repo-reality-gap wording",
            )
        )
        + "\n",
    )
    write_text(
        root,
        CHECK_ZIG_TOOLCHAIN_PATH,
        "\n".join(
            (
                'parser.add_argument("--policy-only", action="store_true")',
                'parser.add_argument("--archive-only", action="store_true")',
                "def resolve_policy_archive():",
                "    pass",
                "def iter_archive_search_roots():",
                "    pass",
                'print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing")',
                'print("ZIG_TOOLCHAIN_STATUS=missing")',
            )
        )
        + "\n",
    )
    write_text(
        root,
        INSTALL_ZIG_PATH,
        "\n".join(
            (
                "def load_policy_archive_sha256(policy_path, target_key):",
                "    return None",
                "def verify_archive_sha256(path, expected):",
                "    return expected",
                "copy_url_to_file(tarball_url, archive_path)",
                "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
                "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
            )
        )
        + "\n",
    )
    write_text(
        root,
        STAGE_HELPER_PATH,
        "\n".join(
            (
                'THIRD_PARTY_DIR = Path("third_party")',
                "EXPECTED_ARCHIVE_SIZES = {",
                '    "x86_64-linux": 58159088,',
                "}",
                'parser.add_argument("--parts-dir", type=Path)',
                'print(f"STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}")',
                'print(f"STAGE_PINNED_ZIG_ARCHIVE_STATUS={status}")',
                'print("STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
            )
        )
        + "\n",
    )
    write_text(
        root,
        THIRD_PARTY_README_PATH,
        "\n".join(
            (
                "# Zigux third-party archives",
                "- target: `x86_64-linux`",
                "- channel: `0.17.0-dev.87+9b177a7d2`",
                "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
                "- sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`",
                "- size: `58159088` bytes",
                "- `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
            )
        )
        + "\n",
    )
    write_text(root, WORKFLOW_PATH, "\n".join(("name: zigux-bootstrap", *WORKFLOW_LINES)) + "\n")
    write_text(root, MAKEFILE_PATH, "\n".join(MAKEFILE_LINES) + "\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="phase2_scripts_readme_toolchain_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            README_PATH,
            read_text(root, README_PATH).replace("installer helper, ", "", 1),
        )
        assert ("MISSING_README_MARKER", "the live toolchain checker, installer helper, direct cross-route packet") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            WORKFLOW_PATH,
            replace_exact_line(
                read_text(root, WORKFLOW_PATH),
                "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
                "run: python3 scripts/zigux/check-zig-toolchain.py --policy-missing",
            ),
        )
        assert ("MISSING_WORKFLOW_LINE", "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW_PATH, duplicate_exact_line(read_text(root, WORKFLOW_PATH), WORKFLOW_LINES[2]))
        assert ("DUPLICATE_WORKFLOW_LINE", f"{WORKFLOW_LINES[2]}:count=2") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            MAKEFILE_PATH,
            replace_exact_line(
                read_text(root, MAKEFILE_PATH),
                "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --missing",
            ),
        )
        assert ("MISSING_MAKEFILE_LINE", "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            CHECK_ZIG_TOOLCHAIN_PATH,
            read_text(root, CHECK_ZIG_TOOLCHAIN_PATH).replace("def resolve_policy_archive():\n", "", 1),
        )
        assert ("MISSING_CHECK_ZIG_TOOLCHAIN_MARKER", "def resolve_policy_archive(") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            INSTALL_ZIG_PATH,
            read_text(root, INSTALL_ZIG_PATH).replace(
                "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)\n",
                "",
                1,
            ),
        )
        assert ("MISSING_INSTALL_ZIG_MARKER", "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            STAGE_HELPER_PATH,
            read_text(root, STAGE_HELPER_PATH).replace('print(f"STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}")\n', "", 1),
        )
        assert ("MISSING_STAGE_HELPER_MARKER", 'print(f"STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}")') in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            THIRD_PARTY_README_PATH,
            read_text(root, THIRD_PARTY_README_PATH).replace(
                "`third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
                "`third_party/zig-bad.tar.xz`",
                1,
            ),
        )
        assert ("MISSING_THIRD_PARTY_README_MARKER", "`third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            POLICY_PATH,
            read_text(root, POLICY_PATH).replace(
                '"archive_target_scope": [\n      "x86_64-linux"\n    ]',
                '"archive_target_scope": [\n      "x86_64-linux",\n      "aarch64-linux"\n    ]',
                1,
            ),
        )
        assert ("UNEXPECTED_ARCHIVE_TARGET_COUNT", "2") in collect_issues(root)
        checks += 1

    print("PHASE2_SCRIPTS_README_TOOLCHAIN_PACKET_SELF_TEST=pass")
    print(f"PHASE2_SCRIPTS_README_TOOLCHAIN_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the scripts-root Phase 2 reminder packet stays aligned with the current toolchain and staged-archive surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_SCRIPTS_README_TOOLCHAIN_PACKET=pass")
    print(f"PHASE2_SCRIPTS_README_MARKER_COUNT={len(README_MARKERS)}")
    print(f"PHASE2_SCRIPTS_README_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_SCRIPTS_README_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())