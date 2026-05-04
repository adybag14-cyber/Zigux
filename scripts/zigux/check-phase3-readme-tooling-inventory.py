#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import runpy
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else Path.cwd().resolve()
README_REL = "scripts/zigux/README.md"
TOOLING_PACKET_REL = "scripts/zigux/check-phase3-tooling-packet.py"
MAKEFILE_REL = "zigux/Makefile"
README_HELPER_SECTION = "Current bootstrap helpers"

PHASE2_VALIDATE_TARGET = "phase2-validate:"
PHASE6_VALIDATE_TARGET = "phase6-validate:"
PHASE7_VALIDATE_TARGET = "phase7-validate:"
PHASE11_VALIDATE_TARGET = "phase11-validate:"
PHASE13_VALIDATE_TARGET = "phase13-validate:"

PHASE2_REQUIRED = ("check-phase2-kconfig-selftest-alignment.py",)
PHASE6_REQUIRED = ("check-phase6-base64-catalog-evidence.py",)
PHASE7_REQUIRED = ("check-phase7-argv-split-parity.py",)
PHASE11_REQUIRED = ("check-phase11-shared-replay-contract.py",)

REQUIRED_PHASE3_FLOW_SNIPPETS = (
    "`validate-phase3.py`, `make -C zigux phase3-validate`, and the bootstrap workflow keep the bounded ABI substrate packet aligned across `scripts/zigux/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase3-abi-slice.md`, `zigux/tests/fixtures/phase3_abi_manifest.json`, and the shared Phase 3 build roots before broader interop replay claims closure.",
    "the supporting survey and contract checks stay inside that same validator-first route: `validate-phase3-roadmap-gap-survey.py`, `validate-phase3-rbtree-interop-survey.py`, `check-phase3-rbtree-shared-lift-contract.py`, `validate-phase3-export-uapi-survey.py`, `validate-phase3-low-level-wrapper-survey.py`, `validate-phase3-policy-unsafe-survey.py`, `check-phase3-policy-unsafe-mmio-consumer.py`, `check-phase3-abi-duplicate-declarations.py`, `check-phase3-abi-layout-packet.py`, `check-phase3-abi-binding-constants.py`, `check-phase3-tooling-packet.py`, `check-phase3-readme-tooling-inventory.py`, `check-phase3-validation-flow.py`, `check-phase3-build-roots.py`, and `check-phase3-canonical-survey-manifest.py`.",
)
REQUIRED_CROSS_PHASE_FLOW_SNIPPETS = (
    "`validate-phase6.py` keeps the shipped Phase 6 leaf-helper packet aligned across `scripts/zigux/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/phase6-helper-parity-catalog.md`, `zigux/tests/phase6_helper_parity_manifest.json`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, the bootstrap workflow, and the four helper-local slice notes before any shared replay claims stay green.",
    "`validate-phase8.py` is the validator-first entrypoint for the parked repo-hosted tooling packet across `tools/lib/subcmd/exec-cmd.zig`, `tools/lib/subcmd/help.zig`, `tools/lib/symbol/kallsyms.zig`, the helper-first `tools/lib/bpf/zigux_segments/` rollout, and the bounded `perf_buffer__poll(timeout_ms)` bookkeeping adjunct.",
    "`validate-phase9.py` is the validator-first entrypoint for the shared runtime-pilot packet across `scripts/zigux/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md`, `zigux/tests/README.md`, `zigux/tests/phase9_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.",
)


