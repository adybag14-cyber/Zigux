#!/usr/bin/env python3
"""Guard the shared Phase 2 validator-pair reminder packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) >= 3 else Path.cwd()

WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
TESTS_README = Path("zigux/tests/README.md")
BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
VALIDATE_PHASE2 = Path("scripts/zigux/validate-phase2.py")
VALIDATE_PHASE2_CLOSURE = Path("scripts/zigux/validate-phase2-closure.py")
MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

VALIDATOR_PATH_MARKERS = (
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
)

CLOSURE_PACKET_LINES = (
    "- shared validator pair: `python3 scripts/zigux/validate-phase2.py` and `python3 scripts/zigux/validate-phase2-closure.py`",
    "- `PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py`",
)

WORKFLOW_LINES = (
    "run: make -C zigux phase2-validate",
    "run: make -C zigux phase2",
    "run: python3 scripts/zigux/validate-phase2.py",
)

MAKEFILE_LINES = (
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    "phase2: phase2-validate",
)

VALIDATE_PHASE2_SNIPPETS = (
    '"scripts/zigux/validate-phase2-closure.py",',
    '"zigux/Makefile",',
    '"zigux/tests/fixtures/phase2_tool_manifest.json",',
    '"run: make -C zigux phase2-validate",',
    '"run: make -C zigux phase2",',
    '"run: python3 scripts/zigux/validate-phase2.py",',
)

VALIDATE_PHASE2_CLOSURE_SNIPPETS = (
    'PHASE2_VALIDATE_REL = Path("scripts/zigux/validate-phase2.py")',
    'PHASE2_CLOSURE_VALIDATE_REL = Path("scripts/zigux/validate-phase2-closure.py")',
    "VALIDATOR_COMMANDS = (",
    '"python3 scripts/zigux/validate-phase2.py",',
    '"python3 scripts/zigux/validate-phase2-closure.py",',
    "PHASE2_VALIDATE_REL,",
    "PHASE2_CLOSURE_VALIDATE_REL,",
)

EXPECTED_VALIDATORS = (
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
)

REMINDER_SURFACES = (
    TESTS_README,
    BOOTSTRAP_NOTES,
    PHASE2_CLOSURE,
)

EXPECTED_SELF_TEST_CASE_COUNT = 24


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


def write_json(path: Path, payload: object) -> None:
    write_text(path, json.dumps(payload, indent=2) + "\n")


def count_exact_line(text: str, needle: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == needle)


def remove_once(text: str, needle: str) -> str:
    if needle not in text:
        raise AssertionError(f"missing marker for mutation: {needle}")
    return text.replace(needle, "", 1)


def replace_exact_line(text: str, needle: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == needle:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"missing exact line for mutation: {needle}")


def duplicate_exact_line(text: str, needle: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == needle:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"missing exact line for duplication: {needle}")


def require_markers(text: str, code: str, markers: tuple[str, ...]) -> list[tuple[str, str]]:
    failures: list[tuple[str, str]] = []
    for marker in markers:
        if marker not in text:
            failures.append((code, marker))
    return failures


def require_exact_lines(
    text: str, code_missing: str, code_duplicate: str, lines: tuple[str, ...]
) -> list[tuple[str, str]]:
    failures: list[tuple[str, str]] = []
    for line in lines:
        count = count_exact_line(text, line)
        if count == 0:
            failures.append((code_missing, line))
        elif count != 1:
            failures.append((code_duplicate, f"{line}:count={count}"))
    return failures


def load_manifest_validators(path: Path) -> object:
    payload = json.loads(read_text(path))
    if not isinstance(payload, dict):
        return ("INVALID_MANIFEST_SHAPE", "root")
    surfaces = payload.get("present_surfaces")
    if not isinstance(surfaces, dict):
        return ("INVALID_MANIFEST_SHAPE", "present_surfaces")
    validators = surfaces.get("validators")
    if not isinstance(validators, list) or not all(isinstance(item, str) for item in validators):
        return ("INVALID_MANIFEST_SHAPE", "validators")
    return validators


def collect_failures(root: Path) -> list[tuple[str, str]]:
    failures: list[tuple[str, str]] = []
    required_paths = (
        *REMINDER_SURFACES,
        WORKFLOW,
        MAKEFILE,
        VALIDATE_PHASE2,
        VALIDATE_PHASE2_CLOSURE,
        MANIFEST,
    )
    for rel in required_paths:
        if not resolve(root, rel).is_file():
            failures.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if failures:
        return failures

    reminder_texts = {rel: read_text(resolve(root, rel)) for rel in REMINDER_SURFACES}
    workflow_text = read_text(resolve(root, WORKFLOW))
    makefile_text = read_text(resolve(root, MAKEFILE))
    validate_phase2_text = read_text(resolve(root, VALIDATE_PHASE2))
    validate_phase2_closure_text = read_text(resolve(root, VALIDATE_PHASE2_CLOSURE))

    for rel, text in reminder_texts.items():
        failures.extend(
            require_markers(text, f"MISSING_REMINDER_MARKER:{rel.as_posix()}", VALIDATOR_PATH_MARKERS)
        )

    failures.extend(
        require_exact_lines(
            reminder_texts[PHASE2_CLOSURE],
            "MISSING_CLOSURE_PACKET_LINE",
            "DUPLICATE_CLOSURE_PACKET_LINE",
            CLOSURE_PACKET_LINES,
        )
    )
    failures.extend(
        require_exact_lines(
            workflow_text, "MISSING_WORKFLOW_LINE", "DUPLICATE_WORKFLOW_LINE", WORKFLOW_LINES
        )
    )
    failures.extend(
        require_exact_lines(
            makefile_text, "MISSING_MAKEFILE_LINE", "DUPLICATE_MAKEFILE_LINE", MAKEFILE_LINES
        )
    )
    failures.extend(
        require_markers(
            validate_phase2_text, "MISSING_VALIDATE_PHASE2_SNIPPET", VALIDATE_PHASE2_SNIPPETS
        )
    )
    failures.extend(
        require_markers(
            validate_phase2_closure_text,
            "MISSING_VALIDATE_PHASE2_CLOSURE_SNIPPET",
            VALIDATE_PHASE2_CLOSURE_SNIPPETS,
        )
    )

    validators = load_manifest_validators(resolve(root, MANIFEST))
    if isinstance(validators, tuple):
        failures.append(validators)
        return failures
    if tuple(validators) != EXPECTED_VALIDATORS:
        failures.append(("VALIDATOR_LIST_MISMATCH", ",".join(validators)))

    return failures


def build_sample_root(root: Path) -> None:
    tests_readme = """# zigux/tests

