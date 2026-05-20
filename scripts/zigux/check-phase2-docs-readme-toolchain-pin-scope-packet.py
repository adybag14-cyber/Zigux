#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
DOCS_README = ROOT / "Documentation" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"

DOCS_MARKERS = (
    "Phase 2 notes",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`third_party/README.md`",
    "the current docs-root Phase 2 reminder packet should stay parked on",
    "the shared Phase 2 toolchain packet",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "keep the repo-local pinned archive contract",
    "keep the installer and direct cross-route packet explicit beside the shipped toolchain, kconfig, genksyms, and make-wrapper surfaces",
)

DOCS_FORBIDDEN_MARKERS = (
    "historical direct cross-route packet members",
    "the remaining historical direct cross-route members",
)

TESTS_MARKERS = (
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
    "Keep the current toolchain self-check and replay surface explicit through `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/install-zig.py --self-test`, and `python3 scripts/zigux/check-phase2-cross.py --self-test`.",
    "current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py`, so keep that returned repo-local pinned-archive workflow, bootstrap guard, and archive README contract explicit here instead of leaving them outside the tests-root reminder",
    "keep the repo-local pinned archive packet explicit through `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`, and the local-first `third_party`, mirror, then direct-download bootstrap order reused by `.github/workflows/zigux-bootstrap.yml` and the two Lane 05 archive checkers",
    "keep the local-first archive workflow replay surface explicit through `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`, `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`, and `python3 scripts/zigux/check-lane05-local-archive-readme.py`.",
    "current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep that returned installer, direct cross-route, and cross-target fixture packet explicit here instead of leaving it in the historical-gap bucket",
)

TESTS_FORBIDDEN_MARKERS = (
    "narrows the remaining repo-reality gap list to the still-missing validator-first, installer, and direct cross-route paths",
    "leaves `scripts/zigux/check-phase2-cross.py` plus `zigux/tests/fixtures/phase2_cross_targets.json` as the remaining historical direct cross-route members",
)

