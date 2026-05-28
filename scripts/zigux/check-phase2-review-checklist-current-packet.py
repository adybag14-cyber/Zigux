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
    "Phase 2 flow - the current fixdep packet stays reviewable through the dedicated governance guard, parity checker, and shipped `phase2-fixdep` wrapper instead of widening back into older shared reminder churn",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` keep the current fixdep governance, determinism, helper, fixture, and CI packet explicit from the scripts root",
    "`python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`, `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py --self-test`, `python3 scripts/zigux/check-fixdep-diff.py`, `zig test scripts/zigux/fixdep.zig`, and `make -C zigux phase2-fixdep` replay the shipped fixdep lane without widening into unrelated Phase 2 surfaces",
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
EXPECTED_REQUIRED_MAKE_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
)
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
            issues.append(("toolchain-policy-upgrade-policy", repr(upgrade_policy)))
            required_make_routes = None
        else:
            required_make_routes = upgrade_policy.get("required_make_routes")
        if required_make_routes != list(EXPECTED_REQUIRED_MAKE_ROUTES):
            issues.append(("toolchain-policy-required-make-routes", repr(required_make_routes)))

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
    issues.extend(collect_structured_issues(tool_manifest, artifact_manifest, cross_targets, toolchain_policy))

    for line in MAKEFILE_LINES:
        if line not in makefile:
            issues.append(("makefile", line))

    return issues


def run(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        for code, detail in issues:
            print(f"PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_MISMATCH={code}:{detail}")
        print(f"PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET=fail count={len(issues)}")
        return 1

    print("PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_REVIEW_MARKER_COUNT={len(REVIEW_CHECKLIST_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_DOCS_MARKER_COUNT={len(DOCS_README_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_NOTES_MARKER_COUNT={len(PHASE2_NOTES_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_TESTS_MARKER_COUNT={len(TESTS_README_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_SCRIPTS_MARKER_COUNT={len(SCRIPTS_README_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_THIRD_PARTY_MARKER_COUNT={len(THIRD_PARTY_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    print(
        "PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_STRUCTURED_CHECK_COUNT="
        f"{len(collect_structured_issues(read_json(resolve_path(root, TOOL_MANIFEST)), read_json(resolve_path(root, ARTIFACT_TOOLS_MANIFEST)), read_json(resolve_path(root, CROSS_TARGETS)), read_json(resolve_path(root, TOOLCHAIN_POLICY))))}"
    )
    return 0


SELFTEST_LAYOUT = {
    DOCS_README: "\n".join(DOCS_README_MARKERS) + "\n",
    PHASE2_NOTES: "\n".join(PHASE2_NOTES_MARKERS) + "\n",
    REVIEW_CHECKLIST: "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n",
    TESTS_README: "\n".join(TESTS_README_MARKERS) + "\n",
    SCRIPTS_README: "\n".join(SCRIPTS_README_MARKERS) + "\n",
    THIRD_PARTY_README: "\n".join(THIRD_PARTY_MARKERS) + "\n",
    MAKEFILE: "\n".join(MAKEFILE_LINES) + "\n",
}

SELFTEST_TOOL_MANIFEST = {
    "scope": EXPECTED_TOOL_MANIFEST_SCOPE,
    "present_surfaces": {
        "make_wrappers": [
            "make -C zigux phase2-toolchain",
            "make -C zigux phase2-cross",
            "make -C zigux phase2-fixdep",
        ],
        "checkers": [
            "scripts/zigux/check-phase2-tool-manifest.py",
            "scripts/zigux/check-phase2-artifact-tools-manifest.py",
            "scripts/zigux/check-phase2-fixdep-gate.py",
        ],
    },
}

SELFTEST_ARTIFACT_MANIFEST = {
    "tooling": {
        "supported_modes": list(EXPECTED_ARTIFACT_SUPPORTED_MODES),
        "checkers": ["scripts/zigux/check-phase2-artifact-tools-manifest.py"],
    }
}

SELFTEST_CROSS_TARGETS = {
    "route": "make -C zigux phase2-cross",
    "cross_targets": [
        {"target": "x86_64-linux", "validation_mode": "archive_required"},
        {"target": "aarch64-linux", "validation_mode": "route_contract_only"},
    ],
}

SELFTEST_TOOLCHAIN_POLICY = {
    "channel": EXPECTED_CHANNEL,
    "archive_sha256": {"x86_64-linux": EXPECTED_ARCHIVE_SHA},
    "upgrade_policy": {
        "required_make_routes": list(EXPECTED_REQUIRED_MAKE_ROUTES),
    },
}


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase2_review_checklist_current_packet_") as tmpdir:
        root = Path(tmpdir)
        for path, content in SELFTEST_LAYOUT.items():
            write_text(resolve_path(root, path), content)
        write_json(resolve_path(root, TOOL_MANIFEST), SELFTEST_TOOL_MANIFEST)
        write_json(resolve_path(root, ARTIFACT_TOOLS_MANIFEST), SELFTEST_ARTIFACT_MANIFEST)
        write_json(resolve_path(root, CROSS_TARGETS), SELFTEST_CROSS_TARGETS)
        write_json(resolve_path(root, TOOLCHAIN_POLICY), SELFTEST_TOOLCHAIN_POLICY)

        issues = collect_issues(root)
        if issues:
            for code, detail in issues:
                print(f"PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_SELF_TEST_MISMATCH={code}:{detail}")
            print(f"PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_SELF_TEST=fail count={len(issues)}")
            return 1

        print("PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_SELF_TEST=pass")
        print(
            "PHASE2_REVIEW_CHECKLIST_CURRENT_PACKET_SELF_TEST_CASE_COUNT="
            f"{len(DOCS_README_MARKERS) + len(PHASE2_NOTES_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(TESTS_README_MARKERS) + len(SCRIPTS_README_MARKERS) + len(THIRD_PARTY_MARKERS) + len(MAKEFILE_LINES) + 8}"
        )
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 review checklist references the current documentation packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to inspect (defaults to the current checkout).",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run a synthetic passing fixture that exercises the checker.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    return run(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
