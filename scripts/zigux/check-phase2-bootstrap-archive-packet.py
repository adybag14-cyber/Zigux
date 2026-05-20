#!/usr/bin/env python3
"""Guard the current Lane 03 bootstrap archive-validation packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
TOOLCHAIN_CHECKER = ROOT / "scripts" / "zigux" / "check-zig-toolchain.py"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
)

TOOLCHAIN_CHECKER_MARKERS = (
    'parser.add_argument("--policy-only"',
    'parser.add_argument("--archive-only"',
    'parser.add_argument("--archive"',
    'parser.add_argument("--archive-target"',
    'parser.add_argument("--allow-missing"',
    "def resolve_policy_archive(",
    "def validate_policy_archive(",
    'print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing")',
    'print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid")',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or \'unresolved\'}")',
)

PHASE2_NOTES_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py` is directly readable on current `master` and keeps the pinned-channel probe, repo-local `.zig-toolchain` fallback, and archive-integrity validation surface explicit beside the reminder guards.",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
)

SCRIPTS_README_MARKERS = (
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` keep the shipped pinned Zig toolchain guard explicit in the live bootstrap action path before the surviving Phase 2 bridge and pinning checks",
    "`scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, and `scripts/zigux/check-phase2-required-make-routes.py` remain the shipped Phase 2 toolchain, reminder, alignment, artifact-support, fixdep, genksyms-bridge, and required-make-route guards that survive on current `master`",
)

EXPECTED_POLICY = {
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
}


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
    raise AssertionError(f"line marker not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"line marker not found: {marker}")


def load_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc.msg}") from exc


def collect_policy_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    payload = load_json(root / TOOLCHAIN_POLICY.relative_to(ROOT))
    if not isinstance(payload, dict):
        return [("INVALID_POLICY_PAYLOAD", type(payload).__name__)]

    for key in ("phase", "channel", "minimum_version"):
        if payload.get(key) != EXPECTED_POLICY[key]:
            issues.append(("POLICY_FIELD_MISMATCH", key))

    archive_sha256 = payload.get("archive_sha256")
    if archive_sha256 != EXPECTED_POLICY["archive_sha256"]:
        issues.append(("POLICY_FIELD_MISMATCH", "archive_sha256"))

    upgrade_policy = payload.get("upgrade_policy")
    if upgrade_policy != EXPECTED_POLICY["upgrade_policy"]:
        issues.append(("POLICY_FIELD_MISMATCH", "upgrade_policy"))

    return issues


def collect_tool_manifest_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    payload = load_json(root / TOOL_MANIFEST.relative_to(ROOT))
    if not isinstance(payload, dict):
        return [("INVALID_TOOL_MANIFEST_PAYLOAD", type(payload).__name__)]

    if payload.get("workflow") != ".github/workflows/zigux-bootstrap.yml":
        issues.append(("TOOL_MANIFEST_FIELD_MISMATCH", "workflow"))

    present_surfaces = payload.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        return issues + [("INVALID_TOOL_MANIFEST_PRESENT_SURFACES", type(present_surfaces).__name__)]

    if present_surfaces.get("policy") != ["scripts/zigux/zig-toolchain-policy.json"]:
        issues.append(("TOOL_MANIFEST_SURFACE_MISMATCH", "policy"))
    if present_surfaces.get("bootstrap_helpers") != ["scripts/zigux/install-zig.py"]:
        issues.append(("TOOL_MANIFEST_SURFACE_MISMATCH", "bootstrap_helpers"))

    checkers = present_surfaces.get("checkers")
    if not isinstance(checkers, list) or "scripts/zigux/check-zig-toolchain.py" not in checkers:
        issues.append(("TOOL_MANIFEST_SURFACE_MISMATCH", "checkers"))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    workflow_text = read_text(root / WORKFLOW.relative_to(ROOT))
    checker_text = read_text(root / TOOLCHAIN_CHECKER.relative_to(ROOT))
    notes_text = read_text(root / PHASE2_NOTES.relative_to(ROOT))
    scripts_readme_text = read_text(root / SCRIPTS_README.relative_to(ROOT))

    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    ordered_positions: list[tuple[str, int]] = []
    workflow_lines = [line.strip() for line in workflow_text.splitlines()]
    for marker in WORKFLOW_LINES:
        if count_exact_lines(workflow_text, marker) == 1:
            ordered_positions.append((marker, workflow_lines.index(marker)))
    for (left_marker, left_index), (right_marker, right_index) in zip(ordered_positions, ordered_positions[1:]):
        if left_index >= right_index:
            issues.append(("OUT_OF_ORDER_WORKFLOW_LINE", f"{left_marker} -> {right_marker}"))

    for marker in TOOLCHAIN_CHECKER_MARKERS:
        if marker not in checker_text:
            issues.append(("MISSING_TOOLCHAIN_CHECKER_MARKER", marker))

    for marker in PHASE2_NOTES_MARKERS:
        if marker not in notes_text:
            issues.append(("MISSING_PHASE2_NOTES_MARKER", marker))

    for marker in SCRIPTS_README_MARKERS:
        if marker not in scripts_readme_text:
            issues.append(("MISSING_SCRIPTS_README_MARKER", marker))

    issues.extend(collect_policy_issues(root))
    issues.extend(collect_tool_manifest_issues(root))
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
    write_text(root / WORKFLOW.relative_to(ROOT), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(root / TOOLCHAIN_CHECKER.relative_to(ROOT), "\n".join(TOOLCHAIN_CHECKER_MARKERS) + "\n")
    write_text(root / PHASE2_NOTES.relative_to(ROOT), "\n".join(PHASE2_NOTES_MARKERS) + "\n")
    write_text(root / SCRIPTS_README.relative_to(ROOT), "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(root / TOOLCHAIN_POLICY.relative_to(ROOT), json.dumps(EXPECTED_POLICY, indent=2) + "\n")
    write_text(
        root / TOOL_MANIFEST.relative_to(ROOT),
        json.dumps(
            {
                "workflow": ".github/workflows/zigux-bootstrap.yml",
                "present_surfaces": {
                    "policy": ["scripts/zigux/zig-toolchain-policy.json"],
                    "bootstrap_helpers": ["scripts/zigux/install-zig.py"],
                    "checkers": [
                        "scripts/zigux/check-zig-toolchain.py",
                        "scripts/zigux/check-phase2-required-make-routes.py",
                    ],
                },
            },
            indent=2,
        )
        + "\n",
    )


def mutate_json(path: Path, mutator) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    mutator(payload)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + len(WORKFLOW_LINES)
        + len(WORKFLOW_LINES)
        + (len(WORKFLOW_LINES) - 1)
        + len(TOOLCHAIN_CHECKER_MARKERS)
        + len(PHASE2_NOTES_MARKERS)
        + len(SCRIPTS_README_MARKERS)
        + 4
        + 3
        + 2
    )

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_archive_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in WORKFLOW_LINES:
            build_sample_root(root)
            path = root / WORKFLOW.relative_to(ROOT)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "run: python3 scripts/zigux/other.py"),
                encoding="utf-8",
            )
            assert (("MISSING_WORKFLOW_LINE", marker)) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_sample_root(root)
            path = root / WORKFLOW.relative_to(ROOT)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert (("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2")) in collect_issues(root)
            checks_run += 1

        for left_marker, right_marker in zip(WORKFLOW_LINES, WORKFLOW_LINES[1:]):
            build_sample_root(root)
            path = root / WORKFLOW.relative_to(ROOT)
            text = path.read_text(encoding="utf-8")
            text = replace_exact_line(text, left_marker, "__swap__")
            text = replace_exact_line(text, right_marker, left_marker)
            text = replace_exact_line(text, "__swap__", right_marker)
            path.write_text(text, encoding="utf-8")
            assert (("OUT_OF_ORDER_WORKFLOW_LINE", f"{left_marker} -> {right_marker}")) in collect_issues(root)
            checks_run += 1

        for marker in TOOLCHAIN_CHECKER_MARKERS:
            build_sample_root(root)
            path = root / TOOLCHAIN_CHECKER.relative_to(ROOT)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert (("MISSING_TOOLCHAIN_CHECKER_MARKER", marker)) in collect_issues(root)
            checks_run += 1

        for marker in PHASE2_NOTES_MARKERS:
            build_sample_root(root)
            path = root / PHASE2_NOTES.relative_to(ROOT)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert (("MISSING_PHASE2_NOTES_MARKER", marker)) in collect_issues(root)
            checks_run += 1

        for marker in SCRIPTS_README_MARKERS:
            build_sample_root(root)
            path = root / SCRIPTS_README.relative_to(ROOT)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert (("MISSING_SCRIPTS_README_MARKER", marker)) in collect_issues(root)
            checks_run += 1

        build_sample_root(root)
        mutate_json(root / TOOLCHAIN_POLICY.relative_to(ROOT), lambda payload: payload.__setitem__("channel", "0.17.0"))
        assert (("POLICY_FIELD_MISMATCH", "channel")) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        mutate_json(
            root / TOOLCHAIN_POLICY.relative_to(ROOT),
            lambda payload: payload["upgrade_policy"].__setitem__("archive_target_scope", ["aarch64-linux"]),
        )
        assert (("POLICY_FIELD_MISMATCH", "upgrade_policy")) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        mutate_json(
            root / TOOLCHAIN_POLICY.relative_to(ROOT),
            lambda payload: payload.__setitem__("archive_sha256", {"x86_64-linux": "0" * 64}),
        )
        assert (("POLICY_FIELD_MISMATCH", "archive_sha256")) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        mutate_json(root / TOOLCHAIN_POLICY.relative_to(ROOT), lambda payload: payload.__setitem__("phase", "Phase 1"))
        assert (("POLICY_FIELD_MISMATCH", "phase")) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        mutate_json(root / TOOL_MANIFEST.relative_to(ROOT), lambda payload: payload.__setitem__("workflow", "broken.yml"))
        assert (("TOOL_MANIFEST_FIELD_MISMATCH", "workflow")) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        mutate_json(
            root / TOOL_MANIFEST.relative_to(ROOT),
            lambda payload: payload["present_surfaces"].__setitem__("policy", []),
        )
        assert (("TOOL_MANIFEST_SURFACE_MISMATCH", "policy")) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        mutate_json(
            root / TOOL_MANIFEST.relative_to(ROOT),
            lambda payload: payload["present_surfaces"].__setitem__("checkers", []),
        )
        assert (("TOOL_MANIFEST_SURFACE_MISMATCH", "checkers")) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        (root / TOOLCHAIN_POLICY.relative_to(ROOT)).write_text("{not-json}\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json" in str(exc)
        else:
            raise AssertionError("invalid policy json did not abort")
        checks_run += 1

        build_sample_root(root)
        (root / TOOL_MANIFEST.relative_to(ROOT)).write_text("{not-json}\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json" in str(exc)
        else:
            raise AssertionError("invalid manifest json did not abort")
        checks_run += 1

    assert checks_run == expected_case_count, (checks_run, expected_case_count)
    print("PHASE2_BOOTSTRAP_ARCHIVE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_ARCHIVE_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the current bootstrap archive-validation packet stays aligned.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in checker coverage")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal current-like sample root")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_ARCHIVE_PACKET=pass")
    print(f"PHASE2_BOOTSTRAP_ARCHIVE_PACKET_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_BOOTSTRAP_ARCHIVE_PACKET_CHECKER_MARKER_COUNT={len(TOOLCHAIN_CHECKER_MARKERS)}")
    print(f"PHASE2_BOOTSTRAP_ARCHIVE_PACKET_REMINDER_MARKER_COUNT={len(PHASE2_NOTES_MARKERS) + len(SCRIPTS_README_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
