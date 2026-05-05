#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

TOOLCHAIN_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
CLOSURE_DOC = Path("Documentation/zigux/phase2-closure.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
VALIDATE_PHASE2 = Path("scripts/zigux/validate-phase2.py")
VALIDATE_PHASE2_CLOSURE = Path("scripts/zigux/validate-phase2-closure.py")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
TARGETS = Path("zigux/tests/fixtures/phase2_cross_targets.json")

REQUIRED_FILES = [
    TOOLCHAIN_NOTES,
    CLOSURE_DOC,
    REVIEW_CHECKLIST,
    VALIDATE_PHASE2,
    VALIDATE_PHASE2_CLOSURE,
    WORKFLOW,
    MAKEFILE,
    TARGETS,
]

EXPECTED_TARGETS = [
    "x86_64-linux-musl",
    "aarch64-linux-musl",
    "riscv64-linux-musl",
]

TOOLCHAIN_NOTE_MARKERS = [
    "python3 scripts/zigux/check-phase2-cross.py --self-test",
    "python3 scripts/zigux/check-phase2-cross.py",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "the three-target compile matrix in `zigux/tests/fixtures/phase2_cross_targets.json` stays separate from the `x86_64-linux` bootstrap archive pin",
]

CLOSURE_MARKERS = [
    "PHASE2_CROSS_TARGET_COUNT=3",
    "PHASE2_CROSS_SELF_TEST=python3 scripts/zigux/check-phase2-cross.py --self-test",
    "PHASE2_CROSS_GATE=python3 scripts/zigux/check-phase2-cross.py",
    "PHASE2_CROSS_ALIGNMENT_SELF_TEST=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "PHASE2_CROSS_ALIGNMENT_GATE=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
]

REVIEW_CHECKLIST_MARKERS = [
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
]

VALIDATE_PHASE2_MARKERS = [
    "check-phase2-cross-selftest-alignment.py",
    "phase2_cross_targets.json",
]

VALIDATE_PHASE2_CLOSURE_MARKERS = [
    "CHECK_PHASE2_CROSS_SELFTEST_ALIGNMENT = ROOT / 'scripts' / 'zigux' / 'check-phase2-cross-selftest-alignment.py'",
    "PHASE2_CROSS_SELF_TEST=python3 scripts/zigux/check-phase2-cross.py --self-test",
    "PHASE2_CROSS_GATE=python3 scripts/zigux/check-phase2-cross.py",
    "PHASE2_CROSS_ALIGNMENT_SELF_TEST=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "PHASE2_CROSS_ALIGNMENT_GATE=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
]

WORKFLOW_MARKERS = [
    "python3 scripts/zigux/check-phase2-cross.py --self-test",
    "python3 scripts/zigux/check-phase2-cross.py --target",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
]

MAKEFILE_MARKERS = [
    "check-phase2-cross.py --self-test",
    "check-phase2-cross-selftest-alignment.py --self-test",
    "check-phase2-cross-selftest-alignment.py",
    "phase2-cross:",
]


def abspath(root: Path, rel: Path) -> Path:
    return root / rel


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
        if not abspath(root, rel).exists():
            issues.append(f"missing_file:{rel.as_posix()}")
    if issues:
        return issues

    issues.extend(
        collect_missing_markers(
            abspath(root, TOOLCHAIN_NOTES).read_text(encoding="utf-8"),
            TOOLCHAIN_NOTE_MARKERS,
            prefix="toolchain_notes",
        )
    )
    issues.extend(
        collect_missing_markers(
            abspath(root, CLOSURE_DOC).read_text(encoding="utf-8"),
            CLOSURE_MARKERS,
            prefix="closure_doc",
        )
    )
    issues.extend(
        collect_missing_markers(
            abspath(root, REVIEW_CHECKLIST).read_text(encoding="utf-8"),
            REVIEW_CHECKLIST_MARKERS,
            prefix="review_checklist",
        )
    )
    issues.extend(
        collect_missing_markers(
            abspath(root, VALIDATE_PHASE2).read_text(encoding="utf-8"),
            VALIDATE_PHASE2_MARKERS,
            prefix="validate_phase2",
        )
    )
    issues.extend(
        collect_missing_markers(
            abspath(root, VALIDATE_PHASE2_CLOSURE).read_text(encoding="utf-8"),
            VALIDATE_PHASE2_CLOSURE_MARKERS,
            prefix="validate_phase2_closure",
        )
    )
    issues.extend(
        collect_missing_markers(
            abspath(root, WORKFLOW).read_text(encoding="utf-8"),
            WORKFLOW_MARKERS,
            prefix="workflow",
        )
    )
    issues.extend(
        collect_missing_markers(
            abspath(root, MAKEFILE).read_text(encoding="utf-8"),
            MAKEFILE_MARKERS,
            prefix="makefile",
        )
    )
    issues.extend(validate_targets_manifest(abspath(root, TARGETS)))
    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(abspath(root, TOOLCHAIN_NOTES), "\n".join(TOOLCHAIN_NOTE_MARKERS) + "\n")
    write_text(abspath(root, CLOSURE_DOC), "\n".join(CLOSURE_MARKERS) + "\n")
    write_text(abspath(root, REVIEW_CHECKLIST), "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(abspath(root, VALIDATE_PHASE2), "\n".join(VALIDATE_PHASE2_MARKERS) + "\n")
    write_text(
        abspath(root, VALIDATE_PHASE2_CLOSURE),
        "\n".join(VALIDATE_PHASE2_CLOSURE_MARKERS) + "\n",
    )
    write_text(abspath(root, WORKFLOW), "\n".join(WORKFLOW_MARKERS) + "\n")
    write_text(abspath(root, MAKEFILE), "\n".join(MAKEFILE_MARKERS) + "\n")
    write_text(
        abspath(root, TARGETS),
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "closed",
                "target_count": len(EXPECTED_TARGETS),
                "targets": EXPECTED_TARGETS,
            }
        )
        + "\n",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase2_cross_selftest_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert validate_root(root) == []

        payload = load_json_object(abspath(root, TARGETS), label="phase2_cross_targets")
        payload["phase"] = "Phase 3"
        write_text(abspath(root, TARGETS), json.dumps(payload) + "\n")
        issues = validate_root(root)
        assert "targets:phase='Phase 3':expected='Phase 2'" in issues

        build_self_test_root(root)
        payload = load_json_object(abspath(root, TARGETS), label="phase2_cross_targets")
        payload["status"] = "open"
        write_text(abspath(root, TARGETS), json.dumps(payload) + "\n")
        issues = validate_root(root)
        assert "targets:status='open':expected='closed'" in issues

        build_self_test_root(root)
        payload = load_json_object(abspath(root, TARGETS), label="phase2_cross_targets")
        payload["target_count"] = 2
        write_text(abspath(root, TARGETS), json.dumps(payload) + "\n")
        issues = validate_root(root)
        assert "targets:target_count=2:expected=3" in issues

        build_self_test_root(root)
        payload = load_json_object(abspath(root, TARGETS), label="phase2_cross_targets")
        payload["targets"] = [
            "x86_64-linux-musl",
            "x86_64-linux-musl",
            "riscv64-linux-musl",
        ]
        write_text(abspath(root, TARGETS), json.dumps(payload) + "\n")
        issues = validate_root(root)
        assert (
            "targets:list=['x86_64-linux-musl', 'x86_64-linux-musl', 'riscv64-linux-musl']:expected=['x86_64-linux-musl', 'aarch64-linux-musl', 'riscv64-linux-musl']"
            in issues
        )

        build_self_test_root(root)
        write_text(abspath(root, VALIDATE_PHASE2), "phase2_cross_targets.json\n")
        issues = validate_root(root)
        assert "validate_phase2:check-phase2-cross-selftest-alignment.py" in issues

        build_self_test_root(root)
        write_text(abspath(root, VALIDATE_PHASE2_CLOSURE), "PHASE2_CROSS_ALIGNMENT_GATE\n")
        issues = validate_root(root)
        assert (
            "validate_phase2_closure:CHECK_PHASE2_CROSS_SELFTEST_ALIGNMENT = ROOT / 'scripts' / 'zigux' / 'check-phase2-cross-selftest-alignment.py'"
            in issues
        )

        build_self_test_root(root)
        write_text(abspath(root, WORKFLOW), "python3 scripts/zigux/check-phase2-cross.py --target\n")
        issues = validate_root(root)
        assert "workflow:python3 scripts/zigux/check-phase2-cross.py --self-test" in issues

        build_self_test_root(root)
        write_text(abspath(root, MAKEFILE), "phase2-cross:\n")
        issues = validate_root(root)
        assert "makefile:check-phase2-cross.py --self-test" in issues

        build_self_test_root(root)
        write_text(abspath(root, TOOLCHAIN_NOTES), "python3 scripts/zigux/check-phase2-cross.py\n")
        issues = validate_root(root)
        assert "toolchain_notes:python3 scripts/zigux/check-phase2-cross.py --self-test" in issues

        build_self_test_root(root)
        abspath(root, TARGETS).unlink()
        issues = validate_root(root)
        assert "missing_file:zigux/tests/fixtures/phase2_cross_targets.json" in issues

    print("PHASE2_CROSS_SELFTEST_ALIGNMENT_SELF_TEST=pass")
    print("PHASE2_CROSS_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT=10")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Keep the Phase 2 cross-target self-test note, workflow, Makefile, "
            "closure references, and manifest aligned with the current checker packet."
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
        f"{len(TOOLCHAIN_NOTE_MARKERS) + len(CLOSURE_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(VALIDATE_PHASE2_MARKERS) + len(VALIDATE_PHASE2_CLOSURE_MARKERS) + len(WORKFLOW_MARKERS) + len(MAKEFILE_MARKERS) + len(EXPECTED_TARGETS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
