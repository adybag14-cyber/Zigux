#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import runpy
import tempfile


_SELF_PATH = Path(__file__).resolve()
ROOT = _SELF_PATH.parents[2] if len(_SELF_PATH.parents) > 2 else Path.cwd().resolve()
README_REL = "scripts/zigux/README.md"
TOOLING_PACKET_SCRIPT_REL = "scripts/zigux/check-phase3-tooling-packet.py"
MAKEFILE_REL = "zigux/Makefile"
README_HELPER_SECTION = "Current bootstrap helpers"
PHASE2_REQUIRED_HELPER_ENTRIES = ("check-phase2-kconfig-selftest-alignment.py",)
PHASE2_VALIDATE_TARGET = "phase2-validate:"
PHASE6_REQUIRED_HELPER_ENTRIES = ("check-phase6-base64-catalog-evidence.py",)
PHASE6_VALIDATE_TARGET = "phase6-validate:"
PHASE7_REQUIRED_HELPER_ENTRIES = ("check-phase7-argv-split-parity.py",)
PHASE7_VALIDATE_TARGET = "phase7-validate:"
PHASE11_REQUIRED_HELPER_ENTRIES = ("check-phase11-shared-replay-contract.py",)
PHASE11_VALIDATE_TARGET = "phase11-validate:"
PHASE13_VALIDATE_TARGET = "phase13-validate:"
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


def _find_duplicate_entries(entries: list[str]) -> list[str]:
    duplicates: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        if entry in seen and entry not in duplicates:
            duplicates.append(entry)
            continue
        seen.add(entry)
    return duplicates


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

    for basename in _find_duplicate_entries(basenames):
        issues.append(f"duplicate_canonical_readme_entry:{basename}")

    if not basenames:
        issues.append("missing_tooling_packet_script_entries")
    return _ordered_unique(basenames), issues


def _makefile_target_raw_helper_records(
    root: Path, target_name: str
) -> tuple[list[tuple[str, bool]], list[str]]:
    makefile_path = root / MAKEFILE_REL
    try:
        makefile = makefile_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [], [f"missing_makefile:{MAKEFILE_REL}"]

    entries: list[tuple[str, bool]] = []
    in_target = False
    for line in makefile.splitlines():
        stripped = line.strip()
        if not in_target:
            if stripped == target_name:
                in_target = True
            continue
        if stripped.endswith(":") and not line.startswith((" ", "\t")):
            break
        if "scripts/zigux/" not in stripped:
            continue
        rel = "scripts/zigux/" + stripped.split("scripts/zigux/", 1)[1].split()[0]
        if rel.endswith(".py"):
            entries.append((Path(rel).name, "--self-test" in stripped))

    if not entries:
        return [], [f"missing_makefile_target_entries:{target_name}"]
    return entries, []


def _require_makefile_target_route_count(
    entries: list[tuple[str, bool]],
    target_name: str,
    basename: str,
    expected_live_count: int,
    expected_self_test_count: int,
    issues: list[str],
) -> None:
    live_count = sum(1 for entry, is_self_test in entries if entry == basename and not is_self_test)
    self_test_count = sum(1 for entry, is_self_test in entries if entry == basename and is_self_test)
    if live_count != expected_live_count:
        issues.append(
            f"unexpected_makefile_live_route_count:{target_name}:{live_count}:{basename}"
        )
    if self_test_count != expected_self_test_count:
        issues.append(
            f"unexpected_makefile_self_test_route_count:{target_name}:{self_test_count}:{basename}"
        )


def _makefile_target_helper_entries(root: Path, target_name: str) -> tuple[list[str], list[str]]:
    entries, issues = _makefile_target_raw_helper_records(root, target_name)
    if issues:
        return [], issues
    ordered_entries = _ordered_unique([basename for basename, _ in entries])
    for basename in ordered_entries:
        expected_self_test_count = 0 if basename.startswith("validate-") else 1
        _require_makefile_target_route_count(
            entries,
            target_name,
            basename,
            1,
            expected_self_test_count,
            issues,
        )
    return ordered_entries, issues


