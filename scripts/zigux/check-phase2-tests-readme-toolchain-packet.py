#!/usr/bin/env python3
"""Guard the live Phase 2 tests-root toolchain packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

TESTS = "zigux/tests/README.md"
BOOTSTRAP = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
REVIEW = "Documentation/zigux/review-checklist.md"
SCRIPTS = "scripts/zigux/README.md"
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"
POLICY = "scripts/zigux/zig-toolchain-policy.json"
THIRD_PARTY = "third_party/README.md"
MANIFEST = "zigux/tests/fixtures/phase2_tool_manifest.json"
INSTALL_ZIG = "scripts/zigux/install-zig.py"
CROSS = "scripts/zigux/check-phase2-cross.py"
TOOLCHAIN = "scripts/zigux/check-zig-toolchain.py"
PIN_SCOPE = "scripts/zigux/check-phase2-toolchain-pin-scope.py"
CROSS_TARGETS = "zigux/tests/fixtures/phase2_cross_targets.json"

CHANNEL = "0.17.0-dev.87+9b177a7d2"
ARCHIVE_TARGET = "x86_64-linux"
ARCHIVE_PATH = f"third_party/zig-{ARCHIVE_TARGET}-{CHANNEL}.tar.xz"
REQUIRED_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
)

TESTS_MARKERS = (
    "## Phase 2 review packet",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`third_party/README.md`",
    f"`{ARCHIVE_PATH}`",
    f"`{CROSS_TARGETS}`",
    "keep the local-first archive workflow replay surface explicit through `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`, `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`, and `python3 scripts/zigux/check-lane05-local-archive-readme.py`.",
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
)

BOOTSTRAP_MARKERS = (
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again",
    "`python3 scripts/zigux/validate-phase2.py`, `python3 scripts/zigux/validate-phase2-closure.py`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` replay the bounded current Phase 2 closure-side, bounded genksyms bridge, and make-wrapper packet without widening it back into older missing-route assumptions.",
)

REVIEW_MARKERS = (
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`scripts/zigux/README.md`",
    "`third_party/README.md`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "current directly readable Phase 2 local-first archive, toolchain, installer, direct cross-route, kbuild, kconfig bridge, docs-shared-reminder, tool-manifest, artifact-support, fixdep, genksyms-bridge, and required-make-route packet",
    "current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet",
)

SCRIPTS_MARKERS = (
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`",
    "keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    *tuple(f"run: make -C zigux {route}" for route in REQUIRED_ROUTES),
)

MAKEFILE_LINES = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "phase2: phase2-validate",
)

SURFACE_PATHS = (
    TESTS,
    BOOTSTRAP,
    REVIEW,
    SCRIPTS,
    WORKFLOW,
    MAKEFILE,
    POLICY,
    THIRD_PARTY,
    MANIFEST,
    INSTALL_ZIG,
    CROSS,
    TOOLCHAIN,
    PIN_SCOPE,
    CROSS_TARGETS,
)

MANIFEST_SURFACES = (
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "zigux/Makefile",
    "third_party/README.md",
    "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
    "zigux/tests/fixtures/phase2_cross_targets.json",
)


def resolve(root: Path, rel: str) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def replace_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"line not found: {marker}")


def collect_marker_issues(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_line_issues(text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_policy_issues(root: Path) -> list[tuple[str, str]]:
    payload = json.loads(read_text(resolve(root, POLICY)))
    if not isinstance(payload, dict):
        return [("INVALID_POLICY_PAYLOAD", type(payload).__name__)]
    upgrade = payload.get("upgrade_policy")
    if not isinstance(upgrade, dict):
        return [("INVALID_UPGRADE_POLICY", type(upgrade).__name__)]
    issues: list[tuple[str, str]] = []
    if payload.get("channel") != CHANNEL:
        issues.append(("POLICY_CHANNEL_MISMATCH", repr(payload.get("channel"))))
    if payload.get("minimum_version") != CHANNEL:
        issues.append(("POLICY_MINIMUM_MISMATCH", repr(payload.get("minimum_version"))))
    if upgrade.get("archive_target_scope") != [ARCHIVE_TARGET]:
        issues.append(("POLICY_ARCHIVE_SCOPE_MISMATCH", repr(upgrade.get("archive_target_scope"))))
    if upgrade.get("required_make_routes") != list(REQUIRED_ROUTES):
        issues.append(("POLICY_ROUTE_LIST_MISMATCH", repr(upgrade.get("required_make_routes"))))
    return issues


def collect_manifest_issues(root: Path) -> list[tuple[str, str]]:
    payload = json.loads(read_text(resolve(root, MANIFEST)))
    if not isinstance(payload, dict):
        return [("INVALID_MANIFEST_PAYLOAD", type(payload).__name__)]
    present = payload.get("present_surfaces")
    if not isinstance(present, dict):
        return [("INVALID_MANIFEST_SURFACES", type(present).__name__)]
    strings = json.dumps(present, sort_keys=True)
    issues = [("MANIFEST_MISSING_SURFACES", surface) for surface in MANIFEST_SURFACES if surface not in strings]
    if payload.get("repo_reality_gaps") != []:
        issues.append(("MANIFEST_NONEMPTY_GAPS", json.dumps(payload.get("repo_reality_gaps"), sort_keys=True)))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    tests = read_text(resolve(root, TESTS))
    bootstrap = read_text(resolve(root, BOOTSTRAP))
    review = read_text(resolve(root, REVIEW))
    scripts = read_text(resolve(root, SCRIPTS))
    workflow = read_text(resolve(root, WORKFLOW))
    makefile = read_text(resolve(root, MAKEFILE))

    issues.extend(collect_marker_issues(tests, TESTS_MARKERS, "MISSING_TESTS_MARKERS"))
    issues.extend(collect_marker_issues(bootstrap, BOOTSTRAP_MARKERS, "MISSING_BOOTSTRAP_MARKERS"))
    issues.extend(collect_marker_issues(review, REVIEW_MARKERS, "MISSING_REVIEW_MARKERS"))
    issues.extend(collect_marker_issues(scripts, SCRIPTS_MARKERS, "MISSING_SCRIPTS_MARKERS"))
    issues.extend(collect_line_issues(workflow, WORKFLOW_LINES, "MISSING_WORKFLOW_LINES", "DUPLICATE_WORKFLOW_LINES"))
    issues.extend(collect_line_issues(makefile, MAKEFILE_LINES, "MISSING_MAKEFILE_LINES", "DUPLICATE_MAKEFILE_LINES"))

    for rel in SURFACE_PATHS:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_SURFACE_PATHS", rel))

    issues.extend(collect_policy_issues(root))
    issues.extend(collect_manifest_issues(root))
    return issues


def build_sample_root(root: Path) -> None:
    write_text(resolve(root, TESTS), "\n".join(["# zigux/tests", *TESTS_MARKERS]) + "\n")
    write_text(resolve(root, BOOTSTRAP), "\n".join(["# bootstrap", *BOOTSTRAP_MARKERS]) + "\n")
    write_text(resolve(root, REVIEW), "\n".join(["# review", *REVIEW_MARKERS]) + "\n")
    write_text(resolve(root, SCRIPTS), "\n".join(["# scripts", *SCRIPTS_MARKERS]) + "\n")
    write_text(resolve(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(resolve(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    write_text(resolve(root, THIRD_PARTY), "\n".join([f"`{ARCHIVE_PATH}`"]) + "\n")
    write_text(resolve(root, INSTALL_ZIG), "present\n")
    write_text(resolve(root, CROSS), "present\n")
    write_text(resolve(root, TOOLCHAIN), "present\n")
    write_text(resolve(root, PIN_SCOPE), "present\n")
    write_text(resolve(root, CROSS_TARGETS), "{\n  \"targets\": []\n}\n")
    write_text(
        resolve(root, POLICY),
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": CHANNEL,
                "minimum_version": CHANNEL,
                "archive_sha256": {ARCHIVE_TARGET: "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": [ARCHIVE_TARGET],
                    "required_make_routes": list(REQUIRED_ROUTES),
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve(root, MANIFEST),
        json.dumps(
            {
                "present_surfaces": {"all": list(MANIFEST_SURFACES)},
                "repo_reality_gaps": [],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_tests_toolchain_packet_") as tmp:
        root = Path(tmp)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        tests_path = resolve(root, TESTS)
        tests_path.write_text(replace_once(tests_path.read_text(encoding="utf-8"), TESTS_MARKERS[0]), encoding="utf-8")
        assert ("MISSING_TESTS_MARKERS", TESTS_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        workflow_path = resolve(root, WORKFLOW)
        workflow_path.write_text(replace_exact_line(workflow_path.read_text(encoding="utf-8"), WORKFLOW_LINES[0]), encoding="utf-8")
        assert ("MISSING_WORKFLOW_LINES", WORKFLOW_LINES[0]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        policy_path = resolve(root, POLICY)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["channel"] = "0.17.0"
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "POLICY_CHANNEL_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        manifest_path = resolve(root, MANIFEST)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["repo_reality_gaps"] = ["gap"]
        manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        assert any(code == "MANIFEST_NONEMPTY_GAPS" for code, _ in collect_issues(root))
        checks += 1

    print("PHASE2_TESTS_README_TOOLCHAIN_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TESTS_README_TOOLCHAIN_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the live Phase 2 tests-root toolchain packet stays aligned.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_TESTS_README_TOOLCHAIN_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        print("PHASE2_TESTS_README_TOOLCHAIN_PACKET=fail")
        for code, value in issues:
            print(f"{code}:{value}")
        return 1

    print("PHASE2_TESTS_README_TOOLCHAIN_PACKET=pass")
    print(f"PHASE2_TESTS_README_TOOLCHAIN_PACKET_TESTS_MARKER_COUNT={len(TESTS_MARKERS)}")
    print(f"PHASE2_TESTS_README_TOOLCHAIN_PACKET_REQUIRED_ROUTE_COUNT={len(REQUIRED_ROUTES)}")
    print(f"PHASE2_TESTS_README_TOOLCHAIN_PACKET_SURFACE_PATH_COUNT={len(SURFACE_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
