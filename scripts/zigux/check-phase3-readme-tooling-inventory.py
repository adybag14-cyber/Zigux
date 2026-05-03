#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import runpy
import tempfile


ROOT = Path(__file__).resolve().parents[2]
README_REL = "scripts/zigux/README.md"
TOOLING_PACKET_SCRIPT_REL = "scripts/zigux/check-phase3-tooling-packet.py"
README_HELPER_SECTION = "Current bootstrap helpers"
REQUIRED_PHASE3_FLOW_SNIPPETS = (
    "`validate-phase3.py` is the validator-first entrypoint for the shared Phase 3 ABI and interop packet, and `make -C zigux phase3-validate` plus the bootstrap workflow replay that same route before the broader build-backed or survey-backed checks run.",
    "`validate-phase3-roadmap-gap-survey.py`, `validate-phase3-rbtree-interop-survey.py`, `check-phase3-rbtree-shared-lift-contract.py`, `validate-phase3-export-uapi-survey.py`, `validate-phase3-low-level-wrapper-survey.py`, `validate-phase3-policy-unsafe-survey.py`, `check-phase3-policy-unsafe-mmio-consumer.py`, `check-phase3-abi-layout-packet.py`, `check-phase3-abi-binding-constants.py`, `check-phase3-tooling-packet.py`, `check-phase3-readme-tooling-inventory.py`, `check-phase3-validation-flow.py`, `check-phase3-build-roots.py`, and `check-phase3-canonical-survey-manifest.py` stay as supporting checks inside that validator-first route rather than standalone bootstrap or release entrypoints.",
)
EXACT_ONCE_PHASE3_FLOW_SNIPPETS = REQUIRED_PHASE3_FLOW_SNIPPETS


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
    issues: list[str] = []

    canonical_helper = namespace.get("canonical_readme_tooling_files")
    if callable(canonical_helper):
        raw_entries, helper_issues = canonical_helper(root)
        issues.extend(helper_issues)
    else:
        raw_entries = namespace.get("REQUIRED_README_TOOLING_FILES")
        if not isinstance(raw_entries, tuple):
            issues.append("missing_tooling_packet_constant:REQUIRED_README_TOOLING_FILES")
            return [], issues

    basenames: list[str] = []
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


def _require_snippets(
    text: str,
    snippets: tuple[str, ...],
    prefix: str,
    issues: list[str],
) -> None:
    for snippet in snippets:
        if snippet not in text:
            issues.append(f"{prefix}:{snippet}")


def _require_exact_count(
    text: str,
    snippets: tuple[str, ...],
    prefix: str,
    expected_count: int,
    issues: list[str],
) -> None:
    for snippet in snippets:
        actual_count = text.count(snippet)
        if actual_count != expected_count:
            issues.append(f"{prefix}:{actual_count}:{snippet}")


