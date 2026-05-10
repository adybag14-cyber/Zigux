#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path(".")

TOOLCHAIN_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
CLOSURE_DOC = Path("Documentation/zigux/phase2-closure.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
SCRIPT_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
VALIDATE_PHASE2 = Path("scripts/zigux/validate-phase2.py")
VALIDATE_PHASE2_CLOSURE = Path("scripts/zigux/validate-phase2-closure.py")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
TARGETS = Path("zigux/tests/fixtures/phase2_cross_targets.json")

REQUIRED_FILES = [
    TOOLCHAIN_NOTES,
    CLOSURE_DOC,
    REVIEW_CHECKLIST,
    SCRIPT_README,
    TESTS_README,
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

EXPECTED_TOOLS = [
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_crc.zig",
    "scripts/zigux/mk_elfconfig.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
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
    "scripts/zigux/check-phase2-cross.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "make -C zigux phase2-cross",
]

SCRIPT_README_MARKERS = [
    "check-phase2-cross-selftest-alignment.py",
    "check-phase2-cross.py",
    "phase2_cross_targets.json",
    "bounded three-target compile matrix",
]

TESTS_README_MARKERS = [
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-cross.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "bounded three-target compile matrix",
]

VALIDATE_PHASE2_MARKERS = [
    "check-phase2-cross-selftest-alignment.py",
    "phase2_cross_targets.json",
]

VALIDATE_PHASE2_CLOSURE_MARKERS = [
    'CHECK_PHASE2_CROSS_SELFTEST_ALIGNMENT = ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"',
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

WORKFLOW_SCOPE_JOB_MARKER = "phase2-cross-scope:"
WORKFLOW_SCOPE_MARKERS = [
    "Detect Phase 2 cross-target scope changes",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "scripts/zigux/zig-toolchain-policy.json",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "should_run=true",
    "should_run=false",
]

EXACT_WORKFLOW_RUN_COUNTS = {
    "python3 scripts/zigux/check-phase2-cross.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}": 1,
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py": 1,
}

MAKEFILE_MARKERS = [
    "check-phase2-cross.py --self-test",
    "check-phase2-cross-selftest-alignment.py --self-test",
    "check-phase2-cross-selftest-alignment.py",
    "phase2-cross:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py",
]

EXACT_MAKEFILE_RUN_COUNTS = {
    "scripts/zigux/check-phase2-cross.py --self-test": 1,
    "scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test": 1,
    "scripts/zigux/check-phase2-cross-selftest-alignment.py": 1,
    "scripts/zigux/check-phase2-cross.py": 1,
}


def abspath(root: Path, rel: Path) -> Path:
    return root / rel


def load_json_object(path: Path, *, label: str) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"{label}:expected_object")
    return payload


def collect_missing_markers(text: str, markers: list[str], *, prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def validate_exact_workflow_runs(text: str) -> list[str]:
    issues: list[str] = []
    lines = [line.strip() for line in text.splitlines()]
    for command, expected_count in EXACT_WORKFLOW_RUN_COUNTS.items():
        expected_line = f"run: {command}"
        count = sum(1 for line in lines if line == expected_line)
        if count != expected_count:
            issues.append(f"workflow_exact_run:{command}:count={count}:expected={expected_count}")
    return issues


def validate_exact_makefile_runs(text: str) -> list[str]:
    issues: list[str] = []
    lines = [line.strip() for line in text.splitlines()]
    for command, expected_count in EXACT_MAKEFILE_RUN_COUNTS.items():
        expected_line = f"cd $(ZIGUX_ROOT) && $(PYTHON) {command}"
        count = sum(1 for line in lines if line == expected_line)
        if count != expected_count:
            issues.append(f"makefile_exact_run:{command}:count={count}:expected={expected_count}")
    return issues


def validate_targets_manifest(path: Path) -> list[str]:
    payload = load_json_object(path, label="phase2_cross_targets")
    issues: list[str] = []
    if payload.get("phase") != "Phase 2":
        issues.append(f"targets:phase={payload.get('phase')!r}:expected='Phase 2'")
    if payload.get("status") != "closed":
        issues.append(f"targets:status={payload.get('status')!r}:expected='closed'")
    if payload.get("target_count") != len(EXPECTED_TARGETS):
        issues.append(f"targets:target_count={payload.get('target_count')!r}:expected={len(EXPECTED_TARGETS)}")
    targets = payload.get("targets")
    if targets != EXPECTED_TARGETS:
        issues.append(f"targets:list={targets!r}:expected={EXPECTED_TARGETS!r}")
    if payload.get("tool_count") != len(EXPECTED_TOOLS):
        issues.append(f"targets:tool_count={payload.get('tool_count')!r}:expected={len(EXPECTED_TOOLS)}")
    tools = payload.get("tools")
    if tools != EXPECTED_TOOLS:
        issues.append(f"targets:tools={tools!r}:expected={EXPECTED_TOOLS!r}")
    return issues


def extract_phase2_cross_scope_block(text: str) -> str:
    start = text.find(WORKFLOW_SCOPE_JOB_MARKER)
    if start == -1:
        return ""
    end = text.find("\n  phase2-cross:\n", start)
    if end == -1:
        return ""
    return text[start:end]


def validate_root(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in REQUIRED_FILES:
        if not abspath(root, rel).exists():
            issues.append(f"missing_file:{rel.as_posix()}")
    if issues:
        return issues

    issues.extend(collect_missing_markers(abspath(root, TOOLCHAIN_NOTES).read_text(encoding="utf-8"), TOOLCHAIN_NOTE_MARKERS, prefix="toolchain_notes"))
    issues.extend(collect_missing_markers(abspath(root, CLOSURE_DOC).read_text(encoding="utf-8"), CLOSURE_MARKERS, prefix="closure_doc"))
    issues.extend(collect_missing_markers(abspath(root, REVIEW_CHECKLIST).read_text(encoding="utf-8"), REVIEW_CHECKLIST_MARKERS, prefix="review_checklist"))
    issues.extend(collect_missing_markers(abspath(root, SCRIPT_README).read_text(encoding="utf-8"), SCRIPT_README_MARKERS, prefix="script_readme"))
    issues.extend(collect_missing_markers(abspath(root, TESTS_README).read_text(encoding="utf-8"), TESTS_README_MARKERS, prefix="tests_readme"))
    issues.extend(collect_missing_markers(abspath(root, VALIDATE_PHASE2).read_text(encoding="utf-8"), VALIDATE_PHASE2_MARKERS, prefix="validate_phase2"))
    issues.extend(collect_missing_markers(abspath(root, VALIDATE_PHASE2_CLOSURE).read_text(encoding="utf-8"), VALIDATE_PHASE2_CLOSURE_MARKERS, prefix="validate_phase2_closure"))

    workflow_text = abspath(root, WORKFLOW).read_text(encoding="utf-8")
    issues.extend(collect_missing_markers(workflow_text, WORKFLOW_MARKERS, prefix="workflow"))
    scope_block = extract_phase2_cross_scope_block(workflow_text)
    if not scope_block:
        issues.append("workflow_scope:phase2-cross-scope")
    else:
        issues.extend(collect_missing_markers(scope_block, WORKFLOW_SCOPE_MARKERS, prefix="workflow_scope"))
    issues.extend(validate_exact_workflow_runs(workflow_text))

    makefile_text = abspath(root, MAKEFILE).read_text(encoding="utf-8")
    issues.extend(collect_missing_markers(makefile_text, MAKEFILE_MARKERS, prefix="makefile"))
    issues.extend(validate_exact_makefile_runs(makefile_text))
    issues.extend(validate_targets_manifest(abspath(root, TARGETS)))
    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(abspath(root, TOOLCHAIN_NOTES), "\n".join(TOOLCHAIN_NOTE_MARKERS) + "\n")
    write_text(abspath(root, CLOSURE_DOC), "\n".join(CLOSURE_MARKERS) + "\n")
    write_text(abspath(root, REVIEW_CHECKLIST), "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(abspath(root, SCRIPT_README), "\n".join(SCRIPT_README_MARKERS) + "\n")
    write_text(abspath(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(abspath(root, VALIDATE_PHASE2), "\n".join(VALIDATE_PHASE2_MARKERS) + "\n")
    write_text(abspath(root, VALIDATE_PHASE2_CLOSURE), "\n".join(VALIDATE_PHASE2_CLOSURE_MARKERS) + "\n")
    workflow_lines = [
        WORKFLOW_SCOPE_JOB_MARKER,
        *WORKFLOW_SCOPE_MARKERS,
        "  phase2-cross:",
        *[f"run: {command}" for command in EXACT_WORKFLOW_RUN_COUNTS],
    ]
    write_text(abspath(root, WORKFLOW), "\n".join(workflow_lines) + "\n")
    write_text(
        abspath(root, MAKEFILE),
        "\n".join(
            [
                "phase2-validate:",
                "phase2-cross:",
                "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test",
                "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
                "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py",
                "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py",
            ]
        )
        + "\n",
    )
    write_text(
        abspath(root, TARGETS),
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "closed",
                "target_count": len(EXPECTED_TARGETS),
                "targets": EXPECTED_TARGETS,
                "tool_count": len(EXPECTED_TOOLS),
                "tools": EXPECTED_TOOLS,
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
        payload["targets"] = ["x86_64-linux-musl", "x86_64-linux-musl", "riscv64-linux-musl"]
        write_text(abspath(root, TARGETS), json.dumps(payload) + "\n")
        issues = validate_root(root)
        assert "targets:list=['x86_64-linux-musl', 'x86_64-linux-musl', 'riscv64-linux-musl']:expected=['x86_64-linux-musl', 'aarch64-linux-musl', 'riscv64-linux-musl']" in issues

        build_self_test_root(root)
        payload = load_json_object(abspath(root, TARGETS), label="phase2_cross_targets")
        payload["tool_count"] = 5
        write_text(abspath(root, TARGETS), json.dumps(payload) + "\n")
        issues = validate_root(root)
        assert "targets:tool_count=5:expected=6" in issues

        build_self_test_root(root)
        payload = load_json_object(abspath(root, TARGETS), label="phase2_cross_targets")
        payload["tools"] = [
            "scripts/zigux/fixdep.zig",
            "scripts/zigux/genksyms.zig",
            "scripts/zigux/mk_elfconfig.zig",
            "scripts/zigux/kconfig/conf_bridge.zig",
            "scripts/zigux/kconfig/confdata_bridge.zig",
            "scripts/zigux/genksyms_crc.zig",
        ]
        write_text(abspath(root, TARGETS), json.dumps(payload) + "\n")
        issues = validate_root(root)
        assert "targets:tools=['scripts/zigux/fixdep.zig', 'scripts/zigux/genksyms.zig', 'scripts/zigux/mk_elfconfig.zig', 'scripts/zigux/kconfig/conf_bridge.zig', 'scripts/zigux/kconfig/confdata_bridge.zig', 'scripts/zigux/genksyms_crc.zig']:expected=['scripts/zigux/fixdep.zig', 'scripts/zigux/genksyms.zig', 'scripts/zigux/genksyms_crc.zig', 'scripts/zigux/mk_elfconfig.zig', 'scripts/zigux/kconfig/conf_bridge.zig', 'scripts/zigux/kconfig/confdata_bridge.zig']" in issues

        build_self_test_root(root)
        write_text(abspath(root, SCRIPT_README), "check-phase2-cross.py\n")
        issues = validate_root(root)
        assert "script_readme:check-phase2-cross-selftest-alignment.py" in issues

        build_self_test_root(root)
        write_text(abspath(root, TESTS_README), "scripts/zigux/check-phase2-cross.py\n")
        issues = validate_root(root)
        assert "tests_readme:scripts/zigux/check-phase2-cross-selftest-alignment.py" in issues

        build_self_test_root(root)
        write_text(abspath(root, VALIDATE_PHASE2), "phase2_cross_targets.json\n")
        issues = validate_root(root)
        assert "validate_phase2:check-phase2-cross-selftest-alignment.py" in issues

        build_self_test_root(root)
        write_text(abspath(root, REVIEW_CHECKLIST), "scripts/zigux/check-phase2-cross-selftest-alignment.py\nmake -C zigux phase2-cross\n")
        issues = validate_root(root)
        assert "review_checklist:zigux/tests/fixtures/phase2_cross_targets.json" in issues

        build_self_test_root(root)
        write_text(abspath(root, REVIEW_CHECKLIST), "scripts/zigux/check-phase2-cross-selftest-alignment.py\nzigux/tests/fixtures/phase2_cross_targets.json\n")
        issues = validate_root(root)
        assert "review_checklist:make -C zigux phase2-cross" in issues

        build_self_test_root(root)
        write_text(
            abspath(root, REVIEW_CHECKLIST),
            "scripts/zigux/check-phase2-cross-selftest-alignment.py\nzigux/tests/fixtures/phase2_cross_targets.json\nmake -C zigux phase2-cross\n",
        )
        issues = validate_root(root)
        assert "review_checklist:scripts/zigux/check-phase2-cross.py" in issues

        build_self_test_root(root)
        changed_markers = [marker for index, marker in enumerate(VALIDATE_PHASE2_CLOSURE_MARKERS) if index != 3]
        write_text(abspath(root, VALIDATE_PHASE2_CLOSURE), "\n".join(changed_markers) + "\n")
        issues = validate_root(root)
        assert "validate_phase2_closure:PHASE2_CROSS_ALIGNMENT_SELF_TEST=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test" in issues

        build_self_test_root(root)
        changed_markers = [marker for index, marker in enumerate(VALIDATE_PHASE2_CLOSURE_MARKERS) if index != 1]
        write_text(abspath(root, VALIDATE_PHASE2_CLOSURE), "\n".join(changed_markers) + "\n")
        issues = validate_root(root)
        assert "validate_phase2_closure:PHASE2_CROSS_SELF_TEST=python3 scripts/zigux/check-phase2-cross.py --self-test" in issues

        build_self_test_root(root)
        write_text(abspath(root, WORKFLOW), "run: python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}\n")
        issues = validate_root(root)
        assert "workflow:python3 scripts/zigux/check-phase2-cross.py --self-test" in issues
        assert "workflow_scope:phase2-cross-scope" in issues

        build_self_test_root(root)
        write_text(
            abspath(root, WORKFLOW),
            "\n".join(
                [
                    WORKFLOW_SCOPE_JOB_MARKER,
                    *WORKFLOW_SCOPE_MARKERS,
                    "  phase2-cross:",
                    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
                    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
                    "run: python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}",
                    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
                    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
                ]
            )
            + "\n",
        )
        issues = validate_root(root)
        assert "workflow_exact_run:python3 scripts/zigux/check-phase2-cross.py --self-test:count=2:expected=1" in issues

        build_self_test_root(root)
        write_text(abspath(root, MAKEFILE), "phase2-cross:\n")
        issues = validate_root(root)
        assert "makefile:check-phase2-cross.py --self-test" in issues

        build_self_test_root(root)
        write_text(
            abspath(root, MAKEFILE),
            "\n".join(
                [
                    "phase2-cross:",
                    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test",
                    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
                    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py",
                    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py",
                    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py",
                ]
            )
            + "\n",
        )
        issues = validate_root(root)
        assert "makefile_exact_run:scripts/zigux/check-phase2-cross.py:count=2:expected=1" in issues

        build_self_test_root(root)
        write_text(abspath(root, TOOLCHAIN_NOTES), "python3 scripts/zigux/check-phase2-cross.py\n")
        issues = validate_root(root)
        assert "toolchain_notes:python3 scripts/zigux/check-phase2-cross.py --self-test" in issues

        build_self_test_root(root)
        workflow_text = abspath(root, WORKFLOW).read_text(encoding="utf-8").replace("scripts/zigux/check-phase2-toolchain-pin-scope.py\n", "", 1)
        write_text(abspath(root, WORKFLOW), workflow_text)
        issues = validate_root(root)
        assert "workflow_scope:scripts/zigux/check-phase2-toolchain-pin-scope.py" in issues

        build_self_test_root(root)
        workflow_text = abspath(root, WORKFLOW).read_text(encoding="utf-8").replace("zigux/tests/fixtures/phase2_cross_targets.json\n", "", 1)
        write_text(abspath(root, WORKFLOW), workflow_text)
        issues = validate_root(root)
        assert "workflow_scope:zigux/tests/fixtures/phase2_cross_targets.json" in issues

        build_self_test_root(root)
        abspath(root, SCRIPT_README).unlink()
        issues = validate_root(root)
        assert "missing_file:scripts/zigux/README.md" in issues

        build_self_test_root(root)
        abspath(root, TESTS_README).unlink()
        issues = validate_root(root)
        assert "missing_file:zigux/tests/README.md" in issues

        build_self_test_root(root)
        abspath(root, TARGETS).unlink()
        issues = validate_root(root)
        assert "missing_file:zigux/tests/fixtures/phase2_cross_targets.json" in issues

        build_self_test_root(root)
        abspath(root, REVIEW_CHECKLIST).unlink()
        issues = validate_root(root)
        assert "missing_file:Documentation/zigux/review-checklist.md" in issues

    print("PHASE2_CROSS_SELFTEST_ALIGNMENT_SELF_TEST=pass")
    print("PHASE2_CROSS_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT=27")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Keep the Phase 2 cross-target self-test note, scripts root, tests root, workflow, "
            "Makefile, closure references, scope detector, and manifest aligned with the current checker packet."
        )
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in alignment coverage without a repo checkout.")
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
        f"{len(TOOLCHAIN_NOTE_MARKERS) + len(CLOSURE_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(SCRIPT_README_MARKERS) + len(TESTS_README_MARKERS) + len(VALIDATE_PHASE2_MARKERS) + len(VALIDATE_PHASE2_CLOSURE_MARKERS) + len(WORKFLOW_MARKERS) + len(WORKFLOW_SCOPE_MARKERS) + len(MAKEFILE_MARKERS) + len(EXPECTED_TARGETS) + len(EXPECTED_TOOLS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
