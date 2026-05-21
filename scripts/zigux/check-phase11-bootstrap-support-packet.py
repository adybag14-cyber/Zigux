#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


PACKET_NAME = "PHASE11_BOOTSTRAP_SUPPORT_PACKET"
SELF_TEST_NAME = f"{PACKET_NAME}_SELF_TEST"

WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
BEFORE_STEP = "Run Phase 10 helper tests"
PACKET_STEPS = ("Validate current Phase 11 support bundle",)
AFTER_STEP = "Self-test current Phase 12 build-only surface checker"

REQUIRED_PATHS = (
    WORKFLOW_PATH,
    Path("scripts/zigux/validate-phase11.py"),
    Path("scripts/zigux/check-phase11-build-inventory.py"),
    Path("scripts/zigux/check-phase11-hvc-cleanup-current-head.py"),
    Path("scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py"),
    Path("zigux/Makefile"),
    Path("Documentation/zigux/phase11-driver-lane-sequencing.md"),
    Path("Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md"),
    Path("zigux/tests/fixtures/phase11_build_inventory.json"),
    Path("zigux/tests/phase11_hvc_export_surface_layout_build.zig"),
    Path("zigux/tests/phase11_hvc_hv_ops_layout_build.zig"),
    Path("zigux/tests/phase11_hvc_cleanup_packet_build.zig"),
    Path("zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig"),
)

FILE_MARKERS: dict[Path, tuple[str, ...]] = {
    WORKFLOW_PATH: (
        BEFORE_STEP,
        *PACKET_STEPS,
        AFTER_STEP,
    ),
    Path("scripts/zigux/validate-phase11.py"): (
        '".github/workflows/zigux-bootstrap.yml"',
        '"scripts/zigux/check-phase11-build-inventory.py"',
        '"scripts/zigux/check-phase11-hvc-cleanup-current-head.py"',
        '"scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py"',
        '"zigux/tests/phase11_hvc_cleanup_packet_build.zig"',
        '"zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig"',
    ),
    Path("zigux/Makefile"): (
        "phase11-validate:",
        "scripts/zigux/validate-phase11.py",
        "phase11_hvc_hv_ops_layout_build.zig",
        "phase11_hvc_export_surface_layout_build.zig",
        "phase11_hvc_cleanup_packet_build.zig",
        "phase11_hvc_targetless_unregister_gap_build.zig",
    ),
    Path("Documentation/zigux/phase11-driver-lane-sequencing.md"): (
        "`scripts/zigux/validate-phase11.py`",
        "`zigux/Makefile`",
        "`make -C zigux phase11-validate`",
        "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
    ),
    Path("Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md"): (
        "`scripts/zigux/check-phase11-build-inventory.py`",
        "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
        "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
        "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
        "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
    ),
    Path("zigux/tests/phase11_hvc_cleanup_packet_build.zig"): (
        'phase11_hvc_cleanup_packet_proof.zig',
        '"phase11-hvc-cleanup-packet-proof"',
        '"Run the focused Phase 11 HVC cleanup packet proof"',
    ),
    Path("zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig"): (
        'phase11_hvc_targetless_unregister_gap.zig',
        '"phase11-hvc-targetless-unregister-gap"',
        '"Run the focused Phase 11 HVC targetless unregister gap proof"',
    ),
}


class PacketError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise PacketError(f"missing required path: {path.as_posix()}") from exc


def ensure_required_paths(root: Path) -> None:
    for relative_path in REQUIRED_PATHS:
        if not (root / relative_path).is_file():
            raise PacketError(f"missing required path: {relative_path.as_posix()}")


def ensure_markers(root: Path) -> None:
    for relative_path, markers in FILE_MARKERS.items():
        content = read_text(root / relative_path)
        for marker in markers:
            if marker not in content:
                raise PacketError(
                    f"missing marker in {relative_path.as_posix()}: {marker}"
                )


def parse_workflow_steps(content: str) -> list[str]:
    steps: list[str] = []
    prefix = "      - name:"
    for line in content.splitlines():
        if line.startswith(prefix):
            steps.append(line[len(prefix) :].strip())
    return steps


def ensure_unique_step(steps: list[str], step: str) -> int:
    count = steps.count(step)
    if count == 0:
        raise PacketError(f"missing workflow step: {step}")
    if count > 1:
        raise PacketError(f"duplicate workflow step: {step}")
    return steps.index(step)


def ensure_workflow_packet(root: Path) -> None:
    steps = parse_workflow_steps(read_text(root / WORKFLOW_PATH))
    ordered_steps = (BEFORE_STEP, *PACKET_STEPS, AFTER_STEP)
    indices = [ensure_unique_step(steps, step) for step in ordered_steps]
    if indices != sorted(indices):
        raise PacketError("workflow packet order drifted")
    for left, right in zip(indices, indices[1:]):
        if right != left + 1:
            raise PacketError("workflow packet is no longer contiguous")


def validate(root: Path) -> None:
    ensure_required_paths(root)
    ensure_markers(root)
    ensure_workflow_packet(root)


