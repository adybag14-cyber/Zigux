#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


_THIS_FILE = Path(__file__).resolve()
ROOT = (
    _THIS_FILE.parents[2]
    if _THIS_FILE.parent.name == "zigux" and _THIS_FILE.parent.parent.name == "scripts"
    else _THIS_FILE.parent
)

REQUIRED_FILES = [
    "Documentation/zigux/phase12-shared-replay-contract.md",
    "Documentation/zigux/phase12-release-coordination-matrix.md",
    "Documentation/zigux/phase12-release-readiness-survey.md",
    "Documentation/zigux/phase12-cross-compile-smoke.md",
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase12-shared-replay-contract.py",
    "scripts/zigux/validate-phase12.py",
    "zigux/tests/README.md",
    "zigux/tests/phase12_build.zig",
    "zigux/tests/phase12_libbpf_only_build.zig",
    "zigux/tests/fixtures/phase12_build_inventory.json",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
]

RAW_COVERAGE_CONTRACT_SENTENCE = (
    "- that same release-facing PMO packet now also names `zigux/tests/phase12_raw_github_coverage_manifest.json` "
    "and `zigux/tests/phase12_raw_github_coverage_survey.zig` directly, so the mixed public-read fallback split stays "
    "tied to manifest-backed and Zig-survey-backed evidence instead of living only in note-level prose."
)

RELEASE_COORDINATION_MATRIX_BULLET = (
    "- `Documentation/zigux/phase12-release-coordination-matrix.md`"
)

SHARED_REPLAY_NOTE_MARKERS = [
    "# Phase 12 Shared Replay Contract",
    "python3 scripts/zigux/check-phase12-build-inventory.py --self-test",
    "python3 scripts/zigux/check-phase12-build-inventory.py",
    "python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test",
    "python3 scripts/zigux/check-phase12-libbpf-snapshot.py",
    "python3 scripts/zigux/check-phase12-libbpf-packet.py --self-test",
    "python3 scripts/zigux/check-phase12-libbpf-packet.py",
    "python3 scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test",
    "python3 scripts/zigux/check-phase12-libbpf-focused-replay.py",
    "python3 scripts/zigux/check-phase12-raw-github-coverage.py --self-test",
    "python3 scripts/zigux/check-phase12-raw-github-coverage.py",
    "python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
    "python3 scripts/zigux/check-phase12-release-readiness-packet.py",
    "python3 scripts/zigux/check-phase12-shared-replay-contract.py --self-test",
    "python3 scripts/zigux/check-phase12-shared-replay-contract.py",
    "python3 scripts/zigux/validate-phase12.py",
    "make -C zigux phase12-validate",
    "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
    "zig build test --build-file zigux/tests/phase12_libbpf_only_build.zig --summary all",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    RELEASE_COORDINATION_MATRIX_BULLET,
    "Documentation/zigux/phase12-release-readiness-survey.md",
    "Documentation/zigux/phase12-cross-compile-smoke.md",
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "- `zigux/tests/phase12_raw_github_coverage_manifest.json`",
    "- `zigux/tests/phase12_raw_github_coverage_survey.zig`",
    RAW_COVERAGE_CONTRACT_SENTENCE,
]

SHARED_REPLAY_NOTE_EXACT_COUNTS = {
    "- `python3 scripts/zigux/check-phase12-shared-replay-contract.py --self-test`": 1,
    "- `python3 scripts/zigux/check-phase12-shared-replay-contract.py`": 1,
    RELEASE_COORDINATION_MATRIX_BULLET: 2,
    "- `zigux/tests/phase12_raw_github_coverage_manifest.json`": 1,
    "- `zigux/tests/phase12_raw_github_coverage_survey.zig`": 1,
    RAW_COVERAGE_CONTRACT_SENTENCE: 1,
}

DOCS_ROOT_MARKERS = [
    "Documentation/zigux/phase12-release-readiness-survey.md",
    "Documentation/zigux/phase12-cross-compile-smoke.md",
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "Documentation/zigux/phase12-nvme-pci-survey.md",
    "Documentation/zigux/phase12-virtio-scsi-survey.md",
    "make -C zigux phase12-validate",
    "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
]

