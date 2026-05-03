#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


def _default_root() -> Path:
    resolved = Path(__file__).resolve()
    if len(resolved.parents) >= 3:
        return resolved.parents[2]
    return resolved.parent


ROOT = _default_root()
README_REL = "scripts/zigux/README.md"
README_HELPER_SECTION = "Current bootstrap helpers"
REQUIRED_BOOTSTRAP_HELPERS = (
    "artifact_diff.py",
    "check-artifact-diff-contract.py",
    "check-zig-toolchain.py",
    "validate-bootstrap.py",
    "install-zig.py",
    "validate-phase1.py",
    "check-phase1-find-bit-validator-anchors.py",
    "check-phase1-bench.py",
    "validate-phase1-closure.py",
    "validate-phase2.py",
    "validate-phase2-closure.py",
    "validate-phase3.py",
    "check-phase3-abi.py",
    "check-phase3-abi-layout-packet.py",
    "check-phase3-abi-binding-constants.py",
    "check-phase3-build-roots.py",
    "check-phase3-canonical-survey-manifest.py",
    "check-phase3-policy-unsafe-mmio-consumer.py",
    "check-phase3-rbtree-shared-lift-contract.py",
    "check-phase3-readme-tooling-inventory.py",
    "check-phase3-tooling-packet.py",
    "check-phase3-validation-flow.py",
    "validate-phase4.py",
    "check-phase4-gate-evidence.py",
    "validate-phase5.py",
    "validate-phase6.py",
    "validate-phase7.py",
    "check-phase7-build-inventory.py",
    "check-phase7-make-wrapper.py",
    "check-phase7-cmdline-parity.py",
    "check-phase7-rbtree-parity.py",
    "validate-phase8.py",
    "check-phase8-tests-readme-alignment.py",
    "check-phase8-perf-buffer-poll-gate.py",
    "validate-phase9.py",
    "check-phase9-validation-flow.py",
    "check-phase9-loader-substrate-plan.py",
    "check-phase9-runtime-loader-commit-alignment.py",
    "check-phase9-loader-non-owner-boundary.py",
    "check-phase9-module-metadata-packet.py",
    "validate-phase10.py",
    "check-phase10-closure-inventory.py",
    "check-phase10-core-packet.py",
    "check-phase10-harness-coverage.py",
    "validate-phase10-closure.py",
    "validate-phase11.py",
    "check-phase11-build-inventory.py",
    "check-phase11-layout-assert-surface.py",
    "check-phase11-hvc-validation-flow.py",
    "check-phase11-hvc-cleanup-alignment.py",
    "check-phase12-build-inventory.py",
    "check-phase12-libbpf-snapshot.py",
    "check-phase12-libbpf-packet.py",
    "check-phase12-libbpf-focused-replay.py",
    "check-phase12-raw-github-coverage.py",
    "validate-phase12.py",
    "check-phase13-libfs-packet.py",
    "check-phase13-devres-packet.py",
    "check-phase13-notifier-packet.py",
    "validate-phase13-release.py",
    "validate-phase14.py",
    "validate-phase15.py",
    "validate-phase3-roadmap-gap-survey.py",
    "validate-phase3-rbtree-interop-survey.py",
    "validate-phase3-export-uapi-survey.py",
    "validate-phase3-low-level-wrapper-survey.py",
    "validate-phase3-policy-unsafe-survey.py",
    "validate_phase3_header_binding_markers.py",
    "validate_phase3_selftest.py",
    "generate-phase3-check-wrappers.py",
    "run-phase3-checks.py",
    "phase3_catalog.py",
    "phase3_check_lib.py",
    "check-phase1-parity.py",
    "check-fixdep-diff.py",
    "check-genksyms-bridge.py",
    "check-phase2-genksyms-bridge-selftest-alignment.py",
    "check-phase2-cross-selftest-alignment.py",
    "check-genksyms-crc-diff.py",
    "check-kconfig-bridge.py",
    "check-phase2-cross.py",
    "check-phase2-toolchain-pin-scope.py",
    "check-mk-elfconfig-diff.py",
    "check-phase6-base64-c-parity.py",
    "check-phase6-bsearch-c-parity.py",
    "check-phase6-checksum-c-parity.py",
    "check-phase6-hexdump-c-parity.py",
)


def _helper_section_entries(readme: str) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    entries: list[str] = []
    found_heading = False
    seen: set[str] = set()

    for line in readme.splitlines():
        stripped = line.strip()
        if not found_heading:
            if stripped == README_HELPER_SECTION:
                found_heading = True
            continue
        if stripped.startswith("- `") and stripped.endswith("`"):
            entry = stripped[len("- `") : -1]
            if entry in seen:
                issues.append(f"duplicate_readme_entry:{entry}")
                continue
            seen.add(entry)
            entries.append(entry)
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


