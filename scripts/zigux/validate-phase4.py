#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/check-phase4-kprobe-example-packet.py",
    "scripts/zigux/check-phase4-workflow-route-counts.py",
    "scripts/zigux/validate-phase4.py",
    "Documentation/zigux/artifact-diff.md",
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "samples/kprobes/Makefile",
    "samples/kprobes/kprobe_example.c",
    "samples/vfs/Makefile",
    "samples/vfs/test-fsmount.c",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/phase4_kprobe_example_manifest.json",
    "zigux/tests/phase4_kprobe_example_survey.zig",
    "zigux/tests/phase4_test_fsmount_manifest.json",
    "zigux/tests/phase4_test_fsmount_survey.zig",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_build.zig",
]

MAKE_LINES = [
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-kprobe-example-packet.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-kprobe-example-packet.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py",
]

BUILD_MARKERS = [
    "phase4_runtime_atomic64_diff_survey.zig",
    "phase4_test_fsmount_survey.zig",
    "phase4_kprobe_example_survey.zig",
    "phase4_perf_baseline_survey.zig",
    "phase4-runtime-atomic64-diff-tests",
    "phase4-test-fsmount-survey-tests",
    "phase4-kprobe-example-survey-tests",
    "phase4-perf-baseline-survey-tests",
    "phase4-bitmap-diff-tests",
]

MATRIX_MARKERS = [
    "phase4_kprobe_example_manifest.json",
    "phase4_kprobe_example_survey.zig",
    "phase4-kprobe-example-survey-tests",
    "zig build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig",
    "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
    "c_anchor_only_until_kprobe_example_starter_lands",
    "samples/zigux/kprobe_example.zig",
    "phase4_test_fsmount_survey.zig",
    "phase4_perf_baseline_manifest.json",
    "perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land",
    "threshold_pending_until_runtime_atomic64_scope_widens",
    "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
]

README_MARKERS = [
    "check-phase4-kprobe-example-packet.py",
    "check-phase4-workflow-route-counts.py",
    "phase4-kprobe-example-survey",
    "phase4-kprobe-example-survey-tests",
    "still-absent `samples/zigux/kprobe_example.zig` sample explicitly survey-only",
    "phase4-perf-baseline-survey-tests",
]

ATOMIC64_DOCS_README_MARKERS = [
    "make -C zigux phase4-runtime-atomic64-diff",
    "phase4-runtime-atomic64-diff-tests",
    "phase4-runtime-atomic64-diff-survey-tests",
]

ATOMIC64_SCRIPTS_README_MARKERS = [
    "phase4-runtime-atomic64-diff",
    "phase4-runtime-atomic64-diff-tests",
    "phase4-runtime-atomic64-diff-survey-tests",
]

TESTS_README_MARKERS = [
    "zigux/tests/phase4_kprobe_example_manifest.json",
    "zigux/tests/phase4_kprobe_example_survey.zig",
    "make -C zigux phase4-kprobe-example-survey",
    "phase4-kprobe-example-survey-tests",
    "c_anchor_only_until_kprobe_example_starter_lands",
]

GATE_EVIDENCE_TARGETS = {
    "PHASE4_VALIDATOR_BLOB_SHA": "scripts/zigux/validate-phase4.py",
    "PHASE4_BUILD_BLOB_SHA": "zigux/tests/phase4_build.zig",
    "PHASE4_MAKEFILE_BLOB_SHA": "zigux/Makefile",
    "PHASE4_WORKFLOW_BLOB_SHA": ".github/workflows/zigux-bootstrap.yml",
    "PHASE4_KPROBE_EXAMPLE_MANIFEST_BLOB_SHA": "zigux/tests/phase4_kprobe_example_manifest.json",
    "PHASE4_KPROBE_EXAMPLE_SURVEY_BLOB_SHA": "zigux/tests/phase4_kprobe_example_survey.zig",
    "PHASE4_TEST_FSMOUNT_SURVEY_BLOB_SHA": "zigux/tests/phase4_test_fsmount_survey.zig",
    "PHASE4_PERF_BASELINE_SURVEY_BLOB_SHA": "zigux/tests/phase4_perf_baseline_survey.zig",
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA": "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "PHASE4_DOC_README_BLOB_SHA": "Documentation/zigux/README.md",
    "PHASE4_SCRIPT_README_BLOB_SHA": "scripts/zigux/README.md",
    "PHASE4_TESTS_README_BLOB_SHA": "zigux/tests/README.md",
}

