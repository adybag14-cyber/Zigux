#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

THIRD_PARTY_README = Path("third_party/README.md")
TESTS_README = Path("zigux/tests/README.md")
PHASE2_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
PHASE2_TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
CHECK_PHASE2_TOOL_MANIFEST = Path("scripts/zigux/check-phase2-tool-manifest.py")
CHECK_PHASE2_TESTS_ALIGNMENT = Path("scripts/zigux/check-phase2-tests-readme-alignment.py")

PAYLOAD = "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"

THIRD_PARTY_MARKERS = (
    "# Zigux third-party archives",
    "- target: `x86_64-linux`",
    "- channel: `0.17.0-dev.87+9b177a7d2`",
    f"- file: `{PAYLOAD}`",
    "- sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`",
    "- size: `58159088` bytes",
    "- Lane 05 bootstrap first reuses and validates `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` when that pinned archive is present.",
    "- Current `master` still keeps the pinned-archive contract reviewable through this README, the allow-missing replay route, and the local-first archive guards even while `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` itself remains absent until same-lane work rematerializes the payload.",
)

TESTS_README_MARKERS = (
    "## Phase 2 review packet",
    "current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py`, so keep that returned repo-local pinned-archive workflow, bootstrap guard, and archive README contract explicit here instead of leaving them outside the tests-root reminder",
    "keep the repo-local pinned archive contract explicit through `third_party/README.md`, the pinned `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` filename plus digest and size contract, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, and the local-first `third_party`, mirror, then direct-download bootstrap order reused by `.github/workflows/zigux-bootstrap.yml` and the two Lane 05 archive checkers while the payload itself remains absent on current `master`",
)

PHASE2_NOTES_MARKERS = (
    "- `third_party/README.md` is directly readable on current `master` and keeps the repo-local pinned archive filename, digest, size, duplicate-copy boundary, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` replay contract explicit beside the policy-driven toolchain packet while the payload itself remains absent until same-lane work rematerializes it.",
    "## Current repo-reality gaps",
    "- The bounded Phase 2 packet still has one current repo-reality gap on `master`: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` remains absent even though its filename, digest, size, local-first fallback order, and allow-missing replay route stay directly reviewable through `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, and the shipped Lane 05 reminder guards.",
)

PHASE2_NOTES_FORBIDDEN = (
    "- `third_party/README.md` is directly readable on current `master` and keeps the repo-local pinned archive filename, digest, size, duplicate-copy boundary, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux` replay contract explicit beside the policy-driven toolchain packet.",
    "- No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
)

TOOL_MANIFEST_NOTE = (
    "Keep the returned installer helper, local-first archive workflow checkers, third_party archive README contract, the pinned archive filename plus digest and size contract, direct cross-route checker, phase2_cross_targets fixture, the manifest-backed genksyms fixture packet, its restored process-output fixture set, the standalone invalid-long-option and ambiguous-long-option version-side-effect proofs, the full fixdep C-versus-Zig parity fixture packet, and the artifact-support manifest checker plus primary artifact_diff helper explicit through the current Phase 2 tool packet while the payload itself stays listed under repo-reality gaps until same-lane work rematerializes it."
)

TOOL_MANIFEST_CHECKER_MARKERS = (
    "REQUIRED_REPO_REALITY_GAPS = (",
    f'    "{PAYLOAD}",',
    '        "third_party/README.md",',
    "REPO_REALITY_GAPS_MISMATCH",
)

TESTS_ALIGNMENT_CHECKER_MARKERS = (
    "REQUIRED_PHASE2_TOOL_MANIFEST_GAPS = (",
    f'    "{PAYLOAD}",',
    '    "third_party/README.md",',
    "PHASE2_TOOL_MANIFEST_GAPS_MISMATCH",
)


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_manifest(root: Path) -> dict[str, object]:
    path = root / PHASE2_TOOL_MANIFEST
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid manifest shape: {path}")
    return payload