def validate(root: Path) -> list[str]:
    readme_path = root / README_REL
    try:
        readme = readme_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"missing_readme:{README_REL}"]

    entries, issues = _helper_section_entries(readme)
    if entries and entries != list(REQUIRED_BOOTSTRAP_HELPERS):
        if len(entries) != len(REQUIRED_BOOTSTRAP_HELPERS):
            issues.append(
                "unexpected_readme_entry_count:"
                f"{len(entries)}:{len(REQUIRED_BOOTSTRAP_HELPERS)}"
            )
        for helper in REQUIRED_BOOTSTRAP_HELPERS:
            if helper not in entries:
                issues.append(f"missing_readme_entry:{helper}")
        for helper in entries:
            if helper not in REQUIRED_BOOTSTRAP_HELPERS:
                issues.append(f"unexpected_readme_entry:{helper}")
        if not any(
            issue.startswith("missing_readme_entry:")
            or issue.startswith("unexpected_readme_entry:")
            for issue in issues
        ):
            issues.append("readme_entry_order_drift:current_bootstrap_helpers")

    for helper in REQUIRED_BOOTSTRAP_HELPERS:
        rel = f"scripts/zigux/{helper}"
        if not (root / rel).exists():
            issues.append(f"missing_repo_file:{rel}")

    return issues


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _fixture_readme(entries: list[str]) -> str:
    return "\n".join(
        [
            "# scripts/zigux",
            "",
            "Current bootstrap helpers",
            *[f"- `{entry}`" for entry in entries],
            "",
        ]
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_scripts_helper_inventory_") as tmp_dir:
        root = Path(tmp_dir) / "repo"
        entries = list(REQUIRED_BOOTSTRAP_HELPERS)

        for helper in entries:
            _write(root / "scripts" / "zigux" / helper, "# stub\n")
        _write(root / README_REL, _fixture_readme(entries))

        issues = validate(root)
        if issues:
            raise SystemExit(
                "scripts-helper-inventory-self-test:baseline_failed:" + ",".join(issues)
            )

        _write(root / README_REL, _fixture_readme(entries[1:]))
        issues = validate(root)
        expected = [
            f"unexpected_readme_entry_count:{len(entries) - 1}:{len(entries)}",
            f"missing_readme_entry:{entries[0]}",
        ]
        if issues != expected:
            raise SystemExit(
                "scripts-helper-inventory-self-test:missing_entry_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        swapped = entries[:]
        swapped[0], swapped[1] = swapped[1], swapped[0]
        _write(root / README_REL, _fixture_readme(swapped))
        issues = validate(root)
        expected = ["readme_entry_order_drift:current_bootstrap_helpers"]
        if issues != expected:
            raise SystemExit(
                "scripts-helper-inventory-self-test:order_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        duplicated = entries[:]
        duplicated.insert(1, duplicated[0])
        _write(root / README_REL, _fixture_readme(duplicated))
        issues = validate(root)
        expected = [f"duplicate_readme_entry:{entries[0]}"]
        if issues != expected:
            raise SystemExit(
                "scripts-helper-inventory-self-test:duplicate_entry_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        extra = entries + ["unexpected-helper.py"]
        _write(root / README_REL, _fixture_readme(extra))
        issues = validate(root)
        expected = [
            f"unexpected_readme_entry_count:{len(entries) + 1}:{len(entries)}",
            "unexpected_readme_entry:unexpected-helper.py",
        ]
        if issues != expected:
            raise SystemExit(
                "scripts-helper-inventory-self-test:unexpected_entry_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        (root / "scripts" / "zigux" / entries[-1]).unlink()
        _write(root / README_REL, _fixture_readme(entries))
        issues = validate(root)
        expected = [f"missing_repo_file:scripts/zigux/{entries[-1]}"]
        if issues != expected:
            raise SystemExit(
                "scripts-helper-inventory-self-test:missing_repo_file_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

    print("SCRIPTS_ZIGUX_HELPER_INVENTORY_SELF_TEST=pass")
    print("SCRIPTS_ZIGUX_HELPER_INVENTORY_SELF_TEST_CASE_COUNT=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the scripts/zigux README helper inventory exact-counted and ordered."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker coverage.")
    parser.add_argument("root", nargs="?", help="Optional repo root override.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = Path(args.root).resolve() if args.root else ROOT
    issues = validate(root)
    if issues:
        print("SCRIPTS_ZIGUX_HELPER_INVENTORY=fail")
        for issue in issues:
            print(issue)
        return 1

    print("SCRIPTS_ZIGUX_HELPER_INVENTORY=pass")
    print(f"SCRIPTS_ZIGUX_HELPER_INVENTORY_ENTRY_COUNT={len(REQUIRED_BOOTSTRAP_HELPERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())