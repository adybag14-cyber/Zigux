#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import runpy
import tempfile


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"
VALIDATOR_REL = "scripts/zigux/validate-phase3.py"


def _ordered_unique(entries: list[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        if entry in seen:
            continue
        seen.add(entry)
        ordered.append(entry)
    return ordered


def _duplicates(entries: list[str]) -> list[str]:
    duplicates: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        if entry in seen and entry not in duplicates:
            duplicates.append(entry)
            continue
        seen.add(entry)
    return duplicates


def _canonical_survey_script_rels(root: Path) -> tuple[list[str], list[str]]:
    validator_path = root / VALIDATOR_REL
    if not validator_path.exists():
        return [], [f"missing_validator:{VALIDATOR_REL}"]

    try:
        namespace = runpy.run_path(str(validator_path))
    except Exception as exc:
        return [], [
            f"validator_load_failed:{VALIDATOR_REL}:{type(exc).__name__}:{exc}"
        ]
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

    build_root_script = namespace.get("BUILD_ROOT_DRIFT_SCRIPT")
    if not (isinstance(build_root_script, tuple) and build_root_script and isinstance(build_root_script[0], str)):
        issues.append("missing_validator_constant:BUILD_ROOT_DRIFT_SCRIPT")
    else:
        rels.append(f"scripts/zigux/{build_root_script[0]}")

    canonical_manifest_script = namespace.get("CANONICAL_SURVEY_MANIFEST_SCRIPT")
    if not (
        isinstance(canonical_manifest_script, tuple)
        and canonical_manifest_script
        and isinstance(canonical_manifest_script[0], str)
    ):
        issues.append("missing_validator_constant:CANONICAL_SURVEY_MANIFEST_SCRIPT")
    else:
        rels.append(f"scripts/zigux/{canonical_manifest_script[0]}")

    for rel in _duplicates(rels):
        issues.append(f"duplicate_canonical_survey_script:{rel}")

    return _ordered_unique(rels), issues


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
        return [f"missing_manifest_file_count:{MANIFEST_REL}"]

    issues: list[str] = []
    if file_count != len(files):
        issues.append(
            f"unexpected_manifest_file_count:{MANIFEST_REL}:{file_count}:{len(files)}"
        )

    canonical_rels, canonical_issues = _canonical_survey_script_rels(root)
    issues.extend(canonical_issues)
    listed = {entry for entry in files if isinstance(entry, str)}
    for rel in canonical_rels:
        if rel not in listed:
            issues.append(f"missing_manifest_survey_script:{rel}")
        if rel in listed and not (root / rel).exists():
            issues.append(f"missing_repo_survey_script:{rel}")
    return issues


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_canonical_survey_manifest_") as tmp_dir:
        root = Path(tmp_dir) / "repo"

        _write(
            root / VALIDATOR_REL,
            "\n".join(
                (
                    "SURVEY_VALIDATION_SCRIPTS = (",
                    '    ("validate-phase3-roadmap-gap-survey.py", "PHASE3_ROADMAP_GAP_SURVEY=fail", "roadmap-gap", "missing_roadmap_anchor"),',
                    '    ("validate-phase3-rbtree-interop-survey.py", "PHASE3_RBTREE_INTEROP_SURVEY=fail", "rbtree-gap", "missing_rbtree_anchor"),',
                    ")",
                    'BUILD_ROOT_DRIFT_SCRIPT = ("check-phase3-build-roots.py", "PHASE3_BUILD_ROOTS=fail", "build-roots", "missing_root")',
                    'CANONICAL_SURVEY_MANIFEST_SCRIPT = ("check-phase3-canonical-survey-manifest.py", "PHASE3_CANONICAL_SURVEY_MANIFEST=fail", "canonical-manifest", "missing_manifest_anchor")',
                    "",
                )
            ),
        )

        canonical_rels = (
            "scripts/zigux/validate-phase3-roadmap-gap-survey.py",
            "scripts/zigux/validate-phase3-rbtree-interop-survey.py",
            "scripts/zigux/check-phase3-build-roots.py",
            "scripts/zigux/check-phase3-canonical-survey-manifest.py",
        )
        for rel in canonical_rels:
            _write(root / rel, "# stub\n")

        _write(
            root / MANIFEST_REL,
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "active",
                    "slice": "abi-substrate-skeleton",
                    "files": list(canonical_rels),
                    "file_count": len(canonical_rels),
                },
                indent=2,
            )
            + "\n",
        )

        issues = validate(root)
        if issues:
            raise SystemExit(
                "phase3-canonical-survey-manifest-self-test:baseline_failed:" + ",".join(issues)
            )

        manifest_path = root / MANIFEST_REL
        broken_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        broken_manifest["files"] = [rel for rel in canonical_rels if rel != canonical_rels[0]]
        _write(manifest_path, json.dumps(broken_manifest, indent=2) + "\n")
        issues = validate(root)
        expected = [
            f"unexpected_manifest_file_count:{MANIFEST_REL}:{len(canonical_rels)}:{len(canonical_rels) - 1}",
            f"missing_manifest_survey_script:{canonical_rels[0]}",
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-canonical-survey-manifest-self-test:missing_manifest_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        broken_manifest["files"] = list(canonical_rels)
        _write(manifest_path, json.dumps(broken_manifest, indent=2) + "\n")
        (root / canonical_rels[-1]).unlink()
        issues = validate(root)
        expected = [f"missing_repo_survey_script:{canonical_rels[-1]}"]
        if issues != expected:
            raise SystemExit(
                "phase3-canonical-survey-manifest-self-test:missing_repo_file_guard_failed:"
                + (",".join(issues) if issues else "none")
            )
        _write(root / canonical_rels[-1], "# stub\n")

        broken_manifest["file_count"] = len(canonical_rels) + 3
        _write(manifest_path, json.dumps(broken_manifest, indent=2) + "\n")
        issues = validate(root)
        expected = [
            f"unexpected_manifest_file_count:{MANIFEST_REL}:{len(canonical_rels) + 3}:{len(canonical_rels)}"
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-canonical-survey-manifest-self-test:file_count_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        broken_manifest.pop("file_count")
        _write(manifest_path, json.dumps(broken_manifest, indent=2) + "\n")
        issues = validate(root)
        expected = [f"missing_manifest_file_count:{MANIFEST_REL}"]
        if issues != expected:
            raise SystemExit(
                "phase3-canonical-survey-manifest-self-test:missing_file_count_guard_failed:"
                + (",".join(issues) if issues else "none")
            )
        broken_manifest["file_count"] = len(canonical_rels)
        _write(manifest_path, json.dumps(broken_manifest, indent=2) + "\n")

        _write(
            root / VALIDATOR_REL,
            "\n".join(
                (
                    "SURVEY_VALIDATION_SCRIPTS = (",
                    '    ("validate-phase3-roadmap-gap-survey.py", "PHASE3_ROADMAP_GAP_SURVEY=fail", "roadmap-gap", "missing_roadmap_anchor"),',
                    '    ("validate-phase3-rbtree-interop-survey.py", "PHASE3_RBTREE_INTEROP_SURVEY=fail", "rbtree-gap", "missing_rbtree_anchor"),',
                    ")",
                    'CANONICAL_SURVEY_MANIFEST_SCRIPT = ("check-phase3-canonical-survey-manifest.py", "PHASE3_CANONICAL_SURVEY_MANIFEST=fail", "canonical-manifest", "missing_manifest_anchor")',
                    "",
                )
            ),
        )
        issues = validate(root)
        expected = ["missing_validator_constant:BUILD_ROOT_DRIFT_SCRIPT"]
        if issues != expected:
            raise SystemExit(
                "phase3-canonical-survey-manifest-self-test:missing_build_root_constant_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(
            root / VALIDATOR_REL,
            "\n".join(
                (
                    "SURVEY_VALIDATION_SCRIPTS = (",
                    '    ("validate-phase3-roadmap-gap-survey.py", "PHASE3_ROADMAP_GAP_SURVEY=fail", "roadmap-gap", "missing_roadmap_anchor"),',
                    '    ("validate-phase3-rbtree-interop-survey.py", "PHASE3_RBTREE_INTEROP_SURVEY=fail", "rbtree-gap", "missing_rbtree_anchor"),',
                    ")",
                    'BUILD_ROOT_DRIFT_SCRIPT = ("check-phase3-build-roots.py", "PHASE3_BUILD_ROOTS=fail", "build-roots", "missing_root")',
                    "",
                )
            ),
        )
        issues = validate(root)
        expected = ["missing_validator_constant:CANONICAL_SURVEY_MANIFEST_SCRIPT"]
        if issues != expected:
            raise SystemExit(
                "phase3-canonical-survey-manifest-self-test:missing_canonical_manifest_constant_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(
            root / VALIDATOR_REL,
            "\n".join(
                (
                    "SURVEY_VALIDATION_SCRIPTS = (",
                    '    ("validate-phase3-roadmap-gap-survey.py", "PHASE3_ROADMAP_GAP_SURVEY=fail", "roadmap-gap", "missing_roadmap_anchor"),',
                    '    "broken-entry",',
                    ")",
                    'BUILD_ROOT_DRIFT_SCRIPT = ("check-phase3-build-roots.py", "PHASE3_BUILD_ROOTS=fail", "build-roots", "missing_root")',
                    'CANONICAL_SURVEY_MANIFEST_SCRIPT = ("check-phase3-canonical-survey-manifest.py", "PHASE3_CANONICAL_SURVEY_MANIFEST=fail", "canonical-manifest", "missing_manifest_anchor")',
                    "",
                )
            ),
        )
        issues = validate(root)
        expected = ["invalid_survey_entry:'broken-entry'"]
        if issues != expected:
            raise SystemExit(
                "phase3-canonical-survey-manifest-self-test:invalid_survey_entry_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(
            root / VALIDATOR_REL,
            "\n".join(
                (
                    "SURVEY_VALIDATION_SCRIPTS = (",
                    '    ("validate-phase3-roadmap-gap-survey.py", "PHASE3_ROADMAP_GAP_SURVEY=fail", "roadmap-gap", "missing_roadmap_anchor"),',
                    '    ("validate-phase3-roadmap-gap-survey.py", "PHASE3_ROADMAP_GAP_SURVEY=fail", "roadmap-gap-dup", "missing_roadmap_anchor_dup"),',
                    '    ("validate-phase3-rbtree-interop-survey.py", "PHASE3_RBTREE_INTEROP_SURVEY=fail", "rbtree-gap", "missing_rbtree_anchor"),',
                    ")",
                    'BUILD_ROOT_DRIFT_SCRIPT = ("check-phase3-build-roots.py", "PHASE3_BUILD_ROOTS=fail", "build-roots", "missing_root")',
                    'CANONICAL_SURVEY_MANIFEST_SCRIPT = ("check-phase3-canonical-survey-manifest.py", "PHASE3_CANONICAL_SURVEY_MANIFEST=fail", "canonical-manifest", "missing_manifest_anchor")',
                    "",
                )
            ),
        )
        issues = validate(root)
        expected = [
            "duplicate_canonical_survey_script:scripts/zigux/validate-phase3-roadmap-gap-survey.py"
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-canonical-survey-manifest-self-test:duplicate_survey_script_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(
            root / VALIDATOR_REL,
            "\n".join(
                (
                    "SURVEY_VALIDATION_SCRIPTS = (",
                    '    ("validate-phase3-roadmap-gap-survey.py", "PHASE3_ROADMAP_GAP_SURVEY=fail", "roadmap-gap", "missing_roadmap_anchor"),',
                    '    ("check-phase3-build-roots.py", "PHASE3_BUILD_ROOTS=fail", "build-roots-dup", "missing_root_dup"),',
                    '    ("validate-phase3-rbtree-interop-survey.py", "PHASE3_RBTREE_INTEROP_SURVEY=fail", "rbtree-gap", "missing_rbtree_anchor"),',
                    ")",
                    'BUILD_ROOT_DRIFT_SCRIPT = ("check-phase3-build-roots.py", "PHASE3_BUILD_ROOTS=fail", "build-roots", "missing_root")',
                    'CANONICAL_SURVEY_MANIFEST_SCRIPT = ("check-phase3-canonical-survey-manifest.py", "PHASE3_CANONICAL_SURVEY_MANIFEST=fail", "canonical-manifest", "missing_manifest_anchor")',
                    "",
                )
            ),
        )
        issues = validate(root)
        expected = [
            "duplicate_canonical_survey_script:scripts/zigux/check-phase3-build-roots.py"
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-canonical-survey-manifest-self-test:duplicate_build_root_script_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        _write(
            root / VALIDATOR_REL,
            "\n".join(
                (
                    'raise RuntimeError("synthetic validator load failure")',
                    "",
                )
            ),
        )
        issues = validate(root)
        expected = [
            f"validator_load_failed:{VALIDATOR_REL}:RuntimeError:synthetic validator load failure"
        ]
        if issues != expected:
            raise SystemExit(
                "phase3-canonical-survey-manifest-self-test:validator_load_failure_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

        (root / VALIDATOR_REL).unlink()
        issues = validate(root)
        expected = [f"missing_validator:{VALIDATOR_REL}"]
        if issues != expected:
            raise SystemExit(
                "phase3-canonical-survey-manifest-self-test:missing_validator_guard_failed:"
                + (",".join(issues) if issues else "none")
            )

    print("PHASE3_CANONICAL_SURVEY_MANIFEST_SELF_TEST=pass")
    print("PHASE3_CANONICAL_SURVEY_MANIFEST_SELF_TEST_CASE_COUNT=11")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 3 manifest aligned with the validator's canonical survey-script list."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker coverage.")
    parser.add_argument("root", nargs="?", help="Optional repo root override.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(Path(args.root).resolve() if args.root else ROOT)
    if issues:
        print("PHASE3_CANONICAL_SURVEY_MANIFEST=fail")
        for issue in issues:
            print(issue)
        return 1

    canonical_rels, _ = _canonical_survey_script_rels(Path(args.root).resolve() if args.root else ROOT)
    print("PHASE3_CANONICAL_SURVEY_MANIFEST=pass")
    print(f"PHASE3_CANONICAL_SURVEY_SCRIPT_COUNT={len(canonical_rels)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
