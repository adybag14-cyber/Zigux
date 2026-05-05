#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


THIS_FILE = Path(__file__).resolve()
ROOT = THIS_FILE.parents[2] if len(THIS_FILE.parents) > 2 else THIS_FILE.parent

NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
REVIEW = ROOT / "Documentation" / "zigux" / "review-checklist.md"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
TARGETS = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
PHASE2_CLOSURE_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2-closure.py"
PHASE2_CROSS_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"
TOOLCHAIN_PIN_SCOPE_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py"
INSTALL_ZIG = ROOT / "scripts" / "zigux" / "install-zig.py"
CHECK_ZIG_TOOLCHAIN = ROOT / "scripts" / "zigux" / "check-zig-toolchain.py"

EXPECTED_TARGETS = [
    "x86_64-linux-musl",
    "aarch64-linux-musl",
    "riscv64-linux-musl",
]

NOTES_MARKERS = [
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
]

CLOSURE_MARKERS = [
    "PHASE2_CROSS_ALIGNMENT_SELF_TEST=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "PHASE2_CROSS_ALIGNMENT_GATE=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
]

REVIEW_MARKERS = [
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-cross.py",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
]

MAKEFILE_MARKERS = [
    "phase2-cross:",
    "scripts/zigux/check-phase2-cross.py",
    "phase2: phase2-validate phase2-tools phase2-kconfig phase2-cross",
]

PHASE2_CLOSURE_VALIDATOR_MARKERS = [
    "CHECK_PHASE2_CROSS_SELFTEST_ALIGNMENT = ROOT / 'scripts' / 'zigux' / 'check-phase2-cross-selftest-alignment.py'",
    "'PHASE2_CROSS_ALIGNMENT_SELF_TEST=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test'",
    "'PHASE2_CROSS_ALIGNMENT_GATE=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py'",
]

PHASE2_CROSS_CHECKER_MARKERS = [
    "PHASE2_CROSS_SELF_TEST=pass",
    "PHASE2_CROSS=pass",
    "phase2_cross_targets.json",
]

TOOLCHAIN_PIN_SCOPE_MARKERS = [
    "phase2_cross_targets.json",
    "check-phase2-cross-selftest-alignment.py --self-test",
    "check-phase2-cross-selftest-alignment.py",
]

INSTALL_ZIG_MARKERS = [
    "ZIG_INSTALL_SELF_TEST=pass",
]

CHECK_ZIG_TOOLCHAIN_MARKERS = [
    "ZIG_TOOLCHAIN_SELF_TEST=pass",
]


def load_json_object(path: Path, *, label: str) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"{label}:expected_object")
    return payload


def collect_missing_markers(text: str, *, label: str, markers: list[str]) -> list[str]:
    return [f"{label}:missing_marker:{marker}" for marker in markers if marker not in text]


def validate_targets_manifest(path: Path) -> list[str]:
    payload = load_json_object(path, label="phase2_cross_targets")
    issues: list[str] = []

    if payload.get("phase") != "Phase 2":
        issues.append("phase2_cross_targets:phase:expected=Phase 2")
    if payload.get("status") != "closed":
        issues.append("phase2_cross_targets:status:expected=closed")

    targets = payload.get("targets")
    if not isinstance(targets, list):
        issues.append("phase2_cross_targets:targets:expected_list")
        return issues

    if payload.get("target_count") != len(targets):
        issues.append(
            f"phase2_cross_targets:target_count={payload.get('target_count')}:expected={len(targets)}"
        )

    seen: set[str] = set()
    discovered: list[str] = []
    for index, item in enumerate(targets):
        if not isinstance(item, str) or not item:
            issues.append(f"phase2_cross_targets:targets[{index}]:expected_nonempty_string")
            continue
        if item in seen:
            issues.append(f"phase2_cross_targets:duplicate_target:{item}")
            continue
        seen.add(item)
        discovered.append(item)

    if discovered != EXPECTED_TARGETS:
        issues.append(f"phase2_cross_targets:targets={discovered!r}:expected={EXPECTED_TARGETS!r}")
    return issues


