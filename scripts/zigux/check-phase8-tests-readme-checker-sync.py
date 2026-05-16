#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import tempfile
from pathlib import Path

VALIDATOR_PATH = Path("scripts/zigux/validate-phase8.py")
CHECKER_PATH = Path("scripts/zigux/check-phase8-tests-readme-alignment.py")
TESTS_README_PATH_NAME = "TESTS_README_PATH"


class MarkerExtractionError(RuntimeError):
    pass


def _load_module(path: Path) -> ast.Module:
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except FileNotFoundError as exc:
        raise MarkerExtractionError(f"missing file: {path}") from exc
    except SyntaxError as exc:
        raise MarkerExtractionError(f"could not parse {path}: {exc}") from exc


def _literal_string(node: ast.AST) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    raise MarkerExtractionError(f"expected string literal, got {ast.dump(node, include_attributes=False)}")


def _extract_tests_readme_markers(path: Path) -> tuple[str, ...]:
    module = _load_module(path)
    aliases: dict[str, str] = {}
    required_markers: ast.Dict | None = None

    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == TESTS_README_PATH_NAME:
                    aliases[target.id] = target.id
                elif isinstance(target, ast.Name) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    aliases[target.id] = node.value.value
                elif isinstance(target, ast.Name) and target.id == "REQUIRED_MARKERS":
                    if not isinstance(node.value, ast.Dict):
                        raise MarkerExtractionError(f"REQUIRED_MARKERS in {path} is not a dict literal")
                    required_markers = node.value

    if required_markers is None:
        raise MarkerExtractionError(f"REQUIRED_MARKERS not found in {path}")

    for key_node, value_node in zip(required_markers.keys, required_markers.values):
        if isinstance(key_node, ast.Name) and key_node.id == TESTS_README_PATH_NAME:
            if not isinstance(value_node, (ast.Tuple, ast.List)):
                raise MarkerExtractionError(f"{path}: TESTS_README_PATH markers are not a tuple/list literal")
            return tuple(_literal_string(element) for element in value_node.elts)
        if isinstance(key_node, ast.Name):
            resolved = aliases.get(key_node.id)
            if resolved == TESTS_README_PATH_NAME:
                if not isinstance(value_node, (ast.Tuple, ast.List)):
                    raise MarkerExtractionError(f"{path}: TESTS_README_PATH markers are not a tuple/list literal")
                return tuple(_literal_string(element) for element in value_node.elts)

    raise MarkerExtractionError(f"TESTS_README_PATH entry not found in REQUIRED_MARKERS for {path}")


def collect_sync_failures(root: Path) -> list[str]:
    validator_markers = _extract_tests_readme_markers(root / VALIDATOR_PATH)
    checker_markers = _extract_tests_readme_markers(root / CHECKER_PATH)

    failures: list[str] = []
    missing_from_checker = [marker for marker in validator_markers if marker not in checker_markers]
    extra_in_checker = [marker for marker in checker_markers if marker not in validator_markers]

    if missing_from_checker:
        failures.append(
            "tests-readme markers missing from dedicated checker: " + ", ".join(sorted(missing_from_checker))
        )
    if extra_in_checker:
        failures.append(
            "tests-readme markers present only in dedicated checker: " + ", ".join(sorted(extra_in_checker))
        )
    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    validator_text = """\
TESTS_README_PATH = \"zigux/tests/README.md\"
REQUIRED_MARKERS = {
    TESTS_README_PATH: (
        \"`scripts/zigux/check-phase8-tests-readme-alignment.py`\",
        \"`scripts/zigux/check-phase8-exec-cmd-packet.py`\",
        \"`zigux/tests/phase8_exec_cmd.zig`\",
    ),
}
"""
    checker_text = """\
TESTS_README_PATH = \"zigux/tests/README.md\"
REQUIRED_MARKERS = {
    TESTS_README_PATH: (
        \"`scripts/zigux/check-phase8-tests-readme-alignment.py`\",
        \"`scripts/zigux/check-phase8-exec-cmd-packet.py`\",
        \"`zigux/tests/phase8_exec_cmd.zig`\",
    ),
}
"""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / VALIDATOR_PATH, validator_text)
        _write(root / CHECKER_PATH, checker_text)
        if collect_sync_failures(root):
            raise AssertionError("matching marker sets should pass")

        _write(
            root / CHECKER_PATH,
            checker_text.replace('        \"`scripts/zigux/check-phase8-exec-cmd-packet.py`\",\n', ""),
        )
        failures = collect_sync_failures(root)
        if len(failures) != 1 or "`scripts/zigux/check-phase8-exec-cmd-packet.py`" not in failures[0]:
            raise AssertionError(f"missing-marker failure did not mention exec-cmd packet: {failures}")

        _write(root / CHECKER_PATH, checker_text + "\n")
        _write(
            root / VALIDATOR_PATH,
            validator_text.replace("    ),\n}\n", '        "`zigux/tests/phase8_help.zig`",\n    ),\n}\n'),
        )
        failures = collect_sync_failures(root)
        if len(failures) != 1 or "`zigux/tests/phase8_help.zig`" not in failures[0]:
            raise AssertionError(f"second missing-marker failure did not mention added marker: {failures}")

        _write(root / VALIDATOR_PATH, validator_text)
        _write(
            root / CHECKER_PATH,
            checker_text.replace("    ),\n}\n", '        "`zigux/tests/phase8_help.zig`",\n    ),\n}\n'),
        )
        failures = collect_sync_failures(root)
        if len(failures) != 1 or "`zigux/tests/phase8_help.zig`" not in failures[0]:
            raise AssertionError(f"extra-marker failure did not mention checker-only marker: {failures}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that validate-phase8.py and check-phase8-tests-readme-alignment.py "
            "enforce the same Phase 8 tests-root marker set."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing scripts/zigux and zigux/tests",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic validator/checker files",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        failures = collect_sync_failures(args.root)
    except MarkerExtractionError as exc:
        print(f"ERROR: {exc}")
        return 1

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 8 tests-readme marker sync check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