ADDITIONAL_GATE_EVIDENCE_MARKERS = [
    "PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=",
]

ATOMIC64_GATE_EVIDENCE_MARKERS = [
    "make -C zigux phase4-runtime-atomic64-diff",
    "phase4-runtime-atomic64-diff-tests",
    "phase4-runtime-atomic64-diff-survey-tests",
    "runtime_atomic64_diff.zig` remains the single replay body",
]


def read_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def read_json(root: Path, rel: str) -> object:
    return json.loads(read_text(root, rel))


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def missing_text(text: str, prefix: str, markers: list[str]) -> list[str]:
    return [f"{prefix}:{m}" for m in markers if m not in text]


def validate_root(root: Path) -> list[str]:
    missing = [f"file:{p}" for p in REQUIRED_FILES if not (root / p).exists()]
    makefile = read_text(root, "zigux/Makefile")
    workflow = read_text(root, ".github/workflows/zigux-bootstrap.yml")
    matrix = read_text(root, "Documentation/zigux/phase4-validation-matrix.md")
    docs_readme = read_text(root, "Documentation/zigux/README.md")
    scripts_readme = read_text(root, "scripts/zigux/README.md")
    tests_readme = read_text(root, "zigux/tests/README.md")
    gate_evidence = read_text(root, "Documentation/zigux/phase4-gate-evidence.md")
    build = read_text(root, "zigux/tests/phase4_build.zig")
    kprobe_survey = read_text(root, "zigux/tests/phase4_kprobe_example_survey.zig")
    kprobe_manifest = read_json(root, "zigux/tests/phase4_kprobe_example_manifest.json")
    perf_manifest = read_json(root, "zigux/tests/phase4_perf_baseline_manifest.json")
    fsmount_manifest = read_json(root, "zigux/tests/phase4_test_fsmount_manifest.json")
    runtime_manifest = read_json(root, "zigux/tests/phase4_runtime_atomic64_diff_manifest.json")

    for line in MAKE_LINES:
        if makefile.splitlines().count(line) != 1:
            missing.append(f"make:{line}")

    missing.extend(missing_text(workflow, "workflow", ["Validate Phase 4 diff gates", "Run Phase 4 diff tests"]))
    missing.extend(missing_text(build, "build", BUILD_MARKERS))
    missing.extend(missing_text(matrix, "matrix", MATRIX_MARKERS))
    missing.extend(missing_text(docs_readme, "docs_readme", README_MARKERS))
    missing.extend(missing_text(docs_readme, "docs_readme_atomic64", ATOMIC64_DOCS_README_MARKERS))
    missing.extend(missing_text(scripts_readme, "scripts_readme", README_MARKERS[:-1]))
    missing.extend(missing_text(scripts_readme, "scripts_readme_atomic64", ATOMIC64_SCRIPTS_README_MARKERS))
    missing.extend(missing_text(tests_readme, "tests_readme", TESTS_README_MARKERS))
    missing.extend(missing_text(gate_evidence, "gate_evidence_atomic64", ATOMIC64_GATE_EVIDENCE_MARKERS))
    missing.extend(
        missing_text(
            kprobe_survey,
            "kprobe_survey",
            [
                "phase4_kprobe_example_manifest.json",
                "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
                "phase4-kprobe-example-survey-tests",
                "samples/zigux/kprobe_example.zig",
                "shared validator now fails closed on the kprobe survey packet itself",
            ],
        )
    )

    if not isinstance(kprobe_manifest, dict) or kprobe_manifest.get("shared_build_replay") != "phase4-kprobe-example-survey-tests":
        missing.append("kprobe_manifest:shared_build_replay")
    if kprobe_manifest.get("threshold_posture") != "c_anchor_only_until_kprobe_example_starter_lands":
        missing.append("kprobe_manifest:threshold_posture")
    if not isinstance(perf_manifest, dict) or perf_manifest.get("lane_key") != "P4-L20":
        missing.append("perf_manifest:lane_key")
    if not isinstance(fsmount_manifest, dict) or fsmount_manifest.get("anchor") != "samples/vfs/test-fsmount.c":
        missing.append("fsmount_manifest:anchor")
    if not isinstance(runtime_manifest, dict) or runtime_manifest.get("anchor") != "lib/atomic64_test.c":
        missing.append("runtime_manifest:anchor")

    if 'obj-$(CONFIG_SAMPLE_KPROBES) += kprobe_example.o' not in read_text(root, "samples/kprobes/Makefile"):
        missing.append("kprobe_anchor:makefile")
    if 'static char symbol[KSYM_NAME_LEN] = "kernel_clone";' not in read_text(root, "samples/kprobes/kprobe_example.c"):
        missing.append("kprobe_anchor:symbol")

    if "shared validator now fails closed on the kprobe survey packet itself" not in gate_evidence:
        missing.append("gate_evidence:kprobe_note")
    for marker, rel in GATE_EVIDENCE_TARGETS.items():
        expected = blob_sha((root / rel).read_bytes())
        if f"{marker}={expected}" not in gate_evidence:
            missing.append(f"gate_evidence:{marker}:{expected}")
    for marker in ADDITIONAL_GATE_EVIDENCE_MARKERS:
        if marker not in gate_evidence:
            missing.append(f"gate_evidence:{marker}")

    return missing


