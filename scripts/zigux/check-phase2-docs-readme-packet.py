#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
DOCS_README = ROOT / "Documentation" / "zigux" / "README.md"

COMPANION_PATHS = (
    ROOT / "Documentation" / "zigux" / "phase2-closure.md",
    ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md",
    ROOT / "Documentation" / "zigux" / "review-checklist.md",
    ROOT / "scripts" / "zigux" / "README.md",
    ROOT / "scripts" / "zigux" / "validate-phase2.py",
    ROOT / "scripts" / "zigux" / "validate-phase2-closure.py",
    ROOT / "zigux" / "Makefile",
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_artifact_tools_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json",
    ROOT / "zigux" / "tests" / "fixtures" / "fixdep" / "cases.json",
)

README_MARKERS = (
    "Phase 2 notes",
    "`Documentation/zigux/phase2-closure.md`",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json` - `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` - `zigux/tests/fixtures/phase2_cross_targets.json`",
    "`scripts/zigux/install-zig.py` - `scripts/zigux/check-zig-toolchain.py` - `scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py` - `scripts/zigux/check-phase2-artifact-tools-manifest.py` - `scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/validate-phase2.py` - `scripts/zigux/validate-phase2-closure.py` - `scripts/zigux/kconfig/conf_bridge.zig` - `scripts/zigux/kconfig/confdata_bridge.zig` - `scripts/zigux/genksyms.zig` - `zigux/Makefile` keep the bounded Phase 2 docs-root packet explicit through the returned closure-side validator pair, the shipped installer and direct cross-route companions, the surviving toolchain, shared-reminder, and manifest guards, the selected kconfig bridge helpers, the bounded genksyms bridge helper packet, the current manifests, and the shipped make-wrapper routes instead of treating that now-rematerialized tranche as historical-only evidence.",
    "`scripts/zigux/check-phase2-tool-manifest.py` and `scripts/zigux/check-phase2-artifact-tools-manifest.py` keep the fixture-backed Phase 2 manifest packet explicit from the docs root beside the shipped reminder and make-wrapper surfaces.",
    "`third_party/README.md`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py` are directly readable on current `master` again, so keep the repo-local pinned archive contract, the `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux` replay, the local-first `third_party`, mirror, then direct-download bootstrap order, and the two shipped Lane 05 reminder guards explicit from the docs root beside the returned toolchain packet.",
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again, so keep the installer and direct cross-route packet explicit beside the shipped toolchain, kconfig, genksyms, and make-wrapper surfaces instead of leaving them in historical-gap wording.",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again, so keep the returned fixdep governance, parity, helper, fixture, and wrapper packet explicit beside the shipped toolchain, kconfig, and genksyms surfaces instead of leaving fixdep implicit in the broader Phase 2 reminder.",
    "`python3 scripts/zigux/validate-phase2.py`, `python3 scripts/zigux/validate-phase2-closure.py`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-validate`, and `make -C zigux phase2` replay the bounded current Phase 2 closure-side, bounded genksyms bridge, and make-wrapper packet without widening it back into older missing-route assumptions.",
)

README_FORBIDDEN_MARKERS = (
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`",
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again, so keep the installer and direct cross-route packet explicit beside the shipped toolchain, kconfig, and make-wrapper surfaces instead of leaving them in historical-gap wording.",
)


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    docs_readme_text = read_text(resolve_path(root, DOCS_README))
    issues.extend(
        collect_missing_markers(
            docs_readme_text,
            README_MARKERS,
            "MISSING_DOCS_README_MARKERS",
        )
    )
    issues.extend(
        collect_forbidden_markers(
            docs_readme_text,
            README_FORBIDDEN_MARKERS,
            "FORBIDDEN_DOCS_README_MARKERS",
        )
    )
    for path in COMPANION_PATHS:
        if not resolve_path(root, path).exists():
            issues.append(("MISSING_COMPANION_PATHS", path.relative_to(ROOT).as_posix()))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_DOCS_README_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, DOCS_README), "\n".join(README_MARKERS) + "\n")
    for path in COMPANION_PATHS:
        write_text(resolve_path(root, path), "present\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(README_MARKERS) + len(README_FORBIDDEN_MARKERS) + len(COMPANION_PATHS) + 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_docs_readme_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in README_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, DOCS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_DOCS_README_MARKERS", marker) in issues
            checks_run += 1

        for marker in README_FORBIDDEN_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, DOCS_README)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_DOCS_README_MARKERS", marker) in issues
            checks_run += 1

        for companion_path in COMPANION_PATHS:
            build_sample_root(root)
            resolve_path(root, companion_path).unlink()
            issues = collect_issues(root)
            assert ("MISSING_COMPANION_PATHS", companion_path.relative_to(ROOT).as_posix()) in issues
            checks_run += 1

        build_sample_root(root)
        resolve_path(root, DOCS_README).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            assert str(resolve_path(root, DOCS_README)) in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing docs README did not abort")

    assert checks_run == expected_case_count
    print("PHASE2_DOCS_README_PACKET_SELF_TEST=pass")
    print(f"PHASE2_DOCS_README_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the docs-root Phase 2 reminder packet aligned to current repo reality."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root for focused replay",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_DOCS_README_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_DOCS_README_PACKET=pass")
    print(f"PHASE2_DOCS_README_PACKET_MARKER_COUNT={len(README_MARKERS)}")
    print(f"PHASE2_DOCS_README_PACKET_FORBIDDEN_MARKER_COUNT={len(README_FORBIDDEN_MARKERS)}")
    print(f"PHASE2_DOCS_README_PACKET_COMPANION_COUNT={len(COMPANION_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
