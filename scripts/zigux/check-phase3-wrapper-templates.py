#!/usr/bin/env python3
"""Fail-close the current Phase 3 wrapper-template cleanup route."""

from __future__ import annotations

import argparse
import importlib.util
import tempfile
from pathlib import Path

GENERATOR_PATH = Path("scripts/zigux/generate-phase3-check-wrappers.py")
SCRIPTS_DIR = Path("scripts/zigux")


def _load_generator(path: Path):
    spec = importlib.util.spec_from_file_location("zigux_phase3_wrapper_generator", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"unable to load wrapper generator from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    generator = repo_root / GENERATOR_PATH
    if not generator.is_file():
        return [f"missing repo file: {GENERATOR_PATH.as_posix()}"]

    try:
        module = _load_generator(generator)
    except Exception as exc:  # pragma: no cover - surfaced in self-test
        return [f"unable to load {GENERATOR_PATH.as_posix()}: {exc}"]

    mismatches = module.sync_wrappers(
        [],
        module.render_wrapper_stub(),
        check=True,
        scripts_dir=repo_root / SCRIPTS_DIR,
    )
    for path in mismatches:
        issues.append(f"stale wrapper template: {path}")
    return issues


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def run_self_test() -> int:
    generator_text = """#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

LEGACY_IMPORT_MARKER = \"from phase3_check_lib import run_from_wrapper\"
LEGACY_CALL_MARKER = \"run_from_wrapper(__file__)\"
WRAPPER_STUB = \"\"\"#!/usr/bin/env python3
from __future__ import annotations

from phase3_check_lib import run_from_wrapper


if __name__ == \\\"__main__\\\":
    raise SystemExit(run_from_wrapper(__file__))
\"\"\"


def render_wrapper_stub() -> str:
    return WRAPPER_STUB


def _is_generated_wrapper(path: Path, expected: str) -> bool:
    text = path.read_text(encoding=\"utf-8\")
    return text == expected or (
        LEGACY_IMPORT_MARKER in text and LEGACY_CALL_MARKER in text
    )


def sync_wrappers(entries, expected, check, scripts_dir):
    mismatches = []
    for path in sorted(scripts_dir.glob(\"check-phase3-*.py\")):
        if _is_generated_wrapper(path, expected):
            mismatches.append(path.as_posix())
    return mismatches
"""

    wrapper_text = """#!/usr/bin/env python3
from __future__ import annotations

from phase3_check_lib import run_from_wrapper


if __name__ == \"__main__\":
    raise SystemExit(run_from_wrapper(__file__))
"""

    legacy_wrapper_text = """#!/usr/bin/env python3
from __future__ import annotations

import sys
from phase3_check_lib import run_from_wrapper


if __name__ == \"__main__\":
    print(sys.version_info[0])
    raise SystemExit(run_from_wrapper(__file__))
"""

    with tempfile.TemporaryDirectory(prefix="zigux_phase3_wrapper_templates_") as temp_dir:
        root = Path(temp_dir)
        _write(root / GENERATOR_PATH, generator_text)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_WRAPPER_TEMPLATES_CHECK_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        issues = validate_repo(root / "missing-root")
        expected_missing = f"missing repo file: {GENERATOR_PATH.as_posix()}"
        if expected_missing not in issues:
            print("PHASE3_WRAPPER_TEMPLATES_CHECK_SELF_TEST=fail")
            print("expected missing generator route was not reported")
            return 1

        _write(root / GENERATOR_PATH, "def broken(:\n")
        issues = validate_repo(root)
        expected_load_failure = f"unable to load {GENERATOR_PATH.as_posix()}:"
        if not any(issue.startswith(expected_load_failure) for issue in issues):
            print("PHASE3_WRAPPER_TEMPLATES_CHECK_SELF_TEST=fail")
            print("expected broken generator load failure was not reported")
            return 1

        _write(root / GENERATOR_PATH, generator_text)
        _write(root / SCRIPTS_DIR / "check-phase3-legacy-wrapper.py", wrapper_text)
        issues = validate_repo(root)
        expected_stale = (
            "stale wrapper template: "
            + str(root / SCRIPTS_DIR / "check-phase3-legacy-wrapper.py")
        )
        if expected_stale not in issues:
            print("PHASE3_WRAPPER_TEMPLATES_CHECK_SELF_TEST=fail")
            print("expected stale wrapper template was not reported")
            return 1

        _write(root / SCRIPTS_DIR / "check-phase3-shared-runner.py", legacy_wrapper_text)
        issues = validate_repo(root)
        expected_legacy_stale = (
            "stale wrapper template: "
            + str(root / SCRIPTS_DIR / "check-phase3-shared-runner.py")
        )
        if expected_legacy_stale not in issues:
            print("PHASE3_WRAPPER_TEMPLATES_CHECK_SELF_TEST=fail")
            print("expected legacy shared-runner wrapper template was not reported")
            return 1

    print("PHASE3_WRAPPER_TEMPLATES_CHECK_SELF_TEST=pass")
    print("PHASE3_WRAPPER_TEMPLATES_CHECK_SELF_TEST_CASE_COUNT=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 wrapper-template cleanup route."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains scripts/zigux/",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_WRAPPER_TEMPLATES_CHECK=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {args.repo_root / GENERATOR_PATH}")
    print("PHASE3_WRAPPER_TEMPLATES_CHECK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
