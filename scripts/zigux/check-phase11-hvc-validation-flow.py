#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile


SCRIPT_NAME = "scripts/zigux/check-phase11-hvc-validation-flow.py"
BUILD_INVENTORY_CHECKER_PATH = "scripts/zigux/check-phase11-build-inventory.py"
LAYOUT_ASSERT_CHECKER_PATH = "scripts/zigux/check-phase11-layout-assert-surface.py"
CHECKER_PATH = "scripts/zigux/check-phase11-hvc-cleanup-alignment.py"
SHARED_REPLAY_CONTRACT_CHECKER_PATH = "scripts/zigux/check-phase11-shared-replay-contract.py"
HEADER_BOUNDARY_PACKET_CHECKER_PATH = "scripts/zigux/check-phase11-header-boundary-packet.py"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"

MAKEFILE_MARKERS = [
    "phase11-validate:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-layout-assert-surface.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-layout-assert-surface.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-validation-flow.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-validation-flow.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-cleanup-alignment.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-cleanup-alignment.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-header-boundary-packet.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-header-boundary-packet.py",
]
MAKEFILE_ORDERED_MARKERS = [
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-layout-assert-surface.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-layout-assert-surface.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-validation-flow.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-validation-flow.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-cleanup-alignment.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-cleanup-alignment.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-header-boundary-packet.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-header-boundary-packet.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py\n",
]

WORKFLOW_MARKERS = [
    "Self-test Phase 11 build inventory checker",
    "python3 scripts/zigux/check-phase11-build-inventory.py --self-test",
    "Self-test Phase 11 layout assert surface checker",
    "python3 scripts/zigux/check-phase11-layout-assert-surface.py --self-test",
    "Self-test Phase 11 hvc validation flow checker",
    "python3 scripts/zigux/check-phase11-hvc-validation-flow.py --self-test",
    "Self-test Phase 11 hvc cleanup alignment checker",
    "python3 scripts/zigux/check-phase11-hvc-cleanup-alignment.py --self-test",
    "Self-test Phase 11 shared replay contract checker",
    "python3 scripts/zigux/check-phase11-shared-replay-contract.py --self-test",
    "Self-test Phase 11 header boundary packet checker",
    "python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test",
    "Validate Phase 11 shared replay contract",
    "python3 scripts/zigux/check-phase11-shared-replay-contract.py",
    "Validate Phase 11 header boundary packet",
    "python3 scripts/zigux/check-phase11-header-boundary-packet.py",
    "Validate Phase 11 simple-driver bundle",
    "make -C zigux phase11-validate",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    missing: list[str] = []

    for rel_path in [
        SCRIPT_NAME,
        BUILD_INVENTORY_CHECKER_PATH,
        LAYOUT_ASSERT_CHECKER_PATH,
        CHECKER_PATH,
        SHARED_REPLAY_CONTRACT_CHECKER_PATH,
        HEADER_BOUNDARY_PACKET_CHECKER_PATH,
        MAKEFILE_PATH,
        WORKFLOW_PATH,
    ]:
        if not (root / rel_path).exists():
            missing.append(f"missing:{rel_path}")
    if missing:
        return missing

    makefile = read_text(root, MAKEFILE_PATH)
    workflow = read_text(root, WORKFLOW_PATH)

    for marker in MAKEFILE_MARKERS:
        if marker not in makefile:
            missing.append(f"make:{marker}")

    last_index = -1
    for marker in MAKEFILE_ORDERED_MARKERS:
        index = makefile.find(marker)
        if index == -1:
            continue
        if index < last_index:
            missing.append(f"make-order:{marker}")
            break
        last_index = index

    for marker in WORKFLOW_MARKERS:
        if marker not in workflow:
            missing.append(f"workflow:{marker}")

    return missing


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / SCRIPT_NAME)],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )


def expect_missing(label: str, root: Path, needle: str) -> None:
    result = run_validator(root)
    if result.returncode == 0:
        raise SystemExit(f"phase11-hvc-flow-self-test:{label}:unexpected_pass")
    if needle not in result.stdout:
        actual = result.stdout.strip() or "none"
        raise SystemExit(
            f"phase11-hvc-flow-self-test:{label}:expected:{needle}:actual:{actual}"
        )