def _ordered_unique(entries: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        if entry not in seen:
            seen.add(entry)
            out.append(entry)
    return out


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _duplicates(entries: list[str]) -> list[str]:
    seen: set[str] = set()
    dupes: list[str] = []
    for entry in entries:
        if entry in seen and entry not in dupes:
            dupes.append(entry)
        seen.add(entry)
    return dupes


def _canonical_phase3_entries(root: Path) -> tuple[list[str], list[str]]:
    packet_path = root / TOOLING_PACKET_REL
    if not packet_path.exists():
        return [], [f"missing_tooling_packet_script:{TOOLING_PACKET_REL}"]

    namespace = runpy.run_path(str(packet_path))
    helper = namespace.get("canonical_readme_tooling_files")
    if callable(helper):
        raw_entries, issues = helper(root)
    else:
        raw_entries = namespace.get("REQUIRED_README_TOOLING_FILES")
        issues = []
        if not isinstance(raw_entries, tuple):
            return [], ["missing_tooling_packet_constant:REQUIRED_README_TOOLING_FILES"]

    basenames: list[str] = []
    for rel in raw_entries:
        if not isinstance(rel, str):
            issues.append(f"invalid_tooling_packet_entry:{rel!r}")
            continue
        if rel.startswith("scripts/zigux/"):
            basenames.append(Path(rel).name)
    for dup in _duplicates(basenames):
        issues.append(f"duplicate_canonical_readme_entry:{dup}")
    if not basenames:
        issues.append("missing_tooling_packet_script_entries")
    return _ordered_unique(basenames), issues


def _makefile_records(root: Path, target: str) -> tuple[list[tuple[str, bool]], list[str]]:
    try:
        text = (root / MAKEFILE_REL).read_text(encoding="utf-8")
    except FileNotFoundError:
        return [], [f"missing_makefile:{MAKEFILE_REL}"]

    in_target = False
    records: list[tuple[str, bool]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not in_target:
            in_target = stripped == target
            continue
        if stripped.endswith(":") and not line.startswith((" ", "\t")):
            break
        if "scripts/zigux/" not in stripped:
            continue
        rel = "scripts/zigux/" + stripped.split("scripts/zigux/", 1)[1].split()[0]
        if rel.endswith(".py"):
            records.append((Path(rel).name, "--self-test" in stripped))
    if not records:
        return [], [f"missing_makefile_target_entries:{target}"]
    return records, []


def _check_route_counts(
    records: list[tuple[str, bool]],
    target: str,
    basename: str,
    expected_live: int,
    expected_self_test: int,
    issues: list[str],
) -> None:
    live = sum(1 for entry, self_test in records if entry == basename and not self_test)
    self_test = sum(1 for entry, self_test in records if entry == basename and self_test)
    if live != expected_live:
        issues.append(f"unexpected_makefile_live_route_count:{target}:{live}:{basename}")
    if self_test != expected_self_test:
        issues.append(
            f"unexpected_makefile_self_test_route_count:{target}:{self_test}:{basename}"
        )


def _named_helper_entries(root: Path, target: str, required: tuple[str, ...]) -> tuple[list[str], list[str]]:
    records, issues = _makefile_records(root, target)
    if issues:
        return [], issues
    for basename in required:
        _check_route_counts(records, target, basename, 1, 1, issues)
    return _ordered_unique([entry for entry, _ in records if entry in required]), issues


def _target_helper_entries(root: Path, target: str) -> tuple[list[str], list[str]]:
    records, issues = _makefile_records(root, target)
    if issues:
        return [], issues
    ordered = _ordered_unique([entry for entry, _ in records])
    for basename in ordered:
        expected_self_test = 0 if basename.startswith("validate-") else 1
        _check_route_counts(records, target, basename, 1, expected_self_test, issues)
    return ordered, issues


def _readme_helper_entries(text: str) -> tuple[list[str], list[str], bool]:
    found = False
    collecting = False
    entries: list[str] = []
    issues: list[str] = []
    seen: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not found:
            if stripped == README_HELPER_SECTION:
                found = True
                collecting = True
            continue
        if not collecting:
            break
        if stripped.startswith("- `") and stripped.endswith("`"):
            name = stripped[3:-1]
            if name in seen:
                issues.append(f"duplicate_readme_entry:{name}")
            else:
                seen.add(name)
                entries.append(name)
            continue
        if not stripped:
            continue
        if entries:
            break
    if not found:
        issues.append(f"missing_readme_section:{README_HELPER_SECTION}")
    elif not entries:
        issues.append("missing_readme_section_entries:current_bootstrap_helpers")
    return entries, issues, found


def validate(root: Path) -> list[str]:
    try:
        readme = (root / README_REL).read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"missing_readme:{README_REL}"]

    phase3_entries, issues = _canonical_phase3_entries(root)
    phase2_entries, phase2_issues = _named_helper_entries(root, PHASE2_VALIDATE_TARGET, PHASE2_REQUIRED)
    phase6_entries, phase6_issues = _named_helper_entries(root, PHASE6_VALIDATE_TARGET, PHASE6_REQUIRED)
    phase7_entries, phase7_issues = _named_helper_entries(root, PHASE7_VALIDATE_TARGET, PHASE7_REQUIRED)
    phase11_entries, phase11_issues = _named_helper_entries(root, PHASE11_VALIDATE_TARGET, PHASE11_REQUIRED)
    phase13_entries, phase13_issues = _target_helper_entries(root, PHASE13_VALIDATE_TARGET)
    issues.extend(phase2_issues + phase6_issues + phase7_issues + phase11_issues + phase13_issues)

    all_entries = _ordered_unique(
        phase3_entries + phase2_entries + phase6_entries + phase7_entries + phase11_entries + phase13_entries
    )
    helper_entries, helper_issues, has_helper_section = _readme_helper_entries(readme)
    if has_helper_section:
        issues.extend(helper_issues)
    else:
        issues.extend(issue for issue in helper_issues if not issue.startswith("missing_readme_section:"))

    for snippet in REQUIRED_PHASE3_FLOW_SNIPPETS:
        if snippet not in readme:
            issues.append(f"missing_phase3_flow_snippet:{snippet}")
        count = readme.count(snippet)
        if count != 1:
            issues.append(f"unexpected_phase3_flow_snippet_count:{count}:{snippet}")
    for snippet in REQUIRED_CROSS_PHASE_FLOW_SNIPPETS:
        if snippet not in readme:
            issues.append(f"missing_cross_phase_flow_snippet:{snippet}")
        count = readme.count(snippet)
        if count != 1:
            issues.append(f"unexpected_cross_phase_flow_snippet_count:{count}:{snippet}")

    for basename in all_entries:
        if not (root / f"scripts/zigux/{basename}").exists():
            issues.append(f"missing_repo_file:scripts/zigux/{basename}")

    if has_helper_section:
        helper_set = set(helper_entries)
        missing_phase3: list[str] = []
        missing_phase13: list[str] = []
        phase3_set = set(phase3_entries)
        phase13_set = set(phase13_entries)
        for basename in all_entries:
            if basename not in helper_set:
                issues.append(f"missing_readme_entry:{basename}")
                if basename in phase3_set:
                    missing_phase3.append(basename)
                if basename in phase13_set:
                    missing_phase13.append(basename)
        if not missing_phase3:
            phase3_order = [entry for entry in helper_entries if entry in phase3_set]
            if phase3_order != phase3_entries:
                issues.append("readme_entry_order_drift:phase3_packet")
        if not missing_phase13:
            phase13_order = [entry for entry in helper_entries if entry in phase13_set]
            if phase13_order != phase13_entries:
                issues.append("readme_entry_order_drift:phase13_validate")

    return issues


def _fixture_phase3_flow() -> str:
    return "\n".join(("Phase 3 flow", *(f"- {s}" for s in REQUIRED_PHASE3_FLOW_SNIPPETS), ""))


def _fixture_cross_phase_flow() -> str:
    return "\n".join(
        (
            "Phase 6 flow",
            f"- {REQUIRED_CROSS_PHASE_FLOW_SNIPPETS[0]}",
            "Phase 8 flow",
            f"- {REQUIRED_CROSS_PHASE_FLOW_SNIPPETS[1]}",
            "Phase 9 flow",
            f"- {REQUIRED_CROSS_PHASE_FLOW_SNIPPETS[2]}",
            "",
        )
    )


def _fixture_makefile() -> str:
    lines = [
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
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-inventory-contract.py --self-test",
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-inventory-contract.py",
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-notifier-packet.py --self-test",
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-notifier-packet.py",
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py",
        "",
        "phase13-test:",
        "\t@true",
        "",
    ]
    return "\n".join(lines)


def _assert_only(issues: list[str], expected: list[str], label: str) -> None:
    if issues != expected:
        raise SystemExit(f"phase3-readme-tooling-inventory-self-test:{label}:{','.join(issues) or 'none'}")


def _baseline_required_rels() -> tuple[tuple[str, ...], tuple[str, ...]]:
    tooling_packet_rels = (
        "scripts/zigux/validate-phase3-roadmap-gap-survey.py",
        "scripts/zigux/check-phase3-build-roots.py",
        "scripts/zigux/check-phase3-tooling-packet.py",
        "scripts/zigux/check-phase3-readme-tooling-inventory.py",
        "scripts/zigux/validate-phase3.py",
    )
    phase13_helper_rels = (
        "scripts/zigux/check-phase13-libfs-packet.py",
        "scripts/zigux/check-phase13-devres-packet.py",
        "scripts/zigux/check-phase13-devres-inventory-contract.py",
        "scripts/zigux/check-phase13-notifier-packet.py",
        "scripts/zigux/validate-phase13-release.py",
    )
    required_rels = tooling_packet_rels + (
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        "scripts/zigux/check-phase6-base64-catalog-evidence.py",
        "scripts/zigux/check-phase7-argv-split-parity.py",
        "scripts/zigux/check-phase11-shared-replay-contract.py",
    ) + phase13_helper_rels
    return tooling_packet_rels, required_rels


def _baseline_readme(required_rels: tuple[str, ...]) -> str:
    helper_lines = "\n".join(f"- `{Path(rel).name}`" for rel in required_rels)
    return "\n".join(
        (
            "# scripts/zigux",
            "",
            "Current bootstrap helpers",
            "- `artifact_diff.py`",
            helper_lines,
            "",
            _fixture_phase3_flow(),
            _fixture_cross_phase_flow(),
        )
    )


def run_self_test() -> int:
    tooling_packet_rels, required_rels = _baseline_required_rels()
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
    baseline_makefile = _fixture_makefile()
    baseline_readme = _baseline_readme(required_rels)

    with tempfile.TemporaryDirectory(prefix="zigux_phase3_readme_tooling_inventory_") as tmp_dir:
        root = Path(tmp_dir) / "repo"
        _write(root / TOOLING_PACKET_REL, tooling_packet_script)
        _write(root / MAKEFILE_REL, baseline_makefile)
        for rel in required_rels:
            if rel != TOOLING_PACKET_REL:
                _write(root / rel, "# stub\n")
        _write(root / README_REL, baseline_readme)
        if validate(root):
            raise SystemExit("phase3-readme-tooling-inventory-self-test:baseline_failed")

        _write(root / README_REL, "\n".join(("# scripts/zigux", "", _fixture_phase3_flow(), _fixture_cross_phase_flow())))
        if validate(root):
            raise SystemExit("phase3-readme-tooling-inventory-self-test:flow_first_readme_guard_failed")
        _write(root / README_REL, baseline_readme)

        _write(
            root / TOOLING_PACKET_REL,
            tooling_packet_script.replace("        ],", f"            {tooling_packet_rels[0]!r},\n        ],", 1),
        )
        _assert_only(validate(root), [f"duplicate_canonical_readme_entry:{Path(tooling_packet_rels[0]).name}"], "duplicate_canonical_entry_guard_failed")
        _write(root / TOOLING_PACKET_REL, tooling_packet_script)

        _write(root / MAKEFILE_REL, "\n".join(("phase2-validate:", "\t@true", "", baseline_makefile)))
        _assert_only(validate(root), [f"missing_makefile_target_entries:{PHASE2_VALIDATE_TARGET}"], "missing_phase2_makefile_guard_failed")
        _write(root / MAKEFILE_REL, baseline_makefile)

        makefile_cases = (
            ("duplicate_phase2_self_test_route_guard_failed", "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test\n", "unexpected_makefile_self_test_route_count:phase2-validate::2:check-phase2-kconfig-selftest-alignment.py"),
            ("duplicate_phase2_makefile_route_guard_failed", "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py\n", "unexpected_makefile_live_route_count:phase2-validate::2:check-phase2-kconfig-selftest-alignment.py"),
            ("duplicate_phase6_self_test_route_guard_failed", "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-base64-catalog-evidence.py --self-test\n", "unexpected_makefile_self_test_route_count:phase6-validate::2:check-phase6-base64-catalog-evidence.py"),
            ("duplicate_phase6_makefile_route_guard_failed", "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-base64-catalog-evidence.py\n", "unexpected_makefile_live_route_count:phase6-validate::2:check-phase6-base64-catalog-evidence.py"),
            ("duplicate_phase7_self_test_route_guard_failed", "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-parity.py --self-test\n", "unexpected_makefile_self_test_route_count:phase7-validate::2:check-phase7-argv-split-parity.py"),
            ("duplicate_phase7_makefile_route_guard_failed", "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-parity.py\n", "unexpected_makefile_live_route_count:phase7-validate::2:check-phase7-argv-split-parity.py"),
            ("duplicate_phase11_makefile_route_guard_failed", "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py\n", "unexpected_makefile_live_route_count:phase11-validate::2:check-phase11-shared-replay-contract.py"),
            ("duplicate_phase11_self_test_route_guard_failed", "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py --self-test\n", "unexpected_makefile_self_test_route_count:phase11-validate::2:check-phase11-shared-replay-contract.py"),
            ("duplicate_phase13_libfs_self_test_route_guard_failed", "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-libfs-packet.py --self-test\n", "unexpected_makefile_self_test_route_count:phase13-validate::2:check-phase13-libfs-packet.py"),
            ("duplicate_phase13_libfs_makefile_route_guard_failed", "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-libfs-packet.py\n", "unexpected_makefile_live_route_count:phase13-validate::2:check-phase13-libfs-packet.py"),
            ("duplicate_phase13_devres_self_test_route_guard_failed", "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py --self-test\n", "unexpected_makefile_self_test_route_count:phase13-validate::2:check-phase13-devres-packet.py"),
            ("duplicate_phase13_makefile_route_guard_failed", "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py\n", "unexpected_makefile_live_route_count:phase13-validate::2:check-phase13-devres-packet.py"),
            ("duplicate_phase13_devres_inventory_self_test_route_guard_failed", "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-inventory-contract.py --self-test\n", "unexpected_makefile_self_test_route_count:phase13-validate::2:check-phase13-devres-inventory-contract.py"),
            ("duplicate_phase13_devres_inventory_makefile_route_guard_failed", "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-inventory-contract.py\n", "unexpected_makefile_live_route_count:phase13-validate::2:check-phase13-devres-inventory-contract.py"),
            ("duplicate_phase13_notifier_self_test_route_guard_failed", "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-notifier-packet.py --self-test\n", "unexpected_makefile_self_test_route_count:phase13-validate::2:check-phase13-notifier-packet.py"),
            ("duplicate_phase13_notifier_makefile_route_guard_failed", "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-notifier-packet.py\n", "unexpected_makefile_live_route_count:phase13-validate::2:check-phase13-notifier-packet.py"),
            ("duplicate_phase13_release_validator_route_guard_failed", "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py\n", "unexpected_makefile_live_route_count:phase13-validate::2:validate-phase13-release.py"),
        )
        for label, line, expected in makefile_cases:
            _write(root / MAKEFILE_REL, baseline_makefile.replace(line, line + line, 1))
            _assert_only(validate(root), [expected], label)
            _write(root / MAKEFILE_REL, baseline_makefile)

        extra_self_test = baseline_makefile.replace(
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py\n",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py --self-test\n",
            1,
        )
        _write(root / MAKEFILE_REL, extra_self_test)
        _assert_only(validate(root), ["unexpected_makefile_self_test_route_count:phase13-validate::1:validate-phase13-release.py"], "unexpected_phase13_release_validator_self_test_route_guard_failed")
        _write(root / MAKEFILE_REL, baseline_makefile)

        _write(root / MAKEFILE_REL, "\n".join(("phase11-validate:", "\t@true", "", baseline_makefile)))
        _assert_only(validate(root), [f"missing_makefile_target_entries:{PHASE11_VALIDATE_TARGET}"], "missing_phase11_makefile_guard_failed")
        _write(root / MAKEFILE_REL, baseline_makefile)

        readme_cases = (
            ("missing_readme_entry_guard_failed", "scripts/zigux/validate-phase3-roadmap-gap-survey.py", f"missing_readme_entry:{Path(tooling_packet_rels[0]).name}"),
            ("missing_phase13_readme_entry_guard_failed", "scripts/zigux/check-phase13-devres-packet.py", "missing_readme_entry:check-phase13-devres-packet.py"),
            ("missing_phase13_devres_inventory_readme_entry_guard_failed", "scripts/zigux/check-phase13-devres-inventory-contract.py", "missing_readme_entry:check-phase13-devres-inventory-contract.py"),
            ("missing_phase11_readme_entry_guard_failed", "scripts/zigux/check-phase11-shared-replay-contract.py", "missing_readme_entry:check-phase11-shared-replay-contract.py"),
            ("missing_phase2_readme_entry_guard_failed", "scripts/zigux/check-phase2-kconfig-selftest-alignment.py", "missing_readme_entry:check-phase2-kconfig-selftest-alignment.py"),
        )
        for label, rel, expected in readme_cases:
            entries = [f"- `{Path(item).name}`" for item in required_rels if item != rel]
            variant = "\n".join(("# scripts/zigux", "", "Current bootstrap helpers", *entries, "", _fixture_phase3_flow(), _fixture_cross_phase_flow()))
            _write(root / README_REL, variant)
            _assert_only(validate(root), [expected], label)

        phase3_order = "\n".join(("# scripts/zigux", "", "Current bootstrap helpers", f"- `{Path(tooling_packet_rels[1]).name}`", f"- `{Path(tooling_packet_rels[0]).name}`", *[f"- `{Path(rel).name}`" for rel in required_rels[2:]], "", _fixture_phase3_flow(), _fixture_cross_phase_flow()))
        _write(root / README_REL, phase3_order)
        _assert_only(validate(root), ["readme_entry_order_drift:phase3_packet"], "order_guard_failed")

        phase13_reordered = (
            "scripts/zigux/check-phase13-devres-packet.py",
            "scripts/zigux/check-phase13-libfs-packet.py",
            "scripts/zigux/check-phase13-devres-inventory-contract.py",
            "scripts/zigux/check-phase13-notifier-packet.py",
            "scripts/zigux/validate-phase13-release.py",
        )
        reordered = "\n".join(
            ("# scripts/zigux", "", "Current bootstrap helpers", "- `artifact_diff.py`",
             *[f"- `{Path(rel).name}`" for rel in tooling_packet_rels + ("scripts/zigux/check-phase2-kconfig-selftest-alignment.py", "scripts/zigux/check-phase6-base64-catalog-evidence.py", "scripts/zigux/check-phase7-argv-split-parity.py", "scripts/zigux/check-phase11-shared-replay-contract.py") + phase13_reordered],
             "", _fixture_phase3_flow(), _fixture_cross_phase_flow())
        )
        _write(root / README_REL, reordered)
        _assert_only(validate(root), ["readme_entry_order_drift:phase13_validate"], "phase13_order_guard_failed")

        duplicate_readme = "\n".join(("# scripts/zigux", "", "Current bootstrap helpers", f"- `{Path(tooling_packet_rels[0]).name}`", f"- `{Path(tooling_packet_rels[0]).name}`", *[f"- `{Path(rel).name}`" for rel in required_rels[1:]], "", _fixture_phase3_flow(), _fixture_cross_phase_flow()))
        _write(root / README_REL, duplicate_readme)
        _assert_only(validate(root), [f"duplicate_readme_entry:{Path(tooling_packet_rels[0]).name}"], "duplicate_readme_entry_guard_failed")

        missing_flow = "\n".join(("# scripts/zigux", "", "Current bootstrap helpers", "- `artifact_diff.py`", *[f"- `{Path(rel).name}`" for rel in required_rels], ""))
        _write(root / README_REL, missing_flow)
        _assert_only(
            validate(root),
            [
                f"missing_phase3_flow_snippet:{REQUIRED_PHASE3_FLOW_SNIPPETS[0]}",
                f"unexpected_phase3_flow_snippet_count:0:{REQUIRED_PHASE3_FLOW_SNIPPETS[0]}",
                f"missing_phase3_flow_snippet:{REQUIRED_PHASE3_FLOW_SNIPPETS[1]}",
                f"unexpected_phase3_flow_snippet_count:0:{REQUIRED_PHASE3_FLOW_SNIPPETS[1]}",
                f"missing_cross_phase_flow_snippet:{REQUIRED_CROSS_PHASE_FLOW_SNIPPETS[0]}",
                f"unexpected_cross_phase_flow_snippet_count:0:{REQUIRED_CROSS_PHASE_FLOW_SNIPPETS[0]}",
                f"missing_cross_phase_flow_snippet:{REQUIRED_CROSS_PHASE_FLOW_SNIPPETS[1]}",
                f"unexpected_cross_phase_flow_snippet_count:0:{REQUIRED_CROSS_PHASE_FLOW_SNIPPETS[1]}",
                f"missing_cross_phase_flow_snippet:{REQUIRED_CROSS_PHASE_FLOW_SNIPPETS[2]}",
                f"unexpected_cross_phase_flow_snippet_count:0:{REQUIRED_CROSS_PHASE_FLOW_SNIPPETS[2]}",
            ],
            "missing_phase3_flow_guard_failed",
        )

        for label, snippet, prefix in (
            ("duplicate_phase3_flow_guard_failed", REQUIRED_PHASE3_FLOW_SNIPPETS[0], "unexpected_phase3_flow_snippet_count"),
            ("duplicate_phase3_supporting_checks_guard_failed", REQUIRED_PHASE3_FLOW_SNIPPETS[1], "unexpected_phase3_flow_snippet_count"),
            ("duplicate_phase6_flow_guard_failed", REQUIRED_CROSS_PHASE_FLOW_SNIPPETS[0], "unexpected_cross_phase_flow_snippet_count"),
            ("duplicate_phase8_flow_guard_failed", REQUIRED_CROSS_PHASE_FLOW_SNIPPETS[1], "unexpected_cross_phase_flow_snippet_count"),
            ("duplicate_phase9_flow_guard_failed", REQUIRED_CROSS_PHASE_FLOW_SNIPPETS[2], "unexpected_cross_phase_flow_snippet_count"),
        ):
            variant = baseline_readme + f"\n- {snippet}\n"
            _write(root / README_REL, variant)
            _assert_only(validate(root), [f"{prefix}:2:{snippet}"], label)

        _write(root / README_REL, baseline_readme)
        (root / tooling_packet_rels[-1]).unlink()
        _assert_only(validate(root), [f"missing_repo_file:{tooling_packet_rels[-1]}"], "missing_repo_file_guard_failed")

    print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass")
    print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST_CASE_COUNT=32")
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

    repo_root = Path(args.root).resolve() if args.root else ROOT
    issues = validate(repo_root)
    if issues:
        print("PHASE3_README_TOOLING_INVENTORY=fail")
        for issue in issues:
            print(issue)
        return 1

    phase3_entries, entry_issues = _canonical_phase3_entries(repo_root)
    phase2_entries, phase2_issues = _named_helper_entries(repo_root, PHASE2_VALIDATE_TARGET, PHASE2_REQUIRED)
    phase6_entries, phase6_issues = _named_helper_entries(repo_root, PHASE6_VALIDATE_TARGET, PHASE6_REQUIRED)
    phase7_entries, phase7_issues = _named_helper_entries(repo_root, PHASE7_VALIDATE_TARGET, PHASE7_REQUIRED)
    phase11_entries, phase11_issues = _named_helper_entries(repo_root, PHASE11_VALIDATE_TARGET, PHASE11_REQUIRED)
    phase13_entries, phase13_issues = _target_helper_entries(repo_root, PHASE13_VALIDATE_TARGET)
    entry_issues.extend(phase2_issues + phase6_issues + phase7_issues + phase11_issues + phase13_issues)
    if entry_issues:
        print("PHASE3_README_TOOLING_INVENTORY=fail")
        for issue in entry_issues:
            print(issue)
        return 1

    entry_count = len(_ordered_unique(phase3_entries + phase2_entries + phase6_entries + phase7_entries + phase11_entries + phase13_entries))
    print("PHASE3_README_TOOLING_INVENTORY=pass")
    print(f"PHASE3_README_TOOLING_INVENTORY_ENTRY_COUNT={entry_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
