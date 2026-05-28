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

PRELUDE_REL_ATTRS = (
    "WORKFLOW_REL",
    "MAKEFILE_REL",
    "PHASE2_CLOSURE_REL",
    "PHASE2_BOOTSTRAP_NOTES_REL",
    "PHASE2_VALIDATE_REL",
    "PHASE2_CLOSURE_VALIDATE_REL",
    "PHASE2_TOOL_MANIFEST_REL",
    "PHASE2_ARTIFACT_TOOLS_MANIFEST_REL",
    "PHASE2_CROSS_TARGETS_REL",
    "GENKSYMS_MANIFEST_REL",
    "GENKSYMS_CASES_REL",
)


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


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def path_attr(module, attr_name: str) -> Path | None:
    value = getattr(module, attr_name, None)
    return value if isinstance(value, Path) else None


def preflight_required_rels(module) -> tuple[Path, ...]:
    rels = [VALIDATOR_REL]
    for attr_name in PRELUDE_REL_ATTRS:
        rel = path_attr(module, attr_name)
        if rel is not None:
            rels.append(rel)
    return tuple(dict.fromkeys(rels))


def manifest_paths(values: list[str]) -> list[str]:
    return [value for value in values if not value.startswith("make -C ")]


def collect_manifest_surface_expectations(
    module, manifest_path: Path
) -> list[tuple[str, tuple[str, ...]]]:
    payload = load_json(manifest_path)
    if not isinstance(payload, dict):
        raise AssertionError("manifest root must stay a dict in the seeded baseline")
    surfaces = payload.get("present_surfaces")
    if not isinstance(surfaces, dict):
        raise AssertionError(
            "manifest present_surfaces must stay a dict in the seeded baseline"
        )

    if hasattr(module, "MANIFEST_SURFACE_KEYS"):
        keys = list(getattr(module, "MANIFEST_SURFACE_KEYS"))
    else:
        keys = list(surfaces.keys())

    expectations: list[tuple[str, tuple[str, ...]]] = []
    for key in keys:
        value = surfaces.get(key)
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise AssertionError(
                f"manifest surface must stay a list[str] in the seeded baseline: {key}"
            )
        expectations.append((key, tuple(value)))
    return expectations


def collect_seed_rels(module, source_root: Path) -> tuple[Path, ...]:
    rels: dict[Path, None] = {rel: None for rel in preflight_required_rels(module)}

    manifest_rel = path_attr(module, "PHASE2_TOOL_MANIFEST_REL")
    if manifest_rel is not None:
        manifest_path = source_root / manifest_rel
        if manifest_path.exists():
            for _, values in collect_manifest_surface_expectations(module, manifest_path):
                for value in manifest_paths(list(values)):
                    rels[Path(value)] = None

    genksyms_manifest_rel = path_attr(module, "GENKSYMS_MANIFEST_REL")
    if genksyms_manifest_rel is not None:
        manifest_path = source_root / genksyms_manifest_rel
        if manifest_path.exists():
            genksyms_manifest = load_json(manifest_path)
            if not isinstance(genksyms_manifest, dict):
                raise AssertionError(
                    "genksyms manifest must stay a dict in the seeded baseline"
                )
            fixture_fn = getattr(module, "expected_genksyms_fixture_paths", None)
            proof_fn = getattr(module, "expected_genksyms_proof_paths", None)
            if callable(fixture_fn):
                for value in fixture_fn(genksyms_manifest):
                    rels[Path(value)] = None
            if callable(proof_fn):
                for value in proof_fn(genksyms_manifest):
                    rels[Path(value)] = None

    return tuple(sorted(rels.keys(), key=lambda rel: rel.as_posix()))


def seed_materialized_root(module, root: Path, source_root: Path) -> None:
    for rel in collect_seed_rels(module, source_root):
        source_path = source_root / rel
        if not source_path.exists():
            raise AssertionError(f"source path missing: {source_path}")
        destination_path = root / rel
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, destination_path)


def assert_issue(module, root: Path, expected: tuple[str, str]) -> None:
    issues = module.collect_issues(root)
    if expected not in issues:
        raise AssertionError(f"missing expected issue {expected!r}; saw {issues!r}")


