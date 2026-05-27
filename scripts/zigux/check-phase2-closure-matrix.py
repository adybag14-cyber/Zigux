#!/usr/bin/env python3
"""Externally widen the Phase 2 closure validator matrix coverage."""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
VALIDATOR_REL = Path("scripts/zigux/validate-phase2-closure.py")


def load_validator(root: Path):
    path = root / VALIDATOR_REL
    spec = importlib.util.spec_from_file_location("zigux_validate_phase2_closure", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"unable to load closure validator: {path}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except FileNotFoundError as exc:
        raise SystemExit(f"unable to load closure validator: {path}") from exc
    return module


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
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


def assert_issue(module, root: Path, expected: tuple[str, str]) -> None:
    issues = module.collect_issues(root)
    if expected not in issues:
        raise AssertionError(f"missing expected issue {expected!r}; saw {issues!r}")


def seed_materialized_root(module, root: Path, source_root: Path) -> None:
    paths_to_copy = {VALIDATOR_REL, *module.REQUIRED_FILES}
    for rel in paths_to_copy:
        source_path = source_root / rel
        if not source_path.exists():
            raise AssertionError(f"source path missing: {source_path}")
        destination_path = root / rel
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, destination_path)
    archive_support_rels = getattr(module, "ARCHIVE_SUPPORT_RELS", ())
    for rel in archive_support_rels:
        if not isinstance(rel, Path):
            continue
        source_path = source_root / rel
        if not source_path.exists():
            continue
        destination_path = root / rel
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, destination_path)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


MANIFEST_EXPECTATION_ATTR_PREFIX = "EXPECTED_MANIFEST_"


def collect_manifest_surface_expectations(module, manifest_path: Path) -> list[tuple[str, tuple[str, ...]]]:
    payload = load_json(manifest_path)
    if not isinstance(payload, dict):
        raise AssertionError("manifest root must stay a dict in the seeded baseline")
    surfaces = payload.get("present_surfaces")
    if not isinstance(surfaces, dict):
        raise AssertionError("manifest present_surfaces must stay a dict in the seeded baseline")

    expectations: list[tuple[str, tuple[str, ...]]] = []
    for attr_name, expected in sorted(vars(module).items()):
        if not attr_name.startswith(MANIFEST_EXPECTATION_ATTR_PREFIX):
            continue
        if not isinstance(expected, tuple) or not all(isinstance(item, str) for item in expected):
            continue

        key = attr_name[len(MANIFEST_EXPECTATION_ATTR_PREFIX) :].lower()
        value = surfaces.get(key)
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise AssertionError(f"manifest surface must stay a list[str] in the seeded baseline: {key}")
        expectations.append((key, expected))
    return expectations


def archive_support_note(module) -> str | None:
    rels = getattr(module, "ARCHIVE_SUPPORT_RELS", None)
    if not isinstance(rels, tuple) or not rels:
        return None
    if not all(isinstance(rel, Path) for rel in rels):
        raise AssertionError("archive support rels must stay tuple[Path, ...] in the seeded baseline")
    return " or ".join(rel.as_posix() for rel in rels)


def remove_archive_support_paths(module, root: Path) -> None:
    rels = getattr(module, "ARCHIVE_SUPPORT_RELS", ())
    for rel in rels:
        path = module.resolve(root, rel)
        if path.exists():
            path.unlink()


