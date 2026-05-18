#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "zigux-alpha" / "BOOTSTRAP_COMMIT_LEDGER.md"
ALPHA_README = ROOT / "zigux-alpha" / "README.md"

PRESENT_REPO_PATHS = (
    "Documentation/zigux/phase2-closure.md",
    "scripts/zigux/README.md",
)

GAP_REPO_PATHS = (
    "Documentation/zigux/artifact-diff.md",
)

LEDGER_MARKERS = (
    "25. `docs(zigux): reopen and close broadened Phase 2 tranche`",
    "- `Documentation/zigux/phase2-closure.md`",
    "- `Documentation/zigux/artifact-diff.md`",
    "- `scripts/zigux/README.md`",
    "- `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`",
    "- current direct-readback note: `Documentation/zigux/phase2-closure.md`, `scripts/zigux/README.md`, and `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md` are directly readable on current `master`",
    "- current direct-readback note: `Documentation/zigux/artifact-diff.md` is still absent on current `master`, so keep this broadened Phase 2 tranche framed as the target same-lane packet rather than fully landed current-master evidence until that companion returns",
    "## Scope Note",
    "- This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.",
    "- Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.",
)

README_MARKERS = (
    "- Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.",
    "- The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.",
    "- [Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)",
)

LEDGER_TEMPLATE = """25. `docs(zigux): reopen and close broadened Phase 2 tranche`
- `Documentation/zigux/phase2-closure.md`
- `Documentation/zigux/artifact-diff.md`
- `scripts/zigux/README.md`
- `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`
- current direct-readback note: `Documentation/zigux/phase2-closure.md`, `scripts/zigux/README.md`, and `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md` are directly readable on current `master`
- current direct-readback note: `Documentation/zigux/artifact-diff.md` is still absent on current `master`, so keep this broadened Phase 2 tranche framed as the target same-lane packet rather than fully landed current-master evidence until that companion returns

## Scope Note

- This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.
- Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.
"""

README_TEMPLATE = """# zigux-alpha

Rules
- Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.
- The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.

Start here
- [Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)
"""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve(root: Path, path: Path) -> Path:
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        rel = path
    return root / rel


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    ledger_text = read_text(resolve(root, LEDGER))
    for marker in LEDGER_MARKERS:
        if marker not in ledger_text:
            issues.append(("MISSING_LEDGER_MARKERS", marker))

    readme_text = read_text(resolve(root, ALPHA_README))
    for marker in README_MARKERS:
        if marker not in readme_text:
            issues.append(("MISSING_README_MARKERS", marker))

    for rel in PRESENT_REPO_PATHS:
        if not resolve(root, Path(rel)).exists():
            issues.append(("MISSING_PRESENT_REPO_PATHS", rel))

    for rel in GAP_REPO_PATHS:
        if resolve(root, Path(rel)).exists():
            issues.append(("UNEXPECTED_PRESENT_GAP_PATHS", rel))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_BOOTSTRAP_LEDGER_TRUTHFULNESS=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(resolve(root, LEDGER), LEDGER_TEMPLATE)
    write_text(resolve(root, ALPHA_README), README_TEMPLATE)
    for rel in PRESENT_REPO_PATHS:
        write_text(resolve(root, Path(rel)), "present\n")


def remove_marker(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(marker)
    return text.replace(marker, "", 1)


def run_self_test() -> int:
    checks = 0
    expected = 1 + len(LEDGER_MARKERS) + len(README_MARKERS) + len(PRESENT_REPO_PATHS) + len(GAP_REPO_PATHS) + 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_ledger_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in LEDGER_MARKERS:
            build_self_test_root(root)
            path = resolve(root, LEDGER)
            write_text(path, remove_marker(read_text(path), marker))
            assert ("MISSING_LEDGER_MARKERS", marker) in collect_issues(root)
            checks += 1

        for marker in README_MARKERS:
            build_self_test_root(root)
            path = resolve(root, ALPHA_README)
            write_text(path, remove_marker(read_text(path), marker))
            assert ("MISSING_README_MARKERS", marker) in collect_issues(root)
            checks += 1

        for rel in PRESENT_REPO_PATHS:
            build_self_test_root(root)
            resolve(root, Path(rel)).unlink()
            assert ("MISSING_PRESENT_REPO_PATHS", rel) in collect_issues(root)
            checks += 1

        for rel in GAP_REPO_PATHS:
            build_self_test_root(root)
            write_text(resolve(root, Path(rel)), "should stay missing\n")
            assert ("UNEXPECTED_PRESENT_GAP_PATHS", rel) in collect_issues(root)
            checks += 1

        build_self_test_root(root)
        resolve(root, LEDGER).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks += 1
        else:
            raise AssertionError("missing ledger did not abort")

    assert checks == expected, (checks, expected)
    print("PHASE2_BOOTSTRAP_LEDGER_TRUTHFULNESS_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_LEDGER_TRUTHFULNESS_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 25 broadened Phase 2 ledger note aligned to current direct-readback repo reality."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_LEDGER_TRUTHFULNESS=pass")
    print(f"PHASE2_BOOTSTRAP_LEDGER_TRUTHFULNESS_LEDGER_MARKER_COUNT={len(LEDGER_MARKERS)}")
    print(f"PHASE2_BOOTSTRAP_LEDGER_TRUTHFULNESS_README_MARKER_COUNT={len(README_MARKERS)}")
    print(f"PHASE2_BOOTSTRAP_LEDGER_TRUTHFULNESS_PRESENT_PATH_COUNT={len(PRESENT_REPO_PATHS)}")
    print(f"PHASE2_BOOTSTRAP_LEDGER_TRUTHFULNESS_GAP_PATH_COUNT={len(GAP_REPO_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
