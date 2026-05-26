#!/usr/bin/env python3
"""Guard the shared Phase 2 make-route packet in closure-side reminder surfaces."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
MAKEFILE = ROOT / "zigux" / "Makefile"

ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
    "phase2",
)
ROUTE_MARKERS = tuple(f"`make -C zigux {route}`" for route in ROUTES)
SHARED_ROUTES_LINE = (
    "- `PHASE2_SHARED_MAKE_ROUTES="
    + ",".join(f"make -C zigux {route}" for route in ROUTES)
    + "`"
)
MINIMAL_CLOSURE_MARKERS = (
    "shipped make-wrapper routes that current `master` can actually replay:",
    SHARED_ROUTES_LINE,
)

EXPECTED_SELF_TEST_CASE_COUNT = 10


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


def count_target_definitions(text: str, route: str) -> int:
    prefix = f"{route}:"
    return sum(1 for line in text.splitlines() if line.strip().startswith(prefix))


def phony_targets_present(text: str) -> set[str]:
    targets: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith(".PHONY:"):
            continue
        _, suffix = stripped.split(":", 1)
        targets.update(token for token in suffix.strip().split() if token)
    return targets


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    closure_text = read_text(resolve_path(root, CLOSURE))
    for marker in MINIMAL_CLOSURE_MARKERS:
        count = count_exact_lines(closure_text, marker)
        if count == 0:
            issues.append(("MISSING_CLOSURE_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_CLOSURE_MARKER", f"{marker}:count={count}"))
    for marker in ROUTE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_ROUTE_MARKER", marker))

    bootstrap_text = read_text(resolve_path(root, BOOTSTRAP_NOTES))
    for marker in ROUTE_MARKERS:
        if marker not in bootstrap_text:
            issues.append(("MISSING_BOOTSTRAP_ROUTE_MARKER", marker))

    review_text = read_text(resolve_path(root, REVIEW_CHECKLIST))
    for marker in ROUTE_MARKERS:
        if marker not in review_text:
            issues.append(("MISSING_REVIEW_ROUTE_MARKER", marker))

    makefile_text = read_text(resolve_path(root, MAKEFILE))
    phony_targets = phony_targets_present(makefile_text)
    for route in ROUTES:
        if route not in phony_targets:
            issues.append(("MISSING_MAKEFILE_PHONY_TARGET", route))
        count = count_target_definitions(makefile_text, route)
        target_line = f"{route}:"
        if count == 0:
            issues.append(("MISSING_MAKEFILE_TARGET", target_line))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_TARGET", f"{target_line}:count={count}"))

    return issues


def build_self_test_root(root: Path) -> None:
    closure_lines = [
        "# Phase 2 Closure",
        "",
        "shipped make-wrapper routes that current `master` can actually replay:",
        *[f"- {marker}" for marker in ROUTE_MARKERS],
        SHARED_ROUTES_LINE,
        "",
    ]
    write_text(resolve_path(root, CLOSURE), "\n".join(closure_lines))

    bootstrap_lines = [
        "# Phase 2 Toolchain Bootstrap Notes",
        "",
        *[f"- {marker}" for marker in ROUTE_MARKERS],
        "",
    ]
    write_text(resolve_path(root, BOOTSTRAP_NOTES), "\n".join(bootstrap_lines))

    review_lines = [
        "# Zigux Review Checklist",
        "",
        *[f"* {marker}" for marker in ROUTE_MARKERS],
        "",
    ]
    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(review_lines))

    makefile_lines = [
        ".PHONY: " + " ".join(ROUTES) + "\n\n",
        *(f"{route}:\n\t@true\n" for route in ROUTES),
    ]
    write_text(resolve_path(root, MAKEFILE), "".join(makefile_lines))


def replace_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


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


def run_cli(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_shared_make_routes_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        closure_path = resolve_path(root, CLOSURE)
        closure_path.write_text(
            replace_exact_line(closure_path.read_text(encoding="utf-8"), SHARED_ROUTES_LINE),
            encoding="utf-8",
        )
        assert ("MISSING_CLOSURE_MARKER", SHARED_ROUTES_LINE) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = resolve_path(root, CLOSURE)
        closure_path.write_text(
            duplicate_exact_line(closure_path.read_text(encoding="utf-8"), SHARED_ROUTES_LINE),
            encoding="utf-8",
        )
        assert ("DUPLICATE_CLOSURE_MARKER", f"{SHARED_ROUTES_LINE}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = resolve_path(root, CLOSURE)
        closure_path.write_text(
            replace_once(closure_path.read_text(encoding="utf-8"), ROUTE_MARKERS[0]),
            encoding="utf-8",
        )
        assert ("MISSING_CLOSURE_ROUTE_MARKER", ROUTE_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        bootstrap_path = resolve_path(root, BOOTSTRAP_NOTES)
        bootstrap_path.write_text(
            replace_once(bootstrap_path.read_text(encoding="utf-8"), ROUTE_MARKERS[1]),
            encoding="utf-8",
        )
        assert ("MISSING_BOOTSTRAP_ROUTE_MARKER", ROUTE_MARKERS[1]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        review_path = resolve_path(root, REVIEW_CHECKLIST)
        review_path.write_text(
            replace_once(review_path.read_text(encoding="utf-8"), ROUTE_MARKERS[2]),
            encoding="utf-8",
        )
        assert ("MISSING_REVIEW_ROUTE_MARKER", ROUTE_MARKERS[2]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_path.write_text(
            replace_exact_line(makefile_path.read_text(encoding="utf-8"), ".PHONY: " + " ".join(ROUTES), ".PHONY:"),
            encoding="utf-8",
        )
        assert ("MISSING_MAKEFILE_PHONY_TARGET", ROUTES[3]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_path.write_text(
            replace_exact_line(makefile_path.read_text(encoding="utf-8"), f"{ROUTES[4]}:"),
            encoding="utf-8",
        )
        assert ("MISSING_MAKEFILE_TARGET", f"{ROUTES[4]}:") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_path.write_text(
            makefile_path.read_text(encoding="utf-8") + f"{ROUTES[5]}:\n\t@true\n",
            encoding="utf-8",
        )
        assert ("DUPLICATE_MAKEFILE_TARGET", f"{ROUTES[5]}::count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        resolve_path(root, CLOSURE).unlink()
        result = run_cli(root)
        assert result.returncode == 1
        assert "required file missing:" in result.stderr
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_SHARED_MAKE_ROUTES_PACKET_SELF_TEST=pass")
    print(f"PHASE2_SHARED_MAKE_ROUTES_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def write_sample_root(root: Path) -> int:
    build_self_test_root(root.resolve())
    print(f"PHASE2_SHARED_MAKE_ROUTES_PACKET_SAMPLE_ROOT={root.resolve()}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the shared Phase 2 make-route packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root for replay validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root)

    issues = collect_issues(args.root.resolve())
    if issues:
        print("PHASE2_SHARED_MAKE_ROUTES_PACKET=fail")
        for code, value in issues:
            print(f"{code}:{value}")
        return 1

    print("PHASE2_SHARED_MAKE_ROUTES_PACKET=pass")
    print(f"PHASE2_SHARED_MAKE_ROUTES_PACKET_ROUTE_COUNT={len(ROUTES)}")
    print("PHASE2_SHARED_MAKE_ROUTES_PACKET_STATUS=present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