SCRIPTS_README_MARKERS = [
    "check-phase12-build-inventory.py",
    "check-phase12-libbpf-snapshot.py",
    "check-phase12-libbpf-packet.py",
    "check-phase12-libbpf-focused-replay.py",
    "check-phase12-raw-github-coverage.py",
    "check-phase12-release-readiness-packet.py",
    "check-phase12-shared-replay-contract.py",
    "validate-phase12.py",
    "Documentation/zigux/phase12-shared-replay-contract.md",
    "zigux/tests/phase12_libbpf_only_build.zig",
]

SCRIPTS_README_ALIAS_MARKER = (
    "- `make -C zigux phase12` keeps the current Phase 12 bundle reviewable through one shared tranche entrypoint "
    "instead of ad hoc complex-driver commands, while the direct `zig build test --build-file "
    "zigux/tests/phase12_libbpf_only_build.zig --summary all` replay intentionally stays outside that "
    "shared wrapper as the dedicated focused libbpf-only shard, and the named `zig build --build-file "
    "zigux/tests/phase12_libbpf_only_build.zig phase12-libbpf-focused-replay --summary all` alias keeps "
    "that same focused rerun explicit from the scripts root."
)

SCRIPTS_README_EXACT_COUNTS = {
    SCRIPTS_README_ALIAS_MARKER: 1,
}

TESTS_README_MARKERS = [
    "Documentation/zigux/phase12-shared-replay-contract.md",
    "scripts/zigux/check-phase12-libbpf-focused-replay.py",
    "zigux/tests/phase12_libbpf_only_build.zig",
    "zigux/tests/phase12_build.zig",
    "Documentation/zigux/phase12-virtio-scsi-survey.md",
    "keep `Documentation/zigux/phase12-shared-replay-contract.md`, `zigux/tests/phase12_build.zig`, `zigux/tests/phase12_libbpf_only_build.zig`, `scripts/zigux/check-phase12-libbpf-focused-replay.py`, `scripts/zigux/validate-phase12.py`, and `zigux/tests/phase12_libbpf_manifest.json` aligned so the tests root names the same shared-versus-focused libbpf replay boundary as the docs-root contract note instead of leaving the dedicated shard implied behind the broader shared build inventory.",
]

TESTS_README_EXACT_COUNTS = {
    TESTS_README_MARKERS[-1]: 1,
}

REVIEW_CHECKLIST_MARKERS = [
    "if the change is a Phase 12 complex-driver or heavy-helper slice, do `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_build.zig`, the four Phase 12 manifests, and the four Phase 12 survey notes still agree on the same bounded tranche, exact surveyed commits, approved roadmap destinations, shared replay contract, and explicit DMA versus object-model blocker posture?",
    "if the change touches the focused Phase 12 libbpf-only replay packet, do `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test`, `scripts/zigux/check-phase12-libbpf-focused-replay.py`, `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_libbpf_only_build.zig`, `zigux/tests/phase12_libbpf_manifest.json`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` still agree on the same dedicated replay shard, review-note hook, and validator-first rollback path instead of leaving that narrower libbpf gate implied behind the broader packet checks?",
    "if the change touches the Phase 12 release-facing PMO packet, do `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/README.md`, `Documentation/zigux/phase12-cross-compile-smoke.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `scripts/zigux/validate-phase12.py`, and `make -C zigux phase12-validate` still keep the active-not-closed release posture, the approved `x86_64-linux-musl`, `aarch64-linux-musl`, and `riscv64-linux-musl` smoke set, and the current two commit-pinned versus two shared-tree-only fallback split explicit?",
]

MAKEFILE_MARKERS = [
    "phase12-validate:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-build-inventory.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-build-inventory.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-libbpf-snapshot.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-libbpf-snapshot.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-libbpf-packet.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-libbpf-packet.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-libbpf-focused-replay.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-raw-github-coverage.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-raw-github-coverage.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-release-readiness-packet.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-shared-replay-contract.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-shared-replay-contract.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase12.py",
]

MAKEFILE_EXACT_COUNTS = {
    MAKEFILE_MARKERS[13]: 1,
    MAKEFILE_MARKERS[14]: 1,
}

WORKFLOW_MARKERS = [
    "Validate Phase 12 degraded-workflow bundle",
    "make -C zigux phase12-validate",
    "Run Phase 12 complex driver tests",
    "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
]

