#!/usr/bin/env python3
"""Guard the current directly readable Phase 2 install-zig helper packet."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
INSTALL_ZIG = ROOT / "scripts" / "zigux" / "install-zig.py"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
DOCS_README = ROOT / "Documentation" / "zigux" / "README.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

INSTALL_ZIG_MARKERS = (
    "INDEX_URL = 'https://ziglang.org/download/index.json'",
    "TOOLCHAIN_POLICY = ROOT / 'scripts' / 'zigux' / 'zig-toolchain-policy.json'",
    "def load_policy_channel(",
    "def load_policy_archive_sha256(",
    "def verify_archive_sha256(",
    "def resolve_target(",
    "def copy_url_to_file(",
    "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
    "print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')",
    "print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')",
    "parser.add_argument('--resolve-only', action='store_true', help='Resolve and print the chosen archive without downloading')",
    "parser.add_argument('--self-test', action='store_true', help='Run built-in target-resolution coverage without downloading')",
    "channel = args.channel or policy_channel",
)

WORKFLOW_MARKERS = (
    "run: python3 scripts/zigux/install-zig.py --self-test",
)

PHASE2_NOTES_MARKERS = (
    "`scripts/zigux/install-zig.py` is directly readable on current `master`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
)

PHASE2_CLOSURE_MARKERS = (
    "- `scripts/zigux/install-zig.py`",
    "- `python3 scripts/zigux/install-zig.py --self-test`",
)

DOCS_README_MARKERS = (
    "- `scripts/zigux/install-zig.py`",
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again, so keep the installer and direct cross-route packet explicit beside the shipped toolchain, kconfig, genksyms, and make-wrapper surfaces instead of leaving them in historical-gap wording.",
)

REVIEW_CHECKLIST_MARKERS = (
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
)

SCRIPTS_README_MARKERS = (
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`",
)

TESTS_README_MARKERS = (
    "- `scripts/zigux/install-zig.py`",
    "Keep the current toolchain self-check and replay surface explicit through `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/install-zig.py --self-test`, and `python3 scripts/zigux/check-phase2-cross.py --self-test`.",
)

FORBIDDEN_INSTALLER_GAP_MARKERS = (
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` stay framed as historical packet members rather than shipped current-`master` evidence",
)

EXPECTED_POLICY_CHANNEL = "0.17.0-dev.87+9b177a7d2"
EXPECTED_POLICY_ARCHIVE_SHA = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


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


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def load_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc.msg}") from exc


def collect_policy_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    payload = load_json(resolve_path(root, POLICY))
    if not isinstance(payload, dict):
        return [("INVALID_POLICY_PAYLOAD", type(payload).__name__)]

    if payload.get("phase") != "Phase 2":
        issues.append(("POLICY_FIELD_MISMATCH", "phase"))
    if payload.get("channel") != EXPECTED_POLICY_CHANNEL:
        issues.append(("POLICY_FIELD_MISMATCH", "channel"))
    if payload.get("minimum_version") != EXPECTED_POLICY_CHANNEL:
        issues.append(("POLICY_FIELD_MISMATCH", "minimum_version"))

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict):
        issues.append(("INVALID_POLICY_ARCHIVE_SHA256", type(archive_sha256).__name__))
        return issues
    if sorted(archive_sha256) != ["x86_64-linux"]:
        issues.append(("POLICY_ARCHIVE_TARGETS_MISMATCH", repr(sorted(archive_sha256))))
    digest = archive_sha256.get("x86_64-linux")
    if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
        issues.append(("INVALID_POLICY_ARCHIVE_DIGEST", repr(digest)))
    elif digest != EXPECTED_POLICY_ARCHIVE_SHA:
        issues.append(("POLICY_ARCHIVE_DIGEST_MISMATCH", digest))

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("INVALID_UPGRADE_POLICY", type(upgrade_policy).__name__))
        return issues
    if upgrade_policy.get("channel_minimum_lockstep") is not True:
        issues.append(("POLICY_UPGRADE_FIELD_MISMATCH", "channel_minimum_lockstep"))
    if upgrade_policy.get("archive_target_scope") != ["x86_64-linux"]:
        issues.append(("POLICY_UPGRADE_FIELD_MISMATCH", "archive_target_scope"))
    if upgrade_policy.get("required_make_routes") != ["phase2-toolchain", "phase2-validate"]:
        issues.append(("POLICY_UPGRADE_FIELD_MISMATCH", "required_make_routes"))
    return issues


def collect_tool_manifest_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    payload = load_json(resolve_path(root, TOOL_MANIFEST))
    if not isinstance(payload, dict):
        return [("INVALID_TOOL_MANIFEST_PAYLOAD", type(payload).__name__)]

    if payload.get("workflow") != ".github/workflows/zigux-bootstrap.yml":
        issues.append(("TOOL_MANIFEST_WORKFLOW_MISMATCH", repr(payload.get("workflow"))))

    present_surfaces = payload.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        return issues + [("INVALID_TOOL_MANIFEST_PRESENT_SURFACES", type(present_surfaces).__name__)]

    bootstrap_helpers = present_surfaces.get("bootstrap_helpers")
    if bootstrap_helpers != ["scripts/zigux/install-zig.py"]:
        issues.append(("TOOL_MANIFEST_BOOTSTRAP_HELPERS_MISMATCH", repr(bootstrap_helpers)))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    install_zig_text = read_text(resolve_path(root, INSTALL_ZIG))
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    notes_text = read_text(resolve_path(root, PHASE2_NOTES))
    closure_text = read_text(resolve_path(root, PHASE2_CLOSURE))
    docs_readme_text = read_text(resolve_path(root, DOCS_README))
    review_text = read_text(resolve_path(root, REVIEW_CHECKLIST))
    scripts_readme_text = read_text(resolve_path(root, SCRIPTS_README))
    tests_readme_text = read_text(resolve_path(root, TESTS_README))

    issues.extend(collect_missing_markers(install_zig_text, INSTALL_ZIG_MARKERS, "MISSING_INSTALL_ZIG_MARKERS"))
    for marker in WORKFLOW_MARKERS:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_MARKERS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_MARKERS", f"{marker}:count={count}"))
    issues.extend(collect_missing_markers(notes_text, PHASE2_NOTES_MARKERS, "MISSING_PHASE2_NOTES_MARKERS"))
    issues.extend(collect_missing_markers(closure_text, PHASE2_CLOSURE_MARKERS, "MISSING_PHASE2_CLOSURE_MARKERS"))
    issues.extend(collect_missing_markers(docs_readme_text, DOCS_README_MARKERS, "MISSING_DOCS_README_MARKERS"))
    issues.extend(collect_missing_markers(review_text, REVIEW_CHECKLIST_MARKERS, "MISSING_REVIEW_CHECKLIST_MARKERS"))
    issues.extend(collect_missing_markers(scripts_readme_text, SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKERS"))
    issues.extend(collect_missing_markers(tests_readme_text, TESTS_README_MARKERS, "MISSING_TESTS_README_MARKERS"))

    for text, code in (
        (notes_text, "FORBIDDEN_PHASE2_NOTES_MARKERS"),
        (docs_readme_text, "FORBIDDEN_DOCS_README_MARKERS"),
        (review_text, "FORBIDDEN_REVIEW_CHECKLIST_MARKERS"),
        (scripts_readme_text, "FORBIDDEN_SCRIPTS_README_MARKERS"),
        (tests_readme_text, "FORBIDDEN_TESTS_README_MARKERS"),
    ):
        issues.extend(collect_forbidden_markers(text, FORBIDDEN_INSTALLER_GAP_MARKERS, code))

    issues.extend(collect_policy_issues(root))
    issues.extend(collect_tool_manifest_issues(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_INSTALL_ZIG_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, INSTALL_ZIG), "\n".join(INSTALL_ZIG_MARKERS) + "\n")
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_MARKERS) + "\n")
    write_text(resolve_path(root, PHASE2_NOTES), "\n".join(PHASE2_NOTES_MARKERS) + "\n")
    write_text(resolve_path(root, PHASE2_CLOSURE), "\n".join(PHASE2_CLOSURE_MARKERS) + "\n")
    write_text(resolve_path(root, DOCS_README), "\n".join(DOCS_README_MARKERS) + "\n")
    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(
        resolve_path(root, POLICY),
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": EXPECTED_POLICY_CHANNEL,
                "minimum_version": EXPECTED_POLICY_CHANNEL,
                "archive_sha256": {"x86_64-linux": EXPECTED_POLICY_ARCHIVE_SHA},
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
        resolve_path(root, TOOL_MANIFEST),
        json.dumps(
            {
                "workflow": ".github/workflows/zigux-bootstrap.yml",
                "present_surfaces": {
                    "bootstrap_helpers": ["scripts/zigux/install-zig.py"],
                },
            },
            indent=2,
        )
        + "\n",
    )


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


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


def mutate_json(path: Path, mutator) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    mutator(payload)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + len(INSTALL_ZIG_MARKERS)
        + len(WORKFLOW_MARKERS)
        + len(WORKFLOW_MARKERS)
        + len(PHASE2_NOTES_MARKERS)
        + len(PHASE2_CLOSURE_MARKERS)
        + len(DOCS_README_MARKERS)
        + len(REVIEW_CHECKLIST_MARKERS)
        + len(SCRIPTS_README_MARKERS)
        + len(TESTS_README_MARKERS)
        + 5
        + 5
        + 2
        + 2
    )
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_install_zig_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in INSTALL_ZIG_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, INSTALL_ZIG)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_INSTALL_ZIG_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "run: python3 scripts/zigux/other.py"), encoding="utf-8")
            assert ("MISSING_WORKFLOW_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_WORKFLOW_MARKERS", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for path_ref, marker_set, code in (
            (PHASE2_NOTES, PHASE2_NOTES_MARKERS, "MISSING_PHASE2_NOTES_MARKERS"),
            (PHASE2_CLOSURE, PHASE2_CLOSURE_MARKERS, "MISSING_PHASE2_CLOSURE_MARKERS"),
            (DOCS_README, DOCS_README_MARKERS, "MISSING_DOCS_README_MARKERS"),
            (REVIEW_CHECKLIST, REVIEW_CHECKLIST_MARKERS, "MISSING_REVIEW_CHECKLIST_MARKERS"),
            (SCRIPTS_README, SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKERS"),
            (TESTS_README, TESTS_README_MARKERS, "MISSING_TESTS_README_MARKERS"),
        ):
            for marker in marker_set:
                build_self_test_root(root)
                path = resolve_path(root, path_ref)
                path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
                assert (code, marker) in collect_issues(root)
                checks_run += 1

        for path_ref, forbidden_code in (
            (PHASE2_NOTES, "FORBIDDEN_PHASE2_NOTES_MARKERS"),
            (DOCS_README, "FORBIDDEN_DOCS_README_MARKERS"),
            (REVIEW_CHECKLIST, "FORBIDDEN_REVIEW_CHECKLIST_MARKERS"),
            (SCRIPTS_README, "FORBIDDEN_SCRIPTS_README_MARKERS"),
            (TESTS_README, "FORBIDDEN_TESTS_README_MARKERS"),
        ):
            build_self_test_root(root)
            path = resolve_path(root, path_ref)
            marker = FORBIDDEN_INSTALLER_GAP_MARKERS[0]
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            assert (forbidden_code, marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        mutate_json(resolve_path(root, POLICY), lambda payload: payload.__setitem__("channel", "0.17.0"))
        assert ("POLICY_FIELD_MISMATCH", "channel") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        mutate_json(resolve_path(root, POLICY), lambda payload: payload["archive_sha256"].__setitem__("x86_64-linux", "0" * 64))
        assert ("POLICY_ARCHIVE_DIGEST_MISMATCH", "0" * 64) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        mutate_json(resolve_path(root, POLICY), lambda payload: payload["upgrade_policy"].__setitem__("archive_target_scope", ["aarch64-linux"]))
        assert ("POLICY_UPGRADE_FIELD_MISMATCH", "archive_target_scope") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        mutate_json(resolve_path(root, TOOL_MANIFEST), lambda payload: payload["present_surfaces"].__setitem__("bootstrap_helpers", []))
        assert ("TOOL_MANIFEST_BOOTSTRAP_HELPERS_MISMATCH", "[]") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        mutate_json(resolve_path(root, TOOL_MANIFEST), lambda payload: payload.__setitem__("workflow", "broken.yml"))
        assert ("TOOL_MANIFEST_WORKFLOW_MISMATCH", "'broken.yml'") in collect_issues(root)
        checks_run += 1

        for path_ref in (INSTALL_ZIG, WORKFLOW):
            build_self_test_root(root)
            resolve_path(root, path_ref).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
            else:
                raise AssertionError(f"missing primary file did not abort: {path_ref}")
            checks_run += 1

        build_self_test_root(root)
        resolve_path(root, POLICY).write_text("{not-json}\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json" in str(exc)
        else:
            raise AssertionError("invalid policy json did not abort")
        checks_run += 1

        build_self_test_root(root)
        resolve_path(root, TOOL_MANIFEST).write_text("{not-json}\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json" in str(exc)
        else:
            raise AssertionError("invalid tool manifest json did not abort")
        checks_run += 1

    assert checks_run == expected_case_count
    print("PHASE2_INSTALL_ZIG_PACKET_SELF_TEST=pass")
    print(f"PHASE2_INSTALL_ZIG_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current Phase 2 install-zig helper packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal current-like sample root for focused checker replays.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        build_self_test_root(args.write_sample_root.resolve())
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_INSTALL_ZIG_PACKET=pass")
    print(f"PHASE2_INSTALL_ZIG_PACKET_INSTALLER_MARKER_COUNT={len(INSTALL_ZIG_MARKERS)}")
    print(f"PHASE2_INSTALL_ZIG_PACKET_REMINDER_MARKER_COUNT={len(PHASE2_NOTES_MARKERS) + len(PHASE2_CLOSURE_MARKERS) + len(DOCS_README_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(SCRIPTS_README_MARKERS) + len(TESTS_README_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
