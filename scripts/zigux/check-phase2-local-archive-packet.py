#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
THIRD_PARTY_README = ROOT / "third_party" / "README.md"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"

REQUIRED_PATHS = (
    ROOT / "scripts" / "zigux" / "check-zig-toolchain.py",
    ROOT / "scripts" / "zigux" / "check-lane05-local-first-archive-workflow.py",
    ROOT / "scripts" / "zigux" / "check-lane05-local-archive-readme.py",
    ROOT / "scripts" / "zigux" / "check-lane05-install-zig-archive-verification.py",
    ROOT / "scripts" / "zigux" / "stage-pinned-zig-archive.py",
    ROOT / "scripts" / "zigux" / "check-lane05-stage-helper-contract.py",
    ROOT / "scripts" / "zigux" / "check-lane05-stage-helper-selftest.py",
    ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json",
    ROOT / "third_party" / "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
)

PHASE2_NOTES_MARKERS = (
    "`third_party/README.md` is directly readable on current `master`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux` replay contract explicit beside the policy-driven toolchain packet.",
    "tries `community-mirrors.txt` before the direct Zig download URL",
    "`python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`",
    "`python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`",
    "`python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test`",
    "`python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test`",
    "`python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test`",
)

REVIEW_CHECKLIST_MARKERS = (
    "`third_party/README.md`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "current directly readable Phase 2 local-first archive, toolchain, installer, direct cross-route, kbuild, kconfig bridge, docs-shared-reminder, tool-manifest, artifact-support, fixdep, genksyms-bridge, and required-make-route packet",
    "current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet",
)

TESTS_README_MARKERS = (
    "current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py`",
    "keep the repo-local pinned archive packet explicit through `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "keep the local-first archive workflow replay surface explicit through `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`, `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`, and `python3 scripts/zigux/check-lane05-local-archive-readme.py`.",
    "Keep the current toolchain self-check and replay surface explicit through `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/install-zig.py --self-test`, and `python3 scripts/zigux/check-phase2-cross.py --self-test`.",
)

THIRD_PARTY_README_MARKERS = (
    "- target: `x86_64-linux`",
    "- channel: `0.17.0-dev.87+9b177a7d2`",
    "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "- sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`",
    "- size: `58159088` bytes",
    "- `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "- Lane 05 bootstrap first reuses and validates `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` when that pinned archive is present.",
    "- If the exact archive file is absent but `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz.parts` is present, `.github/workflows/zigux-bootstrap.yml` stages the same pinned payload locally with `scripts/zigux/stage-pinned-zig-archive.py` before mirror or direct-download fallback.",
    "- Before retrying the mirror or direct-download path, `.github/workflows/zigux-bootstrap.yml` clears the extracted `.zig-toolchain` root plus the cached `community-mirrors.txt` handle so stale partial recovery state is discarded before the next fallback attempt.",
    "- If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL.",
)

WORKFLOW_MARKERS = (
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    'repo_archive_parts_dir="${repo_archive_path}.parts"',
    "python3 scripts/zigux/stage-pinned-zig-archive.py",
    'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
    'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
    'if try_download "$ZIGUX_ZIG_URL"; then',
    "- name: Self-test current Lane 05 local-first archive checker",
    "- name: Check current Lane 05 local-first archive packet",
    "- name: Self-test current Lane 05 local archive README checker",
    "- name: Check current Lane 05 local archive README packet",
    "- name: Self-test current Lane 05 install-zig archive verification checker",
    "- name: Check current Lane 05 install-zig archive verification packet",
    "- name: Self-test current staged pinned Zig archive helper",
    "- name: Self-test current Lane 05 stage helper contract checker",
    "- name: Check current Lane 05 stage helper contract packet",
    "- name: Self-test current Lane 05 stage helper selftest checker",
    "- name: Check current Lane 05 stage helper selftest packet",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_missing_paths(root: Path) -> list[tuple[str, str]]:
    missing: list[tuple[str, str]] = []
    for path in REQUIRED_PATHS:
        resolved = resolve_path(root, path)
        if not resolved.exists():
            missing.append(("MISSING_REQUIRED_PATHS", str(path.relative_to(ROOT))))
    return missing


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(collect_missing_paths(root))
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, PHASE2_NOTES)),
            PHASE2_NOTES_MARKERS,
            "MISSING_PHASE2_NOTES_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, REVIEW_CHECKLIST)),
            REVIEW_CHECKLIST_MARKERS,
            "MISSING_REVIEW_CHECKLIST_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, TESTS_README)),
            TESTS_README_MARKERS,
            "MISSING_TESTS_README_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, THIRD_PARTY_README)),
            THIRD_PARTY_README_MARKERS,
            "MISSING_THIRD_PARTY_README_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, WORKFLOW)),
            WORKFLOW_MARKERS,
            "MISSING_WORKFLOW_MARKERS",
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_LOCAL_ARCHIVE_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, PHASE2_NOTES), "\n".join(PHASE2_NOTES_MARKERS) + "\n")
    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, THIRD_PARTY_README), "\n".join(THIRD_PARTY_README_MARKERS) + "\n")
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_MARKERS) + "\n")
    for path in REQUIRED_PATHS:
        resolved = resolve_path(root, path)
        if resolved.name.endswith(".json"):
            write_text(resolved, "{}\n")
        elif resolved.suffix == ".xz":
            resolved.parent.mkdir(parents=True, exist_ok=True)
            resolved.write_bytes(b"placeholder\n")
        else:
            write_text(resolved, "# current packet placeholder\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(PHASE2_NOTES_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(
        TESTS_README_MARKERS
    ) + len(THIRD_PARTY_README_MARKERS) + len(WORKFLOW_MARKERS) + len(REQUIRED_PATHS)
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_local_archive_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for rel_path, markers, code in (
            (PHASE2_NOTES, PHASE2_NOTES_MARKERS, "MISSING_PHASE2_NOTES_MARKERS"),
            (REVIEW_CHECKLIST, REVIEW_CHECKLIST_MARKERS, "MISSING_REVIEW_CHECKLIST_MARKERS"),
            (TESTS_README, TESTS_README_MARKERS, "MISSING_TESTS_README_MARKERS"),
            (THIRD_PARTY_README, THIRD_PARTY_README_MARKERS, "MISSING_THIRD_PARTY_README_MARKERS"),
            (WORKFLOW, WORKFLOW_MARKERS, "MISSING_WORKFLOW_MARKERS"),
        ):
            for marker in markers:
                build_sample_root(root)
                path = resolve_path(root, rel_path)
                path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
                issues = collect_issues(root)
                assert (code, marker) in issues
                checks_run += 1

        for rel_path in REQUIRED_PATHS:
            build_sample_root(root)
            resolve_path(root, rel_path).unlink()
            issues = collect_issues(root)
            assert ("MISSING_REQUIRED_PATHS", str(rel_path.relative_to(ROOT))) in issues
            checks_run += 1

    assert checks_run == expected_case_count
    print("PHASE2_LOCAL_ARCHIVE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_LOCAL_ARCHIVE_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shared Phase 2 local archive reminder packet aligned to current repo reality."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="Write a minimal passing sample repository tree and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_LOCAL_ARCHIVE_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_LOCAL_ARCHIVE_PACKET=pass")
    print(f"PHASE2_LOCAL_ARCHIVE_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(
        "PHASE2_LOCAL_ARCHIVE_PACKET_MARKER_COUNT="
        f"{len(PHASE2_NOTES_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(TESTS_README_MARKERS) + len(THIRD_PARTY_README_MARKERS) + len(WORKFLOW_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
