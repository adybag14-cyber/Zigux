#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOCS_README = ROOT / "Documentation" / "zigux" / "README.md"
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
THIRD_PARTY_README = ROOT / "third_party" / "README.md"
MAKEFILE = ROOT / "zigux" / "Makefile"
TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
ARTIFACT_TOOLS_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_artifact_tools_manifest.json"
CROSS_TARGETS = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"

DOCS_README_MARKERS = (
    "`scripts/zigux/check-phase2-tool-manifest.py` and `scripts/zigux/check-phase2-artifact-tools-manifest.py` keep the fixture-backed Phase 2 manifest packet explicit from the docs root beside the shipped reminder and make-wrapper surfaces.",
    "`third_party/README.md`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py` are directly readable on current `master` again, so keep the repo-local pinned archive contract",
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again",
    "`python3 scripts/zigux/validate-phase2.py`, `python3 scripts/zigux/validate-phase2-closure.py`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-validate`, and `make -C zigux phase2` replay the bounded current Phase 2 closure-side, bounded genksyms bridge, and make-wrapper packet without widening it back into older missing-route assumptions.",
)

PHASE2_NOTES_MARKERS = (
    "`third_party/README.md` is directly readable on current `master` and keeps the repo-local pinned archive filename, digest, size, duplicate-copy boundary, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux` replay contract explicit beside the policy-driven toolchain packet.",
    "`scripts/zigux/install-zig.py` is directly readable on current `master` and keeps the pinned-channel archive download, SHA-256 verification, and install-root replay path explicit beside the reminder guards.",
    "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit through the pinned `x86_64-linux` `archive_required` lane plus the `aarch64-linux` `route_contract_only` lane, so toolchain follow-through should treat the returned cross packet as present evidence instead of a repo-reality gap.",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, and `zigux/tests/fixtures/fixdep/cases.json` keep the returned fixdep governance, parity, helper, and fixture packet explicit beside the reminder guards, and `make -C zigux phase2-fixdep` keeps its wrapper route inside the same returned make-wrapper packet.",
    "The rematerialized make-wrapper packet is directly readable on current `master` through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`, so keep those routes in the present packet instead of the repo-reality-gap list.",
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, or returned fixdep packet on current `master`.",
)

REVIEW_CHECKLIST_MARKERS = (
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/README.md`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-fixdep`",
    "current directly readable Phase 2 local-first archive, toolchain, installer, direct cross-route, kbuild, kconfig bridge, docs-shared-reminder, tool-manifest, artifact-support, fixdep, genksyms-bridge, and required-make-route packet",
    "current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet",
)

TESTS_README_MARKERS = (
    "current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py`, so keep that returned repo-local pinned-archive workflow, bootstrap guard, and archive README contract explicit here instead of leaving them outside the tests-root reminder",
    "current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep that returned installer, direct cross-route, and cross-target fixture packet explicit here instead of leaving it in the historical-gap bucket",
    "current `master` also directly materializes `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned checker, bridge helper, wrapper, and fixture roster explicit here instead of leaving it outside the tests-root reminder",
    "current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`, so keep that returned fixdep governance, parity, helper, wrapper, and fixture packet explicit here instead of leaving it outside the tests-root reminder",
)

SCRIPTS_README_MARKERS = (
    "Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet, `conf_bridge` and `confdata_bridge` helper surfaces, the restored closure-side validator packet, the manifest-backed kconfig fixture roster, the shipped make-wrapper packet, and the surviving Phase 2 alignment guards instead of replaying older missing-route assumptions inside that now-rematerialized toolchain packet",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`, so keep those installer and direct cross-route surfaces explicit beside the shipped toolchain and kbuild reminder packet instead of leaving them in repo-reality-gap wording",
    "keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
)

THIRD_PARTY_MARKERS = (
    "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "- sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`",
    "- If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL.",
    "- `scripts/zigux/check-lane05-local-first-archive-workflow.py` and `scripts/zigux/check-lane05-local-archive-readme.py` are the shipped reminder guards for that local-first archive path.",
)

