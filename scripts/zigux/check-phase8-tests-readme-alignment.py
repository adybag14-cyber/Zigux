#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys
import tempfile


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = Path(__file__).resolve()

REQUIRED_FILES = {
    "tests_readme": "zigux/tests/README.md",
    "doc_readme": "Documentation/zigux/README.md",
    "perf_slice": "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
    "shared_help_kallsyms_build": "zigux/tests/phase8_help_kallsyms_only_build.zig",
    "focused_build": "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
    "libbpf_segments_build": "zigux/tests/phase8_libbpf_segments_only_build.zig",
    "shared_build": "zigux/tests/phase8_build.zig",
    "makefile": "zigux/Makefile",
    "scripts_readme": "scripts/zigux/README.md",
    "workflow": ".github/workflows/zigux-bootstrap.yml",
}

TESTS_README_MARKERS = [
    "zigux/tests/phase8_exec_cmd_only_build.zig",
    "zigux/tests/phase8_help_only_build.zig",
    "zigux/tests/phase8_help_kallsyms_only_build.zig",
    "zigux/tests/phase8_kallsyms_only_build.zig",
    "zigux/tests/phase8_libbpf_segments_only_build.zig",
    "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
    "zigux/tests/phase8_build.zig",
    "make -C zigux phase8-perf-buffer-poll-test",
    "zigux/tests/phase8_perf_buffer_poll.zig",
    "zigux/tests/phase8_bpf_type_names.zig",
    "zigux/tests/phase8_file_path_handle_bridge.zig",
    "zigux/tests/phase8_bridge_boundary_survey.zig",
    "zigux/tests/phase8_libbpf_segments.zig",
    "scripts/zigux/validate-phase8.py",
    "scripts/zigux/check-phase8-tests-readme-alignment.py",
    "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
]

DOC_README_MARKERS = [
    "Phase 8 notes",
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    "zigux/tests/phase8_help_kallsyms_only_build.zig",
    "zigux/tests/phase8_bridge_boundary_survey.zig",
    "zigux/tests/phase8_file_path_handle_bridge.zig",
    "zigux/tests/phase8_bpf_type_names.zig",
    "zigux/tests/phase8_perf_buffer_poll.zig",
]

PERF_SLICE_MARKERS = [
    "PHASE8_SLICE=perf-buffer-poll-helper",
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    "zigux/tests/phase8_perf_buffer_poll.zig",
    "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
    "phase8-perf-buffer-poll-tests",
    "make -C zigux phase8-perf-buffer-poll-test",
]

SHARED_HELP_KALLSYMS_BUILD_MARKERS = [
    "phase8_help.zig",
    "phase8_kallsyms.zig",
    "phase8-help-tests",
    "phase8-kallsyms-tests",
    "Run focused Phase 8 help and kallsyms tests",
]

FOCUSED_BUILD_MARKERS = [
    "phase8_perf_buffer_poll.zig",
    "phase8-perf-buffer-poll-tests",
    "Run focused Phase 8 perf-buffer poll tests",
]

LIBBPF_SEGMENTS_BUILD_MARKERS = [
    "phase8_libbpf_segments.zig",
    "phase8-libbpf-segment-tests",
    "Run focused Phase 8 libbpf segment survey tests",
]

SHARED_BUILD_MARKERS = [
    "phase8_libbpf_segments.zig",
    "phase8-libbpf-segment-tests",
    "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    "phase8_perf_buffer_poll.zig",
    "phase8-perf-buffer-poll-tests",
]

MAKEFILE_MARKERS = [
    "phase8-validate:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-tests-readme-alignment.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-tests-readme-alignment.py\n",
    "phase8-libbpf-segments-test:",
    "zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
    "phase8-perf-buffer-poll-test:",
    "zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all",
    "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test",
]

