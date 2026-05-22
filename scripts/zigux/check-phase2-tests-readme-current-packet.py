#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
THIRD_PARTY_README = ROOT / "third_party" / "README.md"
MAKEFILE = ROOT / "zigux" / "Makefile"
TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
ARTIFACT_TOOLS_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_artifact_tools_manifest.json"
CROSS_TARGETS = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

TESTS_README_MARKERS = (
    "Keep the current direct-readback Phase 2 kconfig, genksyms, and fixdep packet:",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`zigux/Makefile`",
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`",
    "current `master` now directly materializes `third_party/README.md`",
    "keep the repo-local pinned archive packet explicit through `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "current `master` now directly materializes `scripts/zigux/install-zig.py`",
    "current `master` also directly materializes `scripts/zigux/check-genksyms-bridge.py`",
    "current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`",
    "keep the fixture-backed tool-manifest and artifact-tools-manifest guards",
)

BOOTSTRAP_NOTES_MARKERS = (
    "`third_party/README.md` is directly readable on current `master`",
    "`scripts/zigux/install-zig.py` is directly readable on current `master`",
    "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit",
    "`scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, and the restored `zigux/tests/fixtures/genksyms_bridge/` expected plus process-output fixture roster keep the bounded genksyms bridge helper packet explicit",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, and `zigux/tests/fixtures/fixdep/cases.json` keep the returned fixdep governance, parity, helper, and fixture packet explicit",
    "The rematerialized make-wrapper packet is directly readable on current `master` through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`",
)

SCRIPTS_README_MARKERS = (
    "Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`",
    "keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
)

THIRD_PARTY_MARKERS = (
    "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "- sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`",
    "community-mirrors.txt",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py` and `scripts/zigux/check-lane05-local-archive-readme.py` are the shipped reminder guards for that local-first archive path.",
)

MAKEFILE_LINES = (
    ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig:",
    "phase2-cross:",
    "phase2-genksyms:",
    "phase2-fixdep:",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
)

