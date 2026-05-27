#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

DOCS_README = ROOT / "Documentation" / "zigux" / "README.md"
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
THIRD_PARTY_README = ROOT / "third_party" / "README.md"

DOCS_README_MARKERS = (
    "`scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed Phase 2 manifest packet explicit from the docs root beside the shipped reminder and make-wrapper surfaces.",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the fixture-backed Phase 2 manifest packet explicit from the docs root beside the shipped reminder and make-wrapper surfaces.",
    "`third_party/README.md`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py` are directly readable on current `master` again, so keep the repo-local pinned archive contract",
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again",
    "`python3 scripts/zigux/validate-phase2.py`, `python3 scripts/zigux/validate-phase2-closure.py`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` replay the bounded current Phase 2 closure-side, bounded genksyms bridge, and make-wrapper packet without widening it back into older missing-route assumptions.",
)

DOCS_README_EXACT_COUNT_MARKERS = (
    "`third_party/README.md`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py` are directly readable on current `master` again, so keep the repo-local pinned archive contract",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again",
)

PHASE2_NOTES_MARKERS = (
    "`third_party/README.md` is directly readable on current `master` and keeps the repo-local pinned archive filename, digest, size, duplicate-copy boundary, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux` replay contract explicit beside the policy-driven toolchain packet.",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, and `zigux/tests/fixtures/fixdep/cases.json` keep the returned fixdep governance, parity, helper, and fixture packet explicit beside the reminder guards, and `make -C zigux phase2-fixdep` keeps its wrapper route inside the same returned make-wrapper packet.",
    "The rematerialized make-wrapper packet is directly readable on current `master` through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`, so keep those routes in the present packet instead of the repo-reality-gap list.",
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
)

REVIEW_CHECKLIST_MARKERS = (
    "`third_party/README.md`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "current directly readable Phase 2 local-first archive, toolchain, installer, direct cross-route, kbuild, kconfig bridge, docs-shared-reminder, tool-manifest, artifact-support, fixdep, genksyms-bridge, and required-make-route packet",
    "current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet",
)

TESTS_README_MARKERS = (
    "current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py`, so keep that returned repo-local pinned-archive workflow, bootstrap guard, and archive README contract explicit here instead of leaving them outside the tests-root reminder",
    "keep the local-first archive workflow replay surface explicit through `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`, `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`, and `python3 scripts/zigux/check-lane05-local-archive-readme.py`.",
    "current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`, so keep that returned fixdep governance, parity, helper, wrapper, and fixture packet explicit here instead of leaving it outside the tests-root reminder",
    "current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep that returned installer, direct cross-route, and cross-target fixture packet explicit here instead of leaving it in the historical-gap bucket",
)

THIRD_PARTY_README_MARKERS = (
    "- `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "- Lane 05 bootstrap first reuses and validates `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` when that pinned archive is present.",
    "- If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL.",
    "- `scripts/zigux/check-lane05-local-first-archive-workflow.py` and `scripts/zigux/check-lane05-local-archive-readme.py` are the shipped reminder guards for that local-first archive path.",
)