THIRD_PARTY_EXACT_COUNT_MARKERS = (
    "- If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL.",
    "- `scripts/zigux/check-lane05-local-first-archive-workflow.py` and `scripts/zigux/check-lane05-local-archive-readme.py` are the shipped reminder guards for that local-first archive path.",
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
EXPECTED_ARTIFACT_SUPPORTED_MODES = ("text", "json", "bytes")
EXPECTED_CROSS_TARGETS = (
    ("x86_64-linux", "archive_required"),
    ("aarch64-linux", "route_contract_only"),
)
EXPECTED_REQUIRED_MAKE_ROUTES = ("phase2-toolchain", "phase2-validate", "phase2-cross")
EXPECTED_CHANNEL = "0.17.0-dev.87+9b177a7d2"
EXPECTED_ARCHIVE_SHA = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
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


def collect_missing(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_exact_count(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append((code, f"{count}::{marker}"))
    return issues


def collect_structured_issues(tool_manifest: object, artifact_manifest: object, cross_targets: object, toolchain_policy: object) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    if not isinstance(tool_manifest, dict):
        return [("tool-manifest-type", type(tool_manifest).__name__)]
    if tool_manifest.get("scope") != EXPECTED_TOOL_MANIFEST_SCOPE:
        issues.append(("tool-manifest-scope", str(tool_manifest.get("scope"))))

    present_surfaces = tool_manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("tool-manifest-present-surfaces", type(present_surfaces).__name__))
    else:
        make_wrappers = present_surfaces.get("make_wrappers")
        if not isinstance(make_wrappers, list):
            issues.append(("tool-manifest-make-wrappers", type(make_wrappers).__name__))
        else:
            for route in ("make -C zigux phase2-toolchain", "make -C zigux phase2-cross", "make -C zigux phase2-fixdep"):
                if route not in make_wrappers:
                    issues.append(("tool-manifest-make-route", route))
        checkers = present_surfaces.get("checkers")
        if not isinstance(checkers, list):
            issues.append(("tool-manifest-checkers", type(checkers).__name__))
        else:
            for checker in (
                "scripts/zigux/check-phase2-tool-manifest.py",
                "scripts/zigux/check-phase2-artifact-tools-manifest.py",
                "scripts/zigux/check-phase2-fixdep-gate.py",
            ):
                if checker not in checkers:
                    issues.append(("tool-manifest-checker", checker))

    if not isinstance(artifact_manifest, dict):
        issues.append(("artifact-manifest-type", type(artifact_manifest).__name__))
    else:
        tooling = artifact_manifest.get("tooling")
        if not isinstance(tooling, dict):
            issues.append(("artifact-manifest-tooling", type(tooling).__name__))
        else:
            supported_modes = tooling.get("supported_modes")
            if supported_modes != list(EXPECTED_ARTIFACT_SUPPORTED_MODES):
                issues.append(("artifact-manifest-supported-modes", repr(supported_modes)))
            checkers = tooling.get("checkers")
            if checkers != ["scripts/zigux/check-phase2-artifact-tools-manifest.py"]:
                issues.append(("artifact-manifest-checkers", repr(checkers)))

    if not isinstance(cross_targets, dict):
        issues.append(("cross-targets-type", type(cross_targets).__name__))
    else:
        if cross_targets.get("route") != "make -C zigux phase2-cross":
            issues.append(("cross-route", str(cross_targets.get("route"))))
        entries = cross_targets.get("cross_targets")
        if not isinstance(entries, list):
            issues.append(("cross-targets-list", type(entries).__name__))
        else:
            observed = []
            for entry in entries:
                if isinstance(entry, dict):
                    observed.append((entry.get("target"), entry.get("validation_mode")))
            if observed != list(EXPECTED_CROSS_TARGETS):
                issues.append(("cross-targets-values", repr(observed)))

    if not isinstance(toolchain_policy, dict):
        issues.append(("toolchain-policy-type", type(toolchain_policy).__name__))
    else:
        if toolchain_policy.get("channel") != EXPECTED_CHANNEL:
            issues.append(("toolchain-policy-channel", str(toolchain_policy.get("channel"))))
        archive_sha = toolchain_policy.get("archive_sha256")
        if not isinstance(archive_sha, dict) or archive_sha.get("x86_64-linux") != EXPECTED_ARCHIVE_SHA:
            issues.append(("toolchain-policy-archive-sha", repr(archive_sha)))
        upgrade_policy = toolchain_policy.get("upgrade_policy")
        if not isinstance(upgrade_policy, dict):
            issues.append(("toolchain-policy-upgrade-policy", type(upgrade_policy).__name__))
        else:
            routes = upgrade_policy.get("required_make_routes")
            if routes != list(EXPECTED_REQUIRED_MAKE_ROUTES):
                issues.append(("toolchain-policy-required-routes", repr(routes)))
            if upgrade_policy.get("archive_target_scope") != ["x86_64-linux"]:
                issues.append(("toolchain-policy-target-scope", repr(upgrade_policy.get("archive_target_scope"))))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    docs_readme = read_text(resolve_path(root, DOCS_README))
    phase2_notes = read_text(resolve_path(root, PHASE2_NOTES))
    review_checklist = read_text(resolve_path(root, REVIEW_CHECKLIST))
    tests_readme = read_text(resolve_path(root, TESTS_README))
    scripts_readme = read_text(resolve_path(root, SCRIPTS_README))
    third_party_readme = read_text(resolve_path(root, THIRD_PARTY_README))
    makefile = read_text(resolve_path(root, MAKEFILE))
    tool_manifest = read_json(resolve_path(root, TOOL_MANIFEST))
    artifact_manifest = read_json(resolve_path(root, ARTIFACT_TOOLS_MANIFEST))
    cross_targets = read_json(resolve_path(root, CROSS_TARGETS))
    toolchain_policy = read_json(resolve_path(root, TOOLCHAIN_POLICY))

    issues: list[tuple[str, str]] = []
    issues.extend(collect_missing(docs_readme, DOCS_README_MARKERS, "docs-readme"))
    issues.extend(collect_missing(phase2_notes, PHASE2_NOTES_MARKERS, "phase2-notes"))
    issues.extend(collect_missing(review_checklist, REVIEW_CHECKLIST_MARKERS, "review-checklist"))
    issues.extend(collect_missing(tests_readme, TESTS_README_MARKERS, "tests-readme"))
    issues.extend(collect_missing(scripts_readme, SCRIPTS_README_MARKERS, "scripts-readme"))
    issues.extend(collect_missing(third_party_readme, THIRD_PARTY_MARKERS, "third-party-readme"))
    issues.extend(collect_exact_count(third_party_readme, THIRD_PARTY_EXACT_COUNT_MARKERS, "third-party-readme-count"))
    issues.extend(collect_missing(makefile, MAKEFILE_LINES, "makefile"))
    issues.extend(collect_structured_issues(tool_manifest, artifact_manifest, cross_targets, toolchain_policy))
    return issues


def write_sample_root(root: Path) -> None:
    (root / "Documentation" / "zigux").mkdir(parents=True, exist_ok=True)
    (root / "zigux" / "tests" / "fixtures").mkdir(parents=True, exist_ok=True)
    (root / "scripts" / "zigux").mkdir(parents=True, exist_ok=True)
    (root / "third_party").mkdir(parents=True, exist_ok=True)

    write_text(root / "Documentation" / "zigux" / "README.md", "# sample\n" + "\n".join(DOCS_README_MARKERS) + "\n")
    write_text(root / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md", "# sample\n" + "\n".join(PHASE2_NOTES_MARKERS) + "\n")
    write_text(root / "Documentation" / "zigux" / "review-checklist.md", "# sample\n" + "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(root / "zigux" / "tests" / "README.md", "# sample\n" + "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(root / "scripts" / "zigux" / "README.md", "# sample\n" + "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(root / "third_party" / "README.md", "# sample\n" + "\n".join(THIRD_PARTY_MARKERS) + "\n")
    write_text(root / "zigux" / "Makefile", "\n".join(MAKEFILE_LINES) + "\n")

    write_json(
        root / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json",
        {
            "phase": "Phase 2",
            "status": "active",
            "scope": EXPECTED_TOOL_MANIFEST_SCOPE,
            "present_surfaces": {
                "checkers": [
                    "scripts/zigux/check-phase2-tool-manifest.py",
                    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
                    "scripts/zigux/check-phase2-fixdep-gate.py",
                ],
                "make_wrappers": [
                    "zigux/Makefile",
                    "make -C zigux phase2-toolchain",
                    "make -C zigux phase2-cross",
                    "make -C zigux phase2-fixdep",
                ],
            },
        },
    )
    write_json(
        root / "zigux" / "tests" / "fixtures" / "phase2_artifact_tools_manifest.json",
        {
            "phase": "Phase 2",
            "status": "active",
            "tooling": {
                "primary": ["scripts/zigux/artifact_diff.py"],
                "consumers": ["scripts/zigux/check-kconfig-bridge.py", "scripts/zigux/check-fixdep-diff.py"],
                "checkers": ["scripts/zigux/check-phase2-artifact-tools-manifest.py"],
                "supported_modes": list(EXPECTED_ARTIFACT_SUPPORTED_MODES),
            },
        },
    )
    write_json(
        root / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json",
        {
            "phase": "Phase 2",
            "status": "active",
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
    write_json(
        root / "scripts" / "zigux" / "zig-toolchain-policy.json",
        {
            "phase": "Phase 2",
            "channel": EXPECTED_CHANNEL,
            "minimum_version": EXPECTED_CHANNEL,
            "archive_sha256": {"x86_64-linux": EXPECTED_ARCHIVE_SHA},
            "upgrade_policy": {
                "channel_minimum_lockstep": True,
                "archive_target_scope": ["x86_64-linux"],
                "required_make_routes": list(EXPECTED_REQUIRED_MAKE_ROUTES),
            },
        },
    )


def run_self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_sample_root(root)

        issues = collect_issues(root)
        cases += 1
        if issues:
            raise SystemExit(f"sample root should pass: {issues}")

        review_path = root / "Documentation" / "zigux" / "review-checklist.md"
        review_text = review_path.read_text(encoding="utf-8")
        review_path.write_text(review_text.replace(REVIEW_CHECKLIST_MARKERS[12], "missing checklist summary", 1), encoding="utf-8")
        issues = collect_issues(root)
        cases += 1
        if not any(code == "review-checklist" for code, _ in issues):
            raise SystemExit("expected review-checklist mismatch for missing current-packet summary")
        write_sample_root(root)

        notes_path = root / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
        notes_text = notes_path.read_text(encoding="utf-8")
        notes_path.write_text(notes_text.replace(PHASE2_NOTES_MARKERS[3], "missing fixdep notes marker", 1), encoding="utf-8")
        issues = collect_issues(root)
        cases += 1
        if not any(code == "phase2-notes" for code, _ in issues):
            raise SystemExit("expected phase2-notes mismatch for missing fixdep marker")
        write_sample_root(root)

        docs_path = root / "Documentation" / "zigux" / "README.md"
        docs_text = docs_path.read_text(encoding="utf-8")
        docs_path.write_text(docs_text.replace(DOCS_README_MARKERS[2], "missing cross marker", 1), encoding="utf-8")
        issues = collect_issues(root)
        cases += 1
        if not any(code == "docs-readme" for code, _ in issues):
            raise SystemExit("expected docs-readme mismatch for missing cross marker")
        write_sample_root(root)

        tests_path = root / "zigux" / "tests" / "README.md"
        tests_text = tests_path.read_text(encoding="utf-8")
        tests_path.write_text(tests_text.replace(TESTS_README_MARKERS[3], "missing fixdep packet", 1), encoding="utf-8")
        issues = collect_issues(root)
        cases += 1
        if not any(code == "tests-readme" for code, _ in issues):
            raise SystemExit("expected tests-readme mismatch for missing fixdep packet")
        write_sample_root(root)

        scripts_path = root / "scripts" / "zigux" / "README.md"
        scripts_text = scripts_path.read_text(encoding="utf-8")
        scripts_path.write_text(scripts_text.replace(SCRIPTS_README_MARKERS[1], "missing scripts cross marker", 1), encoding="utf-8")
        issues = collect_issues(root)
        cases += 1
        if not any(code == "scripts-readme" for code, _ in issues):
            raise SystemExit("expected scripts-readme mismatch for missing direct cross marker")
        write_sample_root(root)

        third_party_path = root / "third_party" / "README.md"
        third_party_text = third_party_path.read_text(encoding="utf-8")
        third_party_path.write_text(third_party_text + THIRD_PARTY_MARKERS[3] + "\n", encoding="utf-8")
        issues = collect_issues(root)
        cases += 1
        if not any(code == "third-party-readme-count" for code, _ in issues):
            raise SystemExit("expected third-party exact-count mismatch for duplicate guard marker")
        write_sample_root(root)

        makefile_path = root / "zigux" / "Makefile"
        makefile_text = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(makefile_text.replace(MAKEFILE_LINES[6], "phase2-fixdep route missing", 1), encoding="utf-8")
        issues = collect_issues(root)
        cases += 1
        if not any(code == "makefile" for code, _ in issues):
            raise SystemExit("expected makefile mismatch for missing phase2-fixdep route")
        write_sample_root(root)

        tool_manifest_path = root / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
        tool_manifest = json.loads(tool_manifest_path.read_text(encoding="utf-8"))
        tool_manifest["scope"] = "wrong scope"
        write_json(tool_manifest_path, tool_manifest)
        issues = collect_issues(root)
        cases += 1
        if not any(code == "tool-manifest-scope" for code, _ in issues):
            raise SystemExit("expected tool-manifest scope mismatch")
        write_sample_root(root)

        artifact_manifest_path = root / "zigux" / "tests" / "fixtures" / "phase2_artifact_tools_manifest.json"
        artifact_manifest = json.loads(artifact_manifest_path.read_text(encoding="utf-8"))
        artifact_manifest["tooling"]["supported_modes"] = ["text", "json"]
        write_json(artifact_manifest_path, artifact_manifest)
        issues = collect_issues(root)
        cases += 1
        if not any(code == "artifact-manifest-supported-modes" for code, _ in issues):
            raise SystemExit("expected artifact-manifest supported-modes mismatch")
        write_sample_root(root)

        cross_targets_path = root / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
        cross_targets = json.loads(cross_targets_path.read_text(encoding="utf-8"))
        cross_targets["cross_targets"] = cross_targets["cross_targets"][:1]
        write_json(cross_targets_path, cross_targets)
        issues = collect_issues(root)
        cases += 1
        if not any(code == "cross-targets-values" for code, _ in issues):
            raise SystemExit("expected cross-target mismatch")
        write_sample_root(root)

        policy_path = root / "scripts" / "zigux" / "zig-toolchain-policy.json"
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]
        write_json(policy_path, policy)
        issues = collect_issues(root)
        cases += 1
        if not any(code == "toolchain-policy-required-routes" for code, _ in issues):
            raise SystemExit("expected toolchain-policy required-routes mismatch")

    print("PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_SELF_TEST=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_SELF_TEST_CASE_COUNT={cases}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fail closed when the shared Phase 2 review-checklist current packet drifts away from the live archive, toolchain, direct-cross, fixdep, manifest, and make-wrapper companions."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample root.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return

    if args.self_test:
        run_self_test()
        return

    issues = collect_issues(args.root)
    if issues:
        for code, detail in issues:
            print(f"PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_MISMATCH[{code}]={detail}")
        raise SystemExit(1)

    print("PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_REVIEW_MARKER_COUNT={len(REVIEW_CHECKLIST_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_DOCS_MARKER_COUNT={len(DOCS_README_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_NOTES_MARKER_COUNT={len(PHASE2_NOTES_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_TESTS_MARKER_COUNT={len(TESTS_README_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_SCRIPTS_MARKER_COUNT={len(SCRIPTS_README_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_THIRD_PARTY_MARKER_COUNT={len(THIRD_PARTY_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    print("PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_STRUCTURED_CHECK_COUNT=8")


if __name__ == "__main__":
    main()