EXPECTED_TOOL_MANIFEST_SCOPE = (
    "current directly readable scripts-root toolchain, local-archive, installer, direct cross-route, "
    "kbuild, kconfig, genksyms, make-wrapper, fixdep, and tranche-closure reminder packet"
)
EXPECTED_ARTIFACT_SCOPE = "artifact-diff support for fixture-backed scripts/zigux validation"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in {path}: {exc}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    write_text(path, json.dumps(payload, indent=2) + "\n")


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(collect_missing_markers(read_text(resolve_path(root, TESTS_README)), TESTS_README_MARKERS, "MISSING_TESTS_MARKERS"))
    issues.extend(collect_missing_markers(read_text(resolve_path(root, BOOTSTRAP_NOTES)), BOOTSTRAP_NOTES_MARKERS, "MISSING_BOOTSTRAP_MARKERS"))
    issues.extend(collect_missing_markers(read_text(resolve_path(root, SCRIPTS_README)), SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_MARKERS"))
    issues.extend(collect_missing_markers(read_text(resolve_path(root, THIRD_PARTY_README)), THIRD_PARTY_MARKERS, "MISSING_THIRD_PARTY_MARKERS"))

    makefile_text = read_text(resolve_path(root, MAKEFILE))
    issues.extend(collect_missing_markers(makefile_text, MAKEFILE_LINES, "MISSING_MAKEFILE_LINES"))

    tool_manifest = read_json(resolve_path(root, TOOL_MANIFEST))
    artifact_manifest = read_json(resolve_path(root, ARTIFACT_TOOLS_MANIFEST))
    cross_targets = read_json(resolve_path(root, CROSS_TARGETS))

    if tool_manifest.get("scope") != EXPECTED_TOOL_MANIFEST_SCOPE:
        issues.append(("BAD_TOOL_MANIFEST_SCOPE", repr(tool_manifest.get("scope"))))
    if tool_manifest.get("status") != "active":
        issues.append(("BAD_TOOL_MANIFEST_STATUS", repr(tool_manifest.get("status"))))

    if artifact_manifest.get("scope") != EXPECTED_ARTIFACT_SCOPE:
        issues.append(("BAD_ARTIFACT_SCOPE", repr(artifact_manifest.get("scope"))))
    if artifact_manifest.get("tooling", {}).get("supported_modes") != ["text", "json", "bytes"]:
        issues.append(("BAD_ARTIFACT_SUPPORTED_MODES", repr(artifact_manifest.get("tooling", {}).get("supported_modes"))))
    if artifact_manifest.get("tooling", {}).get("consumers") != [
        "scripts/zigux/check-kconfig-bridge.py",
        "scripts/zigux/check-fixdep-diff.py",
    ]:
        issues.append(("BAD_ARTIFACT_CONSUMERS", repr(artifact_manifest.get("tooling", {}).get("consumers"))))

    if cross_targets.get("route") != "make -C zigux phase2-cross":
        issues.append(("BAD_CROSS_ROUTE", repr(cross_targets.get("route"))))
    if cross_targets.get("archive_target_scope") != ["x86_64-linux"]:
        issues.append(("BAD_CROSS_ARCHIVE_SCOPE", repr(cross_targets.get("archive_target_scope"))))
    expected_targets = [
        {
            "target": "x86_64-linux",
            "review_status": "pinned bootstrap archive",
            "validation_mode": "archive_required",
            "route": "make -C zigux phase2-cross",
        },
        {
            "target": "aarch64-linux",
            "review_status": "route contract only",
            "validation_mode": "route_contract_only",
            "route": "make -C zigux phase2-cross",
        },
    ]
    if cross_targets.get("cross_targets") != expected_targets:
        issues.append(("BAD_CROSS_TARGETS", repr(cross_targets.get("cross_targets"))))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TESTS_README_CURRENT_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, BOOTSTRAP_NOTES), "\n".join(BOOTSTRAP_NOTES_MARKERS) + "\n")
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, THIRD_PARTY_README), "\n".join(THIRD_PARTY_MARKERS) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    write_json(resolve_path(root, TOOL_MANIFEST), {"scope": EXPECTED_TOOL_MANIFEST_SCOPE, "status": "active"})
    write_json(
        resolve_path(root, ARTIFACT_TOOLS_MANIFEST),
        {
            "scope": EXPECTED_ARTIFACT_SCOPE,
            "tooling": {
                "supported_modes": ["text", "json", "bytes"],
                "consumers": [
                    "scripts/zigux/check-kconfig-bridge.py",
                    "scripts/zigux/check-fixdep-diff.py",
                ],
            },
        },
    )
    write_json(
        resolve_path(root, CROSS_TARGETS),
        {
            "route": "make -C zigux phase2-cross",
            "archive_target_scope": ["x86_64-linux"],
            "cross_targets": [
                {
                    "target": "x86_64-linux",
                    "review_status": "pinned bootstrap archive",
                    "validation_mode": "archive_required",
                    "route": "make -C zigux phase2-cross",
                },
                {
                    "target": "aarch64-linux",
                    "review_status": "route contract only",
                    "validation_mode": "route_contract_only",
                    "route": "make -C zigux phase2-cross",
                },
            ],
        },
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_tests_readme_current_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        path = resolve_path(root, TESTS_README)
        path.write_text(path.read_text(encoding="utf-8").replace(TESTS_README_MARKERS[0], "", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_TESTS_MARKERS", TESTS_README_MARKERS[0]) in issues
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, BOOTSTRAP_NOTES)
        path.write_text(path.read_text(encoding="utf-8").replace(BOOTSTRAP_NOTES_MARKERS[0], "", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_BOOTSTRAP_MARKERS", BOOTSTRAP_NOTES_MARKERS[0]) in issues
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, TOOL_MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["scope"] = "wrong"
        write_json(path, payload)
        issues = collect_issues(root)
        assert any(code == "BAD_TOOL_MANIFEST_SCOPE" for code, _ in issues)
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, CROSS_TARGETS)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["route"] = "wrong"
        write_json(path, payload)
        issues = collect_issues(root)
        assert any(code == "BAD_CROSS_ROUTE" for code, _ in issues)
        checks_run += 1

    print("PHASE2_TESTS_README_CURRENT_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TESTS_README_CURRENT_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the live Phase 2 tests-root current packet aligned to the returned current-master reminder surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a passing sample root and exit")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TESTS_README_CURRENT_PACKET=pass")
    print(f"PHASE2_TESTS_README_CURRENT_PACKET_TESTS_MARKER_COUNT={len(TESTS_README_MARKERS)}")
    print(f"PHASE2_TESTS_README_CURRENT_PACKET_BOOTSTRAP_MARKER_COUNT={len(BOOTSTRAP_NOTES_MARKERS)}")
    print(f"PHASE2_TESTS_README_CURRENT_PACKET_SCRIPTS_MARKER_COUNT={len(SCRIPTS_README_MARKERS)}")
    print(f"PHASE2_TESTS_README_CURRENT_PACKET_THIRD_PARTY_MARKER_COUNT={len(THIRD_PARTY_MARKERS)}")
    print(f"PHASE2_TESTS_README_CURRENT_PACKET_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    print("PHASE2_TESTS_README_CURRENT_PACKET_STRUCTURED_CHECK_COUNT=8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