BUILD_MARKERS = [
    "phase12-virtio-net-tests",
    "phase12-virtio-net-survey-tests",
    "phase12-nvme-pci-tests",
    "phase12-nvme-pci-survey-tests",
    "phase12-virtio-scsi-tests",
    "phase12-virtio-scsi-survey-tests",
    "phase12-raw-github-coverage-survey-tests",
    "phase12-libbpf-segment-survey-tests",
    "phase12-libbpf-reviewability-tests",
]

LIBBPF_ONLY_BUILD_MARKERS = [
    "phase12-libbpf-segment-survey-tests",
    "phase12-libbpf-reviewability-tests",
]

BUILD_FIXTURE_MARKERS = [
    "\"phase12-libbpf-segment-survey-tests\"",
    "\"phase12-libbpf-reviewability-tests\"",
]


def read_text(root: Path, relpath: str) -> str:
    return (root / relpath).read_text(encoding="utf-8")


def collect_exact_line_misses(text: str, expected_counts: dict[str, int], prefix: str) -> list[str]:
    missing: list[str] = []
    lines = text.splitlines()
    for marker, expected_count in expected_counts.items():
        actual_count = lines.count(marker)
        if actual_count != expected_count:
            missing.append(f"{prefix}:{marker}:expected={expected_count}:actual={actual_count}")
    return missing


def collect_missing(root: Path) -> list[str]:
    missing: list[str] = []
    for relpath in REQUIRED_FILES:
        if not (root / relpath).exists():
            missing.append(f"missing_file:{relpath}")

    if missing:
        return missing

    source_groups = [
        ("shared_replay_note", "Documentation/zigux/phase12-shared-replay-contract.md", SHARED_REPLAY_NOTE_MARKERS),
        ("docs_root", "Documentation/zigux/README.md", DOCS_ROOT_MARKERS),
        ("scripts_readme", "scripts/zigux/README.md", SCRIPTS_README_MARKERS),
        ("tests_readme", "zigux/tests/README.md", TESTS_README_MARKERS),
        ("review_checklist", "Documentation/zigux/review-checklist.md", REVIEW_CHECKLIST_MARKERS),
        ("makefile", "zigux/Makefile", MAKEFILE_MARKERS),
        ("workflow", ".github/workflows/zigux-bootstrap.yml", WORKFLOW_MARKERS),
        ("phase12_build", "zigux/tests/phase12_build.zig", BUILD_MARKERS),
        ("phase12_libbpf_only_build", "zigux/tests/phase12_libbpf_only_build.zig", LIBBPF_ONLY_BUILD_MARKERS),
        ("phase12_build_fixture", "zigux/tests/fixtures/phase12_build_inventory.json", BUILD_FIXTURE_MARKERS),
    ]

    for label, relpath, markers in source_groups:
        text = read_text(root, relpath)
        for marker in markers:
            if marker not in text:
                missing.append(f"{label}:{marker}")

    exact_count_groups = [
        (
            "shared_replay_note_count",
            "Documentation/zigux/phase12-shared-replay-contract.md",
            SHARED_REPLAY_NOTE_EXACT_COUNTS,
        ),
        ("scripts_readme_count", "scripts/zigux/README.md", SCRIPTS_README_EXACT_COUNTS),
        ("makefile_count", "zigux/Makefile", MAKEFILE_EXACT_COUNTS),
        ("tests_readme_count", "zigux/tests/README.md", TESTS_README_EXACT_COUNTS),
    ]

    for label, relpath, expected_counts in exact_count_groups:
        missing.extend(
            collect_exact_line_misses(read_text(root, relpath), expected_counts, label)
        )

    return missing


