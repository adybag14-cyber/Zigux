#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    ".github/workflows/zigux-bootstrap.yml",
]

EXPECTED_TARGETS = [
    "x86_64-linux-musl",
    "aarch64-linux-musl",
    "riscv64-linux-musl",
]

DOCS_ROOT_MARKERS = [
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "python3 scripts/zigux/check-phase2-cross.py",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
]

TOOLCHAIN_NOTE_MARKERS = [
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "Documentation/zigux/README.md",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
]

REVIEW_CHECKLIST_MARKERS = [
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
]

TESTS_README_MARKERS = [
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
]

VALIDATE_PHASE2_MARKERS = [
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/check-phase2-cross.py --target",
]

VALIDATE_PHASE2_CLOSURE_MARKERS = [
    "CHECK_PHASE2_CROSS_SELFTEST_ALIGNMENT = ROOT / 'scripts' / 'zigux' / 'check-phase2-cross-selftest-alignment.py'",
    "PHASE2_CROSS_ALIGNMENT_SELF_TEST=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "PHASE2_CROSS_ALIGNMENT_GATE=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
]

MAKEFILE_MARKERS = [
    "phase2-validate:",
    "check-phase2-tests-readme-alignment.py",
    "phase2-cross:",
    "scripts/zigux/check-phase2-cross.py",
]

WORKFLOW_MARKERS = [
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py",
    "python3 scripts/zigux/check-phase2-cross.py --target",
]


def load_json_object(path: Path, *, label: str) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"{label}:expected_object")
    return payload


