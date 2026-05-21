#!/usr/bin/env python3
"""Externally widen the Phase 2 closure validator matrix coverage."""

from __future__ import annotations

import argparse
import shutil
import importlib.util
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
VALIDATOR_REL = Path("scripts/zigux/validate-phase2-closure.py")


def load_validator(root: Path):
    path = root / VALIDATOR_REL
    spec = importlib.util.spec_from_file_location("zigux_validate_phase2_closure", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"unable to load closure validator: {path}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except FileNotFoundError as exc:
        raise SystemExit(f"unable to load closure validator: {path}") from exc
    return module


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
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


def assert_issue(module, root: Path, expected: tuple[str, str]) -> None:
    issues = module.collect_issues(root)
    if expected not in issues:
        raise AssertionError(f"missing expected issue {expected!r}; saw {issues!r}")


def seed_validator_self_test_root(module, root: Path) -> None:
    module.build_self_test_root(root)


def seed_materialized_root(module, root: Path, source_root: Path) -> None:
    paths_to_copy = {VALIDATOR_REL, *module.REQUIRED_FILES}
    for rel in paths_to_copy:
        source_path = source_root / rel
        if not source_path.exists():
            raise AssertionError(f"source path missing: {source_path}")
        destination_path = root / rel
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, destination_path)


def run_matrix(module, seed_root) -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_matrix_") as tmp_dir:
        root = Path(tmp_dir)
        seed_root(root)
        if module.collect_issues(root) != []:
            raise AssertionError("expected clean baseline self-test root")
        checks_run += 1

        for marker in module.REQUIRED_CLOSURE_MARKERS:
            seed_root(root)
            path = module.resolve(root, module.PHASE2_CLOSURE_REL)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert_issue(module, root, ("MISSING_CLOSURE_MARKER", marker))
            checks_run += 1

        for marker in module.REQUIRED_CLOSURE_MARKERS:
            seed_root(root)
            path = module.resolve(root, module.PHASE2_CLOSURE_REL)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert_issue(module, root, ("DUPLICATE_CLOSURE_MARKER", f"{marker}:count=2"))
            checks_run += 1

        for marker in module.REQUIRED_WORKFLOW_LINES:
            seed_root(root)
            path = module.resolve(root, module.WORKFLOW_REL)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "run: python3 scripts/zigux/other.py"),
                encoding="utf-8",
            )
            assert_issue(module, root, ("MISSING_WORKFLOW_LINE", marker))
            checks_run += 1

            seed_root(root)
            path = module.resolve(root, module.WORKFLOW_REL)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert_issue(module, root, ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2"))
            checks_run += 1

        for marker in module.REQUIRED_MAKEFILE_LINES:
            seed_root(root)
            path = module.resolve(root, module.MAKEFILE_REL)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "# removed"), encoding="utf-8")
            assert_issue(module, root, ("MISSING_MAKEFILE_LINE", marker))
            checks_run += 1

            seed_root(root)
            path = module.resolve(root, module.MAKEFILE_REL)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert_issue(module, root, ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2"))
            checks_run += 1

        for rel in module.REQUIRED_FILES:
            seed_root(root)
            path = module.resolve(root, rel)
            path.unlink()
            assert_issue(module, root, ("MISSING_REQUIRED_FILE", rel.as_posix()))
            checks_run += 1

    return checks_run


def run_self_test() -> int:
    fake_validator = """\
from pathlib import Path

PHASE2_CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_REL = Path("zigux/Makefile")
MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
REQUIRED_CLOSURE_MARKERS = ("`marker-a`", "`marker-b`")
REQUIRED_WORKFLOW_LINES = ("run: alpha", "run: beta")
REQUIRED_MAKEFILE_LINES = ("phase2-a:", "phase2-b:")
REQUIRED_FILES = (PHASE2_CLOSURE_REL, WORKFLOW_REL, MAKEFILE_REL, MANIFEST_REL)

def resolve(root: Path, rel: Path) -> Path:
    return root / rel

def build_self_test_root(root: Path) -> None:
    resolve(root, PHASE2_CLOSURE_REL).parent.mkdir(parents=True, exist_ok=True)
    resolve(root, PHASE2_CLOSURE_REL).write_text("`marker-a`\\n`marker-b`\\n", encoding="utf-8")
    resolve(root, WORKFLOW_REL).parent.mkdir(parents=True, exist_ok=True)
    resolve(root, WORKFLOW_REL).write_text("run: alpha\\nrun: beta\\n", encoding="utf-8")
    resolve(root, MAKEFILE_REL).parent.mkdir(parents=True, exist_ok=True)
    resolve(root, MAKEFILE_REL).write_text("phase2-a:\\nphase2-b:\\n", encoding="utf-8")
    resolve(root, MANIFEST_REL).parent.mkdir(parents=True, exist_ok=True)
    resolve(root, MANIFEST_REL).write_text("{}\\n", encoding="utf-8")

def _count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)

def collect_issues(root: Path):
    issues = []
    for rel in REQUIRED_FILES:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues
    closure_text = resolve(root, PHASE2_CLOSURE_REL).read_text(encoding="utf-8")
    workflow_text = resolve(root, WORKFLOW_REL).read_text(encoding="utf-8")
    makefile_text = resolve(root, MAKEFILE_REL).read_text(encoding="utf-8")
    for marker in REQUIRED_CLOSURE_MARKERS:
        count = _count_exact_lines(closure_text, marker)
        if count == 0:
            issues.append(("MISSING_CLOSURE_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_CLOSURE_MARKER", f"{marker}:count={count}"))
    for marker in REQUIRED_WORKFLOW_LINES:
        count = _count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))
    for marker in REQUIRED_MAKEFILE_LINES:
        count = _count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))
    return issues
"""

    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_matrix_selftest_") as tmp_dir:
        root = Path(tmp_dir)
        validator_path = root / VALIDATOR_REL
        validator_path.parent.mkdir(parents=True, exist_ok=True)
        validator_path.write_text(fake_validator, encoding="utf-8")
        module = load_validator(root)
        module.build_self_test_root(root)
        checks_run += run_matrix(module, lambda temp_root: seed_materialized_root(module, temp_root, root))

        missing_validator_root = root / "missing-validator-root"
        missing_validator_root.mkdir()
        try:
            load_validator(missing_validator_root)
        except SystemExit as exc:
            assert "unable to load closure validator" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing validator root did not abort")

    print("PHASE2_CLOSURE_MATRIX_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_MATRIX_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the full closure-marker, workflow-line, Makefile-line, and required-file matrix against the Phase 2 closure validator."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    repo_root = args.root.resolve()
    module = load_validator(repo_root)
    checks_run = run_matrix(module, lambda temp_root: seed_materialized_root(module, temp_root, repo_root))
    print("PHASE2_CLOSURE_MATRIX=pass")
    print(f"PHASE2_CLOSURE_MATRIX_CASE_COUNT={checks_run}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