def validate_contract(root: Path) -> int:
    missing = collect_missing(root)
    if missing:
        print("PHASE12_SHARED_REPLAY_CONTRACT=fail")
        print("PHASE12_SHARED_REPLAY_CONTRACT_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE12_SHARED_REPLAY_CONTRACT_MISSING_END")
        return 1

    print("PHASE12_SHARED_REPLAY_CONTRACT=pass")
    print(f"PHASE12_SHARED_REPLAY_NOTE_MARKER_COUNT={len(SHARED_REPLAY_NOTE_MARKERS)}")
    print(f"PHASE12_SHARED_REPLAY_DOCS_ROOT_MARKER_COUNT={len(DOCS_ROOT_MARKERS)}")
    print(f"PHASE12_SHARED_REPLAY_SCRIPTS_README_MARKER_COUNT={len(SCRIPTS_README_MARKERS)}")
    print(f"PHASE12_SHARED_REPLAY_TESTS_README_MARKER_COUNT={len(TESTS_README_MARKERS)}")
    print(f"PHASE12_SHARED_REPLAY_CHECKLIST_MARKER_COUNT={len(REVIEW_CHECKLIST_MARKERS)}")
    print(f"PHASE12_SHARED_REPLAY_MAKEFILE_MARKER_COUNT={len(MAKEFILE_MARKERS)}")
    return 0


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts/zigux/check-phase12-shared-replay-contract.py")],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )


def expect_missing(label: str, result: subprocess.CompletedProcess[str], marker: str) -> None:
    if result.returncode == 0:
        raise SystemExit(f"phase12-shared-replay-self-test:{label}:unexpected_pass")
    if marker not in result.stdout:
        actual = result.stdout.strip() or result.stderr.strip() or "no_output"
        raise SystemExit(
            f"phase12-shared-replay-self-test:{label}:expected:{marker}:actual:{actual}"
        )


