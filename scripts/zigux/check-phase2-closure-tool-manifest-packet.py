#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


def derive_repo_root(script_path: Path) -> Path:
    return script_path.parents[2] if len(script_path.parents) >= 3 else script_path.parent


ROOT = derive_repo_root(Path(__file__).resolve())
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
VALIDATE_PHASE2 = Path("scripts/zigux/validate-phase2.py")
MAKEFILE = Path("zigux/Makefile")
TESTS_README = Path("zigux/tests/README.md")

REQUIRED_PATHS = (
    PHASE2_CLOSURE,
    VALIDATE_PHASE2,
    Path("scripts/zigux/check-phase2-tool-manifest.py"),
    Path("scripts/zigux/check-phase2-artifact-tools-manifest.py"),
    Path("scripts/zigux/validate-phase2-closure.py"),
    MAKEFILE,
    TESTS_README,
    Path("zigux/tests/fixtures/phase2_tool_manifest.json"),
    Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/manifest.json"),
    Path("zigux/tests/fixtures/kconfig_bridge/conf_manifest.json"),
    Path("zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json"),
)

CLOSURE_MARKERS = (
    "manifest: `zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "the fixture-backed tool-manifest and artifact-tools-manifest guards",
)

VALIDATOR_MARKERS = (
    '"scripts/zigux/check-phase2-tool-manifest.py",',
    '"scripts/zigux/check-phase2-artifact-tools-manifest.py",',
    '"zigux/tests/fixtures/phase2_tool_manifest.json",',
    '"zigux/tests/fixtures/phase2_artifact_tools_manifest.json",',
    '"zigux/tests/fixtures/genksyms_bridge/manifest.json",',
    '"zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",',
    '"zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",',
)

MAKEFILE_MARKERS = (
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
)

TESTS_MARKERS = (
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "keep the fixture-backed tool-manifest and artifact-tools-manifest guards",
)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_good_tree(root: Path) -> None:
    write_text(root / PHASE2_CLOSURE, "\n".join(CLOSURE_MARKERS) + "\n")
    write_text(root / VALIDATE_PHASE2, "\n".join(VALIDATOR_MARKERS) + "\n")
    write_text(root / MAKEFILE, "\n".join(MAKEFILE_MARKERS) + "\n")
    write_text(root / TESTS_README, "\n".join(TESTS_MARKERS) + "\n")

    for relative_path in REQUIRED_PATHS:
        path = root / relative_path
        if not path.exists():
            write_text(path, "placeholder\n")


def collect_marker_issues(text: str, markers: tuple[str, ...], prefix: str) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        if marker not in text:
            issues.append(f"missing_marker:{prefix}:{marker}")
    return issues


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    for relative_path in REQUIRED_PATHS:
        if not (root / relative_path).is_file():
            issues.append(f"missing_file:{relative_path.as_posix()}")

    if issues:
        return issues

    issues.extend(
        collect_marker_issues(
            (root / PHASE2_CLOSURE).read_text(encoding="utf-8"),
            CLOSURE_MARKERS,
            PHASE2_CLOSURE.as_posix(),
        )
    )
    issues.extend(
        collect_marker_issues(
            (root / VALIDATE_PHASE2).read_text(encoding="utf-8"),
            VALIDATOR_MARKERS,
            VALIDATE_PHASE2.as_posix(),
        )
    )
    issues.extend(
        collect_marker_issues(
            (root / MAKEFILE).read_text(encoding="utf-8"),
            MAKEFILE_MARKERS,
            MAKEFILE.as_posix(),
        )
    )
    issues.extend(
        collect_marker_issues(
            (root / TESTS_README).read_text(encoding="utf-8"),
            TESTS_MARKERS,
            TESTS_README.as_posix(),
        )
    )
    return issues


def run_self_test() -> int:
    cases_run = 0
    with tempfile.TemporaryDirectory(prefix="phase2_closure_tool_manifest_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_good_tree(root)
        if collect_issues(root):
            raise SystemExit("phase2-closure-tool-manifest:self-test:good_tree")
        cases_run += 1

        build_good_tree(root)
        (root / REQUIRED_PATHS[-1]).unlink()
        issues = collect_issues(root)
        if f"missing_file:{REQUIRED_PATHS[-1].as_posix()}" not in issues:
            raise SystemExit("phase2-closure-tool-manifest:self-test:missing_file")
        cases_run += 1

        build_good_tree(root)
        write_text(root / PHASE2_CLOSURE, "closure drift\n")
        issues = collect_issues(root)
        if not any(issue.startswith(f"missing_marker:{PHASE2_CLOSURE.as_posix()}:") for issue in issues):
            raise SystemExit("phase2-closure-tool-manifest:self-test:closure_marker")
        cases_run += 1

        build_good_tree(root)
        write_text(root / VALIDATE_PHASE2, "validator drift\n")
        issues = collect_issues(root)
        if not any(issue.startswith(f"missing_marker:{VALIDATE_PHASE2.as_posix()}:") for issue in issues):
            raise SystemExit("phase2-closure-tool-manifest:self-test:validator_marker")
        cases_run += 1

        build_good_tree(root)
        write_text(root / MAKEFILE, "make drift\n")
        issues = collect_issues(root)
        if not any(issue.startswith(f"missing_marker:{MAKEFILE.as_posix()}:") for issue in issues):
            raise SystemExit("phase2-closure-tool-manifest:self-test:makefile_marker")
        cases_run += 1

        build_good_tree(root)
        write_text(root / TESTS_README, "tests drift\n")
        issues = collect_issues(root)
        if not any(issue.startswith(f"missing_marker:{TESTS_README.as_posix()}:") for issue in issues):
            raise SystemExit("phase2-closure-tool-manifest:self-test:tests_marker")
        cases_run += 1

    print("PHASE2_CLOSURE_TOOL_MANIFEST_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_TOOL_MANIFEST_PACKET_SELF_TEST_CASE_COUNT={cases_run}")
    return 0


def write_sample_root(sample_root: Path) -> int:
    build_good_tree(sample_root)
    print(f"PHASE2_CLOSURE_TOOL_MANIFEST_PACKET_SAMPLE_ROOT={sample_root}")
    print(f"PHASE2_CLOSURE_TOOL_MANIFEST_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the closure-side Phase 2 tool-manifest packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal current-like sample root and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root)

    issues = collect_issues(args.root)
    if issues:
        print("PHASE2_CLOSURE_TOOL_MANIFEST_PACKET=fail")
        print("PHASE2_CLOSURE_TOOL_MANIFEST_PACKET_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_CLOSURE_TOOL_MANIFEST_PACKET_ISSUES_END")
        return 1

    print("PHASE2_CLOSURE_TOOL_MANIFEST_PACKET=pass")
    print(f"PHASE2_CLOSURE_TOOL_MANIFEST_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_CLOSURE_TOOL_MANIFEST_PACKET_CLOSURE_MARKER_COUNT={len(CLOSURE_MARKERS)}")
    print(f"PHASE2_CLOSURE_TOOL_MANIFEST_PACKET_VALIDATOR_MARKER_COUNT={len(VALIDATOR_MARKERS)}")
    print(f"PHASE2_CLOSURE_TOOL_MANIFEST_PACKET_MAKEFILE_MARKER_COUNT={len(MAKEFILE_MARKERS)}")
    print(f"PHASE2_CLOSURE_TOOL_MANIFEST_PACKET_TESTS_MARKER_COUNT={len(TESTS_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