def _makefile_named_helper_entries(
    root: Path,
    target_name: str,
    required_entries: tuple[str, ...],
) -> tuple[list[str], list[str]]:
    entries, issues = _makefile_target_raw_helper_records(root, target_name)
    if issues:
        return [], issues

    for basename in required_entries:
        _require_makefile_target_route_count(entries, target_name, basename, 1, 1, issues)
    filtered = [basename for basename, _ in entries if basename in required_entries]
    return _ordered_unique(filtered), issues


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

    phase3_required_entries, issues = _canonical_readme_entries(root)
    phase2_required_entries, phase2_issues = _makefile_named_helper_entries(
        root,
        PHASE2_VALIDATE_TARGET,
        PHASE2_REQUIRED_HELPER_ENTRIES,
    )
    phase6_required_entries, phase6_issues = _makefile_named_helper_entries(
        root,
        PHASE6_VALIDATE_TARGET,
        PHASE6_REQUIRED_HELPER_ENTRIES,
    )
    phase7_required_entries, phase7_issues = _makefile_named_helper_entries(
        root,
        PHASE7_VALIDATE_TARGET,
        PHASE7_REQUIRED_HELPER_ENTRIES,
    )
    phase11_required_entries, phase11_issues = _makefile_named_helper_entries(
        root,
        PHASE11_VALIDATE_TARGET,
        PHASE11_REQUIRED_HELPER_ENTRIES,
    )
    phase13_required_entries, phase13_issues = _makefile_target_helper_entries(
        root,
        PHASE13_VALIDATE_TARGET,
    )
    issues.extend(phase2_issues)
    issues.extend(phase6_issues)
    issues.extend(phase7_issues)
    issues.extend(phase11_issues)
    issues.extend(phase13_issues)
    required_entries = _ordered_unique(
        phase3_required_entries
        + phase2_required_entries
        + phase6_required_entries
        + phase7_required_entries
        + phase11_required_entries
        + phase13_required_entries
    )
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

    phase3_required_set = set(phase3_required_entries)
    phase13_required_set = set(phase13_required_entries)
    readme_set = set(readme_entries)

    missing_phase3_entries: list[str] = []
    missing_phase13_entries: list[str] = []

    for basename in required_entries:
        rel = f"scripts/zigux/{basename}"
        if not (root / rel).exists():
            issues.append(f"missing_repo_file:{rel}")
        if basename not in readme_set:
            issues.append(f"missing_readme_entry:{basename}")
            if basename in phase3_required_set:
                missing_phase3_entries.append(basename)
            if basename in phase13_required_set:
                missing_phase13_entries.append(basename)

    phase3_filtered_entries = [basename for basename in readme_entries if basename in phase3_required_set]
    if not missing_phase3_entries and phase3_filtered_entries != phase3_required_entries:
        issues.append("readme_entry_order_drift:phase3_packet")

    phase13_filtered_entries = [
        basename for basename in readme_entries if basename in phase13_required_set
    ]
    if not missing_phase13_entries and phase13_filtered_entries != phase13_required_entries:
        issues.append("readme_entry_order_drift:phase13_validate")

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