def write_file(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    workflow = """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Run Phase 10 helper tests
        run: make -C zigux phase10-test
      - name: Validate current Phase 11 support bundle
        run: make -C zigux phase11-validate
      - name: Self-test current Phase 12 build-only surface checker
        run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test
"""

    validate_phase11 = """#!/usr/bin/env python3
REQUIRED_PATHS = (
    ".github/workflows/zigux-bootstrap.yml",
    "scripts/zigux/check-phase11-build-inventory.py",
    "scripts/zigux/check-phase11-hvc-cleanup-current-head.py",
    "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
)
"""

    makefile = """phase11-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig
"""

    sequencing = """# Phase 11 Driver Lane Sequencing

- `scripts/zigux/validate-phase11.py`
- `zigux/Makefile`
- `make -C zigux phase11-validate`
- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`
"""

    companion = """# Phase 11 HVC Cleanup Alignment Current-Head Companion

- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`
"""

    cleanup_build = """const proof_path = "phase11_hvc_cleanup_packet_proof.zig";
const step_name = "phase11-hvc-cleanup-packet-proof";
const message = "Run the focused Phase 11 HVC cleanup packet proof";
"""

    targetless_build = """const proof_path = "phase11_hvc_targetless_unregister_gap.zig";
const step_name = "phase11-hvc-targetless-unregister-gap";
const message = "Run the focused Phase 11 HVC targetless unregister gap proof";
"""

    write_file(root, WORKFLOW_PATH, workflow)
    write_file(root, Path("scripts/zigux/validate-phase11.py"), validate_phase11)
    write_file(root, Path("scripts/zigux/check-phase11-build-inventory.py"), "present\n")
    write_file(root, Path("scripts/zigux/check-phase11-hvc-cleanup-current-head.py"), "present\n")
    write_file(
        root,
        Path("scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py"),
        "present\n",
    )
    write_file(root, Path("zigux/Makefile"), makefile)
    write_file(
        root,
        Path("Documentation/zigux/phase11-driver-lane-sequencing.md"),
        sequencing,
    )
    write_file(
        root,
        Path("Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md"),
        companion,
    )
    write_file(root, Path("zigux/tests/fixtures/phase11_build_inventory.json"), "{}\n")
    write_file(
        root,
        Path("zigux/tests/phase11_hvc_export_surface_layout_build.zig"),
        "const a = 1;\n",
    )
    write_file(
        root,
        Path("zigux/tests/phase11_hvc_hv_ops_layout_build.zig"),
        "const a = 1;\n",
    )
    write_file(
        root,
        Path("zigux/tests/phase11_hvc_cleanup_packet_build.zig"),
        cleanup_build,
    )
    write_file(
        root,
        Path("zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig"),
        targetless_build,
    )


def expect_failure(mutator) -> None:
    with tempfile.TemporaryDirectory(prefix="phase11-bootstrap-support-") as tmp:
        root = Path(tmp)
        write_sample_root(root)
        mutator(root)
        try:
            validate(root)
        except PacketError:
            return
        raise AssertionError("expected PacketError")


def run_self_test() -> None:
    cases = 0

    with tempfile.TemporaryDirectory(prefix="phase11-bootstrap-support-") as tmp:
        root = Path(tmp)
        write_sample_root(root)
        validate(root)
        cases += 1

    def remove_phase11_step(root: Path) -> None:
        path = root / WORKFLOW_PATH
        content = path.read_text(encoding="utf-8").replace(
            "      - name: Validate current Phase 11 support bundle\n"
            "        run: make -C zigux phase11-validate\n",
            "",
        )
        path.write_text(content, encoding="utf-8")

    expect_failure(remove_phase11_step)
    cases += 1

    def duplicate_phase11_step(root: Path) -> None:
        path = root / WORKFLOW_PATH
        marker = (
            "      - name: Validate current Phase 11 support bundle\n"
            "        run: make -C zigux phase11-validate\n"
        )
        content = path.read_text(encoding="utf-8")
        path.write_text(content.replace(marker, marker + marker), encoding="utf-8")

    expect_failure(duplicate_phase11_step)
    cases += 1

    def break_contiguity(root: Path) -> None:
        path = root / WORKFLOW_PATH
        marker = (
            "      - name: Validate current Phase 11 support bundle\n"
            "        run: make -C zigux phase11-validate\n"
        )
        insert = (
            marker
            + "      - name: Unexpected middle step\n"
            + "        run: echo drift\n"
        )
        content = path.read_text(encoding="utf-8")
        path.write_text(content.replace(marker, insert), encoding="utf-8")

    expect_failure(break_contiguity)
    cases += 1

    def remove_makefile_marker(root: Path) -> None:
        path = root / Path("zigux/Makefile")
        content = path.read_text(encoding="utf-8").replace(
            "phase11_hvc_cleanup_packet_build.zig\n",
            "",
        )
        path.write_text(content, encoding="utf-8")

    expect_failure(remove_makefile_marker)
    cases += 1

    def remove_validator_marker(root: Path) -> None:
        path = root / Path("scripts/zigux/validate-phase11.py")
        content = path.read_text(encoding="utf-8").replace(
            '    "scripts/zigux/check-phase11-build-inventory.py",\n',
            "",
        )
        path.write_text(content, encoding="utf-8")

    expect_failure(remove_validator_marker)
    cases += 1

    def remove_doc_marker(root: Path) -> None:
        path = root / Path(
            "Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md"
        )
        content = path.read_text(encoding="utf-8").replace(
            "- `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`\n",
            "",
        )
        path.write_text(content, encoding="utf-8")

    expect_failure(remove_doc_marker)
    cases += 1

    print(f"{SELF_TEST_NAME}=pass")
    print(f"{SELF_TEST_NAME}_CASE_COUNT={cases}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path, default=None)
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    root = args.root if args.root is not None else Path(__file__).resolve().parents[2]
    try:
        validate(root)
    except PacketError as exc:
        print(f"{PACKET_NAME}=fail")
        print(f"{PACKET_NAME}_REASON={exc}")
        return 1

    print(f"{PACKET_NAME}=pass")
    print(f"{PACKET_NAME}_WORKFLOW_STEP_COUNT={len(PACKET_STEPS)}")
    print(f"{PACKET_NAME}_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