def collect_missing_markers(text: str, markers: list[str], *, prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def validate_targets_manifest(path: Path) -> list[str]:
    payload = load_json_object(path, label="phase2_cross_targets")
    issues: list[str] = []
    if payload.get("phase") != "Phase 2":
        issues.append(f"targets:phase={payload.get('phase')!r}:expected='Phase 2'")
    if payload.get("status") != "closed":
        issues.append(f"targets:status={payload.get('status')!r}:expected='closed'")
    if payload.get("target_count") != len(EXPECTED_TARGETS):
        issues.append(
            "targets:target_count="
            f"{payload.get('target_count')!r}:expected={len(EXPECTED_TARGETS)}"
        )
    targets = payload.get("targets")
    if targets != EXPECTED_TARGETS:
        issues.append(f"targets:list={targets!r}:expected={EXPECTED_TARGETS!r}")
    return issues


def validate_root(root: Path) -> list[str]:
    issues: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")

    if issues:
        return issues

    docs_root = (root / "Documentation/zigux/README.md").read_text(encoding="utf-8")
    toolchain_notes = (
        root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
    ).read_text(encoding="utf-8")
    review = (root / "Documentation/zigux/review-checklist.md").read_text(encoding="utf-8")
    tests_readme = (root / "zigux/tests/README.md").read_text(encoding="utf-8")
    validate_phase2 = (root / "scripts/zigux/validate-phase2.py").read_text(encoding="utf-8")
    validate_phase2_closure = (
        root / "scripts/zigux/validate-phase2-closure.py"
    ).read_text(encoding="utf-8")
    makefile = (root / "zigux/Makefile").read_text(encoding="utf-8")
    workflow = (
        root / ".github/workflows/zigux-bootstrap.yml"
    ).read_text(encoding="utf-8")

    issues.extend(collect_missing_markers(docs_root, DOCS_ROOT_MARKERS, prefix="docs_root"))
    issues.extend(
        collect_missing_markers(
            toolchain_notes,
            TOOLCHAIN_NOTE_MARKERS,
            prefix="toolchain_notes",
        )
    )
    issues.extend(
        collect_missing_markers(
            review,
            REVIEW_CHECKLIST_MARKERS,
            prefix="review_checklist",
        )
    )
    issues.extend(
        collect_missing_markers(
            tests_readme,
            TESTS_README_MARKERS,
            prefix="tests_readme",
        )
    )
    issues.extend(
        collect_missing_markers(
            validate_phase2,
            VALIDATE_PHASE2_MARKERS,
            prefix="validate_phase2",
        )
    )
    issues.extend(
        collect_missing_markers(
            validate_phase2_closure,
            VALIDATE_PHASE2_CLOSURE_MARKERS,
            prefix="validate_phase2_closure",
        )
    )
    issues.extend(collect_missing_markers(makefile, MAKEFILE_MARKERS, prefix="makefile"))
    issues.extend(collect_missing_markers(workflow, WORKFLOW_MARKERS, prefix="workflow"))
    issues.extend(
        validate_targets_manifest(root / "zigux/tests/fixtures/phase2_cross_targets.json")
    )
    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        write_text(root / rel, "")

    write_text(
        root / "Documentation/zigux/README.md",
        "\n".join(DOCS_ROOT_MARKERS) + "\n",
    )
    write_text(
        root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
        "\n".join(TOOLCHAIN_NOTE_MARKERS) + "\n",
    )
    write_text(
        root / "Documentation/zigux/review-checklist.md",
        "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n",
    )
    write_text(
        root / "zigux/tests/README.md",
        "\n".join(TESTS_README_MARKERS) + "\n",
    )
    write_text(
        root / "scripts/zigux/validate-phase2.py",
        "\n".join(VALIDATE_PHASE2_MARKERS) + "\n",
    )
    write_text(
        root / "scripts/zigux/validate-phase2-closure.py",
        "\n".join(VALIDATE_PHASE2_CLOSURE_MARKERS) + "\n",
    )
    write_text(
        root / "zigux/Makefile",
        "\n".join(MAKEFILE_MARKERS) + "\n",
    )
    write_text(
        root / ".github/workflows/zigux-bootstrap.yml",
        "\n".join(WORKFLOW_MARKERS) + "\n",
    )
    write_text(
        root / "zigux/tests/fixtures/phase2_cross_targets.json",
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "closed",
                "target_count": len(EXPECTED_TARGETS),
                "targets": EXPECTED_TARGETS,
            }
        ),
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase2_cross_selftest_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)

        assert validate_root(root) == []

        write_text(root / "Documentation/zigux/README.md", "scripts/zigux/validate-phase2.py\n")
        issues = validate_root(root)
        assert "docs_root:make -C zigux phase2-validate" in issues

        build_self_test_root(root)
        write_text(
            root / "zigux/tests/fixtures/phase2_cross_targets.json",
            json.dumps(
                {
                    "phase": "Phase 2",
                    "status": "closed",
                    "target_count": 2,
                    "targets": EXPECTED_TARGETS[:2],
                }
            ),
        )
        issues = validate_root(root)
        assert "targets:target_count=2:expected=3" in issues

        build_self_test_root(root)
        write_text(
            root / "scripts/zigux/validate-phase2-closure.py",
            "PHASE2_CROSS_ALIGNMENT_GATE=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py\n",
        )
        issues = validate_root(root)
        assert (
            "validate_phase2_closure:PHASE2_CROSS_ALIGNMENT_SELF_TEST=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test"
            in issues
        )

        build_self_test_root(root)
        (root / "scripts/zigux/check-phase2-cross-selftest-alignment.py").unlink()
        issues = validate_root(root)
        assert (
            "missing_file:scripts/zigux/check-phase2-cross-selftest-alignment.py"
            in issues
        )

    print("PHASE2_CROSS_SELFTEST_ALIGNMENT_SELF_TEST=pass")
    print("PHASE2_CROSS_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Keep the Phase 2 cross-target self-test note and closure references "
            "aligned with the current docs, validators, Makefile, workflow, and "
            "three-target compile manifest."
        )
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in alignment coverage without a repo checkout.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_root(ROOT)
    if issues:
        print("PHASE2_CROSS_SELFTEST_ALIGNMENT=fail")
        print("PHASE2_CROSS_SELFTEST_ALIGNMENT_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_CROSS_SELFTEST_ALIGNMENT_ISSUES_END")
        return 1

    print("PHASE2_CROSS_SELFTEST_ALIGNMENT=pass")
    print(
        "PHASE2_CROSS_SELFTEST_ALIGNMENT_MARKER_COUNT="
        f"{len(DOCS_ROOT_MARKERS) + len(TOOLCHAIN_NOTE_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(TESTS_README_MARKERS) + len(VALIDATE_PHASE2_MARKERS) + len(VALIDATE_PHASE2_CLOSURE_MARKERS) + len(MAKEFILE_MARKERS) + len(WORKFLOW_MARKERS) + len(EXPECTED_TARGETS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
