#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
README_PATH = ROOT / "scripts/zigux/README.md"
DOCS_README_PATH = ROOT / "Documentation/zigux/README.md"
TESTS_README_PATH = ROOT / "zigux/tests/README.md"
MAKEFILE_PATH = ROOT / "zigux/Makefile"
WORKFLOW_PATH = ROOT / ".github/workflows/zigux-bootstrap.yml"
BUILD_PATH = ROOT / "zigux/tests/phase11_build.zig"
FIXTURE_PATH = ROOT / "zigux/tests/fixtures/phase11_build_inventory.json"
SHARED_REPLAY_NOTE_PATH = ROOT / "Documentation/zigux/phase11-shared-replay-contract.md"
REVIEW_CHECKLIST_PATH = ROOT / "Documentation/zigux/review-checklist.md"
REVIEW_GUIDE_PATH = ROOT / "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md"
TESTS_COMPANION_PATH = ROOT / "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"

README_MARKERS = [
    "Phase 11 flow",
    "`make -C zigux phase11-validate` is the validator-first entrypoint for the active simple-driver tranche.",
    "`check-phase11-build-inventory.py`, `check-phase11-layout-assert-surface.py`, `check-phase11-hvc-validation-flow.py`, and `check-phase11-hvc-cleanup-alignment.py` keep the build snapshot, the Phase 11 layout-assert survey surface, the shared-versus-dedicated hvc replay contract, and the current hvc cleanup packet explicit before the broader Phase 11 validator runs.",
    "`validate-phase11.py` keeps those pre-replay gates plus `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_hvc_console_manifest.json`, and `zigux/tests/phase11_uapi_header_parity_manifest.json` aligned with `zigux/tests/phase11_build.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and the dedicated hvc_console survey note and validation matrix.",
    "`make -C zigux phase11-hvc-survey` is the dedicated archival replay for `zigux/tests/phase11_hvc_console_survey.zig`, while `make -C zigux phase11` keeps the shared Phase 11 replay plus that dedicated archival step in one published path.",
]
DOCS_README_MARKERS = [
    "`Documentation/zigux/phase11-shared-replay-contract.md` now keeps the shared-versus-dedicated replay boundary explicit from the docs root",
    "`python3 scripts/zigux/check-phase11-build-inventory.py`, `python3 scripts/zigux/check-phase11-layout-assert-surface.py`, `python3 scripts/zigux/check-phase11-hvc-validation-flow.py`, `python3 scripts/zigux/check-phase11-hvc-cleanup-alignment.py`, and `python3 scripts/zigux/check-phase11-shared-replay-contract.py` now keep the build snapshot, layout-assert review surface, the shared replay-contract note, the current hvc cleanup packet, and the shared-versus-dedicated replay boundary explicit as the pre-replay Phase 11 delivery gate behind `make -C zigux phase11-validate`.",
    "`python3 scripts/zigux/check-phase11-shared-replay-contract.py`, `python3 scripts/zigux/validate-phase11.py`, `zigux/tests/fixtures/phase11_build_inventory.json`, `make -C zigux phase11-validate`, and `make -C zigux phase11` now define the shared Phase 11 reviewability path, with the dedicated `zigux/tests/phase11_hvc_console_survey.zig` archival replay still kept separate from `zigux/tests/phase11_build.zig`.",
    "the active Phase 11 simple-driver packet now keeps the four roadmap-backed driver lanes visible from the top-level docs index while keeping the paired UAPI header parity survey explicit as the shared tranche-close boundary.",
]
TESTS_README_MARKERS = [
    "keep `Documentation/zigux/phase11-shared-replay-contract.md`, `zigux/tests/phase11_build.zig`, `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/phase11_dw_wdt_suspend_resume.zig`, `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `scripts/zigux/check-phase11-build-inventory.py`, `scripts/zigux/check-phase11-layout-assert-surface.py`, `scripts/zigux/check-phase11-hvc-validation-flow.py`, `scripts/zigux/check-phase11-hvc-cleanup-alignment.py`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, and `scripts/zigux/validate-phase11.py` aligned so the tests root names the same pre-replay stack, four shared split and adjunct replays, shared-versus-dedicated replay boundary, and shared header packet as the docs-root and validator-first packet.",
    "keep the shared-versus-dedicated replay boundary explicit: `zigux/tests/phase11_build.zig` remains the shared replay for the landed starter packet and explicitly carries `zigux/tests/phase11_dw_wdt_suspend_resume.zig`, `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, and `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, while `zigux/tests/phase11_hvc_console_survey.zig` remains the dedicated archival replay for the exact shared-versus-dedicated delivery contract and `scripts/zigux/check-phase11-header-boundary-packet.py` keeps the shared header-boundary packet explicit beside that split.",
    "- Phase 11: do `Documentation/zigux/phase11-shared-replay-contract.md`, `scripts/zigux/check-phase11-build-inventory.py`, `scripts/zigux/check-phase11-layout-assert-surface.py`, `scripts/zigux/check-phase11-hvc-validation-flow.py`, `scripts/zigux/check-phase11-hvc-cleanup-alignment.py`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, and `zigux/tests/phase11_uapi_header_parity_manifest.json` still keep the pre-replay stack, the shared-versus-dedicated `hvc_console` split, and the shared header-boundary packet aligned?",
]
MAKEFILE_MARKERS = [
    "phase11-validate:",
    "scripts/zigux/check-phase11-build-inventory.py --self-test",
    "scripts/zigux/check-phase11-build-inventory.py",
    "scripts/zigux/check-phase11-layout-assert-surface.py --self-test",
    "scripts/zigux/check-phase11-layout-assert-surface.py",
    "scripts/zigux/check-phase11-hvc-validation-flow.py --self-test",
    "scripts/zigux/check-phase11-hvc-validation-flow.py",
    "scripts/zigux/check-phase11-hvc-cleanup-alignment.py --self-test",
    "scripts/zigux/check-phase11-hvc-cleanup-alignment.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py --self-test",
    "scripts/zigux/validate-phase11.py --self-test",
    "scripts/zigux/validate-phase11.py",
    "phase11-hvc-survey:",
    "$(ZIG) build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all",
]
WORKFLOW_MARKERS = [
    "Self-test Phase 11 simple-driver validator",
    "Self-test Phase 11 build inventory checker",
    "Self-test Phase 11 hvc validation flow checker",
    "Self-test Phase 11 hvc cleanup alignment checker",
    "Self-test Phase 11 layout assert surface checker",
    "Self-test Phase 11 shared replay contract checker",
    "Validate Phase 11 shared replay contract",
    "Validate Phase 11 simple-driver bundle",
    "Run Phase 11 watchdog and console tests",
    "Run dedicated Phase 11 hvc survey replay",
]
BUILD_MARKERS = [
    '    .name = "phase11-dw-wdt-suspend-resume-tests",',
    '    .name = "phase11-dw-wdt-remove-idle-split-tests",',
    '    .name = "phase11-hvc-console-modem-control-split-tests",',
    '    .name = "phase11-hvc-console-poll-retry-split-tests",',
    "    test_step.dependOn(&run_phase11_dw_wdt_suspend_resume_tests.step);",
    "    test_step.dependOn(&run_phase11_dw_wdt_remove_idle_split_tests.step);",
    "    test_step.dependOn(&run_phase11_hvc_console_modem_control_split_tests.step);",
    "    test_step.dependOn(&run_phase11_hvc_console_poll_retry_split_tests.step);",
]
FORBIDDEN_BUILD_MARKERS = [
    "test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
]
SHARED_REPLAY_NOTE_MARKERS = [
    "# Phase 11 Shared Replay Contract",
    "python3 scripts/zigux/check-phase11-shared-replay-contract.py --self-test",
    "python3 scripts/zigux/check-phase11-shared-replay-contract.py",
    "python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test",
    "python3 scripts/zigux/check-phase11-header-boundary-packet.py",
    "python3 scripts/zigux/validate-phase11.py --self-test",
    "make -C zigux phase11-validate",
    "The same contract is fail-closed by `python3 scripts/zigux/check-phase11-shared-replay-contract.py` before the broader validator runs.",
    "zig build test --build-file zigux/tests/phase11_build.zig --summary all",
    "make -C zigux phase11-hvc-survey",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/tests/phase11_build.zig",
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "scripts/zigux/check-phase11-build-inventory.py",
    "scripts/zigux/check-phase11-hvc-validation-flow.py",
    "scripts/zigux/check-phase11-shared-replay-contract.py",
    "zigux/tests/phase11_hvc_console_survey.zig",
    "The paired UAPI and driver-header parity boundary also stays explicit in the same pre-replay gate stack:",
    "zigux/tests/phase11_uapi_header_parity_survey.zig",
]
REVIEW_CHECKLIST_MARKERS = [
    "- if the change touches the active Phase 11 contributor packet, do `Documentation/zigux/phase11-shared-replay-contract.md`, `scripts/zigux/check-phase11-build-inventory.py`, `scripts/zigux/check-phase11-layout-assert-surface.py`, `scripts/zigux/check-phase11-hvc-validation-flow.py`, `scripts/zigux/check-phase11-hvc-cleanup-alignment.py`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, and `zigux/tests/phase11_uapi_header_parity_manifest.json` still keep the pre-replay stack, the shared-versus-dedicated `hvc_console` split, and the shared header-boundary packet aligned?",
    "- if the change is a Phase 11 simple-driver slice, do `scripts/zigux/validate-phase11.py`, `zigux/tests/phase11_build.zig`, the four driver-local Phase 11 manifests, and `zigux/tests/phase11_uapi_header_parity_manifest.json` still agree on the same bounded simple-driver scope, shared replay contract, and explicit ready-next versus blocked follow-up posture?",
    "- if the change touches the shared Phase 11 tooling path, do `zigux/tests/phase11_build.zig`, `zigux/tests/fixtures/phase11_build_inventory.json`, and `zigux/tests/phase11_hvc_console_survey.zig` still agree on the exact shared build inventory and the dedicated-survey boundary instead of silently implying that every Phase 11 survey gate already runs in the shared path?",
    "- if the change touches the shared Phase 11 replay contract packet, do `Documentation/zigux/phase11-shared-replay-contract.md`, `scripts/zigux/validate-phase11.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/fixtures/phase11_build_inventory.json`, and `zigux/tests/phase11_hvc_console_survey.zig` still agree on the same shared-versus-dedicated replay boundary instead of leaving that packet split implicit?",
]
REVIEW_GUIDE_MARKERS = [
    "## Phase 11: Simple-driver packet",
    "- `python3 scripts/zigux/check-phase11-shared-replay-contract.py --self-test`",
    "- `python3 scripts/zigux/check-phase11-shared-replay-contract.py`",
    "- `Documentation/zigux/phase11-shared-replay-contract.md`",
    "- `Documentation/zigux/phase11-uapi-header-parity-survey.md`",
    "- `scripts/zigux/check-phase11-shared-replay-contract.py`",
    "- `scripts/zigux/check-phase11-header-boundary-packet.py`",
    "- Does the shared Phase 11 replay still stay separate from the dedicated archival `hvc_console` survey?",
]
TESTS_COMPANION_MARKERS = [
    "## Phase 11 tests-root packet",
    "- `scripts/zigux/check-phase11-shared-replay-contract.py`",
    "- `zigux/tests/phase11_dw_wdt_suspend_resume.zig`",
    "- `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`",
    "- `zigux/tests/phase11_hvc_console_modem_control_split.zig`",
    "- `zigux/tests/phase11_hvc_console_poll_retry_split.zig`",
    "- Do the pre-replay Phase 11 checkers still describe the same delivery contract that `zigux/tests/phase11_build.zig` and `zigux/tests/fixtures/phase11_build_inventory.json` claim?",
    "- Does `zigux/tests/phase11_hvc_console_survey.zig` still stay separate as the dedicated archival replay while the shared starter packet remains under `zigux/tests/phase11_build.zig`, explicitly includes `zigux/tests/phase11_dw_wdt_suspend_resume.zig`, `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, and `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, and keeps the shared header-boundary packet explicit through `scripts/zigux/check-phase11-header-boundary-packet.py`?",
]
EXPECTED_SHARED_SPLIT_REPLAYS = [
    {
        "test": "phase11-dw-wdt-remove-idle-split-tests",
        "path": "zigux/tests/phase11_dw_wdt_remove_idle_split.zig",
    },
    {
        "test": "phase11-hvc-console-modem-control-split-tests",
        "path": "zigux/tests/phase11_hvc_console_modem_control_split.zig",
    },
    {
        "test": "phase11-hvc-console-poll-retry-split-tests",
        "path": "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
    },
]
EXPECTED_SHARED_REPLAY_MARKERS = [
    {
        "path": "zigux/tests/phase11_dw_wdt_suspend_resume.zig",
        "marker": "    try std.testing.expect(summary.resume_preserves_timeout_programming);",
    },
    {
        "path": "zigux/tests/phase11_dw_wdt_remove_idle_split.zig",
        "marker": "    try std.testing.expect(reset_available_summary.remove_clears_interrupt_status);",
    },
    {
        "path": "zigux/tests/phase11_hvc_console_modem_control_split.zig",
        "marker": "    try std.testing.expectEqual(@as(c_int, -7), summary.tiocmset_result);",
    },
    {
        "path": "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
        "marker": "    try std.testing.expect(dispatch.invokes_sysrq_handler);",
    },
]


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_fixture(path: Path) -> dict[str, object]:
    return json.loads(text(path))


