#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import runpy
import tempfile


ROOT = Path(__file__).resolve().parents[2]
README_REL = "scripts/zigux/README.md"
TOOLING_PACKET_SCRIPT_REL = "scripts/zigux/check-phase3-tooling-packet.py"


def _ordered_unique(entries: list[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        if entry in seen:
            continue
        seen.add(entry)
        ordered.append(entry)
    return ordered


def _canonical_readme_entries(root: Path) -> tuple[list[str], list[str]]:
    tooling_packet_path = root / TOOLING_PACKET_SCRIPT_REL
    if not tooling_packet_path.exists():
        return [], [f"missing_tooling_packet_script:{TOOLING_PACKET_SCRIPT_REL}"]

    namespace = runpy.run_path(str(tooling_packet_path))
    raw_entries = namespace.get("REQUIRED_README_TOOLING_FILES")
    issues: list[str] = []
    basenames: list[str] = []

    if not isinstance(raw_entries, tuple):
        issues.append("missing_tooling_packet_constant:REQUIRED_README_TOOLING_FILES")
        return [], issues

    for rel in raw_entries:
        if not isinstance(rel, str):
            issues.append(f"invalid_tooling_packet_entry:{rel!r}")
            continue
        if not rel.startswith("scripts/zigux/"):
            continue
        basenames.append(Path(rel).name)

    if not basenames:
        issues.append("missing_tooling_packet_script_entries")
    return _ordered_unique(basenames), issues


def validate(root: Path) -> list[str]:
    readme_path = root / README_REL
    try:
        readme = readme_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"missing_readme:{README_REL}"]

    required_entries, issues = _canonical_readme_entries(root)
    for basename in required_entries:
        rel = f"scripts/zigux/{basename}"
        if not (root / rel).exists():
            issues.append(f"missing_repo_file:{rel}")
        if f"- `{basename}`" not in readme:
            issues.append(f"missing_readme_entry:{basename}")
    return issues


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_readme_tooling_inventory_") as tmp_dir:
        root = Path(tmp_dir) / "repo"

        tooling_packet_rels = (
            "scripts/zigux/check-phase3-build-roots.py",
            "scripts/zigux/check-phase3-canonical-survey-manifest.py",
            "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py",
            "scripts/zigux/check-phase3-rbtree-shared-lift-contract.py",
            "scripts/zigux/check-phase3-readme-tooling-inventory.py",
            "scripts/zigux/check-phase3-tooling-packet.py",
            "scripts/zigux/check-phase3-validation-flow.py",
            "scripts/zigux/generate-phase3-check-wrappers.py",
            "scripts/zigux/phase3_catalog.py",
            "scripts/zigux/phase3_check_lib.py",
            "scripts/zigux/run-phase3-checks.py",
            "scripts/zigux/validate-phase3.py",
            "scripts/zigux/validate_phase3_selftest.py",
            "scripts/zigux/validate-phase3-export-uapi-survey.py",
            "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
            "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
            "scripts/zigux/validate-phase3-rbtree-interop-survey.py",
            "scripts/zigux/validate-phase3-roadmap-gap-survey.py",
        )

        tooling_packet_script = "\n".join(
            (
                "REQUIRED_README_TOOLING_FILES = (",
                *[f"    {rel!r}," for rel in tooling_packet_rels],
                ")",
                "",
            )
        )
        _write(root / TOOLING_PACKET_SCRIPT_REL, tooling_packet_script)

        for rel in tooling_packet_rels:
            if rel == TOOLING_PACKET_SCRIPT_REL:
                continue
            _write(root / rel, "# stub\n")

        helper_lines = "\n".join(f"- `{Path(rel).name}`" for rel in tooling_packet_rels)
        _write(
            root / README_REL,
            "# scripts/zigux\n\nCurrent bootstrap helpers\n" + helper_lines + "\n",
        )

        issues = validate(root)
        if issues:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:baseline_failed:" + ",".join(issues)
            )

        _write(
            root / README_REL,
            "# scripts/zigux\n\nCurrent bootstrap helpers\n"
            + "\n".join(
                f"- `{Path(rel).name}`"
                for rel in tooling_packet_rels
                if rel != tooling_packet_rels[0]
            )
            + "\n",
        )
        issues = validate(root)
        expected = f"missing_readme_entry:{Path(tooling_packet_rels[0]).name}"
        if issues != [expected]:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:missing_readme_entry_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(
            root / README_REL,
            "# scripts/zigux\n\nCurrent bootstrap helpers\n" + helper_lines + "\n",
        )
        (root / tooling_packet_rels[-1]).unlink()
        issues = validate(root)
        expected = f"missing_repo_file:{tooling_packet_rels[-1]}"
        if issues != [expected]:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:missing_repo_file_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

    print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass")
    print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST_CASE_COUNT=2")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the scripts/zigux README inventory aligned with the live Phase 3 tooling packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker coverage.")
    parser.add_argument("root", nargs="?", help="Optional repo root override.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(Path(args.root).resolve() if args.root else ROOT)
    if issues:
        print("PHASE3_README_TOOLING_INVENTORY=fail")
        for issue in issues:
            print(issue)
        return 1

    required_entries, entry_issues = _canonical_readme_entries(Path(args.root).resolve() if args.root else ROOT)
    if entry_issues:
        print("PHASE3_README_TOOLING_INVENTORY=fail")
        for issue in entry_issues:
            print(issue)
        return 1

    print("PHASE3_README_TOOLING_INVENTORY=pass")
    print(f"PHASE3_README_TOOLING_INVENTORY_ENTRY_COUNT={len(required_entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
