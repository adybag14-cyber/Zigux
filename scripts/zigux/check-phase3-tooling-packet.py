#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import runpy
import tempfile


_SELF = Path(__file__).resolve()
ROOT = _SELF.parents[2] if len(_SELF.parents) > 2 else _SELF.parent
MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"
VALIDATOR_REL = "scripts/zigux/validate-phase3.py"

REQUIRED_TOOLING_FILES = (
    "scripts/zigux/check-phase3-abi.py",
    "scripts/zigux/check-phase3-abi-duplicate-declarations.py",
    "scripts/zigux/check-phase3-abi-layout-packet.py",
    "scripts/zigux/check-phase3-abi-binding-constants.py",
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
    "scripts/zigux/validate-phase3-roadmap-gap-survey.py",
    "scripts/zigux/validate-phase3-rbtree-interop-survey.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "scripts/zigux/validate_phase3_header_binding_markers.py",
    "scripts/zigux/validate_phase3_core.py",
    "scripts/zigux/validate_phase3_selftest.py",
)

README_PACKET_STATIC_FILES = (
    "scripts/zigux/check-phase3-abi-duplicate-declarations.py",
    "scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "scripts/zigux/check-phase3-tooling-packet.py",
    "scripts/zigux/check-phase3-validation-flow.py",
    "scripts/zigux/generate-phase3-check-wrappers.py",
    "scripts/zigux/phase3_catalog.py",
    "scripts/zigux/phase3_check_lib.py",
    "scripts/zigux/run-phase3-checks.py",
    "scripts/zigux/validate-phase3.py",
    "scripts/zigux/validate_phase3_header_binding_markers.py",
    "scripts/zigux/validate_phase3_selftest.py",
)