def validate_contract(root: Path) -> int:
    missing: list[str] = []
    for label, path, markers in [
        ("readme", root / README_PATH, README_MARKERS),
        ("docs_readme", root / DOCS_README_PATH, DOCS_README_MARKERS),
        ("tests_readme", root / TESTS_README_PATH, TESTS_README_MARKERS),
        ("makefile", root / MAKEFILE_PATH, MAKEFILE_MARKERS),
        ("workflow", root / WORKFLOW_PATH, WORKFLOW_MARKERS),
        ("build", root / BUILD_PATH, BUILD_MARKERS),
        ("shared_replay_note", root / SHARED_REPLAY_NOTE_PATH, SHARED_REPLAY_NOTE_MARKERS),
        ("review_checklist", root / REVIEW_CHECKLIST_PATH, REVIEW_CHECKLIST_MARKERS),
        ("review_guide", root / REVIEW_GUIDE_PATH, REVIEW_GUIDE_MARKERS),
        ("tests_companion", root / TESTS_COMPANION_PATH, TESTS_COMPANION_MARKERS),
    ]:
        source = text(path)
        for marker in markers:
            if marker not in source:
                missing.append(f"{label}:{marker}")

    build_text = text(root / BUILD_PATH)
    for marker in FORBIDDEN_BUILD_MARKERS:
        if marker in build_text:
            missing.append(f"build:forbidden:{marker}")

    fixture = load_fixture(root / FIXTURE_PATH)
    if fixture.get("shared_split_replays") != EXPECTED_SHARED_SPLIT_REPLAYS:
        missing.append("fixture:shared_split_replays")
    if fixture.get("shared_replay_markers") != EXPECTED_SHARED_REPLAY_MARKERS:
        missing.append("fixture:shared_replay_markers")
    for replay in EXPECTED_SHARED_SPLIT_REPLAYS:
        replay_path = root / str(replay["path"])
        if not replay_path.exists():
            missing.append(f"shared_split_replay_file:{replay['path']}")
    for replay in EXPECTED_SHARED_REPLAY_MARKERS:
        replay_path = root / str(replay["path"])
        if not replay_path.exists():
            missing.append(f"shared_replay_file:{replay['path']}")
            continue
        replay_text = text(replay_path)
        if str(replay["marker"]) not in replay_text:
            missing.append(f"shared_replay_marker:{replay['path']}:{replay['marker']}")

    if missing:
        print("PHASE11_SHARED_REPLAY_CONTRACT=fail")
        print("PHASE11_SHARED_REPLAY_CONTRACT_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE11_SHARED_REPLAY_CONTRACT_MISSING_END")
        return 1

    print("PHASE11_SHARED_REPLAY_CONTRACT=pass")
    print(f"PHASE11_SHARED_REPLAY_MARKER_COUNT={len(EXPECTED_SHARED_REPLAY_MARKERS)}")
    print(f"PHASE11_SHARED_SPLIT_REPLAY_COUNT={len(EXPECTED_SHARED_SPLIT_REPLAYS)}")
    print(f"PHASE11_SHARED_REPLAY_NOTE_MARKER_COUNT={len(SHARED_REPLAY_NOTE_MARKERS)}")
    print(f"PHASE11_SHARED_REPLAY_CHECKLIST_MARKER_COUNT={len(REVIEW_CHECKLIST_MARKERS)}")
    print(f"PHASE11_SHARED_REVIEW_GUIDE_MARKER_COUNT={len(REVIEW_GUIDE_MARKERS)}")
    print(f"PHASE11_SHARED_TESTS_COMPANION_MARKER_COUNT={len(TESTS_COMPANION_MARKERS)}")
    return 0


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts/zigux/check-phase11-shared-replay-contract.py")],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )


def expect_missing(label: str, result: subprocess.CompletedProcess[str], marker: str) -> None:
    if result.returncode == 0:
        raise SystemExit(f"phase11-shared-replay-self-test:{label}:unexpected_pass")
    if marker not in result.stdout:
        actual = result.stdout.strip() or result.stderr.strip() or "no_output"
        raise SystemExit(
            f"phase11-shared-replay-self-test:{label}:expected:{marker}:actual:{actual}"
        )


def write_fixture_tree(root: Path) -> None:
    write_text(root / "scripts/zigux/README.md", "\n".join(README_MARKERS) + "\n")
    write_text(root / "Documentation/zigux/README.md", "\n".join(DOCS_README_MARKERS) + "\n")
    write_text(root / "zigux/tests/README.md", "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(root / "zigux/Makefile", "\n".join(MAKEFILE_MARKERS) + "\n")
    write_text(root / ".github/workflows/zigux-bootstrap.yml", "\n".join(WORKFLOW_MARKERS) + "\n")
    build_body = "\n".join(
        BUILD_MARKERS
        + [
            '    const hvc_console_survey_step = b.step("hvc-console-survey", "Run the dedicated Phase 11 hvc_console survey replay");'
        ]
    )
    write_text(root / "zigux/tests/phase11_build.zig", build_body + "\n")
    write_text(
        root / "zigux/tests/fixtures/phase11_build_inventory.json",
        json.dumps(
            {
                "shared_split_replays": EXPECTED_SHARED_SPLIT_REPLAYS,
                "shared_replay_markers": EXPECTED_SHARED_REPLAY_MARKERS,
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / "Documentation/zigux/phase11-shared-replay-contract.md",
        "\n".join(
            [
                "# Phase 11 Shared Replay Contract",
                "",
                "## Pre-Replay Checker Stack",
                "",
                "- `python3 scripts/zigux/check-phase11-shared-replay-contract.py --self-test`",
                "- `python3 scripts/zigux/check-phase11-shared-replay-contract.py`",
                "- `python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test`",
                "- `python3 scripts/zigux/check-phase11-header-boundary-packet.py`",
                "- `python3 scripts/zigux/validate-phase11.py --self-test`",
                "- `python3 scripts/zigux/validate-phase11.py`",
                "",
                "The published wrapper remains `make -C zigux phase11-validate`.",
                "",
                "The same contract is fail-closed by `python3 scripts/zigux/check-phase11-shared-replay-contract.py` before the broader validator runs.",
                "",
                "## Shared Replay Surface",
                "",
                "- `zig build test --build-file zigux/tests/phase11_build.zig --summary all`",
                "",
                "## Dedicated Boundary",
                "",
                "- `make -C zigux phase11-hvc-survey`",
                "- `zigux/tests/phase11_hvc_console_survey.zig`",
                "",
                "The paired UAPI and driver-header parity boundary also stays explicit in the same pre-replay gate stack:",
                "",
                "- `zigux/tests/phase11_uapi_header_parity_survey.zig`",
                "",
                "## Contributor Sync Points",
                "",
                "- `Documentation/zigux/README.md`",
                "- `Documentation/zigux/review-checklist.md`",
                "- `scripts/zigux/README.md`",
                "- `zigux/tests/README.md`",
                "",
                "## Review Use",
                "",
                "- `zigux/tests/phase11_build.zig`",
                "- `zigux/tests/fixtures/phase11_build_inventory.json`",
                "- `scripts/zigux/check-phase11-build-inventory.py`",
                "- `scripts/zigux/check-phase11-hvc-validation-flow.py`",
                "- `scripts/zigux/check-phase11-shared-replay-contract.py`",
                "- `zigux/tests/phase11_hvc_console_survey.zig`",
                "",
            ]
        ),
    )
    write_text(
        root / "Documentation/zigux/review-checklist.md",
        "# Zigux Review Checklist\n\n## ABI and Runtime\n"
        + "\n".join(REVIEW_CHECKLIST_MARKERS)
        + "\n",
    )
    write_text(
        root / "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md",
        "\n".join(REVIEW_GUIDE_MARKERS) + "\n",
    )
    write_text(
        root / "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
        "\n".join(TESTS_COMPANION_MARKERS) + "\n",
    )
    write_text(
        root / "scripts/zigux/check-phase11-shared-replay-contract.py",
        Path(__file__).read_text(encoding="utf-8"),
    )
    for replay in EXPECTED_SHARED_REPLAY_MARKERS:
        write_text(root / str(replay["path"]), str(replay["marker"]) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase11_shared_replay_contract_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_tree(tmp_root)

        baseline = run_checker(tmp_root)
        if baseline.returncode != 0:
            raise SystemExit(
                "phase11-shared-replay-self-test:baseline_failed:"
                f"{baseline.stdout.strip() or baseline.stderr.strip() or 'no_output'}"
            )

        readme_path = tmp_root / "scripts/zigux/README.md"
        readme_backup = text(readme_path)
        write_text(readme_path, readme_backup.replace("Phase 11 flow\n", "", 1))
        expect_missing("missing_readme_section", run_checker(tmp_root), "readme:Phase 11 flow")
        write_text(readme_path, readme_backup)

        docs_readme_path = tmp_root / "Documentation/zigux/README.md"
        docs_readme_backup = text(docs_readme_path)
        write_text(
            docs_readme_path,
            docs_readme_backup.replace(DOCS_README_MARKERS[0] + "\n", "", 1),
        )
        expect_missing(
            "missing_docs_root_contract_marker",
            run_checker(tmp_root),
            f"docs_readme:{DOCS_README_MARKERS[0]}",
        )
        write_text(docs_readme_path, docs_readme_backup)

        write_text(
            docs_readme_path,
            docs_readme_backup.replace(DOCS_README_MARKERS[1] + "\n", "", 1),
        )
        expect_missing(
            "missing_docs_root_checker_gate",
            run_checker(tmp_root),
            f"docs_readme:{DOCS_README_MARKERS[1]}",
        )
        write_text(docs_readme_path, docs_readme_backup)

        write_text(
            docs_readme_path,
            docs_readme_backup.replace(DOCS_README_MARKERS[3] + "\n", "", 1),
        )
        expect_missing(
            "missing_docs_root_header_boundary_summary",
            run_checker(tmp_root),
            f"docs_readme:{DOCS_README_MARKERS[3]}",
        )
        write_text(docs_readme_path, docs_readme_backup)

        tests_readme_path = tmp_root / "zigux/tests/README.md"
        tests_readme_backup = text(tests_readme_path)
        write_text(
            tests_readme_path,
            tests_readme_backup.replace(TESTS_README_MARKERS[0] + "\n", "", 1),
        )
        expect_missing(
            "missing_tests_root_alignment_packet",
            run_checker(tmp_root),
            f"tests_readme:{TESTS_README_MARKERS[0]}",
        )
        write_text(tests_readme_path, tests_readme_backup)

        write_text(
            tests_readme_path,
            tests_readme_backup.replace(TESTS_README_MARKERS[1] + "\n", "", 1),
        )
        expect_missing(
            "missing_tests_root_boundary_marker",
            run_checker(tmp_root),
            f"tests_readme:{TESTS_README_MARKERS[1]}",
        )
        write_text(tests_readme_path, tests_readme_backup)

        write_text(
            tests_readme_path,
            tests_readme_backup.replace(TESTS_README_MARKERS[2] + "\n", "", 1),
        )
        expect_missing(
            "missing_tests_root_contributor_prompt",
            run_checker(tmp_root),
            f"tests_readme:{TESTS_README_MARKERS[2]}",
        )
        write_text(tests_readme_path, tests_readme_backup)

        build_path = tmp_root / "zigux/tests/phase11_build.zig"
        build_backup = text(build_path)
        write_text(
            build_path,
            build_backup + "\n" + FORBIDDEN_BUILD_MARKERS[0] + "\n",
        )
        expect_missing(
            "forbidden_hvc_survey_dep",
            run_checker(tmp_root),
            f"build:forbidden:{FORBIDDEN_BUILD_MARKERS[0]}",
        )
        write_text(build_path, build_backup)

        fixture_path = tmp_root / "zigux/tests/fixtures/phase11_build_inventory.json"
        fixture_backup = text(fixture_path)
        fixture = json.loads(fixture_backup)
        fixture["shared_replay_markers"] = fixture["shared_replay_markers"][:-1]
        write_text(fixture_path, json.dumps(fixture, indent=2) + "\n")
        expect_missing(
            "shared_replay_fixture_drift",
            run_checker(tmp_root),
            "fixture:shared_replay_markers",
        )
        write_text(fixture_path, fixture_backup)

        fixture = json.loads(fixture_backup)
        fixture["shared_split_replays"] = fixture["shared_split_replays"][:-1]
        write_text(fixture_path, json.dumps(fixture, indent=2) + "\n")
        expect_missing(
            "shared_split_replay_fixture_drift",
            run_checker(tmp_root),
            "fixture:shared_split_replays",
        )
        write_text(fixture_path, fixture_backup)

        shared_replay_path = tmp_root / EXPECTED_SHARED_REPLAY_MARKERS[0]["path"]
        shared_replay_backup = text(shared_replay_path)
        write_text(shared_replay_path, "")
        expect_missing(
            "missing_shared_replay_marker",
            run_checker(tmp_root),
            (
                "shared_replay_marker:"
                f"{EXPECTED_SHARED_REPLAY_MARKERS[0]['path']}:"
                f"{EXPECTED_SHARED_REPLAY_MARKERS[0]['marker']}"
            ),
        )
        write_text(shared_replay_path, shared_replay_backup)

        split_replay_path = tmp_root / EXPECTED_SHARED_SPLIT_REPLAYS[0]["path"]
        split_replay_backup = text(split_replay_path)
        split_replay_path.unlink()
        expect_missing(
            "missing_shared_split_replay_file",
            run_checker(tmp_root),
            f"shared_split_replay_file:{EXPECTED_SHARED_SPLIT_REPLAYS[0]['path']}",
        )
        write_text(split_replay_path, split_replay_backup)

        makefile_path = tmp_root / "zigux/Makefile"
        makefile_backup = text(makefile_path)
        write_text(
            makefile_path,
            makefile_backup.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py --self-test\n",
                "",
                1,
            ),
        )
        expect_missing(
            "missing_makefile_checker_self_test",
            run_checker(tmp_root),
            "makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py --self-test",
        )
        write_text(makefile_path, makefile_backup)

        write_text(
            makefile_path,
            makefile_backup.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py\n",
                "",
                1,
            ),
        )
        expect_missing(
            "missing_makefile_checker_run_hook",
            run_checker(tmp_root),
            "makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py --self-test",
        )
        write_text(makefile_path, makefile_backup)

        workflow_path = tmp_root / ".github/workflows/zigux-bootstrap.yml"
        workflow_backup = text(workflow_path)
        write_text(
            workflow_path,
            workflow_backup.replace(
                "Self-test Phase 11 shared replay contract checker\n",
                "",
                1,
            ),
        )
        expect_missing(
            "missing_workflow_checker_step",
            run_checker(tmp_root),
            "workflow:Self-test Phase 11 shared replay contract checker",
        )
        write_text(workflow_path, workflow_backup)

        note_path = tmp_root / "Documentation/zigux/phase11-shared-replay-contract.md"
        note_backup = text(note_path)
        write_text(
            note_path,
            note_backup.replace(
                "- `python3 scripts/zigux/check-phase11-shared-replay-contract.py --self-test`\n",
                "",
                1,
            ),
        )
        expect_missing(
            "missing_note_checker_self_test",
            run_checker(tmp_root),
            "shared_replay_note:python3 scripts/zigux/check-phase11-shared-replay-contract.py --self-test",
        )
        write_text(note_path, note_backup)

        write_text(
            note_path,
            note_backup.replace(
                "- `python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test`\n",
                "",
                1,
            ),
        )
        expect_missing(
            "missing_note_header_boundary_self_test",
            run_checker(tmp_root),
            "shared_replay_note:python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test",
        )
        write_text(note_path, note_backup)

        write_text(
            note_path,
            note_backup.replace(
                "The paired UAPI and driver-header parity boundary also stays explicit in the same pre-replay gate stack:\n",
                "",
                1,
            ),
        )
        expect_missing(
            "missing_note_header_boundary_section",
            run_checker(tmp_root),
            "shared_replay_note:The paired UAPI and driver-header parity boundary also stays explicit in the same pre-replay gate stack:",
        )
        write_text(note_path, note_backup)

        write_text(
            note_path,
            note_backup.replace("- `Documentation/zigux/README.md`\n", "", 1),
        )
        expect_missing(
            "missing_note_docs_root_sync_point",
            run_checker(tmp_root),
            "shared_replay_note:Documentation/zigux/README.md",
        )
        write_text(note_path, note_backup)

        write_text(
            note_path,
            note_backup.replace("- `Documentation/zigux/review-checklist.md`\n", "", 1),
        )
        expect_missing(
            "missing_note_checklist_sync_point",
            run_checker(tmp_root),
            "shared_replay_note:Documentation/zigux/review-checklist.md",
        )
        write_text(note_path, note_backup)

        write_text(
            note_path,
            note_backup.replace("- `scripts/zigux/README.md`\n", "", 1),
        )
        expect_missing(
            "missing_note_scripts_root_sync_point",
            run_checker(tmp_root),
            "shared_replay_note:scripts/zigux/README.md",
        )
        write_text(note_path, note_backup)

        write_text(
            note_path,
            note_backup.replace("- `zigux/tests/README.md`\n", "", 1),
        )
        expect_missing(
            "missing_note_tests_root_sync_point",
            run_checker(tmp_root),
            "shared_replay_note:zigux/tests/README.md",
        )
        write_text(note_path, note_backup)

        checklist_path = tmp_root / "Documentation/zigux/review-checklist.md"
        checklist_backup = text(checklist_path)
        write_text(
            checklist_path,
            checklist_backup.replace(REVIEW_CHECKLIST_MARKERS[0] + "\n", "", 1),
        )
        expect_missing(
            "missing_active_phase11_contributor_prompt",
            run_checker(tmp_root),
            f"review_checklist:{REVIEW_CHECKLIST_MARKERS[0]}",
        )
        write_text(checklist_path, checklist_backup)

        write_text(
            checklist_path,
            checklist_backup.replace(REVIEW_CHECKLIST_MARKERS[2] + "\n", "", 1),
        )
        expect_missing(
            "missing_phase11_checklist_tooling_question",
            run_checker(tmp_root),
            f"review_checklist:{REVIEW_CHECKLIST_MARKERS[2]}",
        )
        write_text(checklist_path, checklist_backup)

        write_text(
            checklist_path,
            checklist_backup.replace(REVIEW_CHECKLIST_MARKERS[3] + "\n", "", 1),
        )
        expect_missing(
            "missing_exact_replay_contract_question",
            run_checker(tmp_root),
            f"review_checklist:{REVIEW_CHECKLIST_MARKERS[3]}",
        )
        write_text(checklist_path, checklist_backup)

        review_guide_path = tmp_root / "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md"
        review_guide_backup = text(review_guide_path)
        write_text(
            review_guide_path,
            review_guide_backup.replace(REVIEW_GUIDE_MARKERS[1] + "\n", "", 1),
        )
        expect_missing(
            "missing_review_guide_checker_self_test",
            run_checker(tmp_root),
            f"review_guide:{REVIEW_GUIDE_MARKERS[1]}",
        )
        write_text(review_guide_path, review_guide_backup)

        write_text(
            review_guide_path,
            review_guide_backup.replace(REVIEW_GUIDE_MARKERS[5] + "\n", "", 1),
        )
        expect_missing(
            "missing_review_guide_header_boundary_checker",
            run_checker(tmp_root),
            f"review_guide:{REVIEW_GUIDE_MARKERS[5]}",
        )
        write_text(review_guide_path, review_guide_backup)

        tests_companion_path = tmp_root / "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"
        tests_companion_backup = text(tests_companion_path)
        write_text(
            tests_companion_path,
            tests_companion_backup.replace(TESTS_COMPANION_MARKERS[1] + "\n", "", 1),
        )
        expect_missing(
            "missing_tests_companion_checker_marker",
            run_checker(tmp_root),
            f"tests_companion:{TESTS_COMPANION_MARKERS[1]}",
        )
        write_text(tests_companion_path, tests_companion_backup)

        write_text(
            tests_companion_path,
            tests_companion_backup.replace(TESTS_COMPANION_MARKERS[-1] + "\n", "", 1),
        )
        expect_missing(
            "missing_tests_companion_expanded_boundary_prompt",
            run_checker(tmp_root),
            f"tests_companion:{TESTS_COMPANION_MARKERS[-1]}",
        )

    print("PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST=pass")
    print("PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST_CASE_COUNT=28")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(run_self_test())
    raise SystemExit(validate_contract(ROOT))