def write_fixture_tree(root: Path) -> None:
    files = {
        "scripts/zigux/artifact_diff.py": "print('ARTIFACT_DIFF_SELF_TEST=pass')\n",
        "scripts/zigux/check-artifact-diff-contract.py": "# ok\n",
        "scripts/zigux/check-phase4-gate-evidence.py": "# ok\n",
        "scripts/zigux/check-phase4-kprobe-example-packet.py": "# ok\n",
        "scripts/zigux/check-phase4-workflow-route-counts.py": "# ok\n",
        "scripts/zigux/validate-phase4.py": "# placeholder\n",
        "Documentation/zigux/artifact-diff.md": "Current Phase 4 use\n",
        "Documentation/zigux/phase4-validation-matrix.md": "\n".join(MATRIX_MARKERS) + "\n",
        "Documentation/zigux/README.md": "\n".join(README_MARKERS + ATOMIC64_DOCS_README_MARKERS) + "\n",
        "scripts/zigux/README.md": "\n".join(README_MARKERS[:-1] + ATOMIC64_SCRIPTS_README_MARKERS) + "\n",
        "zigux/tests/README.md": "\n".join(TESTS_README_MARKERS) + "\n",
        "zigux/Makefile": "\n".join(MAKE_LINES) + "\n",
        ".github/workflows/zigux-bootstrap.yml": "Validate Phase 4 diff gates\nRun Phase 4 diff tests\n",
        "samples/kprobes/Makefile": "obj-$(CONFIG_SAMPLE_KPROBES) += kprobe_example.o\n",
        "samples/kprobes/kprobe_example.c": 'static char symbol[KSYM_NAME_LEN] = "kernel_clone";\n',
        "samples/vfs/Makefile": "userprogs-always-y += test-fsmount\n",
        "samples/vfs/test-fsmount.c": "test-fsmount\n",
        "zigux/tests/atomic64_diff.zig": "atomic64\n",
        "zigux/tests/runtime_atomic64_diff.zig": "runtime atomic64 diff gate keeps post-selftest replay explicit\n",
        "zigux/tests/phase4_runtime_atomic64_diff_manifest.json": json.dumps({"anchor": "lib/atomic64_test.c"}),
        "zigux/tests/phase4_runtime_atomic64_diff_survey.zig": "phase4-runtime-atomic64-diff-survey-tests\n",
        "zigux/tests/phase4_kprobe_example_manifest.json": json.dumps({"shared_build_replay": "phase4-kprobe-example-survey-tests", "threshold_posture": "c_anchor_only_until_kprobe_example_starter_lands"}),
        "zigux/tests/phase4_kprobe_example_survey.zig": "\n".join([
            "phase4_kprobe_example_manifest.json",
            "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
            "phase4-kprobe-example-survey-tests",
            "samples/zigux/kprobe_example.zig",
            "shared validator now fails closed on the kprobe survey packet itself",
        ]) + "\n",
        "zigux/tests/phase4_test_fsmount_manifest.json": json.dumps({"anchor": "samples/vfs/test-fsmount.c"}),
        "zigux/tests/phase4_test_fsmount_survey.zig": "phase4-test-fsmount-survey-tests\n",
        "zigux/tests/phase4_perf_baseline_manifest.json": json.dumps({"lane_key": "P4-L20"}),
        "zigux/tests/phase4_perf_baseline_survey.zig": "phase4-perf-baseline-survey-tests\n",
        "zigux/tests/bitmap_diff.zig": "bitmap\n",
        "zigux/tests/phase4_build.zig": "\n".join(BUILD_MARKERS) + "\n",
    }
    for rel, content in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    workflow_route_checker_sha = blob_sha(
        (root / "scripts/zigux/check-phase4-workflow-route-counts.py").read_bytes()
    )
    evidence = [
        "PHASE4_EVIDENCE_MODE=github_connector_readback",
        "PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions",
        f"PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA={workflow_route_checker_sha}",
        "shared validator now fails closed on the kprobe survey packet itself",
        "make -C zigux phase4-runtime-atomic64-diff",
        "phase4-runtime-atomic64-diff-tests",
        "phase4-runtime-atomic64-diff-survey-tests",
        "runtime_atomic64_diff.zig` remains the single replay body",
    ]
    for marker, rel in GATE_EVIDENCE_TARGETS.items():
        evidence.append(f"{marker}={blob_sha((root / rel).read_bytes())}")
    (root / "Documentation/zigux/phase4-gate-evidence.md").write_text("\n".join(evidence) + "\n", encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_") as tmp:
        root = Path(tmp)
        write_fixture_tree(root)
        assert not validate_root(root), validate_root(root)

        survey = root / "zigux/tests/phase4_kprobe_example_survey.zig"
        survey.write_text(survey.read_text(encoding="utf-8").replace("phase4-kprobe-example-survey-tests\n", ""), encoding="utf-8")
        missing = validate_root(root)
        assert "kprobe_survey:phase4-kprobe-example-survey-tests" in missing, missing

        write_fixture_tree(root)
        docs_readme = root / "Documentation/zigux/README.md"
        docs_readme.write_text(
            docs_readme.read_text(encoding="utf-8").replace("make -C zigux phase4-runtime-atomic64-diff\n", "", 1),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert "docs_readme_atomic64:make -C zigux phase4-runtime-atomic64-diff" in missing, missing

        write_fixture_tree(root)
        makefile = root / "zigux/Makefile"
        makefile.write_text(
            makefile.read_text(encoding="utf-8").replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "make:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test"
            in missing
        ), missing

        write_fixture_tree(root)
        makefile = root / "zigux/Makefile"
        makefile.write_text(
            makefile.read_text(encoding="utf-8").replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "make:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py"
            in missing
        ), missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "runtime_atomic64_diff.zig` remains the single replay body\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "gate_evidence_atomic64:runtime_atomic64_diff.zig` remains the single replay body"
            in missing
        ), missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=",
                "PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_MISSING=",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert "gate_evidence:PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=" in missing, missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "PHASE4_TESTS_README_BLOB_SHA=",
                "PHASE4_TESTS_README_BLOB_MISSING=",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert "gate_evidence:PHASE4_TESTS_README_BLOB_SHA:" in " ".join(missing), missing

    print("PHASE4_VALIDATOR_SELF_TEST=pass")
    return 0


def required_marker_count() -> int:
    return (
        len(MAKE_LINES)
        + len(BUILD_MARKERS)
        + len(MATRIX_MARKERS)
        + len(README_MARKERS)
        + len(ATOMIC64_DOCS_README_MARKERS)
        + len(README_MARKERS[:-1])
        + len(ATOMIC64_SCRIPTS_README_MARKERS)
        + len(TESTS_README_MARKERS)
        + len(GATE_EVIDENCE_TARGETS)
        + len(ADDITIONAL_GATE_EVIDENCE_MARKERS)
        + len(ATOMIC64_GATE_EVIDENCE_MARKERS)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Phase 4 diff bundle.")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()

    missing = validate_root(ROOT)
    if missing:
        print("PHASE4_VALIDATION=fail")
        print("MISSING_PHASE4_MARKERS_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE4_MARKERS_END")
        return 1

    print("PHASE4_VALIDATION=pass")
    print(f"PHASE4_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE4_REQUIRED_MARKER_COUNT={required_marker_count()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