def validate(root: Path) -> list[str]:
    readme_path = root / README_REL
    try:
        readme = readme_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"missing_readme:{README_REL}"]

    required_entries, issues = _canonical_readme_entries(root)
    readme_entries, section_issues = _helper_section_entries(readme)
    issues.extend(section_issues)
    _require_snippets(readme, REQUIRED_PHASE3_FLOW_SNIPPETS, "missing_phase3_flow_snippet", issues)
    _require_exact_count(
        readme,
        EXACT_ONCE_PHASE3_FLOW_SNIPPETS,
        "unexpected_phase3_flow_snippet_count",
        1,
        issues,
    )

    required_set = set(required_entries)
    readme_set = set(readme_entries)

    missing_entries: list[str] = []

    for basename in required_entries:
        rel = f"scripts/zigux/{basename}"
        if not (root / rel).exists():
            issues.append(f"missing_repo_file:{rel}")
        if basename not in readme_set:
            missing_entries.append(basename)
            issues.append(f"missing_readme_entry:{basename}")

    filtered_entries = [basename for basename in readme_entries if basename in required_set]
    if not missing_entries and filtered_entries != required_entries:
        issues.append("readme_entry_order_drift:current_bootstrap_helpers")

    return issues


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _fixture_phase3_flow() -> str:
    return "\n".join(
        (
            "Phase 3 flow",
            f"- {REQUIRED_PHASE3_FLOW_SNIPPETS[0]}",
            f"- {REQUIRED_PHASE3_FLOW_SNIPPETS[1]}",
            "",
        )
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_readme_tooling_inventory_") as tmp_dir:
        root = Path(tmp_dir) / "repo"

        tooling_packet_rels = (
            "scripts/zigux/validate-phase3-roadmap-gap-survey.py",
            "scripts/zigux/check-phase3-build-roots.py",
            "scripts/zigux/check-phase3-tooling-packet.py",
            "scripts/zigux/check-phase3-readme-tooling-inventory.py",
            "scripts/zigux/validate-phase3.py",
        )

        tooling_packet_script = "\n".join(
            (
                "def canonical_readme_tooling_files(root):",
                "    return (",
                "        [",
                *[f"            {rel!r}," for rel in tooling_packet_rels],
                "        ],",
                "        [],",
                "    )",
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
            "\n".join(
                (
                    "# scripts/zigux",
                    "",
                    "Current bootstrap helpers",
                    "- `artifact_diff.py`",
                    helper_lines,
                    "",
                    _fixture_phase3_flow(),
                )
            ),
        )

        issues = validate(root)
        if issues:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:baseline_failed:" + ",".join(issues)
            )

        _write(
            root / README_REL,
            "\n".join(
                (
                    "# scripts/zigux",
                    "",
                    "Current bootstrap helpers",
                    *[
                        f"- `{Path(rel).name}`"
                        for rel in tooling_packet_rels
                        if rel != tooling_packet_rels[0]
                    ],
                    "",
                    _fixture_phase3_flow(),
                )
            ),
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
            "\n".join(
                (
                    "# scripts/zigux",
                    "",
                    "Current bootstrap helpers",
                    f"- `{Path(tooling_packet_rels[1]).name}`",
                    f"- `{Path(tooling_packet_rels[0]).name}`",
                    *[f"- `{Path(rel).name}`" for rel in tooling_packet_rels[2:]],
                    "",
                    _fixture_phase3_flow(),
                )
            ),
        )
        issues = validate(root)
        expected = ["readme_entry_order_drift:current_bootstrap_helpers"]
        if issues != expected:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:order_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(
            root / README_REL,
            "\n".join(
                (
                    "# scripts/zigux",
                    "",
                    "Current bootstrap helpers",
                    f"- `{Path(tooling_packet_rels[0]).name}`",
                    f"- `{Path(tooling_packet_rels[0]).name}`",
                    *[f"- `{Path(rel).name}`" for rel in tooling_packet_rels[1:]],
                    "",
                    _fixture_phase3_flow(),
                )
            ),
        )
        issues = validate(root)
        expected = [f"duplicate_readme_entry:{Path(tooling_packet_rels[0]).name}"]
        if issues != expected:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:duplicate_readme_entry_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(
            root / README_REL,
            "\n".join(
                (
                    "# scripts/zigux",
                    "",
                    "Current bootstrap helpers",
                    "- `artifact_diff.py`",
                    helper_lines,
                    "",
                )
            ),
        )
        issues = validate(root)
        expected = [
            f"missing_phase3_flow_snippet:{REQUIRED_PHASE3_FLOW_SNIPPETS[0]}",
            f"missing_phase3_flow_snippet:{REQUIRED_PHASE3_FLOW_SNIPPETS[1]}",
            f"unexpected_phase3_flow_snippet_count:0:{REQUIRED_PHASE3_FLOW_SNIPPETS[0]}",
            f"unexpected_phase3_flow_snippet_count:0:{REQUIRED_PHASE3_FLOW_SNIPPETS[1]}",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:missing_phase3_flow_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(
            root / README_REL,
            "\n".join(
                (
                    "# scripts/zigux",
                    "",
                    "Current bootstrap helpers",
                    "- `artifact_diff.py`",
                    helper_lines,
                    "",
                    _fixture_phase3_flow() + f"- {REQUIRED_PHASE3_FLOW_SNIPPETS[0]}",
                )
            ),
        )
        issues = validate(root)
        expected = [
            f"unexpected_phase3_flow_snippet_count:2:{REQUIRED_PHASE3_FLOW_SNIPPETS[0]}"
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:duplicate_phase3_flow_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(
            root / README_REL,
            "\n".join(
                (
                    "# scripts/zigux",
                    "",
                    "Current bootstrap helpers",
                    "- `artifact_diff.py`",
                    helper_lines,
                    "",
                    _fixture_phase3_flow() + f"- {REQUIRED_PHASE3_FLOW_SNIPPETS[1]}",
                )
            ),
        )
        issues = validate(root)
        expected = [
            f"unexpected_phase3_flow_snippet_count:2:{REQUIRED_PHASE3_FLOW_SNIPPETS[1]}"
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:duplicate_phase3_supporting_checks_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(
            root / README_REL,
            "\n".join(
                (
                    "# scripts/zigux",
                    "",
                    "Current bootstrap helpers",
                    "- `artifact_diff.py`",
                    helper_lines,
                    "",
                    _fixture_phase3_flow(),
                )
            ),
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
    print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST_CASE_COUNT=7")
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
