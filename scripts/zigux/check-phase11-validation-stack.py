#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
README_PATH = ROOT / "scripts/zigux/README.md"
MAKEFILE_PATH = ROOT / "zigux/Makefile"

README_MARKERS = [
    "Phase 11 flow",
    "`make -C zigux phase11-validate` is the validator-first entrypoint for the active simple-driver tranche.",
    "`validate-phase11.py --self-test` keeps the fast Python gate fail-closed before the live Phase 11 packet is trusted.",
    "`check-phase11-build-inventory.py`, `check-phase11-layout-assert-surface.py`, `check-phase11-hvc-validation-flow.py`, and `check-phase11-hvc-cleanup-alignment.py` keep the build snapshot, the Phase 11 layout-assert survey surface, the shared-versus-dedicated hvc replay contract, and the current hvc cleanup packet explicit before the broader Phase 11 validator runs.",
    "`make -C zigux phase11-hvc-survey` is the dedicated archival replay for `zigux/tests/phase11_hvc_console_survey.zig`, while `make -C zigux phase11` keeps the shared Phase 11 replay plus that dedicated archival step in one published path.",
]

MAKEFILE_MARKERS = [
    "PHONY += phase11-validate phase11-test phase11-hvc-survey phase11",
    "phase11-validate:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-layout-assert-surface.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-layout-assert-surface.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-validation-flow.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-validation-flow.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-cleanup-alignment.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-cleanup-alignment.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py\n",
]


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate(root: Path) -> int:
    readme_text = text(root / "scripts/zigux/README.md")
    makefile_text = text(root / "zigux/Makefile")

    missing: list[str] = []
    for marker in README_MARKERS:
        if marker not in readme_text:
            missing.append(f"readme:{marker}")
    for marker in MAKEFILE_MARKERS:
        if marker not in makefile_text:
            missing.append(f"make:{marker}")

    if missing:
        print("PHASE11_VALIDATION_STACK=fail")
        print("PHASE11_VALIDATION_STACK_MISSING_START")
        for marker in missing:
            print(marker)
        print("PHASE11_VALIDATION_STACK_MISSING_END")
        return 1

    print("PHASE11_VALIDATION_STACK=pass")
    print(f"PHASE11_VALIDATION_STACK_README_MARKER_COUNT={len(README_MARKERS)}")
    print(f"PHASE11_VALIDATION_STACK_MAKEFILE_MARKER_COUNT={len(MAKEFILE_MARKERS)}")
    return 0


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts/zigux/check-phase11-validation-stack.py")],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )


def expect_missing(label: str, root: Path, marker: str) -> None:
    result = run_checker(root)
    if result.returncode == 0:
        raise SystemExit(f"phase11-validation-stack-self-test:{label}:unexpected_pass")
    if marker not in result.stdout:
        actual = result.stdout.strip() or result.stderr.strip() or "no_output"
        raise SystemExit(
            f"phase11-validation-stack-self-test:{label}:expected:{marker}:actual:{actual}"
        )


def write_fixture(root: Path) -> None:
    (root / "scripts/zigux").mkdir(parents=True, exist_ok=True)
    (root / "zigux").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(Path(__file__), root / "scripts/zigux/check-phase11-validation-stack.py")

    (root / "scripts/zigux/README.md").writeText if False else None
    (root / "scripts/zigux/README.md").write_text(
        "# scripts/zigux\n\n"
        "Phase 11 flow\n"
        "- `make -C zigux phase11-validate` is the validator-first entrypoint for the active simple-driver tranche.\n"
        "- `validate-phase11.py --self-test` keeps the fast Python gate fail-closed before the live Phase 11 packet is trusted.\n"
        "- `check-phase11-build-inventory.py`, `check-phase11-layout-assert-surface.py`, `check-phase11-hvc-validation-flow.py`, and `check-phase11-hvc-cleanup-alignment.py` keep the build snapshot, the Phase 11 layout-assert survey surface, the shared-versus-dedicated hvc replay contract, and the current hvc cleanup packet explicit before the broader Phase 11 validator runs.\n"
        "- `make -C zigux phase11-hvc-survey` is the dedicated archival replay for `zigux/tests/phase11_hvc_console_survey.zig`, while `make -C zigux phase11` keeps the shared Phase 11 replay plus that dedicated archival step in one published path.\n",
        encoding="utf-8",
    )
    (root / "zigux/Makefile").write_text(
        "PHONY += phase11-validate phase11-test phase11-hvc-survey phase11\n\n"
        "phase11-validate:\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py --self-test\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-layout-assert-surface.py --self-test\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-layout-assert-surface.py\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-validation-flow.py --self-test\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-validation-flow.py\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-cleanup-alignment.py --self-test\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-cleanup-alignment.py\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py --self-test\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase11_validation_stack_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture(tmp_root)

        baseline = run_checker(tmp_root)
        if baseline.returncode != 0:
            raise SystemExit(
                "phase11-validation-stack-self-test:baseline_failed:"
                f"{baseline.stdout.strip() or baseline.stderr.strip() or 'no_output'}"
            )

        readme_path = tmp_root / "scripts/zigux/README.md"
        readme_backup = readme_path.read_text(encoding="utf-8")
        readme_path.write_text(
            readme_backup.replace(
                "`make -C zigux phase11-hvc-survey` is the dedicated archival replay for `zigux/tests/phase11_hvc_console_survey.zig`, while `make -C zigux phase11` keeps the shared Phase 11 replay plus that dedicated archival step in one published path.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "missing_readme_replay_path",
            tmp_root,
            "readme:`make -C zigux phase11-hvc-survey` is the dedicated archival replay for `zigux/tests/phase11_hvc_console_survey.zig`, while `make -C zigux phase11` keeps the shared Phase 11 replay plus that dedicated archival step in one published path.",
        )
        readme_path.write_text(readme_backup, encoding="utf-8")

        makefile_path = tmp_root / "zigux/Makefile"
        makefile_backup = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            makefile_backup.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "missing_makefile_self_test_hook",
            tmp_root,
            "make:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py --self-test",
        )
        makefile_path.write_text(makefile_backup, encoding="utf-8")

        makefile_path.write_text(
            makefile_backup.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-cleanup-alignment.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "missing_makefile_cleanup_gate",
            tmp_root,
            "make:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-cleanup-alignment.py",
        )

    print("PHASE11_VALIDATION_STACK_SELF_TEST=pass")
    print("PHASE11_VALIDATION_STACK_SELF_TEST_CASE_COUNT=3")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(run_self_test())
    raise SystemExit(validate(ROOT))
