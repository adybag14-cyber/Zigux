#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT_README = ROOT / "Documentation" / "zigux" / "README.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
KCONFIG_SELFTEST_ALIGNMENT = ROOT / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py"
TESTS_README_ALIGNMENT = ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"
TOOLCHAIN_PINNING = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pinning.py"
KBUILD_ROUTES = ROOT / "scripts" / "zigux" / "check-phase2-kbuild-routes.py"
CONF_BRIDGE = ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"
CONFDATA_BRIDGE = ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig"
CASES = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json"
CONF_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json"
CONFDATA_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "confdata_manifest.json"

DOCS_ROOT_README_MARKERS = (
    "`scripts/zigux/check-phase2-kconfig-readme-alignment.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tool-manifest-packets.py`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "the docs-root Phase 2 summary should also keep the current bootstrap-versus-cross verification split explicit",
)

REVIEW_CHECKLIST_MARKERS = (
    "`scripts/zigux/check-phase2-kconfig-readme-alignment.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`",
    "`scripts/zigux/check-kconfig-bridge.py`",
)

TESTS_README_MARKERS = (
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/cases.json`",
    "the current directly readable Phase 2 packet is the scripts-root kbuild and toolchain reminder set plus the live kconfig bridge helpers and their fixture roster",
)

SCRIPTS_README_MARKERS = (
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/cases.json`",
    "the manifest-backed kconfig fixture roster",
)

SURFACE_PATHS = (
    KCONFIG_SELFTEST_ALIGNMENT,
    TESTS_README_ALIGNMENT,
    TOOLCHAIN_PINNING,
    KBUILD_ROUTES,
    CONF_BRIDGE,
    CONFDATA_BRIDGE,
    CASES,
    CONF_MANIFEST,
    CONFDATA_MANIFEST,
)

EXPECTED_CONF_MANIFEST = {
    "tool": "scripts/zigux/kconfig/conf_bridge.zig",
    "status": "closed",
    "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
    "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "case_count": 16,
    "required_case": "helpnewconfig",
    "required_stdout_packet": "helpnewconfig_expected.json",
}

EXPECTED_CONFDATA_MANIFEST = {
    "tool": "scripts/zigux/kconfig/confdata_bridge.zig",
    "status": "closed",
    "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
    "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "case_count": 14,
    "required_case": "duplicate_malformed_quoted_assignment",
    "required_expected_packet": "duplicate_malformed_quoted_assignment_expected.json",
}

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(DOCS_ROOT_README_MARKERS)
    + len(REVIEW_CHECKLIST_MARKERS)
    + len(TESTS_README_MARKERS)
    + len(SCRIPTS_README_MARKERS)
    + len(SURFACE_PATHS)
    + 6
)


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def read_text(root: Path, path: Path) -> str:
    resolved = resolve_path(root, path)
    try:
        return resolved.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {resolved}") from exc


def write_text(root: Path, path: Path, content: str) -> None:
    resolved = resolve_path(root, path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(content, encoding="utf-8")


def load_json_object(root: Path, path: Path, *, label: str) -> dict[str, object]:
    resolved = resolve_path(root, path)
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {resolved}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{label}:invalid_json:{exc.msg}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"{label}:expected_object")
    return payload


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def validate_conf_manifest(payload: dict[str, object]) -> list[str]:
    issues: list[str] = []
    if payload.get("tool") != EXPECTED_CONF_MANIFEST["tool"]:
        issues.append(f"tool={payload.get('tool')!r}")
    if payload.get("status") != EXPECTED_CONF_MANIFEST["status"]:
        issues.append(f"status={payload.get('status')!r}")
    if payload.get("fixture_root") != EXPECTED_CONF_MANIFEST["fixture_root"]:
        issues.append(f"fixture_root={payload.get('fixture_root')!r}")
    if payload.get("fixture_case_source") != EXPECTED_CONF_MANIFEST["fixture_case_source"]:
        issues.append(f"fixture_case_source={payload.get('fixture_case_source')!r}")
    if payload.get("case_count") != EXPECTED_CONF_MANIFEST["case_count"]:
        issues.append(f"case_count={payload.get('case_count')!r}")

    cases = payload.get("cases")
    if not isinstance(cases, list):
        issues.append("cases=expected_list")
    elif EXPECTED_CONF_MANIFEST["required_case"] not in cases:
        issues.append(f"cases:missing:{EXPECTED_CONF_MANIFEST['required_case']}")

    stdout_packet = payload.get("stdout_packet")
    if not isinstance(stdout_packet, list):
        issues.append("stdout_packet=expected_list")
    elif EXPECTED_CONF_MANIFEST["required_stdout_packet"] not in stdout_packet:
        issues.append(f"stdout_packet:missing:{EXPECTED_CONF_MANIFEST['required_stdout_packet']}")

    return issues