SCRIPTS_README_MARKERS = [
    "check-phase8-tests-readme-alignment.py",
    "Phase 8 flow",
    "make -C zigux phase8-validate",
    "zigux/tests/phase8_help_kallsyms_only_build.zig",
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    "zigux/tests/phase8_bridge_boundary_survey.zig",
    "zigux/tests/phase8_libbpf_segments_only_build.zig",
    "zigux/tests/phase8_perf_buffer_poll.zig",
    "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
]

WORKFLOW_MARKERS = [
    "Validate Phase 8 tooling gates",
    "make -C zigux phase8-validate",
    "Run focused Phase 8 libbpf segment survey tests",
    "zig test zigux/tests/phase8_libbpf_segments.zig",
    "zigux/tests/phase8_libbpf_segments_only_build.zig",
    "Run focused Phase 8 perf-buffer poll tests",
    "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
    "Run Phase 8 tooling tests",
    "zig build test --build-file zigux/tests/phase8_build.zig --summary all",
]


def resolve_root() -> Path:
    args = sys.argv[1:]
    if "--root" in args:
        index = args.index("--root")
        try:
            return Path(args[index + 1]).resolve()
        except IndexError as exc:
            raise SystemExit("--root requires a path") from exc
    env_root = (
        Path(os.environ["ZIGUX_PHASE8_ROOT"]).resolve()
        if "ZIGUX_PHASE8_ROOT" in os.environ
        else None
    )
    if env_root is not None:
        return env_root
    return DEFAULT_ROOT


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    missing: list[str] = []

    for label, rel_path in REQUIRED_FILES.items():
        if not (root / rel_path).exists():
            missing.append(f"missing:{label}:{rel_path}")
    if missing:
        return missing

    tests_readme = read_text(root, REQUIRED_FILES["tests_readme"])
    doc_readme = read_text(root, REQUIRED_FILES["doc_readme"])
    perf_slice = read_text(root, REQUIRED_FILES["perf_slice"])
    shared_help_kallsyms_build = read_text(
        root, REQUIRED_FILES["shared_help_kallsyms_build"]
    )
    focused_build = read_text(root, REQUIRED_FILES["focused_build"])
    libbpf_segments_build = read_text(root, REQUIRED_FILES["libbpf_segments_build"])
    shared_build = read_text(root, REQUIRED_FILES["shared_build"])
    makefile = read_text(root, REQUIRED_FILES["makefile"])
    scripts_readme = read_text(root, REQUIRED_FILES["scripts_readme"])
    workflow = read_text(root, REQUIRED_FILES["workflow"])

    for marker in TESTS_README_MARKERS:
        if marker not in tests_readme:
            missing.append(f"tests_readme:{marker}")

    for marker in DOC_README_MARKERS:
        if marker not in doc_readme:
            missing.append(f"doc_readme:{marker}")

    for marker in PERF_SLICE_MARKERS:
        if marker not in perf_slice:
            missing.append(f"perf_slice:{marker}")

    for marker in SHARED_HELP_KALLSYMS_BUILD_MARKERS:
        if marker not in shared_help_kallsyms_build:
            missing.append(f"shared_help_kallsyms_build:{marker}")

    for marker in FOCUSED_BUILD_MARKERS:
        if marker not in focused_build:
            missing.append(f"focused_build:{marker}")

    for marker in LIBBPF_SEGMENTS_BUILD_MARKERS:
        if marker not in libbpf_segments_build:
            missing.append(f"libbpf_segments_build:{marker}")

    for marker in SHARED_BUILD_MARKERS:
        if marker not in shared_build:
            missing.append(f"shared_build:{marker}")

    for marker in MAKEFILE_MARKERS:
        if marker not in makefile:
            missing.append(f"makefile:{marker}")

    for marker in SCRIPTS_README_MARKERS:
        if marker not in scripts_readme:
            missing.append(f"scripts_readme:{marker}")

    for marker in WORKFLOW_MARKERS:
        if marker not in workflow:
            missing.append(f"workflow:{marker}")

    return missing


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts/zigux/check-phase8-tests-readme-alignment.py"), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )


