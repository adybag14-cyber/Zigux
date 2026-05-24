#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
TESTS_README = Path("zigux/tests/README.md")
PHASE2_TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
MAKEFILE = Path("zigux/Makefile")
CLOSURE_ARCHIVE_CONTRACT_CHECKER = Path("scripts/zigux/check-phase2-closure-archive-contract.py")

PAYLOAD = "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"

REQUIRED_TESTS_README_MARKERS = (
    "current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py`, so keep that returned repo-local pinned-archive workflow, bootstrap guard, and archive README contract explicit here instead of leaving them outside the tests-root reminder",
    "keep the repo-local pinned archive contract explicit through `third_party/README.md`, the pinned `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` filename plus digest and size contract, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, and the local-first `third_party`, mirror, then direct-download bootstrap order reused by `.github/workflows/zigux-bootstrap.yml` and the two Lane 05 archive checkers while the payload itself remains absent on current `master`",
    "Keep the current toolchain self-check and replay surface explicit through `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/install-zig.py --self-test`, and `python3 scripts/zigux/check-phase2-cross.py --self-test`.",
)

FORBIDDEN_TESTS_README_MARKERS = (
    "keep the repo-local pinned archive packet explicit through `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`, and the local-first `third_party`, mirror, then direct-download bootstrap order reused by `.github/workflows/zigux-bootstrap.yml` and the two Lane 05 archive checkers",
)

REQUIRED_CLOSURE_MARKERS = (
    "The closure-side archive-contract packet now stays explicit through `scripts/zigux/check-phase2-archive-contract-packet.py`, `third_party/README.md`, `zigux/tests/README.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `scripts/zigux/check-phase2-tool-manifest.py`, and `scripts/zigux/check-phase2-tests-readme-alignment.py` while `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` remains the lone current repo-reality gap on `master`.",
    f"`PHASE2_CURRENT_GAP_PACKET={PAYLOAD}`",
)

REQUIRED_MAKEFILE_LINES = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-archive-contract-packet.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-closure-archive-contract.py",
)

REQUIRED_CLOSURE_CHECKER_MARKERS = (
    f'PAYLOAD = "{PAYLOAD}"',
    "PHASE2_CLOSURE_ARCHIVE_CONTRACT=pass",
)

REQUIRED_MANIFEST_NOTE = (
    "Keep the returned installer helper, local-first archive workflow checkers, third_party archive README contract, the pinned archive filename plus digest and size contract, direct cross-route checker, phase2_cross_targets fixture, the manifest-backed genksyms fixture packet, its restored process-output fixture set, the standalone invalid-long-option and ambiguous-long-option version-side-effect proofs, the full fixdep C-versus-Zig parity fixture packet, and the artifact-support manifest checker plus primary artifact_diff helper explicit through the current Phase 2 tool packet while the payload itself stays listed under repo-reality gaps until same-lane work rematerializes it."
)

REQUIRED_MANIFEST_ARCHIVE_SUPPORT = ["third_party/README.md"]
REQUIRED_MANIFEST_GAPS = [PAYLOAD]
REQUIRED_MANIFEST_REVIEW_SURFACES = ["zigux/tests/README.md"]


def resolve_path(root: Path, rel: Path) -> Path:
    try:
        return root / rel.relative_to(ROOT)
    except ValueError:
        return root / rel