## Phase 2 review packet

  * `scripts/zigux/validate-phase2.py`
  * `scripts/zigux/validate-phase2-closure.py`
"""
    bootstrap_notes = """# Phase 2 Toolchain Bootstrap Notes

- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/check-phase2-bootstrap-workflow-routes.py`, and `zigux/Makefile` keep the bounded closure-side, closure-validator, validator-entrypoint, bootstrap workflow-route, and tests-facing packet reviewable
"""
    closure_note = """# Phase 2 Closure

## Status

- shared validator pair: `python3 scripts/zigux/validate-phase2.py` and `python3 scripts/zigux/validate-phase2-closure.py`

## Shared Replay Routes

- `PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py`

## Reminder

- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
"""
    workflow = """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Run current Phase 2 validate make route
        run: make -C zigux phase2-validate
      - name: Run current Phase 2 aggregate make route
        run: make -C zigux phase2
      - name: Validate current Phase 2 tool packet
        run: python3 scripts/zigux/validate-phase2.py
"""
    makefile = """phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep
\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py

phase2: phase2-validate
"""
    validate_phase2 = """#!/usr/bin/env python3
REQUIRED_PATHS = (
    "scripts/zigux/validate-phase2-closure.py",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
)
REQUIRED_WORKFLOW_LINES = (
    "run: make -C zigux phase2-validate",
    "run: make -C zigux phase2",
    "run: python3 scripts/zigux/validate-phase2.py",
)
"""
    validate_phase2_closure = """#!/usr/bin/env python3
from pathlib import Path
PHASE2_VALIDATE_REL = Path("scripts/zigux/validate-phase2.py")
PHASE2_CLOSURE_VALIDATE_REL = Path("scripts/zigux/validate-phase2-closure.py")
VALIDATOR_COMMANDS = (
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py",
)
REQUIRED_FILES = (
    PHASE2_VALIDATE_REL,
    PHASE2_CLOSURE_VALIDATE_REL,
)
"""
    manifest = {
        "present_surfaces": {
            "validators": list(EXPECTED_VALIDATORS),
        },
        "repo_reality_gaps": [],
    }

    write_text(resolve(root, TESTS_README), tests_readme)
    write_text(resolve(root, BOOTSTRAP_NOTES), bootstrap_notes)
    write_text(resolve(root, PHASE2_CLOSURE), closure_note)
    write_text(resolve(root, WORKFLOW), workflow)
    write_text(resolve(root, MAKEFILE), makefile)
    write_text(resolve(root, VALIDATE_PHASE2), validate_phase2)
    write_text(resolve(root, VALIDATE_PHASE2_CLOSURE), validate_phase2_closure)
    write_json(resolve(root, MANIFEST), manifest)


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_validator_pair_surface_") as tmpdir:
        root = Path(tmpdir)

        build_sample_root(root)
        assert collect_failures(root) == []
        checks += 1

        for rel in REMINDER_SURFACES:
            for marker in VALIDATOR_PATH_MARKERS:
                build_sample_root(root)
                path = resolve(root, rel)
                write_text(path, remove_once(read_text(path), marker))
                assert any(
                    code.startswith("MISSING_REMINDER_MARKER") and detail == marker
                    for code, detail in collect_failures(root)
                )
                checks += 1

        for line in CLOSURE_PACKET_LINES:
            build_sample_root(root)
            path = resolve(root, PHASE2_CLOSURE)
            write_text(path, replace_exact_line(read_text(path), line, "- dropped"))
            assert ("MISSING_CLOSURE_PACKET_LINE", line) in collect_failures(root)
            checks += 1

        build_sample_root(root)
        path = resolve(root, PHASE2_CLOSURE)
        write_text(path, duplicate_exact_line(read_text(path), CLOSURE_PACKET_LINES[0]))
        assert (
            "DUPLICATE_CLOSURE_PACKET_LINE",
            f"{CLOSURE_PACKET_LINES[0]}:count=2",
        ) in collect_failures(root)
        checks += 1

        for line in WORKFLOW_LINES:
            build_sample_root(root)
            path = resolve(root, WORKFLOW)
            write_text(path, replace_exact_line(read_text(path), line, "run: python3 scripts/zigux/other.py"))
            assert ("MISSING_WORKFLOW_LINE", line) in collect_failures(root)
            checks += 1

        build_sample_root(root)
        path = resolve(root, WORKFLOW)
        write_text(path, duplicate_exact_line(read_text(path), WORKFLOW_LINES[0]))
        assert ("DUPLICATE_WORKFLOW_LINE", f"{WORKFLOW_LINES[0]}:count=2") in collect_failures(root)
        checks += 1

        for line in MAKEFILE_LINES:
            build_sample_root(root)
            path = resolve(root, MAKEFILE)
            write_text(path, replace_exact_line(read_text(path), line, "# removed"))
            assert ("MISSING_MAKEFILE_LINE", line) in collect_failures(root)
            checks += 1

        build_sample_root(root)
        path = resolve(root, MAKEFILE)
        write_text(path, duplicate_exact_line(read_text(path), MAKEFILE_LINES[-1]))
        assert ("DUPLICATE_MAKEFILE_LINE", f"{MAKEFILE_LINES[-1]}:count=2") in collect_failures(root)
        checks += 1

        for snippet in (VALIDATE_PHASE2_SNIPPETS[0], VALIDATE_PHASE2_SNIPPETS[-1]):
            build_sample_root(root)
            path = resolve(root, VALIDATE_PHASE2)
            write_text(path, remove_once(read_text(path), snippet))
            assert ("MISSING_VALIDATE_PHASE2_SNIPPET", snippet) in collect_failures(root)
            checks += 1

        for snippet in (VALIDATE_PHASE2_CLOSURE_SNIPPETS[0], VALIDATE_PHASE2_CLOSURE_SNIPPETS[-1]):
            build_sample_root(root)
            path = resolve(root, VALIDATE_PHASE2_CLOSURE)
            write_text(path, remove_once(read_text(path), snippet))
            assert ("MISSING_VALIDATE_PHASE2_CLOSURE_SNIPPET", snippet) in collect_failures(root)
            checks += 1

        build_sample_root(root)
        path = resolve(root, MANIFEST)
        payload = json.loads(read_text(path))
        payload["present_surfaces"]["validators"] = ["scripts/zigux/validate-phase2-closure.py"]
        write_json(path, payload)
        assert (
            "VALIDATOR_LIST_MISMATCH",
            "scripts/zigux/validate-phase2-closure.py",
        ) in collect_failures(root)
        checks += 1

        build_sample_root(root)
        path = resolve(root, MANIFEST)
        write_json(path, {"present_surfaces": {"validators": "drifted"}, "repo_reality_gaps": []})
        assert ("INVALID_MANIFEST_SHAPE", "validators") in collect_failures(root)
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_VALIDATOR_PAIR_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_VALIDATOR_PAIR_SURFACE_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        return 0

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        print("PHASE2_VALIDATOR_PAIR_SURFACE=fail")
        for code, detail in failures:
            print(f"{code}:{detail}")
        return 1

    print("PHASE2_VALIDATOR_PAIR_SURFACE=pass")
    print(f"PHASE2_VALIDATOR_PAIR_SURFACE_REMINDER_SURFACE_COUNT={len(REMINDER_SURFACES)}")
    print(f"PHASE2_VALIDATOR_PAIR_SURFACE_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_VALIDATOR_PAIR_SURFACE_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    print(f"PHASE2_VALIDATOR_PAIR_SURFACE_VALIDATOR_COUNT={len(EXPECTED_VALIDATORS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