def run_matrix(module, seed_root) -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_matrix_") as tmp_dir:
        root = Path(tmp_dir)
        seed_root(root)
        if module.collect_issues(root) != []:
            raise AssertionError("expected clean baseline self-test root")
        checks_run += 1

        for marker in getattr(module, "REQUIRED_CLOSURE_MARKERS", ()):
            seed_root(root)
            path = module.resolve(root, module.PHASE2_CLOSURE_REL)
            path.write_text(
                replace_once(path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert_issue(module, root, ("MISSING_CLOSURE_MARKER", marker))
            checks_run += 1

        for marker in getattr(module, "REQUIRED_WORKFLOW_LINES", ()):
            seed_root(root)
            path = module.resolve(root, module.WORKFLOW_REL)
            path.write_text(
                replace_exact_line(
                    path.read_text(encoding="utf-8"),
                    marker,
                    "run: python3 scripts/zigux/other.py",
                ),
                encoding="utf-8",
            )
            assert_issue(module, root, ("MISSING_WORKFLOW_LINE", marker))
            checks_run += 1

            seed_root(root)
            path = module.resolve(root, module.WORKFLOW_REL)
            path.write_text(
                duplicate_exact_line(path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert_issue(module, root, ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2"))
            checks_run += 1

        for marker in getattr(module, "REQUIRED_MAKEFILE_LINES", ()):
            seed_root(root)
            path = module.resolve(root, module.MAKEFILE_REL)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "# removed"),
                encoding="utf-8",
            )
            assert_issue(module, root, ("MISSING_MAKEFILE_LINE", marker))
            checks_run += 1

            seed_root(root)
            path = module.resolve(root, module.MAKEFILE_REL)
            path.write_text(
                duplicate_exact_line(path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert_issue(module, root, ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2"))
            checks_run += 1

        seed_root(root)
        manifest_path = module.resolve(root, module.PHASE2_TOOL_MANIFEST_REL)
        payload = load_json(manifest_path)
        payload["repo_reality_gaps"] = ["drifted-gap"]
        write_json(manifest_path, payload)
        assert_issue(module, root, ("UNEXPECTED_MANIFEST_GAPS", "['drifted-gap']"))
        checks_run += 1

        seed_root(root)
        manifest_path = module.resolve(root, module.PHASE2_TOOL_MANIFEST_REL)
        payload = load_json(manifest_path)
        del payload["repo_reality_gaps"]
        write_json(manifest_path, payload)
        assert_issue(module, root, ("UNEXPECTED_MANIFEST_GAPS", "None"))
        checks_run += 1

        seed_root(root)
        manifest_path = module.resolve(root, module.PHASE2_TOOL_MANIFEST_REL)
        payload = load_json(manifest_path)
        payload["repo_reality_gaps"] = {}
        write_json(manifest_path, payload)
        assert_issue(module, root, ("UNEXPECTED_MANIFEST_GAPS", "{}"))
        checks_run += 1

        seed_root(root)
        manifest_path = module.resolve(root, module.PHASE2_TOOL_MANIFEST_REL)
        write_json(manifest_path, [])
        assert_issue(module, root, ("INVALID_MANIFEST_SHAPE", "root"))
        checks_run += 1

        seed_root(root)
        manifest_path = module.resolve(root, module.PHASE2_TOOL_MANIFEST_REL)
        payload = load_json(manifest_path)
        payload["present_surfaces"] = []
        write_json(manifest_path, payload)
        assert_issue(module, root, ("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        checks_run += 1

        seed_root(root)
        manifest_path = module.resolve(root, module.PHASE2_TOOL_MANIFEST_REL)
        for key, expected in collect_manifest_surface_expectations(module, manifest_path):
            seed_root(root)
            manifest_path = module.resolve(root, module.PHASE2_TOOL_MANIFEST_REL)
            payload = load_json(manifest_path)
            del payload["present_surfaces"][key]
            write_json(manifest_path, payload)
            assert_issue(module, root, ("INVALID_MANIFEST_SHAPE", key))
            checks_run += 1

            seed_root(root)
            manifest_path = module.resolve(root, module.PHASE2_TOOL_MANIFEST_REL)
            payload = load_json(manifest_path)
            payload["present_surfaces"][key] = "drifted"
            write_json(manifest_path, payload)
            assert_issue(module, root, ("INVALID_MANIFEST_SHAPE", key))
            checks_run += 1

            seed_root(root)
            manifest_path = module.resolve(root, module.PHASE2_TOOL_MANIFEST_REL)
            payload = load_json(manifest_path)
            payload["present_surfaces"][key] = [123]
            write_json(manifest_path, payload)
            assert_issue(module, root, ("INVALID_MANIFEST_SHAPE", key))
            checks_run += 1

            for marker in expected:
                if marker.startswith("make -C "):
                    continue
                seed_root(root)
                marker_path = module.resolve(root, Path(marker))
                marker_path.unlink()
                if Path(marker) in preflight_required_rels(module):
                    assert_issue(module, root, ("MISSING_REQUIRED_FILE", marker))
                else:
                    assert_issue(module, root, ("MISSING_MANIFEST_SURFACE", f"{key}:{marker}"))
                checks_run += 1

        seed_root(root)
        genksyms_manifest_rel = path_attr(module, "GENKSYMS_MANIFEST_REL")
        if genksyms_manifest_rel is not None:
            genksyms_manifest_path = module.resolve(root, genksyms_manifest_rel)
            payload = load_json(genksyms_manifest_path)
            fixture_root = payload["fixture_root"]
            payload["process_output_packet"] = ["drifted_expected.json"]
            write_json(genksyms_manifest_path, payload)
            assert_issue(
                module,
                root,
                (
                    "MISSING_MANIFEST_SURFACE",
                    f"fixture_roster:{fixture_root}/drifted_expected.json",
                ),
            )
            assert_issue(
                module,
                root,
                (
                    "MISSING_CLOSURE_LINE",
                    "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET="
                    f"{fixture_root}/drifted_expected.json",
                ),
            )
            checks_run += 1

            seed_root(root)
            genksyms_manifest_path = module.resolve(root, genksyms_manifest_rel)
            payload = load_json(genksyms_manifest_path)
            payload["standalone_proof_packet"] = ["scripts/zigux/drifted-proof.zig"]
            write_json(genksyms_manifest_path, payload)
            assert_issue(
                module,
                root,
                (
                    "MISSING_MANIFEST_SURFACE",
                    "bridge_helpers:scripts/zigux/drifted-proof.zig",
                ),
            )
            checks_run += 1

        for rel in preflight_required_rels(module):
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
PHASE2_BOOTSTRAP_NOTES_REL = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
PHASE2_VALIDATE_REL = Path("scripts/zigux/validate-phase2.py")
PHASE2_CLOSURE_VALIDATE_REL = Path("scripts/zigux/validate-phase2-closure.py")
PHASE2_TOOL_MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
PHASE2_ARTIFACT_TOOLS_MANIFEST_REL = Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json")
PHASE2_CROSS_TARGETS_REL = Path("zigux/tests/fixtures/phase2_cross_targets.json")
GENKSYMS_MANIFEST_REL = Path("zigux/tests/fixtures/genksyms_bridge/manifest.json")
GENKSYMS_CASES_REL = Path("zigux/tests/fixtures/genksyms_bridge/cases.json")
MANIFEST_SURFACE_KEYS = (
    "review_surfaces",
    "closure_notes",
    "validators",
    "checkers",
    "bootstrap_helpers",
    "archive_support",
    "artifact_support",
    "bridge_helpers",
    "cross_route_support",
    "fixdep_support",
    "fixture_roster",
    "make_wrappers",
    "policy",
)
REQUIRED_CLOSURE_MARKERS = ("`marker-a`", "`marker-b`", "`bridge-proof`")
REQUIRED_WORKFLOW_LINES = ("run: alpha", "run: beta")
REQUIRED_MAKEFILE_LINES = ("phase2-a:", "phase2-b:")

def resolve(root: Path, rel: Path) -> Path:
    return root / rel

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def read_json(path: Path):
    return json.loads(read_text(path))

def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)

def require_string_list(issues, manifest, key):
    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return []
    value = present_surfaces.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(("INVALID_MANIFEST_SHAPE", key))
        return []
    return list(value)

def manifest_paths(values):
    return [value for value in values if not value.startswith("make -C ")]

def expected_genksyms_fixture_paths(genksyms_manifest):
    fixture_root = genksyms_manifest["fixture_root"]
    paths = [GENKSYMS_CASES_REL.as_posix(), GENKSYMS_MANIFEST_REL.as_posix()]
    for key in ("bridge_expected_packet", "help_packet", "process_output_packet"):
        for value in genksyms_manifest[key]:
            paths.append(f"{fixture_root}/{value}")
    return paths

def expected_genksyms_proof_paths(genksyms_manifest):
    return list(genksyms_manifest["standalone_proof_packet"])

def build_self_test_root(root: Path) -> None:
    process_output_packet = ["expected-a.json", "expected-b.json"]
    manifest = {
        "repo_reality_gaps": [],
        "present_surfaces": {
            "review_surfaces": ["Documentation/zigux/README.md"],
            "closure_notes": [
                PHASE2_CLOSURE_REL.as_posix(),
                PHASE2_BOOTSTRAP_NOTES_REL.as_posix(),
            ],
            "validators": [
                PHASE2_VALIDATE_REL.as_posix(),
                PHASE2_CLOSURE_VALIDATE_REL.as_posix(),
            ],
            "checkers": ["scripts/zigux/check-phase2-tool-manifest.py"],
            "bootstrap_helpers": ["scripts/zigux/install-zig.py"],
            "archive_support": ["third_party/README.md", "third_party/archive.tar.xz"],
            "artifact_support": [
                "scripts/zigux/artifact_diff.py",
                PHASE2_ARTIFACT_TOOLS_MANIFEST_REL.as_posix(),
            ],
            "bridge_helpers": [
                "scripts/zigux/genksyms.zig",
                "scripts/zigux/genksyms_proof.zig",
            ],
            "cross_route_support": [
                "scripts/zigux/check-phase2-cross.py",
                PHASE2_CROSS_TARGETS_REL.as_posix(),
            ],
            "fixdep_support": [
                "scripts/zigux/fixdep.zig",
                "scripts/zigux/check-fixdep-diff.py",
            ],
            "fixture_roster": [
                GENKSYMS_CASES_REL.as_posix(),
                GENKSYMS_MANIFEST_REL.as_posix(),
                "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json",
                "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
                "zigux/tests/fixtures/genksyms_bridge/expected-a.json",
                "zigux/tests/fixtures/genksyms_bridge/expected-b.json",
            ],
            "make_wrappers": ["zigux/Makefile", "make -C zigux phase2"],
            "policy": ["scripts/zigux/zig-toolchain-policy.json"],
        },
    }
    genksyms_manifest = {
        "fixture_root": "zigux/tests/fixtures/genksyms_bridge",
        "bridge_expected_packet": ["minimal_expected.json"],
        "help_packet": ["help_expected.json"],
        "process_output_packet": process_output_packet,
        "standalone_proof_packet": ["scripts/zigux/genksyms_proof.zig"],
    }

    write_text(
        resolve(root, PHASE2_CLOSURE_REL),
        (
            "# Closure\\n"
            "- `marker-a`\\n"
            "- `marker-b`\\n"
            "- `bridge-proof`\\n"
            "- `PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET="
            "zigux/tests/fixtures/genksyms_bridge/expected-a.json,"
            "zigux/tests/fixtures/genksyms_bridge/expected-b.json`\\n"
        ),
    )
    write_text(resolve(root, WORKFLOW_REL), "run: alpha\\nrun: beta\\n")
    write_text(resolve(root, MAKEFILE_REL), "phase2-a:\\nphase2-b:\\n")
    write_text(resolve(root, PHASE2_BOOTSTRAP_NOTES_REL), "notes\\n")
    write_text(resolve(root, PHASE2_VALIDATE_REL), "validate\\n")
    write_text(resolve(root, PHASE2_CLOSURE_VALIDATE_REL), "validate-closure\\n")
    write_text(
        resolve(root, PHASE2_TOOL_MANIFEST_REL),
        json.dumps(manifest, indent=2) + "\\n",
    )
    write_text(
        resolve(root, PHASE2_ARTIFACT_TOOLS_MANIFEST_REL),
        json.dumps({"artifact": True}, indent=2) + "\\n",
    )
    write_text(resolve(root, PHASE2_CROSS_TARGETS_REL), "[]\\n")
    write_text(
        resolve(root, GENKSYMS_MANIFEST_REL),
        json.dumps(genksyms_manifest, indent=2) + "\\n",
    )
    write_text(resolve(root, GENKSYMS_CASES_REL), "[]\\n")
    for rel in (
        "Documentation/zigux/README.md",
        "scripts/zigux/check-phase2-tool-manifest.py",
        "scripts/zigux/install-zig.py",
        "third_party/README.md",
        "third_party/archive.tar.xz",
        "scripts/zigux/artifact_diff.py",
        "scripts/zigux/genksyms.zig",
        "scripts/zigux/genksyms_proof.zig",
        "scripts/zigux/check-phase2-cross.py",
        "scripts/zigux/fixdep.zig",
        "scripts/zigux/check-fixdep-diff.py",
        "scripts/zigux/zig-toolchain-policy.json",
        "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json",
        "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
        "zigux/tests/fixtures/genksyms_bridge/expected-a.json",
        "zigux/tests/fixtures/genksyms_bridge/expected-b.json",
    ):
        write_text(resolve(root, Path(rel)), "present\\n")

def collect_issues(root: Path):
    issues = []
    for rel in (
        WORKFLOW_REL,
        MAKEFILE_REL,
        PHASE2_CLOSURE_REL,
        PHASE2_BOOTSTRAP_NOTES_REL,
        PHASE2_VALIDATE_REL,
        PHASE2_CLOSURE_VALIDATE_REL,
        PHASE2_TOOL_MANIFEST_REL,
        PHASE2_ARTIFACT_TOOLS_MANIFEST_REL,
        PHASE2_CROSS_TARGETS_REL,
        GENKSYMS_MANIFEST_REL,
        GENKSYMS_CASES_REL,
    ):
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    closure_text = read_text(resolve(root, PHASE2_CLOSURE_REL))
    workflow_text = read_text(resolve(root, WORKFLOW_REL))
    makefile_text = read_text(resolve(root, MAKEFILE_REL))
    manifest = read_json(resolve(root, PHASE2_TOOL_MANIFEST_REL))
    genksyms_manifest = read_json(resolve(root, GENKSYMS_MANIFEST_REL))

    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues
    if not isinstance(genksyms_manifest, dict):
        issues.append(("INVALID_GENKSYMS_MANIFEST_SHAPE", "root"))
        return issues

    if manifest.get("repo_reality_gaps") != []:
        issues.append(("UNEXPECTED_MANIFEST_GAPS", repr(manifest.get("repo_reality_gaps"))))

    manifest_surface_values = {}
    for key in MANIFEST_SURFACE_KEYS:
        manifest_surface_values[key] = require_string_list(issues, manifest, key)
    if issues:
        return issues

    for key, values in manifest_surface_values.items():
        for value in manifest_paths(values):
            if not resolve(root, Path(value)).exists():
                issues.append(("MISSING_MANIFEST_SURFACE", f"{key}:{value}"))

    fixture_roster = set(manifest_surface_values["fixture_roster"])
    bridge_helpers = set(manifest_surface_values["bridge_helpers"])
    for path in expected_genksyms_fixture_paths(genksyms_manifest):
        if path not in fixture_roster:
            issues.append(("MISSING_MANIFEST_SURFACE", f"fixture_roster:{path}"))
    for path in expected_genksyms_proof_paths(genksyms_manifest):
        if path not in bridge_helpers:
            issues.append(("MISSING_MANIFEST_SURFACE", f"bridge_helpers:{path}"))

    expected_line = (
        "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET="
        + ",".join(
            f"zigux/tests/fixtures/genksyms_bridge/{item}"
            for item in genksyms_manifest["process_output_packet"]
        )
    )
    if f"`{expected_line}`" not in closure_text:
        issues.append(("MISSING_CLOSURE_LINE", expected_line))

    for marker in REQUIRED_CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))
    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))
    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))
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
        checks_run += run_matrix(
            module, lambda temp_root: seed_materialized_root(module, temp_root, root)
        )

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
        description=(
            "Run the full closure-marker, workflow-line, Makefile-line, manifest-shape, "
            "and required-file matrix against the Phase 2 closure validator."
        )
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    repo_root = args.root.resolve()
    module = load_validator(repo_root)
    checks_run = run_matrix(
        module, lambda temp_root: seed_materialized_root(module, temp_root, repo_root)
    )
    print("PHASE2_CLOSURE_MATRIX=pass")
    print(f"PHASE2_CLOSURE_MATRIX_CASE_COUNT={checks_run}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