def validate_confdata_manifest(payload: dict[str, object]) -> list[str]:
    issues: list[str] = []
    if payload.get("tool") != EXPECTED_CONFDATA_MANIFEST["tool"]:
        issues.append(f"tool={payload.get('tool')!r}")
    if payload.get("status") != EXPECTED_CONFDATA_MANIFEST["status"]:
        issues.append(f"status={payload.get('status')!r}")
    if payload.get("fixture_root") != EXPECTED_CONFDATA_MANIFEST["fixture_root"]:
        issues.append(f"fixture_root={payload.get('fixture_root')!r}")
    if payload.get("fixture_case_source") != EXPECTED_CONFDATA_MANIFEST["fixture_case_source"]:
        issues.append(f"fixture_case_source={payload.get('fixture_case_source')!r}")
    if payload.get("case_count") != EXPECTED_CONFDATA_MANIFEST["case_count"]:
        issues.append(f"case_count={payload.get('case_count')!r}")

    cases = payload.get("cases")
    if not isinstance(cases, list):
        issues.append("cases=expected_list")
    elif EXPECTED_CONFDATA_MANIFEST["required_case"] not in cases:
        issues.append(f"cases:missing:{EXPECTED_CONFDATA_MANIFEST['required_case']}")

    expected_packet = payload.get("expected_packet")
    if not isinstance(expected_packet, list):
        issues.append("expected_packet=expected_list")
    elif EXPECTED_CONFDATA_MANIFEST["required_expected_packet"] not in expected_packet:
        issues.append(
            f"expected_packet:missing:{EXPECTED_CONFDATA_MANIFEST['required_expected_packet']}"
        )

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    docs_root_readme_text = read_text(root, DOCS_ROOT_README)
    review_checklist_text = read_text(root, REVIEW_CHECKLIST)
    tests_readme_text = read_text(root, TESTS_README)
    scripts_readme_text = read_text(root, SCRIPTS_README)

    issues.extend(
        collect_missing_markers(
            docs_root_readme_text,
            DOCS_ROOT_README_MARKERS,
            "MISSING_DOCS_ROOT_README_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            review_checklist_text,
            REVIEW_CHECKLIST_MARKERS,
            "MISSING_REVIEW_CHECKLIST_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            tests_readme_text,
            TESTS_README_MARKERS,
            "MISSING_TESTS_README_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            scripts_readme_text,
            SCRIPTS_README_MARKERS,
            "MISSING_SCRIPTS_README_MARKERS",
        )
    )

    for path in SURFACE_PATHS:
        if not resolve_path(root, path).exists():
            issues.append(("MISSING_SURFACE_PATHS", path.relative_to(ROOT).as_posix()))

    conf_manifest_path = resolve_path(root, CONF_MANIFEST)
    if conf_manifest_path.exists():
        for item in validate_conf_manifest(load_json_object(root, CONF_MANIFEST, label="conf_manifest")):
            issues.append(("INVALID_CONF_MANIFEST", item))

    confdata_manifest_path = resolve_path(root, CONFDATA_MANIFEST)
    if confdata_manifest_path.exists():
        for item in validate_confdata_manifest(
            load_json_object(root, CONFDATA_MANIFEST, label="confdata_manifest")
        ):
            issues.append(("INVALID_CONFDATA_MANIFEST", item))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_KCONFIG_README_ALIGNMENT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def build_self_test_root(root: Path) -> None:
    for path, markers in (
        (DOCS_ROOT_README, DOCS_ROOT_README_MARKERS),
        (REVIEW_CHECKLIST, REVIEW_CHECKLIST_MARKERS),
        (TESTS_README, TESTS_README_MARKERS),
        (SCRIPTS_README, SCRIPTS_README_MARKERS),
    ):
        write_text(root, path, "\n".join(markers) + "\n")

    for path in (
        KCONFIG_SELFTEST_ALIGNMENT,
        TESTS_README_ALIGNMENT,
        TOOLCHAIN_PINNING,
        KBUILD_ROUTES,
        CONF_BRIDGE,
        CONFDATA_BRIDGE,
    ):
        write_text(root, path, "# present\n" if path.suffix == ".py" else "// present\n")

    write_text(root, CASES, "[]\n")
    write_text(
        root,
        CONF_MANIFEST,
        json.dumps(
            {
                "tool": EXPECTED_CONF_MANIFEST["tool"],
                "status": EXPECTED_CONF_MANIFEST["status"],
                "fixture_root": EXPECTED_CONF_MANIFEST["fixture_root"],
                "fixture_case_source": EXPECTED_CONF_MANIFEST["fixture_case_source"],
                "case_count": EXPECTED_CONF_MANIFEST["case_count"],
                "cases": ["helpnewconfig"],
                "stdout_packet": ["helpnewconfig_expected.json"],
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root,
        CONFDATA_MANIFEST,
        json.dumps(
            {
                "tool": EXPECTED_CONFDATA_MANIFEST["tool"],
                "status": EXPECTED_CONFDATA_MANIFEST["status"],
                "fixture_root": EXPECTED_CONFDATA_MANIFEST["fixture_root"],
                "fixture_case_source": EXPECTED_CONFDATA_MANIFEST["fixture_case_source"],
                "case_count": EXPECTED_CONFDATA_MANIFEST["case_count"],
                "cases": ["duplicate_malformed_quoted_assignment"],
                "expected_packet": ["duplicate_malformed_quoted_assignment_expected.json"],
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_kconfig_readme_alignment_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for path, markers, code in (
            (DOCS_ROOT_README, DOCS_ROOT_README_MARKERS, "MISSING_DOCS_ROOT_README_MARKERS"),
            (REVIEW_CHECKLIST, REVIEW_CHECKLIST_MARKERS, "MISSING_REVIEW_CHECKLIST_MARKERS"),
            (TESTS_README, TESTS_README_MARKERS, "MISSING_TESTS_README_MARKERS"),
            (SCRIPTS_README, SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKERS"),
        ):
            for marker in markers:
                build_self_test_root(root)
                resolved = resolve_path(root, path)
                resolved.write_text(replace_once(resolved.read_text(encoding="utf-8"), marker), encoding="utf-8")
                assert (code, marker) in collect_issues(root)
                checks_run += 1

        for path in SURFACE_PATHS:
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            assert ("MISSING_SURFACE_PATHS", path.relative_to(ROOT).as_posix()) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        write_text(root, CONF_MANIFEST, json.dumps({"tool": "wrong"}, indent=2) + "\n")
        assert any(code == "INVALID_CONF_MANIFEST" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        write_text(root, CONFDATA_MANIFEST, json.dumps({"tool": "wrong"}, indent=2) + "\n")
        assert any(code == "INVALID_CONFDATA_MANIFEST" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        write_text(root, CONF_MANIFEST, "[]\n")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert str(exc) == "conf_manifest:expected_object"
            checks_run += 1
        else:
            raise AssertionError("non-object conf manifest did not abort")

        build_self_test_root(root)
        write_text(root, CONFDATA_MANIFEST, "{\n")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert str(exc).startswith("confdata_manifest:invalid_json:")
            checks_run += 1
        else:
            raise AssertionError("invalid confdata manifest did not abort")

        build_self_test_root(root)
        resolve_path(root, DOCS_ROOT_README).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing docs readme did not abort")

        build_self_test_root(root)
        resolve_path(root, SCRIPTS_README).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing scripts readme did not abort")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_KCONFIG_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_README_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Keep the current Phase 2 docs-root, checklist, tests-root, and scripts-root "
            "kconfig reviewer surfaces aligned with the live bridge packet."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_KCONFIG_README_ALIGNMENT=pass")
    print(f"PHASE2_KCONFIG_README_ALIGNMENT_DOC_MARKER_COUNT={len(DOCS_ROOT_README_MARKERS)}")
    print(f"PHASE2_KCONFIG_README_ALIGNMENT_REVIEW_MARKER_COUNT={len(REVIEW_CHECKLIST_MARKERS)}")
    print(f"PHASE2_KCONFIG_README_ALIGNMENT_TESTS_MARKER_COUNT={len(TESTS_README_MARKERS)}")
    print(f"PHASE2_KCONFIG_README_ALIGNMENT_SCRIPTS_MARKER_COUNT={len(SCRIPTS_README_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