BOOTSTRAP_MARKERS = (
    "# Phase 2 Toolchain Bootstrap Notes",
    "`scripts/zigux/zig-toolchain-policy.json` currently pins Phase 2 to channel `0.17.0-dev.87+9b177a7d2`, keeps the minimum version in lockstep, limits archive digests to `x86_64-linux`, and names `phase2-toolchain` plus `phase2-validate` as the required Linux-style make routes when those routes are rematerialized.",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/install-zig.py` is directly readable on current `master` and keeps the pinned-channel archive download, SHA-256 verification, and install-root replay path explicit beside the reminder guards.",
    "`scripts/zigux/check-zig-toolchain.py` is directly readable on current `master` and keeps the pinned-channel probe, repo-local `.zig-toolchain` fallback, and archive-integrity validation surface explicit beside the reminder guards.",
    "`third_party/README.md` is directly readable on current `master` and keeps the repo-local pinned archive filename, digest, size, duplicate-copy boundary, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux` replay contract explicit beside the policy-driven toolchain packet.",
    "`.github/workflows/zigux-bootstrap.yml` now runs `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "The rematerialized make-wrapper packet is directly readable on current `master` through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`, so keep those routes in the present packet instead of the repo-reality-gap list.",
    "- No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, or returned fixdep packet on current `master`.",
    "toolchain pin-scope alignment",
)

BOOTSTRAP_FORBIDDEN_MARKERS = (
    "historical packet members until same-lane work rematerializes them on `master`",
    "Treat older validator-first-only Phase 2 names as current repo-reality gaps inside the bounded toolchain, installer, direct cross-route, local-first archive, or returned fixdep packet on current `master`.",
)

DOCS_EXACT_COUNT_MARKERS = (
    "keep the repo-local pinned archive contract",
    "keep the installer and direct cross-route packet explicit beside the shipped toolchain, kconfig, genksyms, and make-wrapper surfaces",
)

TESTS_EXACT_COUNT_MARKERS = (
    "Keep the current toolchain self-check and replay surface explicit through `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/install-zig.py --self-test`, and `python3 scripts/zigux/check-phase2-cross.py --self-test`.",
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
)

BOOTSTRAP_EXACT_COUNT_MARKERS = (
    "- No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, or returned fixdep packet on current `master`.",
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


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def collect_exact_count_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append((code, f"{count}::{marker}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    docs_text = read_text(resolve_path(root, DOCS_README))
    tests_text = read_text(resolve_path(root, TESTS_README))
    bootstrap_text = read_text(resolve_path(root, BOOTSTRAP_NOTES))
    issues: list[tuple[str, str]] = []
    issues.extend(collect_missing_markers(docs_text, DOCS_MARKERS, "MISSING_DOCS_MARKERS"))
    issues.extend(collect_forbidden_markers(docs_text, DOCS_FORBIDDEN_MARKERS, "FORBIDDEN_DOCS_MARKERS"))
    issues.extend(collect_exact_count_markers(docs_text, DOCS_EXACT_COUNT_MARKERS, "EXACT_COUNT_DOCS_MARKERS"))
    issues.extend(collect_missing_markers(tests_text, TESTS_MARKERS, "MISSING_TESTS_MARKERS"))
    issues.extend(collect_forbidden_markers(tests_text, TESTS_FORBIDDEN_MARKERS, "FORBIDDEN_TESTS_MARKERS"))
    issues.extend(collect_exact_count_markers(tests_text, TESTS_EXACT_COUNT_MARKERS, "EXACT_COUNT_TESTS_MARKERS"))
    issues.extend(collect_missing_markers(bootstrap_text, BOOTSTRAP_MARKERS, "MISSING_BOOTSTRAP_MARKERS"))
    issues.extend(collect_forbidden_markers(bootstrap_text, BOOTSTRAP_FORBIDDEN_MARKERS, "FORBIDDEN_BOOTSTRAP_MARKERS"))
    issues.extend(collect_exact_count_markers(bootstrap_text, BOOTSTRAP_EXACT_COUNT_MARKERS, "EXACT_COUNT_BOOTSTRAP_MARKERS"))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_DOCS_README_TOOLCHAIN_PIN_SCOPE_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_root(root: Path) -> None:
    write_text(resolve_path(root, DOCS_README), "\n".join(DOCS_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_MARKERS) + "\n")
    write_text(resolve_path(root, BOOTSTRAP_NOTES), "\n".join(BOOTSTRAP_MARKERS) + "\n")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + len(DOCS_MARKERS)
        + len(DOCS_FORBIDDEN_MARKERS)
        + len(DOCS_EXACT_COUNT_MARKERS)
        + len(TESTS_MARKERS)
        + len(TESTS_FORBIDDEN_MARKERS)
        + len(TESTS_EXACT_COUNT_MARKERS)
        + len(BOOTSTRAP_MARKERS)
        + len(BOOTSTRAP_FORBIDDEN_MARKERS)
        + len(BOOTSTRAP_EXACT_COUNT_MARKERS)
        + 3
    )
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_docs_readme_toolchain_pin_scope_") as tmp_dir:
        root = Path(tmp_dir)
        build_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in DOCS_MARKERS:
            build_root(root)
            path = resolve_path(root, DOCS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_DOCS_MARKERS", marker) in issues
            checks_run += 1

        for marker in DOCS_FORBIDDEN_MARKERS:
            build_root(root)
            path = resolve_path(root, DOCS_README)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_DOCS_MARKERS", marker) in issues
            checks_run += 1

        for marker in DOCS_EXACT_COUNT_MARKERS:
            build_root(root)
            path = resolve_path(root, DOCS_README)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("EXACT_COUNT_DOCS_MARKERS", f"2::{marker}") in issues
            checks_run += 1

        for marker in TESTS_MARKERS:
            build_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_TESTS_MARKERS", marker) in issues
            checks_run += 1

        for marker in TESTS_FORBIDDEN_MARKERS:
            build_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_TESTS_MARKERS", marker) in issues
            checks_run += 1

        for marker in TESTS_EXACT_COUNT_MARKERS:
            build_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("EXACT_COUNT_TESTS_MARKERS", f"2::{marker}") in issues
            checks_run += 1

        for marker in BOOTSTRAP_MARKERS:
            build_root(root)
            path = resolve_path(root, BOOTSTRAP_NOTES)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_BOOTSTRAP_MARKERS", marker) in issues
            checks_run += 1

        for marker in BOOTSTRAP_FORBIDDEN_MARKERS:
            build_root(root)
            path = resolve_path(root, BOOTSTRAP_NOTES)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_BOOTSTRAP_MARKERS", marker) in issues
            checks_run += 1

        for marker in BOOTSTRAP_EXACT_COUNT_MARKERS:
            build_root(root)
            path = resolve_path(root, BOOTSTRAP_NOTES)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("EXACT_COUNT_BOOTSTRAP_MARKERS", f"2::{marker}") in issues
            checks_run += 1

        for rel_path in (DOCS_README, TESTS_README, BOOTSTRAP_NOTES):
            build_root(root)
            resolve_path(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                assert str(resolve_path(root, rel_path)) in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert checks_run == expected_case_count
    print("PHASE2_DOCS_README_TOOLCHAIN_PIN_SCOPE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_DOCS_README_TOOLCHAIN_PIN_SCOPE_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the docs-root Phase 2 toolchain pin-scope packet aligned across the docs root, tests README, and bootstrap notes."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    parser.add_argument("--write-sample-root", type=Path, default=None, help="Write a minimal passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_root(args.write_sample_root.resolve())
        print(f"PHASE2_DOCS_README_TOOLCHAIN_PIN_SCOPE_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_DOCS_README_TOOLCHAIN_PIN_SCOPE_PACKET=pass")
    print(f"PHASE2_DOCS_README_TOOLCHAIN_PIN_SCOPE_PACKET_DOCS_MARKER_COUNT={len(DOCS_MARKERS)}")
    print(f"PHASE2_DOCS_README_TOOLCHAIN_PIN_SCOPE_PACKET_TESTS_MARKER_COUNT={len(TESTS_MARKERS)}")
    print(f"PHASE2_DOCS_README_TOOLCHAIN_PIN_SCOPE_PACKET_BOOTSTRAP_MARKER_COUNT={len(BOOTSTRAP_MARKERS)}")
    print(
        "PHASE2_DOCS_README_TOOLCHAIN_PIN_SCOPE_PACKET_FORBIDDEN_MARKER_COUNT="
        f"{len(DOCS_FORBIDDEN_MARKERS) + len(TESTS_FORBIDDEN_MARKERS) + len(BOOTSTRAP_FORBIDDEN_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