def clone_fixture_root(destination_root: Path) -> None:
    script_target = destination_root / "scripts/zigux/check-phase8-tests-readme-alignment.py"
    script_target.parent.mkdir(parents=True, exist_ok=True)
    script_target.write_text(SCRIPT_PATH.read_text(encoding="utf-8"), encoding="utf-8")

    tests_readme = destination_root / REQUIRED_FILES["tests_readme"]
    tests_readme.parent.mkdir(parents=True, exist_ok=True)
    tests_readme.write_text(
        "\n".join(
            [
                "# zigux/tests",
                "",
                "- zigux/tests/phase8_exec_cmd_only_build.zig",
                "- zigux/tests/phase8_help_only_build.zig",
                "- zigux/tests/phase8_help_kallsyms_only_build.zig",
                "- zigux/tests/phase8_kallsyms_only_build.zig",
                "- zigux/tests/phase8_libbpf_segments.zig",
                "- zigux/tests/phase8_libbpf_segments_only_build.zig",
                "- zigux/tests/phase8_bpf_type_names.zig",
                "- zigux/tests/phase8_file_path_handle_bridge.zig",
                "- zigux/tests/phase8_bridge_boundary_survey.zig",
                "- zigux/tests/phase8_perf_buffer_poll.zig",
                "- zigux/tests/phase8_perf_buffer_poll_only_build.zig",
                "- zigux/tests/phase8_build.zig",
                "- make -C zigux phase8-perf-buffer-poll-test",
                "- scripts/zigux/validate-phase8.py",
                "- scripts/zigux/check-phase8-tests-readme-alignment.py",
                "- scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
                "- Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
                "",
            ]
        ),
        encoding="utf-8",
    )

    doc_readme = destination_root / REQUIRED_FILES["doc_readme"]
    doc_readme.parent.mkdir(parents=True, exist_ok=True)
    doc_readme.write_text(
        "\n".join(
            [
                "# Zigux Documentation",
                "",
                "## Phase 8 notes",
                "- Documentation/zigux/phase8-perf-buffer-poll-slice.md",
                "- tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
                "- zigux/tests/phase8_help_kallsyms_only_build.zig",
                "- zigux/tests/phase8_bridge_boundary_survey.zig",
                "- zigux/tests/phase8_file_path_handle_bridge.zig",
                "- zigux/tests/phase8_bpf_type_names.zig",
                "- zigux/tests/phase8_perf_buffer_poll.zig",
                "",
            ]
        ),
        encoding="utf-8",
    )

    perf_slice = destination_root / REQUIRED_FILES["perf_slice"]
    perf_slice.parent.mkdir(parents=True, exist_ok=True)
    perf_slice.write_text(
        "\n".join(
            [
                "# Phase 8 Perf Buffer Poll Slice",
                "",
                "- PHASE8_SLICE=perf-buffer-poll-helper",
                "- tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
                "- zigux/tests/phase8_perf_buffer_poll.zig",
                "- zigux/tests/phase8_perf_buffer_poll_only_build.zig",
                "- phase8-perf-buffer-poll-tests",
                "- make -C zigux phase8-perf-buffer-poll-test",
                "",
            ]
        ),
        encoding="utf-8",
    )

    shared_help_kallsyms_build = destination_root / REQUIRED_FILES["shared_help_kallsyms_build"]
    shared_help_kallsyms_build.parent.mkdir(parents=True, exist_ok=True)
    shared_help_kallsyms_build.write_text(
        "\n".join(
            [
                'const help_root = "phase8_help.zig";',
                'const kallsyms_root = "phase8_kallsyms.zig";',
                'const help_name = "phase8-help-tests";',
                'const kallsyms_name = "phase8-kallsyms-tests";',
                'const desc = "Run focused Phase 8 help and kallsyms tests";',
                "",
            ]
        ),
        encoding="utf-8",
    )

    focused_build = destination_root / REQUIRED_FILES["focused_build"]
    focused_build.parent.mkdir(parents=True, exist_ok=True)
    focused_build.write_text(
        "\n".join(
            [
                'const root = "phase8_perf_buffer_poll.zig";',
                'const name = "phase8-perf-buffer-poll-tests";',
                'const desc = "Run focused Phase 8 perf-buffer poll tests";',
                "",
            ]
        ),
        encoding="utf-8",
    )

    libbpf_segments_build = destination_root / REQUIRED_FILES["libbpf_segments_build"]
    libbpf_segments_build.parent.mkdir(parents=True, exist_ok=True)
    libbpf_segments_build.write_text(
        "\n".join(
            [
                'const root = "phase8_libbpf_segments.zig";',
                'const name = "phase8-libbpf-segment-tests";',
                'const desc = "Run focused Phase 8 libbpf segment survey tests";',
                "",
            ]
        ),
        encoding="utf-8",
    )

    shared_build = destination_root / REQUIRED_FILES["shared_build"]
    shared_build.parent.mkdir(parents=True, exist_ok=True)
    shared_build.write_text(
        "\n".join(
            [
                'const libbpf_segments_test = "phase8_libbpf_segments.zig";',
                'const libbpf_segments_name = "phase8-libbpf-segment-tests";',
                'const perf_buffer_poll_root = "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig";',
                'const perf_buffer_poll_test = "phase8_perf_buffer_poll.zig";',
                'const perf_buffer_poll_name = "phase8-perf-buffer-poll-tests";',
                "",
            ]
        ),
        encoding="utf-8",
    )

    makefile = destination_root / REQUIRED_FILES["makefile"]
    makefile.parent.mkdir(parents=True, exist_ok=True)
    makefile.write_text(
        "\n".join(
            [
                "phase8-validate:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase8.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-tests-readme-alignment.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase8.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-tests-readme-alignment.py",
                "phase8-libbpf-segments-test:",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
                "phase8-perf-buffer-poll-test:",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all",
                "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test",
                "",
            ]
        ),
        encoding="utf-8",
    )

    scripts_readme = destination_root / REQUIRED_FILES["scripts_readme"]
    scripts_readme.parent.mkdir(parents=True, exist_ok=True)
    scripts_readme.write_text(
        "\n".join(
            [
                "# scripts/zigux",
                "",
                "- check-phase8-tests-readme-alignment.py",
                "",
                "## Phase 8 flow",
                "- make -C zigux phase8-validate",
                "- zigux/tests/phase8_help_kallsyms_only_build.zig",
                "- Documentation/zigux/phase8-perf-buffer-poll-slice.md",
                "- tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
                "- zigux/tests/phase8_bridge_boundary_survey.zig",
                "- zigux/tests/phase8_libbpf_segments_only_build.zig",
                "- zigux/tests/phase8_perf_buffer_poll.zig",
                "- zigux/tests/phase8_perf_buffer_poll_only_build.zig",
                "",
            ]
        ),
        encoding="utf-8",
    )

    workflow = destination_root / REQUIRED_FILES["workflow"]
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text(
        "\n".join(
            [
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Validate Phase 8 tooling gates",
                "        run: make -C zigux phase8-validate",
                "      - name: Run focused Phase 8 libbpf segment survey tests",
                "        run: |",
                "          zig test zigux/tests/phase8_libbpf_segments.zig",
                "          zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
                "      - name: Run focused Phase 8 perf-buffer poll tests",
                "        run: zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all",
                "      - name: Run Phase 8 tooling tests",
                "        run: zig build test --build-file zigux/tests/phase8_build.zig --summary all",
                "",
            ]
        ),
        encoding="utf-8",
    )