def _fixture_makefile() -> str:
    return "\n".join(
        (
            "phase2-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
            "",
            "phase6-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-base64-catalog-evidence.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-base64-catalog-evidence.py",
            "",
            "phase7-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-parity.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-parity.py",
            "",
            "phase11-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py",
            "",
            "phase13-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-libfs-packet.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-libfs-packet.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-notifier-packet.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-notifier-packet.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py",
            "",
            "phase13-test:",
            "\t@true",
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
        phase2_helper_rels = ("scripts/zigux/check-phase2-kconfig-selftest-alignment.py",)
        phase6_helper_rels = ("scripts/zigux/check-phase6-base64-catalog-evidence.py",)
        phase7_helper_rels = ("scripts/zigux/check-phase7-argv-split-parity.py",)
        phase11_helper_rels = ("scripts/zigux/check-phase11-shared-replay-contract.py",)
        phase13_helper_rels = (
            "scripts/zigux/check-phase13-libfs-packet.py",
            "scripts/zigux/check-phase13-devres-packet.py",
            "scripts/zigux/check-phase13-notifier-packet.py",
            "scripts/zigux/validate-phase13-release.py",
        )
        required_rels = (
            tooling_packet_rels
            + phase2_helper_rels
            + phase6_helper_rels
            + phase7_helper_rels
            + phase11_helper_rels
            + phase13_helper_rels
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
        _write(root / MAKEFILE_REL, _fixture_makefile())

        for rel in required_rels:
            if rel == TOOLING_PACKET_SCRIPT_REL:
                continue
            _write(root / rel, "# stub\n")

        helper_lines = "\n".join(f"- `{Path(rel).name}`" for rel in required_rels)
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
            root / TOOLING_PACKET_SCRIPT_REL,
            "\n".join(
                (
                    "def canonical_readme_tooling_files(root):",
                    "    return (",
                    "        [",
                    *[f"            {rel!r}," for rel in tooling_packet_rels],
                    f"            {tooling_packet_rels[0]!r},",
                    "        ],",
                    "        [],",
                    "    )",
                    "",
                )
            ),
        )
        issues = validate(root)
        expected = [f"duplicate_canonical_readme_entry:{Path(tooling_packet_rels[0]).name}"]
        if issues != expected:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:duplicate_canonical_entry_guard_failed:"
                + (",".join(issues) if issues else "none")
            )
        _write(root / TOOLING_PACKET_SCRIPT_REL, tooling_packet_script)

        _write(
            root / MAKEFILE_REL,
            "\n".join(
                (
                    "phase2-validate:",
                    "\t@true",
                    "",
                    _fixture_makefile(),
                )
            ),
        )
        issues = validate(root)
        expected = [f"missing_makefile_target_entries:{PHASE2_VALIDATE_TARGET}"]
        if issues != expected:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:missing_phase2_makefile_guard_failed:"
                + (",".join(issues) if issues else "none")
            )
        _write(root / MAKEFILE_REL, _fixture_makefile())

        _write(
            root / MAKEFILE_REL,
            _fixture_makefile().replace(
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test\n',
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test\n'
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test\n',
                1,
            ),
        )
        issues = validate(root)
        expected = [
            "unexpected_makefile_self_test_route_count:phase2-validate::2:check-phase2-kconfig-selftest-alignment.py"
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:duplicate_phase2_self_test_route_guard_failed:"
                + (",".join(issues) if issues else "none")
            )
        _write(root / MAKEFILE_REL, _fixture_makefile())

        _write(
            root / MAKEFILE_REL,
            _fixture_makefile().replace(
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-base64-catalog-evidence.py --self-test\n',
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-base64-catalog-evidence.py --self-test\n'
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-base64-catalog-evidence.py --self-test\n',
                1,
            ),
        )
        issues = validate(root)
        expected = [
            "unexpected_makefile_self_test_route_count:phase6-validate::2:check-phase6-base64-catalog-evidence.py"
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:duplicate_phase6_self_test_route_guard_failed:"
                + (",".join(issues) if issues else "none")
            )
        _write(root / MAKEFILE_REL, _fixture_makefile())

        _write(
            root / MAKEFILE_REL,
            _fixture_makefile().replace(
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-parity.py --self-test\n',
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-parity.py --self-test\n'
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-parity.py --self-test\n',
                1,
            ),
        )
        issues = validate(root)
        expected = [
            "unexpected_makefile_self_test_route_count:phase7-validate::2:check-phase7-argv-split-parity.py"
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:duplicate_phase7_self_test_route_guard_failed:"
                + (",".join(issues) if issues else "none")
            )
        _write(root / MAKEFILE_REL, _fixture_makefile())

        _write(
            root / MAKEFILE_REL,
            _fixture_makefile().replace(
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-parity.py\n',
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-parity.py\n'
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-parity.py\n',
                1,
            ),
        )
        issues = validate(root)
        expected = [
            "unexpected_makefile_live_route_count:phase7-validate::2:check-phase7-argv-split-parity.py"
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:duplicate_phase7_makefile_route_guard_failed:"
                + (",".join(issues) if issues else "none")
            )
        _write(root / MAKEFILE_REL, _fixture_makefile())

        _write(
            root / MAKEFILE_REL,
            _fixture_makefile().replace(
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py\n',
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py\n'
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py\n',
                1,
            ),
        )
        issues = validate(root)
        expected = [
            "unexpected_makefile_live_route_count:phase11-validate::2:check-phase11-shared-replay-contract.py"
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:duplicate_phase11_makefile_route_guard_failed:"
                + (",".join(issues) if issues else "none")
            )
        _write(
            root / MAKEFILE_REL,
            _fixture_makefile().replace(
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py --self-test\n',
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py --self-test\n'
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py --self-test\n',
                1,
            ),
        )
        issues = validate(root)
        expected = [
            "unexpected_makefile_self_test_route_count:phase11-validate::2:check-phase11-shared-replay-contract.py"
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:duplicate_phase11_self_test_route_guard_failed:"
                + (",".join(issues) if issues else "none")
            )
        _write(root / MAKEFILE_REL, _fixture_makefile())

        _write(
            root / MAKEFILE_REL,
            _fixture_makefile().replace(
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py --self-test\n',
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py --self-test\n'
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py --self-test\n',
                1,
            ),
        )
        issues = validate(root)
        expected = [
            "unexpected_makefile_self_test_route_count:phase13-validate::2:check-phase13-devres-packet.py"
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:duplicate_phase13_devres_self_test_route_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(
            root / MAKEFILE_REL,
            _fixture_makefile().replace(
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py\n',
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py\n'
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py\n',
                1,
            ),
        )
        issues = validate(root)
        expected = [
            "unexpected_makefile_live_route_count:phase13-validate::2:check-phase13-devres-packet.py"
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:duplicate_phase13_makefile_route_guard_failed:"
                + (",".join(issues) if issues else "none")
            )
        _write(root / MAKEFILE_REL, _fixture_makefile())

        _write(
            root / MAKEFILE_REL,
            _fixture_makefile().replace(
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py\n',
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py\n'
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py\n',
                1,
            ),
        )
        issues = validate(root)
        expected = [
            "unexpected_makefile_live_route_count:phase13-validate::2:validate-phase13-release.py"
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:duplicate_phase13_release_validator_route_guard_failed:"
                + (",".join(issues) if issues else "none")
            )
        _write(root / MAKEFILE_REL, _fixture_makefile())

        _write(
            root / MAKEFILE_REL,
            _fixture_makefile().replace(
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py\n',
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py\n'
                '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py --self-test\n',
                1,
            ),
        )
        issues = validate(root)
        expected = [
            "unexpected_makefile_self_test_route_count:phase13-validate::1:validate-phase13-release.py"
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:unexpected_phase13_release_validator_self_test_route_guard_failed:"
                + (",".join(issues) if issues else "none")
            )
        _write(root / MAKEFILE_REL, _fixture_makefile())

        _write(
            root / MAKEFILE_REL,
            "\n".join(
                (
                    "phase11-validate:",
                    "\t@true",
                    "",
                    _fixture_makefile(),
                )
            ),
        )
        issues = validate(root)
        expected = [f"missing_makefile_target_entries:{PHASE11_VALIDATE_TARGET}"]
        if issues != expected:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:missing_phase11_makefile_guard_failed:"
                + (",".join(issues) if issues else "none")
            )
        _write(root / MAKEFILE_REL, _fixture_makefile())

        _write(
            root / README_REL,
            "\n".join(
                (
                    "# scripts/zigux",
                    "",
                    "Current bootstrap helpers",
                    *[
                        f"- `{Path(rel).name}`"
                        for rel in required_rels
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
                    *[
                        f"- `{Path(rel).name}`"
                        for rel in required_rels
                        if rel != "scripts/zigux/check-phase13-devres-packet.py"
                    ],
                    "",
                    _fixture_phase3_flow(),
                )
            ),
        )
        issues = validate(root)
        expected = ["missing_readme_entry:check-phase13-devres-packet.py"]
        if issues != expected:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:missing_phase13_readme_entry_guard_failed:"
                + (",".join(issues) if issues else "none")
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
                        for rel in required_rels
                        if rel != "scripts/zigux/check-phase11-shared-replay-contract.py"
                    ],
                    "",
                    _fixture_phase3_flow(),
                )
            ),
        )
        issues = validate(root)
        expected = ["missing_readme_entry:check-phase11-shared-replay-contract.py"]
        if issues != expected:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:missing_phase11_readme_entry_guard_failed:"
                + (",".join(issues) if issues else "none")
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
                        for rel in required_rels
                        if rel != "scripts/zigux/check-phase2-kconfig-selftest-alignment.py"
                    ],
                    "",
                    _fixture_phase3_flow(),
                )
            ),
        )
        issues = validate(root)
        expected = ["missing_readme_entry:check-phase2-kconfig-selftest-alignment.py"]
        if issues != expected:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:missing_phase2_readme_entry_guard_failed:"
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
                    *[f"- `{Path(rel).name}`" for rel in required_rels[2:]],
                    "",
                    _fixture_phase3_flow(),
                )
            ),
        )
        issues = validate(root)
        expected = ["readme_entry_order_drift:phase3_packet"]
        if issues != expected:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:order_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        reordered_phase13_helper_rels = (
            "scripts/zigux/check-phase13-devres-packet.py",
            "scripts/zigux/check-phase13-libfs-packet.py",
            "scripts/zigux/check-phase13-notifier-packet.py",
            "scripts/zigux/validate-phase13-release.py",
        )
        reordered_helper_lines = "\n".join(
            f"- `{Path(rel).name}`"
            for rel in tooling_packet_rels
            + phase2_helper_rels
            + phase6_helper_rels
            + phase7_helper_rels
            + phase11_helper_rels
            + reordered_phase13_helper_rels
        )
        _write(
            root / README_REL,
            "\n".join(
                (
                    "# scripts/zigux",
                    "",
                    "Current bootstrap helpers",
                    "- `artifact_diff.py`",
                    reordered_helper_lines,
                    "",
                    _fixture_phase3_flow(),
                )
            ),
        )
        issues = validate(root)
        expected = ["readme_entry_order_drift:phase13_validate"]
        if issues != expected:
            raise SystemExit(
                "phase3-readme-tooling-inventory-self-test:phase13_order_guard_failed:"
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
                    *[f"- `{Path(rel).name}`" for rel in required_rels[1:]],
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
            f"unexpected_phase3_flow_snippet_count:0:{REQUIRED_PHASE3_FLOW_SNIPPETS[1]}"
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
    print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST_CASE_COUNT=23")
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

    root = Path(args.root).resolve() if args.root else ROOT
    phase3_required_entries, entry_issues = _canonical_readme_entries(root)
    phase2_required_entries, phase2_issues = _makefile_named_helper_entries(
        root,
        PHASE2_VALIDATE_TARGET,
        PHASE2_REQUIRED_HELPER_ENTRIES,
    )
    phase6_required_entries, phase6_issues = _makefile_named_helper_entries(
        root,
        PHASE6_VALIDATE_TARGET,
        PHASE6_REQUIRED_HELPER_ENTRIES,
    )
    phase7_required_entries, phase7_issues = _makefile_named_helper_entries(
        root,
        PHASE7_VALIDATE_TARGET,
        PHASE7_REQUIRED_HELPER_ENTRIES,
    )
    phase11_required_entries, phase11_issues = _makefile_named_helper_entries(
        root,
        PHASE11_VALIDATE_TARGET,
        PHASE11_REQUIRED_HELPER_ENTRIES,
    )
    phase13_required_entries, phase13_issues = _makefile_target_helper_entries(
        root,
        PHASE13_VALIDATE_TARGET,
    )
    entry_issues.extend(phase2_issues)
    entry_issues.extend(phase6_issues)
    entry_issues.extend(phase7_issues)
    entry_issues.extend(phase11_issues)
    entry_issues.extend(phase13_issues)
    if entry_issues:
        print("PHASE3_README_TOOLING_INVENTORY=fail")
        for issue in entry_issues:
            print(issue)
        return 1

    print("PHASE3_README_TOOLING_INVENTORY=pass")
    print(
        "PHASE3_README_TOOLING_INVENTORY_ENTRY_COUNT="
        f"{len(_ordered_unique(phase3_required_entries + phase2_required_entries + phase6_required_entries + phase7_required_entries + phase11_required_entries + phase13_required_entries))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
