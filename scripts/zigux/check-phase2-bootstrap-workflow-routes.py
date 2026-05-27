#!/usr/bin/env python3
"""Guard the current Phase 2 bootstrap make-route packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) >= 3 else Path.cwd()

BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")

ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
)

NOTE_MARKERS = tuple(f"`make -C zigux {route}`" for route in (*ROUTES, "phase2"))
WORKFLOW_LINES = tuple(f"run: make -C zigux {route}" for route in (*ROUTES, "phase2"))
MAKEFILE_RULE_LINES = (
    *(f"{route}:" for route in ROUTES),
    "phase2: phase2-validate",
)
PHONY_TOKENS = (
    ".PHONY:",
    *ROUTES,
    "phase2",
)
EXPECTED_SELF_TEST_CASE_COUNT = 20


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def count_exact_lines(text: str, needle: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == needle)


def require_substrings(text: str, label: str, needles: tuple[str, ...]) -> list[str]:
    return [f"{label}:missing:{needle}" for needle in needles if needle not in text]


def require_exact_line_counts(text: str, label: str, needles: tuple[str, ...]) -> list[str]:
    failures: list[str] = []
    for needle in needles:
        count = count_exact_lines(text, needle)
        if count != 1:
            failures.append(f"{label}:expected_once:actual_count={count}:{needle}")
    return failures


def phony_line(text: str) -> str:
    for line in text.splitlines():
        if line.startswith(".PHONY:"):
            return line
    return ""


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in (BOOTSTRAP_NOTES, WORKFLOW, MAKEFILE):
        if not resolve(root, rel).is_file():
            failures.append(f"missing_file:{rel.as_posix()}")
    if failures:
        return failures

    note_text = read_text(resolve(root, BOOTSTRAP_NOTES))
    workflow_text = read_text(resolve(root, WORKFLOW))
    makefile_text = read_text(resolve(root, MAKEFILE))

    failures.extend(require_substrings(note_text, BOOTSTRAP_NOTES.as_posix(), NOTE_MARKERS))
    failures.extend(require_exact_line_counts(workflow_text, WORKFLOW.as_posix(), WORKFLOW_LINES))
    failures.extend(require_exact_line_counts(makefile_text, MAKEFILE.as_posix(), MAKEFILE_RULE_LINES))
    failures.extend(require_substrings(phony_line(makefile_text), f"{MAKEFILE.as_posix()}:phony", PHONY_TOKENS))
    return failures


def build_sample_root(root: Path) -> None:
    note_lines = [
        "# Phase 2 Toolchain Bootstrap Notes",
        "",
        "## Current direct packet",
        "",
        "The rematerialized make-wrapper packet is directly readable on current `master` through "
        + ", ".join(NOTE_MARKERS[:-1])
        + f", and {NOTE_MARKERS[-1]}, so keep those routes in the present packet instead of the repo-reality-gap list.",
        "",
    ]
    workflow_lines = [
        "name: zigux-bootstrap",
        "jobs:",
        "  bootstrap:",
        "    steps:",
        *(
            line
            for route_line in WORKFLOW_LINES
            for line in ("      - name: route", f"        {route_line}")
        ),
        "",
    ]
    makefile_lines = [
        ".PHONY: " + " ".join((*ROUTES, "phase2")),
        "",
        *(f"{route}:\n\t@echo {route}" for route in ROUTES),
        "",
        "phase2: phase2-validate",
        "\t@echo phase2",
        "",
    ]

    write_text(resolve(root, BOOTSTRAP_NOTES), "\n".join(note_lines))
    write_text(resolve(root, WORKFLOW), "\n".join(workflow_lines))
    write_text(resolve(root, MAKEFILE), "\n".join(makefile_lines))


def remove_first(text: str, needle: str) -> str:
    if needle not in text:
        raise AssertionError(f"missing needle for mutation: {needle}")
    return text.replace(needle, "", 1)


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_workflow_routes_") as tmpdir:
        root = Path(tmpdir)

        build_sample_root(root)
        assert collect_failures(root) == []
        checks += 1

        note_path = resolve(root, BOOTSTRAP_NOTES)
        workflow_path = resolve(root, WORKFLOW)
        makefile_path = resolve(root, MAKEFILE)

        build_sample_root(root)
        note_path.write_text(remove_first(note_path.read_text(encoding="utf-8"), NOTE_MARKERS[1]), encoding="utf-8")
        assert any(NOTE_MARKERS[1] in failure for failure in collect_failures(root))
        checks += 1

        for workflow_line in (WORKFLOW_LINES[0], WORKFLOW_LINES[-1]):
            build_sample_root(root)
            workflow_path.write_text(remove_first(workflow_path.read_text(encoding="utf-8"), workflow_line), encoding="utf-8")
            assert any(workflow_line in failure for failure in collect_failures(root))
            checks += 1

        build_sample_root(root)
        workflow_text = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            workflow_text + "      - name: duplicate-route\n" + f"        {WORKFLOW_LINES[2]}\n",
            encoding="utf-8",
        )
        assert any(WORKFLOW_LINES[2] in failure for failure in collect_failures(root))
        checks += 1

        for makefile_line in (MAKEFILE_RULE_LINES[0], MAKEFILE_RULE_LINES[-1]):
            build_sample_root(root)
            makefile_path.write_text(remove_first(makefile_path.read_text(encoding="utf-8"), makefile_line), encoding="utf-8")
            assert any(makefile_line in failure for failure in collect_failures(root))
            checks += 1

        build_sample_root(root)
        makefile_path.write_text(
            makefile_path.read_text(encoding="utf-8").replace(
                ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
                ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-fixdep phase2-validate phase2",
                1,
            ),
            encoding="utf-8",
        )
        assert any("phony" in failure for failure in collect_failures(root))
        checks += 1

        for rel in (BOOTSTRAP_NOTES, WORKFLOW, MAKEFILE):
            build_sample_root(root)
            resolve(root, rel).unlink()
            assert f"missing_file:{rel.as_posix()}" in collect_failures(root)
            checks += 1

        for marker in (NOTE_MARKERS[0], NOTE_MARKERS[3], NOTE_MARKERS[6]):
            build_sample_root(root)
            note_path.write_text(remove_first(note_path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert any(marker in failure for failure in collect_failures(root))
            checks += 1

        for workflow_line in (WORKFLOW_LINES[1], WORKFLOW_LINES[4], WORKFLOW_LINES[-1]):
            build_sample_root(root)
            workflow_path.write_text(remove_first(workflow_path.read_text(encoding="utf-8"), workflow_line), encoding="utf-8")
            assert any(workflow_line in failure for failure in collect_failures(root))
            checks += 1

        build_sample_root(root)
        makefile_path.write_text(remove_first(makefile_path.read_text(encoding="utf-8"), MAKEFILE_RULE_LINES[3]), encoding="utf-8")
        assert any(MAKEFILE_RULE_LINES[3] in failure for failure in collect_failures(root))
        checks += 1

        build_sample_root(root)
        makefile_path.write_text(remove_first(makefile_path.read_text(encoding="utf-8"), "phase2-cross"), encoding="utf-8")
        assert any("phase2-cross" in failure for failure in collect_failures(root))
        checks += 1

        build_sample_root(root)
        note_path.write_text(note_path.read_text(encoding="utf-8").replace("phase2-tools", "phase2-tools-drift", 1), encoding="utf-8")
        assert any("phase2-tools" in failure for failure in collect_failures(root))
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_SELF_TEST_CASE_COUNT={checks}")
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
        for failure in failures:
            print(failure)
        return 1

    print("PHASE2_BOOTSTRAP_WORKFLOW_ROUTES=pass")
    print(f"PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_NOTE_MARKER_COUNT={len(NOTE_MARKERS)}")
    print(f"PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_BOOTSTRAP_WORKFLOW_ROUTES_MAKEFILE_LINE_COUNT={len(MAKEFILE_RULE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())