def read_text(root: Path, rel: Path) -> str:
    path = resolve_path(root, rel)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: Path, content: str) -> None:
    path = resolve_path(root, rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_manifest(root: Path) -> dict[str, object]:
    path = resolve_path(root, PHASE2_TOOL_MANIFEST)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"required json has invalid top-level shape: {path}")
    return payload


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    tests_readme_text = read_text(root, TESTS_README)
    for marker in REQUIRED_TESTS_README_MARKERS:
        if marker not in tests_readme_text:
            issues.append(("MISSING_TESTS_README_MARKER", marker))
    for marker in FORBIDDEN_TESTS_README_MARKERS:
        if marker in tests_readme_text:
            issues.append(("FORBIDDEN_TESTS_README_MARKER", marker))

    closure_text = read_text(root, PHASE2_CLOSURE)
    for marker in REQUIRED_CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    makefile_text = read_text(root, MAKEFILE)
    for marker in REQUIRED_MAKEFILE_LINES:
        count = makefile_text.count(marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{count}::{marker}"))

    closure_checker_text = read_text(root, CLOSURE_ARCHIVE_CONTRACT_CHECKER)
    for marker in REQUIRED_CLOSURE_CHECKER_MARKERS:
        if marker not in closure_checker_text:
            issues.append(("MISSING_CLOSURE_CHECKER_MARKER", marker))

    manifest = read_manifest(root)
    notes = manifest.get("notes")
    if not isinstance(notes, list) or REQUIRED_MANIFEST_NOTE not in notes:
        issues.append(("MISSING_MANIFEST_NOTE", REQUIRED_MANIFEST_NOTE))

    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
    else:
        archive_support = surfaces.get("archive_support")
        if archive_support != REQUIRED_MANIFEST_ARCHIVE_SUPPORT:
            issues.append(("ARCHIVE_SUPPORT_MISMATCH", json.dumps(archive_support, sort_keys=True)))
        review_surfaces = surfaces.get("review_surfaces")
        if not isinstance(review_surfaces, list) or any(
            marker not in review_surfaces for marker in REQUIRED_MANIFEST_REVIEW_SURFACES
        ):
            issues.append(("REVIEW_SURFACE_MISMATCH", json.dumps(review_surfaces, sort_keys=True)))

    manifest_gaps = manifest.get("repo_reality_gaps")
    if manifest_gaps != REQUIRED_MANIFEST_GAPS:
        issues.append(("REPO_REALITY_GAP_MISMATCH", json.dumps(manifest_gaps, sort_keys=True)))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TESTS_ROOT_SUMMARY=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(root, TESTS_README, "\n".join(REQUIRED_TESTS_README_MARKERS) + "\n")
    write_text(root, PHASE2_CLOSURE, "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n")
    write_text(
        root,
        MAKEFILE,
        "\n".join(
            (
                "phase2-validate:",
                *[f"\t{line}" for line in REQUIRED_MAKEFILE_LINES],
            )
        )
        + "\n",
    )
    write_text(root, CLOSURE_ARCHIVE_CONTRACT_CHECKER, "\n".join(REQUIRED_CLOSURE_CHECKER_MARKERS) + "\n")
    write_text(
        root,
        PHASE2_TOOL_MANIFEST,
        json.dumps(
            {
                "notes": [REQUIRED_MANIFEST_NOTE],
                "present_surfaces": {
                    "archive_support": REQUIRED_MANIFEST_ARCHIVE_SUPPORT,
                    "review_surfaces": REQUIRED_MANIFEST_REVIEW_SURFACES,
                },
                "repo_reality_gaps": REQUIRED_MANIFEST_GAPS,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_tests_root_summary_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        tests_readme_path = resolve_path(root, TESTS_README)
        original_tests_text = tests_readme_path.read_text(encoding="utf-8")
        for marker in REQUIRED_TESTS_README_MARKERS:
            build_self_test_root(root)
            tests_readme_path.write_text(replace_once(original_tests_text, marker), encoding="utf-8")
            assert ("MISSING_TESTS_README_MARKER", marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        tests_readme_path.write_text(original_tests_text + FORBIDDEN_TESTS_README_MARKERS[0] + "\n", encoding="utf-8")
        assert ("FORBIDDEN_TESTS_README_MARKER", FORBIDDEN_TESTS_README_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        closure_path = resolve_path(root, PHASE2_CLOSURE)
        original_closure_text = closure_path.read_text(encoding="utf-8")
        for marker in REQUIRED_CLOSURE_MARKERS:
            build_self_test_root(root)
            closure_path.write_text(replace_once(original_closure_text, marker), encoding="utf-8")
            assert ("MISSING_CLOSURE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_path.write_text("phase2-validate:\n", encoding="utf-8")
        assert any(code == "MISSING_MAKEFILE_LINE" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve_path(root, PHASE2_TOOL_MANIFEST)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["repo_reality_gaps"] = []
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        assert ("REPO_REALITY_GAP_MISMATCH", "[]") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["present_surfaces"]["archive_support"] = [PAYLOAD]
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        assert any(code == "ARCHIVE_SUPPORT_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        checker_path = resolve_path(root, CLOSURE_ARCHIVE_CONTRACT_CHECKER)
        checker_path.write_text("broken\n", encoding="utf-8")
        assert any(code == "MISSING_CLOSURE_CHECKER_MARKER" for code, _ in collect_issues(root))
        checks_run += 1

    print("PHASE2_TESTS_ROOT_SUMMARY=self-test-pass")
    print(f"PHASE2_TESTS_ROOT_SUMMARY_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 22 Phase 2 tests-root summary aligned with the archive-truthfulness packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TESTS_ROOT_SUMMARY=pass")
    print(f"PHASE2_TESTS_ROOT_SUMMARY_GAP={PAYLOAD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