def collect_missing_checker_markers(root: Path, rel: Path, markers: tuple[str, ...]) -> list[tuple[str, str]]:
    text = read_text(root, rel)
    return [
        ("MISSING_CHECKER_MARKER", f"{rel}:{marker}")
        for marker in markers
        if marker not in text
    ]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    third_party_text = read_text(root, THIRD_PARTY_README)
    for marker in THIRD_PARTY_MARKERS:
        if marker not in third_party_text:
            issues.append(("MISSING_THIRD_PARTY_MARKER", marker))

    tests_text = read_text(root, TESTS_README)
    for marker in TESTS_README_MARKERS:
        if marker not in tests_text:
            issues.append(("MISSING_TESTS_MARKER", marker))

    notes_text = read_text(root, PHASE2_NOTES)
    for marker in PHASE2_NOTES_MARKERS:
        if marker not in notes_text:
            issues.append(("MISSING_PHASE2_NOTES_MARKER", marker))
    for marker in PHASE2_NOTES_FORBIDDEN:
        if marker in notes_text:
            issues.append(("FORBIDDEN_PHASE2_NOTES_MARKER", marker))

    manifest = read_manifest(root)
    if manifest.get("repo_reality_gaps") != [PAYLOAD]:
        issues.append(("MANIFEST_GAPS_MISMATCH", repr(manifest.get("repo_reality_gaps"))))

    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        issues.append(("INVALID_MANIFEST_SURFACES", "present_surfaces"))
    else:
        archive_support = surfaces.get("archive_support")
        if archive_support != ["third_party/README.md"]:
            issues.append(("ARCHIVE_SUPPORT_MISMATCH", repr(archive_support)))
        notes = manifest.get("notes")
        if not isinstance(notes, list) or TOOL_MANIFEST_NOTE not in notes:
            issues.append(("MISSING_MANIFEST_NOTE", TOOL_MANIFEST_NOTE))

    issues.extend(
        collect_missing_checker_markers(
            root, CHECK_PHASE2_TOOL_MANIFEST, TOOL_MANIFEST_CHECKER_MARKERS
        )
    )
    issues.extend(
        collect_missing_checker_markers(
            root, CHECK_PHASE2_TESTS_ALIGNMENT, TESTS_ALIGNMENT_CHECKER_MARKERS
        )
    )

    return issues


def build_self_test_root(root: Path) -> None:
    write_text(root, THIRD_PARTY_README, "\n".join(THIRD_PARTY_MARKERS) + "\n")
    write_text(root, TESTS_README, "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(root, PHASE2_NOTES, "\n".join(PHASE2_NOTES_MARKERS) + "\n")
    write_text(
        root,
        PHASE2_TOOL_MANIFEST,
        json.dumps(
            {
                "notes": [TOOL_MANIFEST_NOTE],
                "present_surfaces": {"archive_support": ["third_party/README.md"]},
                "repo_reality_gaps": [PAYLOAD],
            },
            indent=2,
        )
        + "\n",
    )
    write_text(root, CHECK_PHASE2_TOOL_MANIFEST, "\n".join(TOOL_MANIFEST_CHECKER_MARKERS) + "\n")
    write_text(root, CHECK_PHASE2_TESTS_ALIGNMENT, "\n".join(TESTS_ALIGNMENT_CHECKER_MARKERS) + "\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="phase2_archive_contract_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        write_text(root, THIRD_PARTY_README, "# broken\n")
        assert any(code == "MISSING_THIRD_PARTY_MARKER" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        write_text(root, TESTS_README, "# broken\n")
        assert any(code == "MISSING_TESTS_MARKER" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        write_text(root, PHASE2_NOTES, "# broken\n")
        assert any(code == "MISSING_PHASE2_NOTES_MARKER" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        write_text(
            root,
            PHASE2_NOTES,
            "\n".join(PHASE2_NOTES_MARKERS + PHASE2_NOTES_FORBIDDEN) + "\n",
        )
        assert any(code == "FORBIDDEN_PHASE2_NOTES_MARKER" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        write_text(
            root,
            PHASE2_TOOL_MANIFEST,
            json.dumps(
                {
                    "notes": [],
                    "present_surfaces": {"archive_support": ["third_party/README.md", PAYLOAD]},
                    "repo_reality_gaps": [],
                },
                indent=2,
            )
            + "\n",
        )
        manifest_issues = collect_issues(root)
        assert ("MANIFEST_GAPS_MISMATCH", "[]") in manifest_issues
        assert any(code == "ARCHIVE_SUPPORT_MISMATCH" for code, _ in manifest_issues)
        assert any(code == "MISSING_MANIFEST_NOTE" for code, _ in manifest_issues)
        checks_run += 1

        build_self_test_root(root)
        write_text(root, CHECK_PHASE2_TOOL_MANIFEST, "missing\n")
        assert any(code == "MISSING_CHECKER_MARKER" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        write_text(root, CHECK_PHASE2_TESTS_ALIGNMENT, "missing\n")
        assert any(code == "MISSING_CHECKER_MARKER" for code, _ in collect_issues(root))
        checks_run += 1

    print("PHASE2_ARCHIVE_CONTRACT_PACKET_SELF_TEST=pass")
    print(f"PHASE2_ARCHIVE_CONTRACT_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 22 absent-payload archive contract packet aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        print("PHASE2_ARCHIVE_CONTRACT_PACKET=fail")
        for code, value in issues:
            print(f"{code}:{value}")
        return 1

    print("PHASE2_ARCHIVE_CONTRACT_PACKET=pass")
    print(f"PHASE2_ARCHIVE_CONTRACT_GAP={PAYLOAD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
