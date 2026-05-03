#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
README_REL = "scripts/zigux/README.md"
MAKEFILE_REL = "zigux/Makefile"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"
README_HELPER_SECTION = "Current bootstrap helpers"
SCRIPT_PATTERN = re.compile(r"(?:python3|\$\(PYTHON\))\s+scripts/zigux/([A-Za-z0-9_.-]+\.py)(?:\s|$)")
REQUIRED_ROUTE_LINES = {
    MAKEFILE_REL: (
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-scripts-readme-helper-inventory.py --self-test",
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-scripts-readme-helper-inventory.py",
    ),
    WORKFLOW_REL: (
        "        run: python3 scripts/zigux/check-scripts-readme-helper-inventory.py --self-test",
        "        run: python3 scripts/zigux/check-scripts-readme-helper-inventory.py",
    ),
}


def _ordered_unique(entries: list[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        if entry in seen:
            continue
        seen.add(entry)
        ordered.append(entry)
    return ordered


def _read_text(root: Path, rel: str) -> tuple[str | None, list[str]]:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8"), []
    except FileNotFoundError:
        return None, [f"missing_repo_file:{rel}"]


def _helper_section_entries(readme: str) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    entries: list[str] = []
    found_heading = False
    collecting = False
    seen: set[str] = set()

    for line in readme.splitlines():
        stripped = line.strip()
        if not found_heading:
            if stripped == README_HELPER_SECTION:
                found_heading = True
                collecting = True
            continue

        if not collecting:
            break
        if stripped.startswith("- `") and stripped.endswith("`"):
            basename = stripped[len("- `") : -1]
            if basename in seen:
                issues.append(f"duplicate_readme_entry:{basename}")
                continue
            seen.add(basename)
            entries.append(basename)
            continue
        if not stripped:
            continue
        if entries:
            break

    if not found_heading:
        issues.append(f"missing_readme_section:{README_HELPER_SECTION}")
    elif not entries:
        issues.append("missing_readme_section_entries:current_bootstrap_helpers")
    return entries, issues


def _canonical_helper_entries(makefile: str, workflow: str) -> list[str]:
    matches = SCRIPT_PATTERN.findall(makefile)
    matches.extend(SCRIPT_PATTERN.findall(workflow))
    return _ordered_unique(matches)


def _require_route_lines(text: str, rel: str, issues: list[str]) -> None:
    lines = text.splitlines()
    for line in REQUIRED_ROUTE_LINES[rel]:
        count = sum(1 for candidate in lines if candidate.strip() == line.strip())
        if count != 1:
            issues.append(f"unexpected_route_line_count:{rel}:{count}:{line.strip()}")


def validate(root: Path) -> list[str]:
    readme, issues = _read_text(root, README_REL)
    if readme is None:
        return issues

    makefile, makefile_issues = _read_text(root, MAKEFILE_REL)
    workflow, workflow_issues = _read_text(root, WORKFLOW_REL)
    issues.extend(makefile_issues)
    issues.extend(workflow_issues)
    if makefile is None or workflow is None:
        return issues

    readme_entries, readme_issues = _helper_section_entries(readme)
    issues.extend(readme_issues)
    _require_route_lines(makefile, MAKEFILE_REL, issues)
    _require_route_lines(workflow, WORKFLOW_REL, issues)

    canonical_entries = _canonical_helper_entries(makefile, workflow)
    if not canonical_entries:
        issues.append("missing_canonical_helper_entries")
        return issues

    canonical_set = set(canonical_entries)
    readme_set = set(readme_entries)

    for entry in canonical_entries:
        rel = f"scripts/zigux/{entry}"
        if not (root / rel).exists():
            issues.append(f"missing_repo_file:{rel}")
        if entry not in readme_set:
            issues.append(f"missing_readme_entry:{entry}")

    for entry in readme_entries:
        if entry not in canonical_set:
            issues.append(f"unexpected_readme_entry:{entry}")

    if len(readme_entries) != len(canonical_entries):
        issues.append(
            f"readme_entry_count_mismatch:{len(readme_entries)}:{len(canonical_entries)}"
        )

    return issues


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_scripts_readme_helper_inventory_") as tmp_dir:
        root = Path(tmp_dir) / "repo"

        helper_entries = (
            "validate-bootstrap.py",
            "install-zig.py",
            "check-zig-toolchain.py",
            "check-phase2-kconfig-selftest-alignment.py",
            "check-phase7-argv-split-parity.py",
            "check-scripts-readme-helper-inventory.py",
        )

        helper_lines = "\n".join(f"- `{entry}`" for entry in helper_entries)
        _write(
            root / README_REL,
            "\n".join(
                (
                    "# scripts/zigux",
                    "",
                    "Current bootstrap helpers",
                    helper_lines,
                    "",
                    "Phase 1 flow",
                    "- placeholder",
                    "",
                )
            ),
        )
        _write(
            root / MAKEFILE_REL,
            "\n".join(
                (
                    "scripts-readme-validate:",
                    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-scripts-readme-helper-inventory.py --self-test",
                    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-scripts-readme-helper-inventory.py",
                    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-bootstrap.py",
                    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
                    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
                    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-parity.py --self-test",
                    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-parity.py",
                    "",
                )
            ),
        )
        _write(
            root / WORKFLOW_REL,
            "\n".join(
                (
                    "- name: Validate scripts README helper inventory",
                    "  run: python3 scripts/zigux/check-scripts-readme-helper-inventory.py",
                    "- name: Self-test scripts README helper inventory checker",
                    "  run: python3 scripts/zigux/check-scripts-readme-helper-inventory.py --self-test",
                    "- name: Setup",
                    "  run: python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
                    "- name: Validate bootstrap files",
                    "  run: python3 scripts/zigux/validate-bootstrap.py",
                    "- name: Show version",
                    "  run: python3 scripts/zigux/check-zig-toolchain.py",
                    "- name: Self-test Phase 2 kconfig alignment checker",
                    "  run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
                    "- name: Check Phase 2 kconfig alignment",
                    "  run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
                    "- name: Self-test Phase 7 argv split parity checker",
                    "  run: python3 scripts/zigux/check-phase7-argv-split-parity.py --self-test",
                    "- name: Check Phase 7 argv split parity",
                    "  run: python3 scripts/zigux/check-phase7-argv-split-parity.py",
                    "",
                )
            ),
        )

        for entry in helper_entries:
            _write(root / "scripts" / "zigux" / entry, "# stub\n")

        issues = validate(root)
        if issues:
            raise SystemExit(
                "scripts-readme-helper-inventory-self-test:baseline_failed:"
                + ",".join(issues)
            )

        _write(
            root / README_REL,
            "\n".join(
                (
                    "# scripts/zigux",
                    "",
                    "Current bootstrap helpers",
                    "\n".join(
                        f"- `{entry}`"
                        for entry in helper_entries
                        if entry != "check-phase7-argv-split-parity.py"
                    ),
                    "",
                )
            ),
        )
        issues = validate(root)
        expected = [
            "missing_readme_entry:check-phase7-argv-split-parity.py",
            "readme_entry_count_mismatch:5:6",
        ]
        if issues != expected:
            raise SystemExit(
                "scripts-readme-helper-inventory-self-test:missing_readme_entry_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(
            root / README_REL,
            "\n".join(
                (
                    "# scripts/zigux",
                    "",
                    "Current bootstrap helpers",
                    "\n".join(
                        (
                            "- `validate-bootstrap.py`",
                            "- `install-zig.py`",
                            "- `check-zig-toolchain.py`",
                            "- `check-phase2-kconfig-selftest-alignment.py`",
                            "- `check-phase7-argv-split-parity.py`",
                            "- `check-scripts-readme-helper-inventory.py`",
                            "- `unexpected-helper.py`",
                        )
                    ),
                    "",
                )
            ),
        )
        issues = validate(root)
        expected = [
            "unexpected_readme_entry:unexpected-helper.py",
            "readme_entry_count_mismatch:7:6",
        ]
        if issues != expected:
            raise SystemExit(
                "scripts-readme-helper-inventory-self-test:unexpected_readme_entry_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(
            root / README_REL,
            "\n".join(
                (
                    "# scripts/zigux",
                    "",
                    "Current bootstrap helpers",
                    "\n".join(
                        (
                            "- `validate-bootstrap.py`",
                            "- `install-zig.py`",
                            "- `check-zig-toolchain.py`",
                            "- `check-phase2-kconfig-selftest-alignment.py`",
                            "- `check-phase2-kconfig-selftest-alignment.py`",
                            "- `check-phase7-argv-split-parity.py`",
                            "- `check-scripts-readme-helper-inventory.py`",
                        )
                    ),
                    "",
                )
            ),
        )
        issues = validate(root)
        expected = [
            "duplicate_readme_entry:check-phase2-kconfig-selftest-alignment.py",
        ]
        if issues != expected:
            raise SystemExit(
                "scripts-readme-helper-inventory-self-test:duplicate_readme_entry_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(
            root / README_REL,
            "\n".join(
                (
                    "# scripts/zigux",
                    "",
                    "Current bootstrap helpers",
                    helper_lines,
                    "",
                    "Phase 1 flow",
                    "- placeholder",
                    "",
                )
            ),
        )
        _write(
            root / MAKEFILE_REL,
            "\n".join(
                (
                    "scripts-readme-validate:",
                    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-scripts-readme-helper-inventory.py",
                    "",
                )
            ),
        )
        issues = validate(root)
        expected = [
            "unexpected_route_line_count:zigux/Makefile:0:cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-scripts-readme-helper-inventory.py --self-test",
        ]
        if issues != expected:
            raise SystemExit(
                "scripts-readme-helper-inventory-self-test:missing_makefile_route_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(
            root / README_REL,
            "\n".join(
                (
                    "# scripts/zigux",
                    "",
                    "Current bootstrap helpers",
                    helper_lines,
                    "",
                    "Phase 1 flow",
                    "- placeholder",
                    "",
                )
            ),
        )
        _write(
            root / MAKEFILE_REL,
            "\n".join(
                (
                    "scripts-readme-validate:",
                    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-scripts-readme-helper-inventory.py --self-test",
                    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-scripts-readme-helper-inventory.py",
                    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-bootstrap.py",
                    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
                    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
                    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-parity.py --self-test",
                    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-parity.py",
                    "",
                )
            ),
        )

        _write(
            root / WORKFLOW_REL,
            "\n".join(
                (
                    "- name: Validate scripts README helper inventory",
                    "  run: python3 scripts/zigux/check-scripts-readme-helper-inventory.py",
                    "- name: Setup",
                    "  run: python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
                    "",
                )
            ),
        )
        issues = validate(root)
        expected = [
            "unexpected_route_line_count:.github/workflows/zigux-bootstrap.yml:0:run: python3 scripts/zigux/check-scripts-readme-helper-inventory.py --self-test",
            "unexpected_readme_entry:check-zig-toolchain.py",
            "readme_entry_count_mismatch:6:5",
        ]
        if issues != expected:
            raise SystemExit(
                "scripts-readme-helper-inventory-self-test:missing_workflow_route_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

    print("SCRIPTS_README_HELPER_INVENTORY_SELF_TEST=pass")
    print("SCRIPTS_README_HELPER_INVENTORY_SELF_TEST_CASE_COUNT=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shared scripts/zigux README helper inventory aligned with live repo-owned Python entrypoints."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker coverage.")
    parser.add_argument("root", nargs="?", help="Optional repo root override.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = Path(args.root).resolve() if args.root else ROOT
    issues = validate(root)
    if issues:
        print("SCRIPTS_README_HELPER_INVENTORY=fail")
        for issue in issues:
            print(issue)
        return 1

    canonical_entries = _canonical_helper_entries(
        (root / MAKEFILE_REL).read_text(encoding="utf-8"),
        (root / WORKFLOW_REL).read_text(encoding="utf-8"),
    )
    print("SCRIPTS_README_HELPER_INVENTORY=pass")
    print(f"SCRIPTS_README_HELPER_INVENTORY_ENTRY_COUNT={len(canonical_entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