def run_matrix(module, seed_root) -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_matrix_") as tmp_dir:
        root = Path(tmp_dir)
        seed_root(root)
        if module.collect_issues(root) != []:
            raise AssertionError("expected clean baseline self-test root")
        checks_run += 1

        for marker in module.REQUIRED_CLOSURE_MARKERS:
            seed_root(root)
            path = module.resolve(root, module.PHASE2_CLOSURE_REL)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert_issue(module, root, ("MISSING_CLOSURE_MARKER", marker))
            checks_run += 1

        for marker in module.REQUIRED_WORKFLOW_LINES:
            seed_root(root)
            path = module.resolve(root, module.WORKFLOW_REL)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "run: python3 scripts/zigux/other.py"),
                encoding="utf-8",
            )
            assert_issue(module, root, ("MISSING_WORKFLOW_LINE", marker))
            checks_run += 1

            seed_root(root)
            path = module.resolve(root, module.WORKFLOW_REL)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert_issue(module, root, ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2"))
            checks_run += 1

        for marker in module.REQUIRED_MAKEFILE_LINES:
            seed_root(root)
            path = module.resolve(root, module.MAKEFILE_REL)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "# removed"), encoding="utf-8")
            assert_issue(module, root, ("MISSING_MAKEFILE_LINE", marker))
            checks_run += 1

            seed_root(root)
            path = module.resolve(root, module.MAKEFILE_REL)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert_issue(module, root, ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2"))
            checks_run += 1

        seed_root(root)
        manifest_path = module.resolve(root, module.MANIFEST_REL)
        payload = load_json(manifest_path)
        payload["repo_reality_gaps"] = ["drifted-gap"]
        write_json(manifest_path, payload)
        assert_issue(module, root, ("UNEXPECTED_MANIFEST_GAPS", "['drifted-gap']"))
        checks_run += 1

        seed_root(root)
        manifest_path = module.resolve(root, module.MANIFEST_REL)
        payload = load_json(manifest_path)
        del payload["repo_reality_gaps"]
        write_json(manifest_path, payload)
        assert_issue(module, root, ("UNEXPECTED_MANIFEST_GAPS", "None"))
        checks_run += 1

        seed_root(root)
        manifest_path = module.resolve(root, module.MANIFEST_REL)
        payload = load_json(manifest_path)
        payload["repo_reality_gaps"] = {}
        write_json(manifest_path, payload)
        assert_issue(module, root, ("UNEXPECTED_MANIFEST_GAPS", "{}"))
        checks_run += 1

        seed_root(root)
        manifest_path = module.resolve(root, module.MANIFEST_REL)
        write_json(manifest_path, [])
        assert_issue(module, root, ("INVALID_MANIFEST_SHAPE", "root"))
        checks_run += 1

        seed_root(root)
        manifest_path = module.resolve(root, module.MANIFEST_REL)
        payload = load_json(manifest_path)
        payload["present_surfaces"] = []
        write_json(manifest_path, payload)
        assert_issue(module, root, ("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        checks_run += 1

        seed_root(root)
        manifest_path = module.resolve(root, module.MANIFEST_REL)
        for key, expected in collect_manifest_surface_expectations(module, manifest_path):
            seed_root(root)
            manifest_path = module.resolve(root, module.MANIFEST_REL)
            payload = load_json(manifest_path)
            del payload["present_surfaces"][key]
            write_json(manifest_path, payload)
            assert_issue(module, root, ("INVALID_MANIFEST_SHAPE", key))
            checks_run += 1

            seed_root(root)
            manifest_path = module.resolve(root, module.MANIFEST_REL)
            payload = load_json(manifest_path)
            payload["present_surfaces"][key] = "drifted"
            write_json(manifest_path, payload)
            assert_issue(module, root, ("INVALID_MANIFEST_SHAPE", key))
            checks_run += 1

            seed_root(root)
            manifest_path = module.resolve(root, module.MANIFEST_REL)
            payload = load_json(manifest_path)
            payload["present_surfaces"][key] = [123]
            write_json(manifest_path, payload)
            assert_issue(module, root, ("INVALID_MANIFEST_SHAPE", key))
            checks_run += 1

            for marker in expected:
                seed_root(root)
                manifest_path = module.resolve(root, module.MANIFEST_REL)
                payload = load_json(manifest_path)
                payload["present_surfaces"][key].remove(marker)
                write_json(manifest_path, payload)
                assert_issue(module, root, ("MISSING_MANIFEST_SURFACE", f"{key}:{marker}"))
                checks_run += 1

        support_note = archive_support_note(module)
        archive_readme_rel = getattr(module, "ARCHIVE_README_REL", None)
        if support_note is not None and isinstance(archive_readme_rel, Path):
            archive_parts_rel = getattr(module, "ARCHIVE_PARTS_MANIFEST_REL", None)
            if isinstance(archive_parts_rel, Path):
                seed_root(root)
                remove_archive_support_paths(module, root)
                manifest_path = module.resolve(root, module.MANIFEST_REL)
                payload = load_json(manifest_path)
                payload["present_surfaces"]["archive_support"] = [
                    archive_readme_rel.as_posix(),
                    archive_parts_rel.as_posix(),
                ]
                write_json(manifest_path, payload)
                parts_manifest_path = module.resolve(root, archive_parts_rel)
                parts_manifest_path.parent.mkdir(parents=True, exist_ok=True)
                write_json(parts_manifest_path, {"parts": []})
                if module.collect_issues(root) != []:
                    raise AssertionError("expected archive parts fallback baseline to stay clean")
                checks_run += 1

            seed_root(root)
            remove_archive_support_paths(module, root)
            manifest_path = module.resolve(root, module.MANIFEST_REL)
            payload = load_json(manifest_path)
            payload["present_surfaces"]["archive_support"] = [archive_readme_rel.as_posix()]
            write_json(manifest_path, payload)
            assert_issue(module, root, ("MISSING_REQUIRED_ARCHIVE_SUPPORT", support_note))
            assert_issue(module, root, ("MISSING_MANIFEST_ARCHIVE_SUPPORT", support_note))
            checks_run += 1

            seed_root(root)
            manifest_path = module.resolve(root, module.MANIFEST_REL)
            payload = load_json(manifest_path)
            payload["present_surfaces"]["archive_support"] = [archive_readme_rel.as_posix()]
            write_json(manifest_path, payload)
            assert_issue(module, root, ("MISSING_MANIFEST_ARCHIVE_SUPPORT", support_note))
            checks_run += 1

        seed_root(root)
        cases_path = module.resolve(root, module.KCONFIG_CASES_REL)
        write_json(cases_path, [])
        assert_issue(module, root, ("KCONFIG_CASE_PACKET_MISMATCH", "root"))
        checks_run += 1

        seed_root(root)
        cases_path = module.resolve(root, module.KCONFIG_CASES_REL)
        payload = load_json(cases_path)
        payload["conf_cases"][0]["expected"] = "drifted.json"
        write_json(cases_path, payload)
        assert_issue(module, root, ("CONF_CASE_PACKET_MISMATCH", "conf_cases"))
        checks_run += 1

        seed_root(root)
        cases_path = module.resolve(root, module.KCONFIG_CASES_REL)
        payload = load_json(cases_path)
        payload["confdata_cases"][0]["expected"] = "drifted.json"
        write_json(cases_path, payload)
        assert_issue(module, root, ("CONFDATA_CASE_PACKET_MISMATCH", "confdata_cases"))
        checks_run += 1

        seed_root(root)
        conf_manifest_path = module.resolve(root, module.CONF_MANIFEST_REL)
        payload = load_json(conf_manifest_path)
        payload["case_count"] = 999
        write_json(conf_manifest_path, payload)
        assert_issue(module, root, ("CONF_MANIFEST_MISMATCH", "root"))
        checks_run += 1

        seed_root(root)
        confdata_manifest_path = module.resolve(root, module.CONFDATA_MANIFEST_REL)
        payload = load_json(confdata_manifest_path)
        payload["case_count"] = 999
        write_json(confdata_manifest_path, payload)
        assert_issue(module, root, ("CONFDATA_MANIFEST_MISMATCH", "root"))
        checks_run += 1

        seed_root(root)
        genksyms_cases_path = module.resolve(root, module.GENKSYMS_CASES_REL)
        payload = load_json(genksyms_cases_path)
        payload[0]["expected_file"] = "drifted.json"
        write_json(genksyms_cases_path, payload)
        assert_issue(module, root, ("GENKSYMS_CASE_PACKET_MISMATCH", "cases"))
        checks_run += 1

        seed_root(root)
        genksyms_manifest_path = module.resolve(root, module.GENKSYMS_MANIFEST_REL)
        payload = load_json(genksyms_manifest_path)
        payload["process_output_packet"] = ["invalid_option_expected.json"]
        write_json(genksyms_manifest_path, payload)
        assert_issue(module, root, ("GENKSYMS_MANIFEST_MISMATCH", "root"))
        checks_run += 1

        for rel in module.REQUIRED_FILES:
            seed_root(root)
            path = module.resolve(root, rel)
            path.unlink()
            assert_issue(module, root, ("MISSING_REQUIRED_FILE", rel.as_posix()))
            checks_run += 1

    return checks_run


def run_self_test() -> int:
    fake_validator = """\
from pathlib import Path
import json

PHASE2_CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_REL = Path("zigux/Makefile")
MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
KCONFIG_CASES_REL = Path("zigux/tests/fixtures/kconfig_bridge/cases.json")
CONF_MANIFEST_REL = Path("zigux/tests/fixtures/kconfig_bridge/conf_manifest.json")
CONFDATA_MANIFEST_REL = Path("zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json")
GENKSYMS_CASES_REL = Path("zigux/tests/fixtures/genksyms_bridge/cases.json")
GENKSYMS_MANIFEST_REL = Path("zigux/tests/fixtures/genksyms_bridge/manifest.json")
ARCHIVE_README_REL = Path("third_party/README.md")
ARCHIVE_PAYLOAD_REL = Path("third_party/archive-b.tar.xz")
ARCHIVE_PARTS_MANIFEST_REL = Path("third_party/archive-b.tar.xz.parts/manifest.json")
ARCHIVE_SUPPORT_RELS = (ARCHIVE_PAYLOAD_REL, ARCHIVE_PARTS_MANIFEST_REL)
REQUIRED_CLOSURE_MARKERS = ("`marker-a`", "`marker-b`")
REQUIRED_WORKFLOW_LINES = ("run: alpha", "run: beta")
REQUIRED_MAKEFILE_LINES = ("phase2-a:", "phase2-b:")
REQUIRED_FILES = (
    PHASE2_CLOSURE_REL,
    WORKFLOW_REL,
    MAKEFILE_REL,
    MANIFEST_REL,
    KCONFIG_CASES_REL,
    CONF_MANIFEST_REL,
    CONFDATA_MANIFEST_REL,
    GENKSYMS_CASES_REL,
    GENKSYMS_MANIFEST_REL,
    ARCHIVE_README_REL,
)
EXPECTED_CONF_CASE_DETAILS = [{"name": "conf", "expected": "conf.json"}]
EXPECTED_CONFDATA_CASE_DETAILS = [{"name": "confdata", "expected": "confdata.json"}]
EXPECTED_CONF_MANIFEST = {"tool": "conf", "case_count": 1}
EXPECTED_CONFDATA_MANIFEST = {"tool": "confdata", "case_count": 1}
EXPECTED_GENKSYMS_CASES = [{"name": "genksyms", "expected_file": "genksyms.json"}]
EXPECTED_GENKSYMS_MANIFEST = {"tool": "genksyms", "process_output_packet": ["genksyms.json"]}
EXPECTED_MANIFEST_REVIEW_SURFACES = ("review-a.md", "review-b.md")
EXPECTED_MANIFEST_CLOSURE_NOTES = ("closure-a.md", "closure-b.md")
EXPECTED_MANIFEST_VALIDATORS = ("validate-a.py", "validate-b.py")
EXPECTED_MANIFEST_CHECKERS = ("checker-a.py", "checker-b.py")
EXPECTED_MANIFEST_BOOTSTRAP_HELPERS = ("bootstrap-a.py", "bootstrap-b.py")
EXPECTED_MANIFEST_ARCHIVE_SUPPORT = (ARCHIVE_README_REL.as_posix(),)
DEFAULT_MANIFEST_ARCHIVE_SUPPORT = (*EXPECTED_MANIFEST_ARCHIVE_SUPPORT, ARCHIVE_PAYLOAD_REL.as_posix())
EXPECTED_MANIFEST_BRIDGE_HELPERS = ("bridge-a.zig", "bridge-b.zig")
EXPECTED_MANIFEST_FIXTURE_ROSTER = ("fixture-a.json", "fixture-b.json")
EXPECTED_MANIFEST_POLICY = ("policy-a.json",)

def resolve(root: Path, rel: Path) -> Path:
    return root / rel

def build_self_test_root(root: Path) -> None:
    resolve(root, PHASE2_CLOSURE_REL).parent.mkdir(parents=True, exist_ok=True)
    resolve(root, PHASE2_CLOSURE_REL).write_text("`marker-a`\n`marker-b`\n", encoding="utf-8")
    resolve(root, WORKFLOW_REL).parent.mkdir(parents=True, exist_ok=True)
    resolve(root, WORKFLOW_REL).write_text("run: alpha\nrun: beta\n", encoding="utf-8")
    resolve(root, MAKEFILE_REL).parent.mkdir(parents=True, exist_ok=True)
    resolve(root, MAKEFILE_REL).write_text("phase2-a:\nphase2-b:\n", encoding="utf-8")
    resolve(root, MANIFEST_REL).parent.mkdir(parents=True, exist_ok=True)
    resolve(root, MANIFEST_REL).write_text(json.dumps({
        "repo_reality_gaps": [],
        "present_surfaces": {
            "review_surfaces": list(EXPECTED_MANIFEST_REVIEW_SURFACES),
            "closure_notes": list(EXPECTED_MANIFEST_CLOSURE_NOTES),
            "validators": list(EXPECTED_MANIFEST_VALIDATORS),
            "checkers": list(EXPECTED_MANIFEST_CHECKERS),
            "bootstrap_helpers": list(EXPECTED_MANIFEST_BOOTSTRAP_HELPERS),
            "archive_support": list(DEFAULT_MANIFEST_ARCHIVE_SUPPORT),
            "bridge_helpers": list(EXPECTED_MANIFEST_BRIDGE_HELPERS),
            "fixture_roster": list(EXPECTED_MANIFEST_FIXTURE_ROSTER),
            "policy": list(EXPECTED_MANIFEST_POLICY),
            "out_of_scope": ["extra-surface.md"],
        },
    }, indent=2) + "\n", encoding="utf-8")
    resolve(root, KCONFIG_CASES_REL).parent.mkdir(parents=True, exist_ok=True)
    resolve(root, KCONFIG_CASES_REL).write_text(json.dumps({
        "conf_cases": EXPECTED_CONF_CASE_DETAILS,
        "confdata_cases": EXPECTED_CONFDATA_CASE_DETAILS,
    }, indent=2) + "\n", encoding="utf-8")
    resolve(root, CONF_MANIFEST_REL).parent.mkdir(parents=True, exist_ok=True)
    resolve(root, CONF_MANIFEST_REL).write_text(json.dumps(EXPECTED_CONF_MANIFEST, indent=2) + "\n", encoding="utf-8")
    resolve(root, CONFDATA_MANIFEST_REL).parent.mkdir(parents=True, exist_ok=True)
    resolve(root, CONFDATA_MANIFEST_REL).write_text(json.dumps(EXPECTED_CONFDATA_MANIFEST, indent=2) + "\n", encoding="utf-8")
    resolve(root, GENKSYMS_CASES_REL).parent.mkdir(parents=True, exist_ok=True)
    resolve(root, GENKSYMS_CASES_REL).write_text(json.dumps(EXPECTED_GENKSYMS_CASES, indent=2) + "\n", encoding="utf-8")
    resolve(root, GENKSYMS_MANIFEST_REL).parent.mkdir(parents=True, exist_ok=True)
    resolve(root, GENKSYMS_MANIFEST_REL).write_text(json.dumps(EXPECTED_GENKSYMS_MANIFEST, indent=2) + "\n", encoding="utf-8")
    resolve(root, ARCHIVE_README_REL).parent.mkdir(parents=True, exist_ok=True)
    resolve(root, ARCHIVE_README_REL).write_text("archive readme\n", encoding="utf-8")
    resolve(root, ARCHIVE_PAYLOAD_REL).parent.mkdir(parents=True, exist_ok=True)
    resolve(root, ARCHIVE_PAYLOAD_REL).write_text("archive payload\n", encoding="utf-8")

def _count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)

def require_manifest_list(issues, manifest, key):
    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return None
    value = surfaces.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(("INVALID_MANIFEST_SHAPE", key))
        return None
    return list(value)

def expect_subset(issues, label, actual, expected):
    if actual is None:
        return
    for marker in expected:
        if marker not in actual:
            issues.append(("MISSING_MANIFEST_SURFACE", f"{label}:{marker}"))

def collect_archive_support_issues(root: Path, archive_support):
    issues = []
    note = " or ".join(rel.as_posix() for rel in ARCHIVE_SUPPORT_RELS)
    if not any(resolve(root, rel).exists() for rel in ARCHIVE_SUPPORT_RELS):
        issues.append(("MISSING_REQUIRED_ARCHIVE_SUPPORT", note))
    if archive_support is not None and not any(rel.as_posix() in archive_support for rel in ARCHIVE_SUPPORT_RELS):
        issues.append(("MISSING_MANIFEST_ARCHIVE_SUPPORT", note))
    return issues

def collect_case_manifest_issues(issues, kconfig_cases, conf_manifest, confdata_manifest, genksyms_cases, genksyms_manifest):
    if not isinstance(kconfig_cases, dict):
        issues.append(("KCONFIG_CASE_PACKET_MISMATCH", "root"))
    else:
        if kconfig_cases.get("conf_cases") != EXPECTED_CONF_CASE_DETAILS:
            issues.append(("CONF_CASE_PACKET_MISMATCH", "conf_cases"))
        if kconfig_cases.get("confdata_cases") != EXPECTED_CONFDATA_CASE_DETAILS:
            issues.append(("CONFDATA_CASE_PACKET_MISMATCH", "confdata_cases"))
    if conf_manifest != EXPECTED_CONF_MANIFEST:
        issues.append(("CONF_MANIFEST_MISMATCH", "root"))
    if confdata_manifest != EXPECTED_CONFDATA_MANIFEST:
        issues.append(("CONFDATA_MANIFEST_MISMATCH", "root"))
    if genksyms_cases != EXPECTED_GENKSYMS_CASES:
        issues.append(("GENKSYMS_CASE_PACKET_MISMATCH", "cases"))
    if genksyms_manifest != EXPECTED_GENKSYMS_MANIFEST:
        issues.append(("GENKSYMS_MANIFEST_MISMATCH", "root"))

def collect_issues(root: Path):
    issues = []
    for rel in REQUIRED_FILES:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues
    closure_text = resolve(root, PHASE2_CLOSURE_REL).read_text(encoding="utf-8")
    workflow_text = resolve(root, WORKFLOW_REL).read_text(encoding="utf-8")
    makefile_text = resolve(root, MAKEFILE_REL).read_text(encoding="utf-8")
    manifest = json.loads(resolve(root, MANIFEST_REL).read_text(encoding="utf-8"))
    kconfig_cases = json.loads(resolve(root, KCONFIG_CASES_REL).read_text(encoding="utf-8"))
    conf_manifest = json.loads(resolve(root, CONF_MANIFEST_REL).read_text(encoding="utf-8"))
    confdata_manifest = json.loads(resolve(root, CONFDATA_MANIFEST_REL).read_text(encoding="utf-8"))
    genksyms_cases = json.loads(resolve(root, GENKSYMS_CASES_REL).read_text(encoding="utf-8"))
    genksyms_manifest = json.loads(resolve(root, GENKSYMS_MANIFEST_REL).read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues
    for marker in REQUIRED_CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))
    for marker in REQUIRED_WORKFLOW_LINES:
        count = _count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))
    for marker in REQUIRED_MAKEFILE_LINES:
        count = _count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))
    if manifest.get("repo_reality_gaps") != []:
        issues.append(("UNEXPECTED_MANIFEST_GAPS", repr(manifest.get("repo_reality_gaps"))))
    expect_subset(issues, "review_surfaces", require_manifest_list(issues, manifest, "review_surfaces"), EXPECTED_MANIFEST_REVIEW_SURFACES)
    expect_subset(issues, "closure_notes", require_manifest_list(issues, manifest, "closure_notes"), EXPECTED_MANIFEST_CLOSURE_NOTES)
    expect_subset(issues, "validators", require_manifest_list(issues, manifest, "validators"), EXPECTED_MANIFEST_VALIDATORS)
    expect_subset(issues, "checkers", require_manifest_list(issues, manifest, "checkers"), EXPECTED_MANIFEST_CHECKERS)
    expect_subset(issues, "bootstrap_helpers", require_manifest_list(issues, manifest, "bootstrap_helpers"), EXPECTED_MANIFEST_BOOTSTRAP_HELPERS)
    archive_support = require_manifest_list(issues, manifest, "archive_support")
    expect_subset(issues, "archive_support", archive_support, EXPECTED_MANIFEST_ARCHIVE_SUPPORT)
    issues.extend(collect_archive_support_issues(root, archive_support))
    expect_subset(issues, "bridge_helpers", require_manifest_list(issues, manifest, "bridge_helpers"), EXPECTED_MANIFEST_BRIDGE_HELPERS)
    expect_subset(issues, "fixture_roster", require_manifest_list(issues, manifest, "fixture_roster"), EXPECTED_MANIFEST_FIXTURE_ROSTER)
    expect_subset(issues, "policy", require_manifest_list(issues, manifest, "policy"), EXPECTED_MANIFEST_POLICY)
    collect_case_manifest_issues(issues, kconfig_cases, conf_manifest, confdata_manifest, genksyms_cases, genksyms_manifest)
    return issues
"""

    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_matrix_selftest_") as tmp_dir:
        root = Path(tmp_dir)
        validator_path = root / VALIDATOR_REL
        validator_path.parent.mkdir(parents=True, exist_ok=True)
        validator_path.write_text(fake_validator, encoding="utf-8")
        module = load_validator(root)
        module.build_self_test_root(root)
        checks_run += run_matrix(module, lambda temp_root: seed_materialized_root(module, temp_root, root))

        missing_validator_root = root / "missing-validator-root"
        missing_validator_root.mkdir()
        try:
            load_validator(missing_validator_root)
        except SystemExit as exc:
            assert "unable to load closure validator" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing validator root did not abort")

    print("PHASE2_CLOSURE_MATRIX_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_MATRIX_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the full closure-marker, workflow-line, Makefile-line, manifest-shape, and required-file matrix against the Phase 2 closure validator."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    repo_root = args.root.resolve()
    module = load_validator(repo_root)
    checks_run = run_matrix(module, lambda temp_root: seed_materialized_root(module, temp_root, repo_root))
    print("PHASE2_CLOSURE_MATRIX=pass")
    print(f"PHASE2_CLOSURE_MATRIX_CASE_COUNT={checks_run}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