def clone_fixture_root(destination_root: Path) -> None:
    script_target = destination_root / SCRIPT_NAME
    script_target.parent.mkdir(parents=True, exist_ok=True)
    script_target.write_text(Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")

    build_inventory_checker_target = destination_root / BUILD_INVENTORY_CHECKER_PATH
    build_inventory_checker_target.parent.mkdir(parents=True, exist_ok=True)
    build_inventory_checker_target.write_text("#!/usr/bin/env python3\nprint('placeholder')\n", encoding="utf-8")

    layout_assert_checker_target = destination_root / LAYOUT_ASSERT_CHECKER_PATH
    layout_assert_checker_target.parent.mkdir(parents=True, exist_ok=True)
    layout_assert_checker_target.write_text("#!/usr/bin/env python3\nprint('placeholder')\n", encoding="utf-8")

    checker_target = destination_root / CHECKER_PATH
    checker_target.parent.mkdir(parents=True, exist_ok=True)
    checker_target.write_text("#!/usr/bin/env python3\nprint('placeholder')\n", encoding="utf-8")

    shared_replay_contract_checker_target = destination_root / SHARED_REPLAY_CONTRACT_CHECKER_PATH
    shared_replay_contract_checker_target.parent.mkdir(parents=True, exist_ok=True)
    shared_replay_contract_checker_target.write_text("#!/usr/bin/env python3\nprint('placeholder')\n", encoding="utf-8")

    header_boundary_packet_checker_target = destination_root / HEADER_BOUNDARY_PACKET_CHECKER_PATH
    header_boundary_packet_checker_target.parent.mkdir(parents=True, exist_ok=True)
    header_boundary_packet_checker_target.write_text("#!/usr/bin/env python3\nprint('placeholder')\n", encoding="utf-8")

    makefile_target = destination_root / MAKEFILE_PATH
    makefile_target.parent.mkdir(parents=True, exist_ok=True)
    makefile_target.write_text(
        "\n".join(
            [
                "phase11-validate:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-layout-assert-surface.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-layout-assert-surface.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-validation-flow.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-validation-flow.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-cleanup-alignment.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-cleanup-alignment.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-header-boundary-packet.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-header-boundary-packet.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py",
                "",
            ]
        ),
        encoding="utf-8",
    )

    workflow_target = destination_root / WORKFLOW_PATH
    workflow_target.parent.mkdir(parents=True, exist_ok=True)
    workflow_target.write_text(
        "\n".join(
            [
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Self-test Phase 11 build inventory checker",
                "        run: python3 scripts/zigux/check-phase11-build-inventory.py --self-test",
                "      - name: Self-test Phase 11 layout assert surface checker",
                "        run: python3 scripts/zigux/check-phase11-layout-assert-surface.py --self-test",
                "      - name: Self-test Phase 11 hvc validation flow checker",
                "        run: python3 scripts/zigux/check-phase11-hvc-validation-flow.py --self-test",
                "      - name: Self-test Phase 11 hvc cleanup alignment checker",
                "        run: python3 scripts/zigux/check-phase11-hvc-cleanup-alignment.py --self-test",
                "      - name: Self-test Phase 11 shared replay contract checker",
                "        run: python3 scripts/zigux/check-phase11-shared-replay-contract.py --self-test",
                "      - name: Self-test Phase 11 header boundary packet checker",
                "        run: python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test",
                "      - name: Validate Phase 11 shared replay contract",
                "        run: python3 scripts/zigux/check-phase11-shared-replay-contract.py",
                "      - name: Validate Phase 11 header boundary packet",
                "        run: python3 scripts/zigux/check-phase11-header-boundary-packet.py",
                "      - name: Validate Phase 11 simple-driver bundle",
                "        run: make -C zigux phase11-validate",
                "",
            ]
        ),
        encoding="utf-8",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase11_hvc_flow_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        clone_fixture_root(tmp_root)

        baseline = run_validator(tmp_root)
        if baseline.returncode != 0:
            raise SystemExit(
                "phase11-hvc-flow-self-test:baseline_failed:"
                f"{baseline.stdout.strip() or baseline.stderr.strip() or 'no_output'}"
            )

        makefile_path = tmp_root / MAKEFILE_PATH
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace(
                "scripts/zigux/check-phase11-layout-assert-surface.py --self-test",
                "scripts/zigux/check-phase11-build-inventory.py",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "makefile_layout_assert_self_test_hook",
            tmp_root,
            "make:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-layout-assert-surface.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "scripts/zigux/check-phase11-build-inventory.py --self-test",
                "scripts/zigux/check-phase11-build-inventory.py",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "makefile_build_inventory_self_test_hook",
            tmp_root,
            "make:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py --self-test\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py\n",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py --self-test\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "makefile_build_inventory_self_test_order",
            tmp_root,
            "make-order:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py\n",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-layout-assert-surface.py --self-test\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-layout-assert-surface.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "makefile_layout_assert_run_hook",
            tmp_root,
            "make:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-layout-assert-surface.py",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-layout-assert-surface.py\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-validation-flow.py --self-test\n",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-validation-flow.py --self-test\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-layout-assert-surface.py\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "makefile_layout_assert_order",
            tmp_root,
            "make-order:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-validation-flow.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "scripts/zigux/check-phase11-hvc-validation-flow.py --self-test",
                "scripts/zigux/check-phase11-build-inventory.py",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "makefile_validation_flow_self_test_hook",
            tmp_root,
            "make:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-validation-flow.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "scripts/zigux/check-phase11-hvc-cleanup-alignment.py --self-test",
                "scripts/zigux/check-phase11-build-inventory.py",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "makefile_cleanup_self_test_hook",
            tmp_root,
            "make:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-cleanup-alignment.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-validation-flow.py\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-cleanup-alignment.py --self-test\n",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-cleanup-alignment.py --self-test\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-validation-flow.py\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "makefile_validation_flow_order",
            tmp_root,
            "make-order:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-cleanup-alignment.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "scripts/zigux/check-phase11-shared-replay-contract.py --self-test",
                "scripts/zigux/check-phase11-build-inventory.py",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "makefile_shared_replay_self_test_hook",
            tmp_root,
            "make:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "scripts/zigux/check-phase11-header-boundary-packet.py --self-test",
                "scripts/zigux/check-phase11-build-inventory.py",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "makefile_header_boundary_self_test_hook",
            tmp_root,
            "make:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-header-boundary-packet.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        workflow_path = tmp_root / WORKFLOW_PATH
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            original_workflow.replace(
                "Self-test Phase 11 build inventory checker",
                "Self-test Phase 11 build snapshot checker",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "workflow_build_inventory_self_test_step",
            tmp_root,
            "workflow:Self-test Phase 11 build inventory checker",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        workflow_path.write_text(
            original_workflow.replace(
                "Self-test Phase 11 layout assert surface checker",
                "Self-test Phase 11 layout surface checker",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "workflow_layout_assert_self_test_step",
            tmp_root,
            "workflow:Self-test Phase 11 layout assert surface checker",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        workflow_path.write_text(
            original_workflow.replace(
                "Self-test Phase 11 hvc validation flow checker",
                "Self-test Phase 11 hvc flow checker",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "workflow_validation_flow_self_test_step",
            tmp_root,
            "workflow:Self-test Phase 11 hvc validation flow checker",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        workflow_path.write_text(
            original_workflow.replace(
                "Self-test Phase 11 hvc cleanup alignment checker",
                "Self-test Phase 11 build inventory checker",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "workflow_cleanup_self_test_step",
            tmp_root,
            "workflow:Self-test Phase 11 hvc cleanup alignment checker",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        workflow_path.write_text(
            original_workflow.replace(
                "Validate Phase 11 shared replay contract",
                "Validate Phase 11 replay contract",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "workflow_shared_replay_validate_step",
            tmp_root,
            "workflow:Validate Phase 11 shared replay contract",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        workflow_path.write_text(
            original_workflow.replace(
                "Validate Phase 11 header boundary packet",
                "Validate Phase 11 header packet",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "workflow_header_boundary_validate_step",
            tmp_root,
            "workflow:Validate Phase 11 header boundary packet",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        checker_path = tmp_root / CHECKER_PATH
        checker_path.unlink()
        expect_missing(
            "checker_file_presence",
            tmp_root,
            f"missing:{CHECKER_PATH}",
        )
        clone_fixture_root(tmp_root)

        build_inventory_checker_path = tmp_root / BUILD_INVENTORY_CHECKER_PATH
        build_inventory_checker_path.unlink()
        expect_missing(
            "build_inventory_checker_file_presence",
            tmp_root,
            f"missing:{BUILD_INVENTORY_CHECKER_PATH}",
        )
        clone_fixture_root(tmp_root)

        layout_assert_checker_path = tmp_root / LAYOUT_ASSERT_CHECKER_PATH
        layout_assert_checker_path.unlink()
        expect_missing(
            "layout_assert_checker_file_presence",
            tmp_root,
            f"missing:{LAYOUT_ASSERT_CHECKER_PATH}",
        )
        clone_fixture_root(tmp_root)

        shared_replay_contract_checker_path = tmp_root / SHARED_REPLAY_CONTRACT_CHECKER_PATH
        shared_replay_contract_checker_path.unlink()
        expect_missing(
            "shared_replay_contract_checker_file_presence",
            tmp_root,
            f"missing:{SHARED_REPLAY_CONTRACT_CHECKER_PATH}",
        )
        clone_fixture_root(tmp_root)

        header_boundary_packet_checker_path = tmp_root / HEADER_BOUNDARY_PACKET_CHECKER_PATH
        header_boundary_packet_checker_path.unlink()
        expect_missing(
            "header_boundary_packet_checker_file_presence",
            tmp_root,
            f"missing:{HEADER_BOUNDARY_PACKET_CHECKER_PATH}",
        )

    print("PHASE11_HVC_VALIDATION_FLOW_SELF_TEST=pass")
    print("PHASE11_HVC_VALIDATION_FLOW_SELF_TEST_CASE_COUNT=18")
    return 0


if "--self-test" in sys.argv[1:]:
    raise SystemExit(run_self_test())


ROOT = Path(__file__).resolve().parents[2]
problems = validate(ROOT)
if problems:
    print("PHASE11_HVC_VALIDATION_FLOW=fail")
    print("PHASE11_HVC_VALIDATION_FLOW_MISSING_START")
    for problem in problems:
        print(problem)
    print("PHASE11_HVC_VALIDATION_FLOW_MISSING_END")
    raise SystemExit(1)

print("PHASE11_HVC_VALIDATION_FLOW=pass")
print(f"PHASE11_HVC_VALIDATION_FLOW_ROOT={ROOT}")