def write_fixture_tree(root: Path) -> None:
    note_lines = list(SHARED_REPLAY_NOTE_MARKERS)
    note_lines[note_lines.index("python3 scripts/zigux/check-phase12-shared-replay-contract.py --self-test")] = (
        "- `python3 scripts/zigux/check-phase12-shared-replay-contract.py --self-test`"
    )
    note_lines[note_lines.index("python3 scripts/zigux/check-phase12-shared-replay-contract.py")] = (
        "- `python3 scripts/zigux/check-phase12-shared-replay-contract.py`"
    )
    write_text(
        root / "Documentation/zigux/phase12-shared-replay-contract.md",
        "\n".join(note_lines) + "\n",
    )
    write_text(
        root / "Documentation/zigux/phase12-release-coordination-matrix.md",
        "\n".join(
            [
                "# Phase 12 Release Coordination Matrix",
                "PHASE12_STATUS=active",
                "PHASE12_RELEASE_CLOSED=no",
                "make -C zigux phase12-validate",
                "make -C zigux phase12",
                "Documentation/zigux/phase12-shared-replay-contract.md",
                "x86_64-linux-musl",
                "aarch64-linux-musl",
                "riscv64-linux-musl",
                "PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2",
                "PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2",
            ]
        )
        + "\n",
    )
    write_text(
        root / "Documentation/zigux/phase12-release-readiness-survey.md",
        "\n".join(
            [
                "PHASE12_STATUS=active",
                "make -C zigux phase12-validate",
                "make -C zigux phase12",
                "Documentation/zigux/phase12-shared-replay-contract.md",
                "x86_64-linux-musl",
                "aarch64-linux-musl",
                "riscv64-linux-musl",
                "PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2",
                "PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2",
                "PHASE12_RELEASE_CLOSED=no",
            ]
        )
        + "\n",
    )
    write_text(root / "Documentation/zigux/phase12-cross-compile-smoke.md", "x86_64-linux-musl\naarch64-linux-musl\nriscv64-linux-musl\n")
    write_text(
        root / "Documentation/zigux/phase12-raw-github-coverage-survey.md",
        "commit-pinned\nshared-tree-only\nDocumentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md\nDocumentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md\nDocumentation/zigux/phase12-virtio-net-survey.md\nDocumentation/zigux/phase12-libbpf-segment-survey.md\n",
    )
    write_text(root / "Documentation/zigux/README.md", "\n".join(DOCS_ROOT_MARKERS) + "\n")
    write_text(root / "Documentation/zigux/review-checklist.md", "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(
        root / "scripts/zigux/README.md",
        "\n".join([*SCRIPTS_README_MARKERS, SCRIPTS_README_ALIAS_MARKER]) + "\n",
    )
    write_text(root / "zigux/tests/README.md", "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(root / "scripts/zigux/validate-phase12.py", "\n".join(MAKEFILE_MARKERS) + "\nDocumentation/zigux/phase12-release-readiness-survey.md\n")
    write_text(root / "zigux/tests/phase12_build.zig", "\n".join(BUILD_MARKERS) + "\n")
    write_text(root / "zigux/tests/phase12_libbpf_only_build.zig", "\n".join(LIBBPF_ONLY_BUILD_MARKERS) + "\n")
    write_text(root / "zigux/tests/fixtures/phase12_build_inventory.json", "\n".join(BUILD_FIXTURE_MARKERS) + "\n")
    write_text(root / "zigux/Makefile", "\n".join(MAKEFILE_MARKERS) + "\n")
    write_text(root / ".github/workflows/zigux-bootstrap.yml", "\n".join(WORKFLOW_MARKERS) + "\n")
    write_text(
        root / "scripts/zigux/check-phase12-shared-replay-contract.py",
        Path(__file__).read_text(encoding="utf-8"),
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase12_shared_replay_contract_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_tree(tmp_root)

        baseline = run_checker(tmp_root)
        if baseline.returncode != 0:
            raise SystemExit(
                "phase12-shared-replay-self-test:baseline_failed:"
                f"{baseline.stdout.strip() or baseline.stderr.strip() or 'no_output'}"
            )

        matrix_path = tmp_root / "Documentation/zigux/phase12-release-coordination-matrix.md"
        matrix_backup = matrix_path.read_text(encoding="utf-8")
        matrix_path.unlink()
        expect_missing(
            "missing_release_coordination_matrix_file",
            run_checker(tmp_root),
            "missing_file:Documentation/zigux/phase12-release-coordination-matrix.md",
        )
        write_text(matrix_path, matrix_backup)

        note_path = tmp_root / "Documentation/zigux/phase12-shared-replay-contract.md"
        note_backup = note_path.read_text(encoding="utf-8")
        write_text(note_path, note_backup.replace("make -C zigux phase12-validate\n", "", 1))
        expect_missing(
            "missing_note_validate_route",
            run_checker(tmp_root),
            "shared_replay_note:make -C zigux phase12-validate",
        )
        write_text(note_path, note_backup)

        write_text(
            note_path,
            note_backup.replace(RELEASE_COORDINATION_MATRIX_BULLET + "\n", "", 1),
        )
        expect_missing(
            "missing_note_release_coordination_matrix_bullet",
            run_checker(tmp_root),
            f"shared_replay_note_count:{RELEASE_COORDINATION_MATRIX_BULLET}:expected=2:actual=1",
        )
        write_text(note_path, note_backup)

        write_text(
            note_path,
            note_backup + RELEASE_COORDINATION_MATRIX_BULLET + "\n",
        )
        expect_missing(
            "duplicate_note_release_coordination_matrix_bullet",
            run_checker(tmp_root),
            f"shared_replay_note_count:{RELEASE_COORDINATION_MATRIX_BULLET}:expected=2:actual=3",
        )
        write_text(note_path, note_backup)

        write_text(
            note_path,
            note_backup.replace("- `python3 scripts/zigux/check-phase12-shared-replay-contract.py --self-test`\n", "", 1),
        )
        expect_missing(
            "missing_note_contract_checker_self_test",
            run_checker(tmp_root),
            "shared_replay_note:python3 scripts/zigux/check-phase12-shared-replay-contract.py --self-test",
        )
        write_text(note_path, note_backup)

        write_text(
            note_path,
            note_backup + "- `python3 scripts/zigux/check-phase12-shared-replay-contract.py --self-test`\n",
        )
        expect_missing(
            "duplicate_note_contract_checker_self_test",
            run_checker(tmp_root),
            "shared_replay_note_count:- `python3 scripts/zigux/check-phase12-shared-replay-contract.py --self-test`:expected=1:actual=2",
        )
        write_text(note_path, note_backup)

        write_text(
            note_path,
            note_backup + "- `python3 scripts/zigux/check-phase12-shared-replay-contract.py`\n",
        )
        expect_missing(
            "duplicate_note_contract_checker_live_route",
            run_checker(tmp_root),
            "shared_replay_note_count:- `python3 scripts/zigux/check-phase12-shared-replay-contract.py`:expected=1:actual=2",
        )
        write_text(note_path, note_backup)

        write_text(
            note_path,
            note_backup.replace("- `zigux/tests/phase12_raw_github_coverage_manifest.json`\n", "", 1),
        )
        expect_missing(
            "missing_note_raw_coverage_manifest_bullet",
            run_checker(tmp_root),
            "shared_replay_note:- `zigux/tests/phase12_raw_github_coverage_manifest.json`",
        )
        write_text(note_path, note_backup)

        write_text(
            note_path,
            note_backup + "- `zigux/tests/phase12_raw_github_coverage_manifest.json`\n",
        )
        expect_missing(
            "duplicate_note_raw_coverage_manifest_bullet",
            run_checker(tmp_root),
            "shared_replay_note_count:- `zigux/tests/phase12_raw_github_coverage_manifest.json`:expected=1:actual=2",
        )
        write_text(note_path, note_backup)

        write_text(
            note_path,
            note_backup.replace("- `zigux/tests/phase12_raw_github_coverage_survey.zig`\n", "", 1),
        )
        expect_missing(
            "missing_note_raw_coverage_survey_bullet",
            run_checker(tmp_root),
            "shared_replay_note:- `zigux/tests/phase12_raw_github_coverage_survey.zig`",
        )
        write_text(note_path, note_backup)

        write_text(
            note_path,
            note_backup + "- `zigux/tests/phase12_raw_github_coverage_survey.zig`\n",
        )
        expect_missing(
            "duplicate_note_raw_coverage_survey_bullet",
            run_checker(tmp_root),
            "shared_replay_note_count:- `zigux/tests/phase12_raw_github_coverage_survey.zig`:expected=1:actual=2",
        )
        write_text(note_path, note_backup)

        write_text(
            note_path,
            note_backup.replace(RAW_COVERAGE_CONTRACT_SENTENCE + "\n", "", 1),
        )
        expect_missing(
            "missing_note_raw_coverage_contract_sentence",
            run_checker(tmp_root),
            f"shared_replay_note:{RAW_COVERAGE_CONTRACT_SENTENCE}",
        )
        write_text(note_path, note_backup)

        write_text(
            note_path,
            note_backup + RAW_COVERAGE_CONTRACT_SENTENCE + "\n",
        )
        expect_missing(
            "duplicate_note_raw_coverage_contract_sentence",
            run_checker(tmp_root),
            f"shared_replay_note_count:{RAW_COVERAGE_CONTRACT_SENTENCE}:expected=1:actual=2",
        )
        write_text(note_path, note_backup)

        docs_root_path = tmp_root / "Documentation/zigux/README.md"
        docs_root_backup = docs_root_path.read_text(encoding="utf-8")
        write_text(
            docs_root_path,
            docs_root_backup.replace("Documentation/zigux/phase12-release-readiness-survey.md\n", "", 1),
        )
        expect_missing(
            "missing_docs_root_release_note",
            run_checker(tmp_root),
            "docs_root:Documentation/zigux/phase12-release-readiness-survey.md",
        )
        write_text(docs_root_path, docs_root_backup)

        scripts_readme_path = tmp_root / "scripts/zigux/README.md"
        scripts_readme_backup = scripts_readme_path.read_text(encoding="utf-8")
        write_text(
            scripts_readme_path,
            scripts_readme_backup.replace("Documentation/zigux/phase12-shared-replay-contract.md\n", "", 1),
        )
        expect_missing(
            "missing_scripts_readme_contract_link",
            run_checker(tmp_root),
            "scripts_readme:Documentation/zigux/phase12-shared-replay-contract.md",
        )
        write_text(scripts_readme_path, scripts_readme_backup)

        write_text(
            scripts_readme_path,
            scripts_readme_backup.replace("check-phase12-shared-replay-contract.py\n", "", 1),
        )
        expect_missing(
            "missing_scripts_readme_contract_checker",
            run_checker(tmp_root),
            "scripts_readme:check-phase12-shared-replay-contract.py",
        )
        write_text(scripts_readme_path, scripts_readme_backup)

        write_text(
            scripts_readme_path,
            scripts_readme_backup.replace(SCRIPTS_README_ALIAS_MARKER + "\n", "", 1),
        )
        expect_missing(
            "missing_scripts_readme_alias_sentence",
            run_checker(tmp_root),
            f"scripts_readme_count:{SCRIPTS_README_ALIAS_MARKER}:expected=1:actual=0",
        )
        write_text(scripts_readme_path, scripts_readme_backup)

        write_text(
            scripts_readme_path,
            scripts_readme_backup + SCRIPTS_README_ALIAS_MARKER + "\n",
        )
        expect_missing(
            "duplicate_scripts_readme_alias_sentence",
            run_checker(tmp_root),
            f"scripts_readme_count:{SCRIPTS_README_ALIAS_MARKER}:expected=1:actual=2",
        )
        write_text(scripts_readme_path, scripts_readme_backup)

        tests_readme_path = tmp_root / "zigux/tests/README.md"
        tests_readme_backup = tests_readme_path.read_text(encoding="utf-8")
        write_text(
            tests_readme_path,
            tests_readme_backup.replace("Documentation/zigux/phase12-virtio-scsi-survey.md\n", "", 1),
        )
        expect_missing(
            "missing_tests_readme_storage_survey",
            run_checker(tmp_root),
            "tests_readme:Documentation/zigux/phase12-virtio-scsi-survey.md",
        )
        write_text(tests_readme_path, tests_readme_backup)

        write_text(
            tests_readme_path,
            tests_readme_backup + TESTS_README_MARKERS[-1] + "\n",
        )
        expect_missing(
            "duplicate_tests_readme_boundary_sentence",
            run_checker(tmp_root),
            f"tests_readme_count:{TESTS_README_MARKERS[-1]}:expected=1:actual=2",
        )
        write_text(tests_readme_path, tests_readme_backup)

        checklist_path = tmp_root / "Documentation/zigux/review-checklist.md"
        checklist_backup = checklist_path.read_text(encoding="utf-8")
        write_text(
            checklist_path,
            checklist_backup.replace(REVIEW_CHECKLIST_MARKERS[2] + "\n", "", 1),
        )
        expect_missing(
            "missing_checklist_release_question",
            run_checker(tmp_root),
            f"review_checklist:{REVIEW_CHECKLIST_MARKERS[2]}",
        )
        write_text(checklist_path, checklist_backup)

        makefile_path = tmp_root / "zigux/Makefile"
        makefile_backup = makefile_path.read_text(encoding="utf-8")
        write_text(
            makefile_path,
            makefile_backup.replace(MAKEFILE_MARKERS[11] + "\n", "", 1),
        )
        expect_missing(
            "missing_makefile_release_guard",
            run_checker(tmp_root),
            f"makefile:{MAKEFILE_MARKERS[11]}",
        )
        write_text(makefile_path, makefile_backup)

        write_text(
            makefile_path,
            makefile_backup.replace(MAKEFILE_MARKERS[13] + "\n", "", 1),
        )
        expect_missing(
            "missing_makefile_contract_checker_self_test",
            run_checker(tmp_root),
            f"makefile:{MAKEFILE_MARKERS[13]}",
        )
        write_text(makefile_path, makefile_backup)

        write_text(
            makefile_path,
            makefile_backup + MAKEFILE_MARKERS[13] + "\n",
        )
        expect_missing(
            "duplicate_makefile_contract_checker_self_test",
            run_checker(tmp_root),
            f"makefile_count:{MAKEFILE_MARKERS[13]}:expected=1:actual=2",
        )
        write_text(makefile_path, makefile_backup)

        write_text(
            makefile_path,
            makefile_backup + MAKEFILE_MARKERS[14] + "\n",
        )
        expect_missing(
            "duplicate_makefile_contract_checker_live_route",
            run_checker(tmp_root),
            f"makefile_count:{MAKEFILE_MARKERS[14]}:expected=1:actual=2",
        )
        write_text(makefile_path, makefile_backup)

        build_path = tmp_root / "zigux/tests/phase12_build.zig"
        build_backup = build_path.read_text(encoding="utf-8")
        write_text(
            build_path,
            build_backup.replace("phase12-libbpf-reviewability-tests\n", "", 1),
        )
        expect_missing(
            "missing_shared_build_reviewability_test",
            run_checker(tmp_root),
            "phase12_build:phase12-libbpf-reviewability-tests",
        )
        write_text(build_path, build_backup)

    print("PHASE12_SHARED_REPLAY_CONTRACT_SELF_TEST=pass")
    print("PHASE12_SHARED_REPLAY_CONTRACT_SELF_TEST_CASE_COUNT=26")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(run_self_test())
    raise SystemExit(validate_contract(ROOT))