def _ordered_unique(entries: list[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        if entry in seen:
            continue
        seen.add(entry)
        ordered.append(entry)
    return ordered


def _raw_readme_tooling_files(root: Path) -> tuple[list[str], list[str]]:
    validator_path = root / VALIDATOR_REL
    if not validator_path.exists():
        return [], [f"missing_validator:{VALIDATOR_REL}"]

    namespace = runpy.run_path(str(validator_path))
    issues: list[str] = []
    rels: list[str] = []

    survey_scripts = namespace.get("SURVEY_VALIDATION_SCRIPTS")
    if not isinstance(survey_scripts, tuple):
        issues.append("missing_validator_constant:SURVEY_VALIDATION_SCRIPTS")
    else:
        for entry in survey_scripts:
            if not (isinstance(entry, tuple) and entry and isinstance(entry[0], str)):
                issues.append(f"invalid_survey_entry:{entry!r}")
                continue
            rels.append(f"scripts/zigux/{entry[0]}")

    for constant_name in ("BUILD_ROOT_DRIFT_SCRIPT", "CANONICAL_SURVEY_MANIFEST_SCRIPT"):
        constant = namespace.get(constant_name)
        if not (isinstance(constant, tuple) and constant and isinstance(constant[0], str)):
            issues.append(f"missing_validator_constant:{constant_name}")
            continue
        rels.append(f"scripts/zigux/{constant[0]}")

    rels.extend(README_PACKET_STATIC_FILES)
    return rels, issues


def canonical_readme_tooling_files(root: Path) -> tuple[list[str], list[str]]:
    raw_rels, issues = _raw_readme_tooling_files(root)
    duplicates: list[str] = []
    seen: set[str] = set()
    for rel in raw_rels:
        if rel in seen and rel not in duplicates:
            duplicates.append(rel)
            continue
        seen.add(rel)
    issues.extend(f"duplicate_readme_tooling_file:{rel}" for rel in duplicates)
    return _ordered_unique(raw_rels), issues


_default_readme_files, _default_readme_issues = canonical_readme_tooling_files(ROOT)
REQUIRED_README_TOOLING_FILES = tuple(_default_readme_files)
REQUIRED_README_TOOLING_FILE_ISSUES = tuple(_default_readme_issues)


def validate(root: Path) -> list[str]:
    manifest_path = root / MANIFEST_REL
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"missing_manifest:{MANIFEST_REL}"]
    except json.JSONDecodeError as exc:
        return [f"invalid_manifest_json:{MANIFEST_REL}:{exc}"]

    files = manifest.get("files")
    if not isinstance(files, list):
        return [f"missing_manifest_files:{MANIFEST_REL}"]

    file_count = manifest.get("file_count")
    if not isinstance(file_count, int):
        return [f"invalid_manifest_file_count:{MANIFEST_REL}:{file_count!r}"]
    expected_file_count = len(files)
    if file_count != expected_file_count:
        return [
            f"unexpected_manifest_file_count:{MANIFEST_REL}:{file_count}:{expected_file_count}"
        ]

    issues: list[str] = []
    listed = {entry for entry in files if isinstance(entry, str)}

    for rel in REQUIRED_TOOLING_FILES:
        if rel not in listed:
            issues.append(f"missing_tooling_file:{rel}")
        elif not (root / rel).exists():
            issues.append(f"missing_repo_file:{rel}")

    readme_files, readme_issues = canonical_readme_tooling_files(root)
    issues.extend(readme_issues)
    for rel in readme_files:
        if not (root / rel).exists():
            issues.append(f"missing_readme_tooling_file:{rel}")

    return issues


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _fixture_validator(*extra_survey_files: str) -> str:
    survey_files = (
        "validate-phase3-roadmap-gap-survey.py",
        "validate-phase3-rbtree-interop-survey.py",
        "check-phase3-rbtree-shared-lift-contract.py",
        "check-phase3-abi-binding-constants.py",
        *extra_survey_files,
    )
    lines = ["SURVEY_VALIDATION_SCRIPTS = ("]
    for name in survey_files:
        lines.append(f'    ("{name}", "FAIL", "gate", "issue"),')
    lines.extend(
        (
            ")",
            'BUILD_ROOT_DRIFT_SCRIPT = ("check-phase3-build-roots.py", "FAIL", "gate", "issue")',
            'CANONICAL_SURVEY_MANIFEST_SCRIPT = ("check-phase3-canonical-survey-manifest.py", "FAIL", "gate", "issue")',
            "",
        )
    )
    return "\n".join(lines)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_tooling_packet_") as tmp_dir:
        root = Path(tmp_dir) / "repo"
        manifest_path = root / MANIFEST_REL

        _write(root / VALIDATOR_REL, _fixture_validator())

        for rel in REQUIRED_TOOLING_FILES:
            if rel == VALIDATOR_REL:
                continue
            _write(root / rel, "# stub\n")

        readme_files, readme_issues = canonical_readme_tooling_files(root)
        if readme_issues:
            raise SystemExit(
                "phase3-tooling-packet-self-test:canonical_readme_derivation_failed:"
                + ",".join(readme_issues)
            )
        for rel in readme_files:
            if rel == VALIDATOR_REL:
                continue
            _write(root / rel, "# stub\n")

        _write(
            manifest_path,
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "active",
                    "slice": "abi-substrate-skeleton",
                    "files": list(REQUIRED_TOOLING_FILES),
                    "file_count": len(REQUIRED_TOOLING_FILES),
                },
                indent=2,
            )
            + "\n",
        )

        issues = validate(root)
        if issues:
            raise SystemExit("phase3-tooling-packet-self-test:baseline_failed:" + ",".join(issues))

        broken_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        broken_manifest["file_count"] = len(REQUIRED_TOOLING_FILES) - 1
        _write(manifest_path, json.dumps(broken_manifest, indent=2) + "\n")
        issues = validate(root)
        expected = [
            f"unexpected_manifest_file_count:{MANIFEST_REL}:{len(REQUIRED_TOOLING_FILES) - 1}:{len(REQUIRED_TOOLING_FILES)}"
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-tooling-packet-self-test:manifest_file_count_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        broken_manifest["file_count"] = str(len(REQUIRED_TOOLING_FILES))
        _write(manifest_path, json.dumps(broken_manifest, indent=2) + "\n")
        issues = validate(root)
        expected = [
            f"invalid_manifest_file_count:{MANIFEST_REL}:{str(len(REQUIRED_TOOLING_FILES))!r}"
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-tooling-packet-self-test:manifest_file_count_type_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(
            manifest_path,
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "active",
                    "slice": "abi-substrate-skeleton",
                    "files": list(REQUIRED_TOOLING_FILES),
                    "file_count": len(REQUIRED_TOOLING_FILES),
                },
                indent=2,
            )
            + "\n",
        )

        broken_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        missing_manifest_rel = "scripts/zigux/validate_phase3_header_binding_markers.py"
        broken_manifest["files"] = [
            rel for rel in REQUIRED_TOOLING_FILES if rel != missing_manifest_rel
        ]
        broken_manifest["file_count"] = len(broken_manifest["files"])
        _write(manifest_path, json.dumps(broken_manifest, indent=2) + "\n")
        issues = validate(root)
        if issues != [f"missing_tooling_file:{missing_manifest_rel}"]:
            raise SystemExit(
                "phase3-tooling-packet-self-test:missing_manifest_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(
            manifest_path,
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "active",
                    "slice": "abi-substrate-skeleton",
                    "files": list(REQUIRED_TOOLING_FILES),
                    "file_count": len(REQUIRED_TOOLING_FILES),
                },
                indent=2,
            )
            + "\n",
        )
        repo_only_rel = "scripts/zigux/validate_phase3_core.py"
        (root / repo_only_rel).unlink()
        issues = validate(root)
        if issues != [f"missing_repo_file:{repo_only_rel}"]:
            raise SystemExit(
                "phase3-tooling-packet-self-test:missing_repo_file_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(root / repo_only_rel, "# stub\n")
        readme_only_rel = "scripts/zigux/validate-phase3-roadmap-gap-survey.py"
        (root / readme_only_rel).unlink()
        issues = validate(root)
        if issues != [f"missing_readme_tooling_file:{readme_only_rel}"]:
            raise SystemExit(
                "phase3-tooling-packet-self-test:missing_readme_tooling_file_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(root / readme_only_rel, "# stub\n")
        _write(
            root / VALIDATOR_REL,
            _fixture_validator("validate_phase3_header_binding_markers.py"),
        )
        issues = validate(root)
        expected = [
            "duplicate_readme_tooling_file:scripts/zigux/validate_phase3_header_binding_markers.py"
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-tooling-packet-self-test:duplicate_header_binding_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

    print("PHASE3_TOOLING_PACKET_SELF_TEST=pass")
    print("PHASE3_TOOLING_PACKET_SELF_TEST_CASE_COUNT=7")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shared Phase 3 manifest aligned with the live repo-tooling packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker coverage.")
    parser.add_argument("root", nargs="?", help="Optional repo root override.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(Path(args.root).resolve() if args.root else ROOT)
    if issues:
        print("PHASE3_TOOLING_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    readme_files, _ = canonical_readme_tooling_files(Path(args.root).resolve() if args.root else ROOT)
    print("PHASE3_TOOLING_PACKET=pass")
    print(f"PHASE3_TOOLING_PACKET_FILE_COUNT={len(REQUIRED_TOOLING_FILES)}")
    print(f"PHASE3_TOOLING_PACKET_README_FILE_COUNT={len(readme_files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