def validate_workflow(text: str) -> list[str]:
    issues: list[str] = []
    if "phase2-cross:" in text:
        issues.append("workflow:unexpected_makefile_fragment:phase2-cross:")

    required_fragments = [
        "name: phase2-cross",
        "python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}",
    ]
    issues.extend(collect_missing_markers(text, label="workflow", markers=required_fragments))

    for target in EXPECTED_TARGETS:
        if target not in text:
            issues.append(f"workflow:missing_target:{target}")
    return issues


def validate_root(root: Path) -> list[str]:
    required_files = [
        NOTES,
        CLOSURE,
        REVIEW,
        WORKFLOW,
        MAKEFILE,
        TARGETS,
        PHASE2_CLOSURE_VALIDATOR,
        PHASE2_CROSS_CHECKER,
        TOOLCHAIN_PIN_SCOPE_CHECKER,
        INSTALL_ZIG,
        CHECK_ZIG_TOOLCHAIN,
    ]
    missing_files = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
    if missing_files:
        return [f"missing_file:{item}" for item in missing_files]

    issues: list[str] = []
    issues.extend(collect_missing_markers(NOTES.read_text(encoding="utf-8"), label="notes", markers=NOTES_MARKERS))
    issues.extend(collect_missing_markers(CLOSURE.read_text(encoding="utf-8"), label="closure", markers=CLOSURE_MARKERS))
    issues.extend(collect_missing_markers(REVIEW.read_text(encoding="utf-8"), label="review", markers=REVIEW_MARKERS))
    issues.extend(collect_missing_markers(MAKEFILE.read_text(encoding="utf-8"), label="makefile", markers=MAKEFILE_MARKERS))
    issues.extend(
        collect_missing_markers(
            PHASE2_CLOSURE_VALIDATOR.read_text(encoding="utf-8"),
            label="phase2_closure_validator",
            markers=PHASE2_CLOSURE_VALIDATOR_MARKERS,
        )
    )
    issues.extend(
        collect_missing_markers(
            PHASE2_CROSS_CHECKER.read_text(encoding="utf-8"),
            label="phase2_cross_checker",
            markers=PHASE2_CROSS_CHECKER_MARKERS,
        )
    )
    issues.extend(
        collect_missing_markers(
            TOOLCHAIN_PIN_SCOPE_CHECKER.read_text(encoding="utf-8"),
            label="toolchain_pin_scope_checker",
            markers=TOOLCHAIN_PIN_SCOPE_MARKERS,
        )
    )
    issues.extend(
        collect_missing_markers(
            INSTALL_ZIG.read_text(encoding="utf-8"),
            label="install_zig",
            markers=INSTALL_ZIG_MARKERS,
        )
    )
    issues.extend(
        collect_missing_markers(
            CHECK_ZIG_TOOLCHAIN.read_text(encoding="utf-8"),
            label="check_zig_toolchain",
            markers=CHECK_ZIG_TOOLCHAIN_MARKERS,
        )
    )
    issues.extend(validate_targets_manifest(TARGETS))
    issues.extend(validate_workflow(WORKFLOW.read_text(encoding="utf-8")))
    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(
        root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
        "\n".join(NOTES_MARKERS) + "\n",
    )
    write_text(
        root / "Documentation/zigux/phase2-closure.md",
        "\n".join(CLOSURE_MARKERS) + "\n",
    )
    write_text(
        root / "Documentation/zigux/review-checklist.md",
        "\n".join(REVIEW_MARKERS) + "\n",
    )
    write_text(
        root / ".github/workflows/zigux-bootstrap.yml",
        "\n".join(
            [
                "name: phase2-cross",
                "x86_64-linux-musl",
                "aarch64-linux-musl",
                "riscv64-linux-musl",
                "python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}",
            ]
        )
        + "\n",
    )
    write_text(
        root / "zigux/Makefile",
        "\n".join(MAKEFILE_MARKERS) + "\n",
    )
    write_text(
        root / "scripts/zigux/validate-phase2-closure.py",
        "\n".join(PHASE2_CLOSURE_VALIDATOR_MARKERS) + "\n",
    )
    write_text(
        root / "scripts/zigux/check-phase2-cross.py",
        "\n".join(PHASE2_CROSS_CHECKER_MARKERS) + "\n",
    )
    write_text(
        root / "scripts/zigux/check-phase2-toolchain-pin-scope.py",
        "\n".join(TOOLCHAIN_PIN_SCOPE_MARKERS) + "\n",
    )
    write_text(
        root / "scripts/zigux/install-zig.py",
        "\n".join(INSTALL_ZIG_MARKERS) + "\n",
    )
    write_text(
        root / "scripts/zigux/check-zig-toolchain.py",
        "\n".join(CHECK_ZIG_TOOLCHAIN_MARKERS) + "\n",
    )
    write_text(
        root / "zigux/tests/fixtures/phase2_cross_targets.json",
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "closed",
                "target_count": 3,
                "targets": EXPECTED_TARGETS,
            }
        ),
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase2_cross_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        global ROOT, NOTES, CLOSURE, REVIEW, WORKFLOW, MAKEFILE, TARGETS
        global PHASE2_CLOSURE_VALIDATOR, PHASE2_CROSS_CHECKER
        global TOOLCHAIN_PIN_SCOPE_CHECKER, INSTALL_ZIG, CHECK_ZIG_TOOLCHAIN

        original_root = ROOT
        original_paths = (
            NOTES,
            CLOSURE,
            REVIEW,
            WORKFLOW,
            MAKEFILE,
            TARGETS,
            PHASE2_CLOSURE_VALIDATOR,
            PHASE2_CROSS_CHECKER,
            TOOLCHAIN_PIN_SCOPE_CHECKER,
            INSTALL_ZIG,
            CHECK_ZIG_TOOLCHAIN,
        )

        ROOT = root
        NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
        CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
        REVIEW = ROOT / "Documentation" / "zigux" / "review-checklist.md"
        WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
        MAKEFILE = ROOT / "zigux" / "Makefile"
        TARGETS = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
        PHASE2_CLOSURE_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2-closure.py"
        PHASE2_CROSS_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"
        TOOLCHAIN_PIN_SCOPE_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py"
        INSTALL_ZIG = ROOT / "scripts" / "zigux" / "install-zig.py"
        CHECK_ZIG_TOOLCHAIN = ROOT / "scripts" / "zigux" / "check-zig-toolchain.py"

        try:
            build_self_test_root(root)
            assert validate_root(root) == []

            write_text(WORKFLOW, "name: phase2-cross\n")
            issues = validate_root(root)
            assert "workflow:missing_target:x86_64-linux-musl" in issues
            assert (
                "workflow:missing_marker:python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}"
                in issues
            )

            build_self_test_root(root)
            write_text(
                TARGETS,
                json.dumps(
                    {
                        "phase": "Phase 2",
                        "status": "closed",
                        "target_count": 3,
                        "targets": ["x86_64-linux-musl", "x86_64-linux-musl", "riscv64-linux-musl"],
                    }
                ),
            )
            issues = validate_root(root)
            assert "phase2_cross_targets:duplicate_target:x86_64-linux-musl" in issues

            build_self_test_root(root)
            write_text(REVIEW, "scripts/zigux/check-phase2-cross.py\n")
            issues = validate_root(root)
            assert "review:missing_marker:scripts/zigux/check-phase2-cross-selftest-alignment.py" in issues
        finally:
            ROOT = original_root
            (
                NOTES,
                CLOSURE,
                REVIEW,
                WORKFLOW,
                MAKEFILE,
                TARGETS,
                PHASE2_CLOSURE_VALIDATOR,
                PHASE2_CROSS_CHECKER,
                TOOLCHAIN_PIN_SCOPE_CHECKER,
                INSTALL_ZIG,
                CHECK_ZIG_TOOLCHAIN,
            ) = original_paths

    print("PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass")
    print("PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the bounded Phase 2 cross-target self-test contract aligned across docs, workflow, and validators."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in alignment coverage without a repo checkout.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_root(ROOT)
    if issues:
        print("PHASE2_CROSS_ALIGNMENT=fail")
        print("PHASE2_CROSS_ALIGNMENT_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_CROSS_ALIGNMENT_ISSUES_END")
        return 1

    print("PHASE2_CROSS_ALIGNMENT=pass")
    print("PHASE2_CROSS_ALIGNMENT_TARGET_COUNT=3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