def expect_missing(label: str, root: Path, needle: str) -> None:
    result = run_validator(root)
    if result.returncode == 0:
        raise SystemExit(f"phase8-tests-readme-self-test:{label}:unexpected_pass")
    if needle not in result.stdout:
        actual = result.stdout.strip() or "none"
        raise SystemExit(
            f"phase8-tests-readme-self-test:{label}:expected:{needle}:actual:{actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_tests_readme_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        clone_fixture_root(tmp_root)

        baseline = run_validator(tmp_root)
        if baseline.returncode != 0:
            raise SystemExit(
                "phase8-tests-readme-self-test:baseline_failed:"
                f"{baseline.stdout.strip() or baseline.stderr.strip() or 'no_output'}"
            )

        tests_readme_path = tmp_root / REQUIRED_FILES["tests_readme"]
        original_tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            original_tests_readme.replace(
                "- zigux/tests/phase8_exec_cmd_only_build.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "tests_readme_exec_cmd_only_build",
            tmp_root,
            "tests_readme:zigux/tests/phase8_exec_cmd_only_build.zig",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "- zigux/tests/phase8_help_only_build.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "tests_readme_help_only_build",
            tmp_root,
            "tests_readme:zigux/tests/phase8_help_only_build.zig",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "- zigux/tests/phase8_help_kallsyms_only_build.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "tests_readme_help_kallsyms_only_build",
            tmp_root,
            "tests_readme:zigux/tests/phase8_help_kallsyms_only_build.zig",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "- zigux/tests/phase8_kallsyms_only_build.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "tests_readme_kallsyms_only_build",
            tmp_root,
            "tests_readme:zigux/tests/phase8_kallsyms_only_build.zig",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "- zigux/tests/phase8_perf_buffer_poll_only_build.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "tests_readme_perf_buffer_poll_only_build",
            tmp_root,
            "tests_readme:zigux/tests/phase8_perf_buffer_poll_only_build.zig",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "- make -C zigux phase8-perf-buffer-poll-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "tests_readme_perf_buffer_poll_make_target",
            tmp_root,
            "tests_readme:make -C zigux phase8-perf-buffer-poll-test",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "- zigux/tests/phase8_libbpf_segments_only_build.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "tests_readme_libbpf_segments_only_build",
            tmp_root,
            "tests_readme:zigux/tests/phase8_libbpf_segments_only_build.zig",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "- zigux/tests/phase8_perf_buffer_poll.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "tests_readme_perf_buffer_poll",
            tmp_root,
            "tests_readme:zigux/tests/phase8_perf_buffer_poll.zig",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "- zigux/tests/phase8_bpf_type_names.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "tests_readme_bpf_type_names",
            tmp_root,
            "tests_readme:zigux/tests/phase8_bpf_type_names.zig",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "- zigux/tests/phase8_file_path_handle_bridge.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "tests_readme_file_path_handle_bridge",
            tmp_root,
            "tests_readme:zigux/tests/phase8_file_path_handle_bridge.zig",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "- zigux/tests/phase8_bridge_boundary_survey.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "tests_readme_bridge_boundary_survey",
            tmp_root,
            "tests_readme:zigux/tests/phase8_bridge_boundary_survey.zig",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "- zigux/tests/phase8_libbpf_segments.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "tests_readme_libbpf_segments",
            tmp_root,
            "tests_readme:zigux/tests/phase8_libbpf_segments.zig",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "- zigux/tests/phase8_build.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "tests_readme_shared_build",
            tmp_root,
            "tests_readme:zigux/tests/phase8_build.zig",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "- scripts/zigux/validate-phase8.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "tests_readme_validate_phase8",
            tmp_root,
            "tests_readme:scripts/zigux/validate-phase8.py",
        )

        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")
        tests_readme_path.write_text(
            original_tests_readme.replace(
                "- scripts/zigux/check-phase8-tests-readme-alignment.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "tests_readme_check_phase8_tests_readme_alignment",
            tmp_root,
            "tests_readme:scripts/zigux/check-phase8-tests-readme-alignment.py",
        )

        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")
        tests_readme_path.write_text(
            original_tests_readme.replace(
                "- scripts/zigux/check-phase8-perf-buffer-poll-gate.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "tests_readme_check_phase8_perf_buffer_poll_gate",
            tmp_root,
            "tests_readme:scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
        )

        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")
        tests_readme_path.write_text(
            original_tests_readme.replace(
                "- Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "tests_readme_bridge_boundary",
            tmp_root,
            "tests_readme:Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        doc_readme_path = tmp_root / REQUIRED_FILES["doc_readme"]
        original_doc_readme = doc_readme_path.read_text(encoding="utf-8")
        doc_readme_path.write_text(
            original_doc_readme.replace(
                "- zigux/tests/phase8_perf_buffer_poll.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "doc_readme_perf_buffer_poll",
            tmp_root,
            "doc_readme:zigux/tests/phase8_perf_buffer_poll.zig",
        )
        doc_readme_path.write_text(original_doc_readme, encoding="utf-8")

        doc_readme_path.write_text(
            original_doc_readme.replace(
                "- zigux/tests/phase8_bridge_boundary_survey.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "doc_readme_bridge_boundary_survey",
            tmp_root,
            "doc_readme:zigux/tests/phase8_bridge_boundary_survey.zig",
        )
        doc_readme_path.write_text(original_doc_readme, encoding="utf-8")

        doc_readme_path.write_text(
            original_doc_readme.replace(
                "- zigux/tests/phase8_file_path_handle_bridge.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "doc_readme_file_path_handle_bridge",
            tmp_root,
            "doc_readme:zigux/tests/phase8_file_path_handle_bridge.zig",
        )
        doc_readme_path.write_text(original_doc_readme, encoding="utf-8")

        doc_readme_path.write_text(
            original_doc_readme.replace(
                "## Phase 8 notes\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "doc_readme_phase8_notes_heading",
            tmp_root,
            "doc_readme:Phase 8 notes",
        )
        doc_readme_path.write_text(original_doc_readme, encoding="utf-8")

        doc_readme_path.write_text(
            original_doc_readme.replace(
                "- zigux/tests/phase8_help_kallsyms_only_build.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "doc_readme_help_kallsyms_only_build",
            tmp_root,
            "doc_readme:zigux/tests/phase8_help_kallsyms_only_build.zig",
        )
        doc_readme_path.write_text(original_doc_readme, encoding="utf-8")

        doc_readme_path.write_text(
            original_doc_readme.replace(
                "- Documentation/zigux/phase8-perf-buffer-poll-slice.md\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "doc_readme_perf_slice_reference",
            tmp_root,
            "doc_readme:Documentation/zigux/phase8-perf-buffer-poll-slice.md",
        )
        doc_readme_path.write_text(original_doc_readme, encoding="utf-8")

        doc_readme_path.write_text(
            original_doc_readme.replace(
                "- zigux/tests/phase8_bpf_type_names.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "doc_readme_bpf_type_names",
            tmp_root,
            "doc_readme:zigux/tests/phase8_bpf_type_names.zig",
        )
        doc_readme_path.write_text(original_doc_readme, encoding="utf-8")

        doc_readme_path.write_text(
            original_doc_readme.replace(
                "- tools/lib/bpf/zigux_segments/perf_buffer_poll.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "doc_readme_perf_buffer_poll_helper",
            tmp_root,
            "doc_readme:tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        )
        doc_readme_path.write_text(original_doc_readme, encoding="utf-8")

        perf_slice_path = tmp_root / REQUIRED_FILES["perf_slice"]
        original_perf_slice = perf_slice_path.read_text(encoding="utf-8")
        perf_slice_path.write_text(
            original_perf_slice.replace(
                "- zigux/tests/phase8_perf_buffer_poll_only_build.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "perf_slice_focused_build_reference",
            tmp_root,
            "perf_slice:zigux/tests/phase8_perf_buffer_poll_only_build.zig",
        )
        perf_slice_path.write_text(original_perf_slice, encoding="utf-8")

        perf_slice_path.write_text(
            original_perf_slice.replace(
                "- phase8-perf-buffer-poll-tests\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "perf_slice_artifact_name",
            tmp_root,
            "perf_slice:phase8-perf-buffer-poll-tests",
        )
        perf_slice_path.write_text(original_perf_slice, encoding="utf-8")

        perf_slice_path.write_text(
            original_perf_slice.replace(
                "- make -C zigux phase8-perf-buffer-poll-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "perf_slice_make_target",
            tmp_root,
            "perf_slice:make -C zigux phase8-perf-buffer-poll-test",
        )
        perf_slice_path.write_text(original_perf_slice, encoding="utf-8")

        shared_help_kallsyms_build_path = tmp_root / REQUIRED_FILES["shared_help_kallsyms_build"]
        original_shared_help_kallsyms_build = shared_help_kallsyms_build_path.read_text(
            encoding="utf-8"
        )
        shared_help_kallsyms_build_path.write_text(
            original_shared_help_kallsyms_build.replace(
                'const kallsyms_name = "phase8-kallsyms-tests";\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "shared_help_kallsyms_build_kallsyms_name",
            tmp_root,
            "shared_help_kallsyms_build:phase8-kallsyms-tests",
        )
        shared_help_kallsyms_build_path.write_text(
            original_shared_help_kallsyms_build,
            encoding="utf-8",
        )

        focused_build_path = tmp_root / REQUIRED_FILES["focused_build"]
        original_focused_build = focused_build_path.read_text(encoding="utf-8")
        focused_build_path.write_text(
            original_focused_build.replace(
                'const name = "phase8-perf-buffer-poll-tests";\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "focused_build_artifact_name",
            tmp_root,
            "focused_build:phase8-perf-buffer-poll-tests",
        )
        focused_build_path.write_text(original_focused_build, encoding="utf-8")

        libbpf_segments_build_path = tmp_root / REQUIRED_FILES["libbpf_segments_build"]
        original_libbpf_segments_build = libbpf_segments_build_path.read_text(encoding="utf-8")
        libbpf_segments_build_path.write_text(
            original_libbpf_segments_build.replace(
                'const name = "phase8-libbpf-segment-tests";\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "libbpf_segments_build_artifact_name",
            tmp_root,
            "libbpf_segments_build:phase8-libbpf-segment-tests",
        )
        libbpf_segments_build_path.write_text(original_libbpf_segments_build, encoding="utf-8")

        shared_build_path = tmp_root / REQUIRED_FILES["shared_build"]
        original_shared_build = shared_build_path.read_text(encoding="utf-8")
        shared_build_path.write_text(
            original_shared_build.replace(
                'const perf_buffer_poll_name = "phase8-perf-buffer-poll-tests";\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "shared_build_artifact_name",
            tmp_root,
            "shared_build:phase8-perf-buffer-poll-tests",
        )
        shared_build_path.write_text(original_shared_build, encoding="utf-8")

        shared_build_path.write_text(
            original_shared_build.replace(
                'const libbpf_segments_name = "phase8-libbpf-segment-tests";\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "shared_build_libbpf_segments_artifact_name",
            tmp_root,
            "shared_build:phase8-libbpf-segment-tests",
        )
        shared_build_path.write_text(original_shared_build, encoding="utf-8")

        shared_build_path.write_text(
            original_shared_build.replace(
                "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
                "../../tools/lib/bpf/zigux_segments/perf_buffer_wait.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "shared_build_helper_path",
            tmp_root,
            "shared_build:../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        )
        shared_build_path.write_text(original_shared_build, encoding="utf-8")

        makefile_path = tmp_root / REQUIRED_FILES["makefile"]
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-tests-readme-alignment.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "makefile_checker_self_test_hook",
            tmp_root,
            "makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-tests-readme-alignment.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-tests-readme-alignment.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "makefile_checker_hook",
            tmp_root,
            "makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-tests-readme-alignment.py",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "phase8-perf-buffer-poll-test:\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "makefile_perf_buffer_poll_target",
            tmp_root,
            "makefile:phase8-perf-buffer-poll-test:",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "phase8-libbpf-segments-test:\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "makefile_libbpf_segments_target",
            tmp_root,
            "makefile:phase8-libbpf-segments-test:",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test",
                "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-perf-buffer-wait-test phase8-test",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "makefile_phase8_bundle",
            tmp_root,
            "makefile:phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        scripts_readme_path = tmp_root / REQUIRED_FILES["scripts_readme"]
        original_scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "- check-phase8-tests-readme-alignment.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "scripts_readme_checker",
            tmp_root,
            "scripts_readme:check-phase8-tests-readme-alignment.py",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "- make -C zigux phase8-validate\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "scripts_readme_phase8_flow",
            tmp_root,
            "scripts_readme:make -C zigux phase8-validate",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "- zigux/tests/phase8_help_kallsyms_only_build.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "scripts_readme_help_kallsyms_only_build",
            tmp_root,
            "scripts_readme:zigux/tests/phase8_help_kallsyms_only_build.zig",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "- zigux/tests/phase8_bridge_boundary_survey.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "scripts_readme_bridge_boundary_survey",
            tmp_root,
            "scripts_readme:zigux/tests/phase8_bridge_boundary_survey.zig",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "- zigux/tests/phase8_libbpf_segments_only_build.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "scripts_readme_libbpf_segments_only_build",
            tmp_root,
            "scripts_readme:zigux/tests/phase8_libbpf_segments_only_build.zig",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "- zigux/tests/phase8_perf_buffer_poll.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "scripts_readme_perf_buffer_poll",
            tmp_root,
            "scripts_readme:zigux/tests/phase8_perf_buffer_poll.zig",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "- zigux/tests/phase8_perf_buffer_poll_only_build.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "scripts_readme_perf_buffer_poll_only_build",
            tmp_root,
            "scripts_readme:zigux/tests/phase8_perf_buffer_poll_only_build.zig",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "- Documentation/zigux/phase8-perf-buffer-poll-slice.md\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "scripts_readme_perf_buffer_poll_slice",
            tmp_root,
            "scripts_readme:Documentation/zigux/phase8-perf-buffer-poll-slice.md",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "- tools/lib/bpf/zigux_segments/perf_buffer_poll.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "scripts_readme_perf_buffer_poll_helper",
            tmp_root,
            "scripts_readme:tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        workflow_path = tmp_root / REQUIRED_FILES["workflow"]
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            original_workflow.replace(
                "      - name: Run focused Phase 8 perf-buffer poll tests\n"
                "        run: zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "workflow_focused_perf_buffer_poll_hook",
            tmp_root,
            "workflow:Run focused Phase 8 perf-buffer poll tests",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        workflow_path.write_text(
            original_workflow.replace(
                "      - name: Run focused Phase 8 libbpf segment survey tests\n"
                "        run: |\n"
                "          zig test zigux/tests/phase8_libbpf_segments.zig\n"
                "          zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "workflow_focused_libbpf_segments_hook",
            tmp_root,
            "workflow:Run focused Phase 8 libbpf segment survey tests",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        workflow_path.write_text(
            original_workflow.replace(
                "      - name: Validate Phase 8 tooling gates\n"
                "        run: make -C zigux phase8-validate\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "workflow_validate_hook",
            tmp_root,
            "workflow:Validate Phase 8 tooling gates",
        )

    print("PHASE8_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    print("PHASE8_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT=51")
    return 0


if "--self-test" in sys.argv[1:]:
    raise SystemExit(run_self_test())


ROOT = resolve_root()
problems = validate(ROOT)
if problems:
    print("PHASE8_TESTS_README_ALIGNMENT=fail")
    print("PHASE8_TESTS_README_ALIGNMENT_MISSING_START")
    for problem in problems:
        print(problem)
    print("PHASE8_TESTS_README_ALIGNMENT_MISSING_END")
    raise SystemExit(1)

print("PHASE8_TESTS_README_ALIGNMENT=pass")
print(f"PHASE8_TESTS_README_ALIGNMENT_ROOT={ROOT}")