THIRD_PARTY_README_EXACT_COUNT_MARKERS = (
    "- If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL.",
    "- `scripts/zigux/check-lane05-local-first-archive-workflow.py` and `scripts/zigux/check-lane05-local-archive-readme.py` are the shipped reminder guards for that local-first archive path.",
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


def collect_missing(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_exact_count(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append((code, f"{count}::{marker}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    docs_readme = read_text(resolve_path(root, DOCS_README))
    phase2_notes = read_text(resolve_path(root, PHASE2_NOTES))
    review_checklist = read_text(resolve_path(root, REVIEW_CHECKLIST))
    tests_readme = read_text(resolve_path(root, TESTS_README))
    third_party_readme = read_text(resolve_path(root, THIRD_PARTY_README))

    issues: list[tuple[str, str]] = []
    issues.extend(collect_missing(docs_readme, DOCS_README_MARKERS, "docs-readme"))
    issues.extend(collect_exact_count(docs_readme, DOCS_README_EXACT_COUNT_MARKERS, "docs-readme-count"))
    issues.extend(collect_missing(phase2_notes, PHASE2_NOTES_MARKERS, "phase2-notes"))
    issues.extend(collect_missing(review_checklist, REVIEW_CHECKLIST_MARKERS, "review-checklist"))
    issues.extend(collect_missing(tests_readme, TESTS_README_MARKERS, "tests-readme"))
    issues.extend(collect_missing(third_party_readme, THIRD_PARTY_README_MARKERS, "third-party-readme"))
    issues.extend(collect_exact_count(third_party_readme, THIRD_PARTY_README_EXACT_COUNT_MARKERS, "third-party-readme-count"))
    return issues


def write_sample_root(root: Path) -> None:
    (root / "Documentation" / "zigux").mkdir(parents=True, exist_ok=True)
    (root / "zigux" / "tests").mkdir(parents=True, exist_ok=True)
    (root / "third_party").mkdir(parents=True, exist_ok=True)

    (root / "Documentation" / "zigux" / "README.md").write_text(
        "\n".join((" # sample".strip(), *DOCS_README_MARKERS)) + "\n",
        encoding="utf-8",
    )
    (root / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md").write_text(
        "\n".join((" # sample".strip(), *PHASE2_NOTES_MARKERS)) + "\n",
        encoding="utf-8",
    )
    (root / "Documentation" / "zigux" / "review-checklist.md").write_text(
        "\n".join((" # sample".strip(), *REVIEW_CHECKLIST_MARKERS)) + "\n",
        encoding="utf-8",
    )
    (root / "zigux" / "tests" / "README.md").write_text(
        "\n".join((" # sample".strip(), *TESTS_README_MARKERS)) + "\n",
        encoding="utf-8",
    )
    (root / "third_party" / "README.md").write_text(
        "\n".join((" # sample".strip(), *THIRD_PARTY_README_MARKERS)) + "\n",
        encoding="utf-8",
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

        docs_path = root / "Documentation" / "zigux" / "README.md"
        docs_text = docs_path.read_text(encoding="utf-8")
        docs_path.write_text(
            docs_text.replace(DOCS_README_MARKERS[2], "missing archive marker", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        cases += 1
        if not any(code == "docs-readme" for code, _ in issues):
            raise SystemExit("expected docs-readme failure for missing local-first archive marker")
        write_sample_root(root)

        notes_path = root / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
        notes_text = notes_path.read_text(encoding="utf-8")
        notes_path.write_text(
            notes_text.replace(PHASE2_NOTES_MARKERS[1], "missing fixdep marker", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        cases += 1
        if not any(code == "phase2-notes" for code, _ in issues):
            raise SystemExit("expected phase2-notes failure for missing fixdep marker")
        write_sample_root(root)

        checklist_path = root / "Documentation" / "zigux" / "review-checklist.md"
        checklist_text = checklist_path.read_text(encoding="utf-8")
        checklist_path.write_text(
            checklist_text.replace(REVIEW_CHECKLIST_MARKERS[7], "missing packet summary", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        cases += 1
        if not any(code == "review-checklist" for code, _ in issues):
            raise SystemExit("expected review-checklist failure for missing packet summary")
        write_sample_root(root)

        third_party_path = root / "third_party" / "README.md"
        third_party_text = third_party_path.read_text(encoding="utf-8")
        third_party_path.write_text(
            third_party_text + THIRD_PARTY_README_MARKERS[3] + "\n",
            encoding="utf-8",
        )
        issues = collect_issues(root)
        cases += 1
        if not any(code == "third-party-readme-count" for code, _ in issues):
            raise SystemExit("expected third-party exact-count failure for duplicate guard line")
        write_sample_root(root)

        tests_path = root / "zigux" / "tests" / "README.md"
        tests_text = tests_path.read_text(encoding="utf-8")
        tests_path.write_text(
            tests_text.replace(TESTS_README_MARKERS[2], "missing fixdep packet", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        cases += 1
        if not any(code == "tests-readme" for code, _ in issues):
            raise SystemExit("expected tests-readme failure for missing fixdep packet marker")

    print("PHASE2_DOCS_README_CURRENT_PACKET_SELF_TEST=pass")
    print(f"PHASE2_DOCS_README_CURRENT_PACKET_SELF_TEST_CASE_COUNT={cases}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fail closed when the shared Phase 2 docs-root current packet drifts on local-first archive, direct cross-route, fixdep, or companion reminder surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample root.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE2_DOCS_README_CURRENT_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return

    if args.self_test:
        run_self_test()
        return

    issues = collect_issues(args.root)
    if issues:
        for code, detail in issues:
            print(f"PHASE2_DOCS_README_CURRENT_PACKET_MISMATCH[{code}]={detail}")
        raise SystemExit(1)

    print("PHASE2_DOCS_README_CURRENT_PACKET=pass")
    print(f"PHASE2_DOCS_README_CURRENT_PACKET_DOCS_MARKER_COUNT={len(DOCS_README_MARKERS)}")
    print(f"PHASE2_DOCS_README_CURRENT_PACKET_NOTES_MARKER_COUNT={len(PHASE2_NOTES_MARKERS)}")
    print(f"PHASE2_DOCS_README_CURRENT_PACKET_REVIEW_MARKER_COUNT={len(REVIEW_CHECKLIST_MARKERS)}")
    print(f"PHASE2_DOCS_README_CURRENT_PACKET_TESTS_MARKER_COUNT={len(TESTS_README_MARKERS)}")
    print(f"PHASE2_DOCS_README_CURRENT_PACKET_THIRD_PARTY_MARKER_COUNT={len(THIRD_PARTY_README_MARKERS)}")


if __name__ == "__main__":
    main()
