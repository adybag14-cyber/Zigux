#!/usr/bin/env python3
"""Guard the current Phase 2 toolchain make-wrapper action path."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else Path.cwd()

WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
SCRIPTS_README = Path("scripts/zigux/README.md")
TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
CHECK_ZIG_TOOLCHAIN = Path("scripts/zigux/check-zig-toolchain.py")
ARCHIVE_VERIFICATION = Path("scripts/zigux/check-lane05-install-zig-archive-verification.py")
TOOLCHAIN_PINNING = Path("scripts/zigux/check-phase2-toolchain-pinning.py")
TOOLCHAIN_PIN_SCOPE = Path("scripts/zigux/check-phase2-toolchain-pin-scope.py")
TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
ARCHIVE_README = Path("third_party/README.md")
ARCHIVE_PAYLOAD = Path("third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz")

REQUIRED_FILES = (
    WORKFLOW,
    MAKEFILE,
    SCRIPTS_README,
    TOOL_MANIFEST,
    CHECK_ZIG_TOOLCHAIN,
    ARCHIVE_VERIFICATION,
    TOOLCHAIN_PINNING,
    TOOLCHAIN_PIN_SCOPE,
    TOOLCHAIN_POLICY,
    ARCHIVE_README,
    ARCHIVE_PAYLOAD,
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: make -C zigux phase2-toolchain",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
)

REQUIRED_SCRIPTS_README_MARKERS = (
    "`.github/workflows/zigux-bootstrap.yml`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-lane05-install-zig-archive-verification.py`",
    "`scripts/zigux/zig-toolchain-policy.json`",
    "`third_party/README.md`",
    "`zigux/Makefile`",
    "`make -C zigux phase2-toolchain`",
)

EXPECTED_CHECKERS = (
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
)

EXPECTED_MAKE_WRAPPERS = (
    "zigux/Makefile",
    "make -C zigux phase2-toolchain",
)

EXPECTED_POLICY = ("scripts/zigux/zig-toolchain-policy.json",)

EXPECTED_ARCHIVE_SUPPORT = (
    "third_party/README.md",
    "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
)


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


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def require_manifest_list(
    issues: list[tuple[str, str]], manifest: dict[str, object], category: str
) -> list[str] | None:
    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return None
    value = surfaces.get(category)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(("INVALID_MANIFEST_SHAPE", category))
        return None
    return list(value)


def expect_subset(
    issues: list[tuple[str, str]], label: str, actual: list[str] | None, expected: tuple[str, ...]
) -> None:
    if actual is None:
        return
    for marker in expected:
        if marker not in actual:
            issues.append(("MISSING_MANIFEST_SURFACE", f"{label}:{marker}"))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_FILES:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    workflow_text = read_text(resolve(root, WORKFLOW))
    makefile_text = read_text(resolve(root, MAKEFILE))
    scripts_readme_text = read_text(resolve(root, SCRIPTS_README))
    manifest = read_json(resolve(root, TOOL_MANIFEST))
    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues

    if manifest.get("workflow") != WORKFLOW.as_posix():
        issues.append(("INVALID_MANIFEST_WORKFLOW", repr(manifest.get("workflow"))))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_SCRIPTS_README_MARKERS:
        if marker not in scripts_readme_text:
            issues.append(("MISSING_SCRIPTS_README_MARKER", marker))

    expect_subset(
        issues,
        "checkers",
        require_manifest_list(issues, manifest, "checkers"),
        EXPECTED_CHECKERS,
    )
    expect_subset(
        issues,
        "make_wrappers",
        require_manifest_list(issues, manifest, "make_wrappers"),
        EXPECTED_MAKE_WRAPPERS,
    )
    expect_subset(
        issues,
        "policy",
        require_manifest_list(issues, manifest, "policy"),
        EXPECTED_POLICY,
    )
    expect_subset(
        issues,
        "archive_support",
        require_manifest_list(issues, manifest, "archive_support"),
        EXPECTED_ARCHIVE_SUPPORT,
    )

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_TOOLCHAIN_ACTION_PATH=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    workflow_lines = ["name: zigux-bootstrap", *REQUIRED_WORKFLOW_LINES]
    makefile_lines = [
        "PYTHON ?= python3",
        "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
        "",
        *REQUIRED_MAKEFILE_LINES,
    ]
    readme_lines = [
        "# scripts/zigux",
        "",
        "## Phase 2",
        "",
        "- `scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, and `scripts/zigux/check-lane05-install-zig-archive-verification.py` remain the shipped Phase 2 toolchain, reminder, alignment, artifact-support, fixdep, genksyms-bridge, and required-make-route guards that survive on current `master`",
        "- `.github/workflows/zigux-bootstrap.yml`, `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` keep the shipped pinned Zig toolchain guard explicit in the live bootstrap action path before the surviving Phase 2 bridge and pinning checks",
        "- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, `make -C zigux phase2`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set",
        "- `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`, so keep those installer and direct cross-route surfaces explicit beside the shipped toolchain and kbuild reminder packet instead of leaving them in repo-reality-gap wording",
        "- `scripts/zigux/zig-toolchain-policy.json` and `third_party/README.md` remain explicit current Phase 2 toolchain packet anchors beside the shipped make-wrapper route and archive verifier guard",
    ]

    write_text(resolve(root, WORKFLOW), "\n".join(workflow_lines) + "\n")
    write_text(resolve(root, MAKEFILE), "\n".join(makefile_lines) + "\n")
    write_text(resolve(root, SCRIPTS_README), "\n".join(readme_lines) + "\n")
    for rel in (
        CHECK_ZIG_TOOLCHAIN,
        ARCHIVE_VERIFICATION,
        TOOLCHAIN_PINNING,
        TOOLCHAIN_PIN_SCOPE,
        TOOLCHAIN_POLICY,
        ARCHIVE_README,
        ARCHIVE_PAYLOAD,
    ):
        write_text(resolve(root, rel), "present\n")
    write_text(
        resolve(root, TOOL_MANIFEST),
        json.dumps(
            {
                "workflow": WORKFLOW.as_posix(),
                "present_surfaces": {
                    "checkers": list(EXPECTED_CHECKERS),
                    "make_wrappers": list(EXPECTED_MAKE_WRAPPERS),
                    "policy": list(EXPECTED_POLICY),
                    "archive_support": list(EXPECTED_ARCHIVE_SUPPORT),
                },
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    expected_case_count = (
        1
        + len(REQUIRED_WORKFLOW_LINES)
        + len(REQUIRED_WORKFLOW_LINES)
        + len(REQUIRED_MAKEFILE_LINES)
        + len(REQUIRED_MAKEFILE_LINES)
        + len(REQUIRED_SCRIPTS_README_MARKERS)
        + 4
        + len(REQUIRED_FILES)
        + 1
    )
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_action_path_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_sample_root(root)
            workflow_path = resolve(root, WORKFLOW)
            workflow_path.write_text(
                replace_exact_line(
                    workflow_path.read_text(encoding="utf-8"),
                    marker,
                    "run: python3 scripts/zigux/other.py",
                ),
                encoding="utf-8",
            )
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_sample_root(root)
            workflow_path = resolve(root, WORKFLOW)
            workflow_path.write_text(
                duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2") in collect_issues(root)
            checks += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_sample_root(root)
            makefile_path = resolve(root, MAKEFILE)
            makefile_path.write_text(
                replace_exact_line(
                    makefile_path.read_text(encoding="utf-8"),
                    marker,
                    "# removed",
                ),
                encoding="utf-8",
            )
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_sample_root(root)
            makefile_path = resolve(root, MAKEFILE)
            makefile_path.write_text(
                duplicate_exact_line(makefile_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2") in collect_issues(root)
            checks += 1

        for marker in REQUIRED_SCRIPTS_README_MARKERS:
            build_sample_root(root)
            readme_path = resolve(root, SCRIPTS_README)
            readme_path.write_text(
                replace_once(readme_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_SCRIPTS_README_MARKER", marker) in collect_issues(root)
            checks += 1

        for category, marker in (
            ("checkers", EXPECTED_CHECKERS[0]),
            ("make_wrappers", EXPECTED_MAKE_WRAPPERS[1]),
            ("policy", EXPECTED_POLICY[0]),
            ("archive_support", EXPECTED_ARCHIVE_SUPPORT[1]),
        ):
            build_sample_root(root)
            manifest_path = resolve(root, TOOL_MANIFEST)
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            payload["present_surfaces"][category].remove(marker)
            manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            assert ("MISSING_MANIFEST_SURFACE", f"{category}:{marker}") in collect_issues(root)
            checks += 1

        for rel in REQUIRED_FILES:
            build_sample_root(root)
            resolve(root, rel).unlink()
            assert ("MISSING_REQUIRED_FILE", rel.as_posix()) in collect_issues(root)
            checks += 1

        build_sample_root(root)
        manifest_path = resolve(root, TOOL_MANIFEST)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["workflow"] = "wrong.yml"
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_MANIFEST_WORKFLOW", "'wrong.yml'") in collect_issues(root)
        checks += 1

    assert checks == expected_case_count, (checks, expected_case_count)
    print("PHASE2_TOOLCHAIN_ACTION_PATH_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_ACTION_PATH_SELF_TEST_CASE_COUNT={checks}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repo root to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in self tests")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a passing minimal sample root and exit",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        return 0

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLCHAIN_ACTION_PATH=pass")
    print(f"PHASE2_TOOLCHAIN_ACTION_PATH_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE2_TOOLCHAIN_ACTION_PATH_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_TOOLCHAIN_ACTION_PATH_MAKEFILE_LINE_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    print(f"PHASE2_TOOLCHAIN_ACTION_PATH_README_MARKER_COUNT={len(REQUIRED_SCRIPTS_README_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
