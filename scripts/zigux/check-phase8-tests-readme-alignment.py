#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys
import tempfile


DEFAULT_ROOT = Path(__file__).resolve().parent
SCRIPT_PATH = Path(__file__).resolve()

REQUIRED_FILES = {
    "tests_readme": "zigux/tests/README.md",
    "perf_slice": "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
    "shared_build": "zigux/tests/phase8_build.zig",
    "makefile": "zigux/Makefile",
}

TESTS_README_MARKERS = [
    "zigux/tests/phase8_perf_buffer_poll.zig",
    "zigux/tests/phase8_bpf_type_names.zig",
    "zigux/tests/phase8_libbpf_segments.zig",
    "scripts/zigux/validate-phase8.py",
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
]

PERF_SLICE_MARKERS = [
    "PHASE8_SLICE=perf-buffer-poll-helper",
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    "zigux/tests/phase8_perf_buffer_poll.zig",
    "phase8-perf-buffer-poll-tests",
]

SHARED_BUILD_MARKERS = [
    "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    "phase8_perf_buffer_poll.zig",
    "phase8-perf-buffer-poll-tests",
]

MAKEFILE_MARKERS = [
    "phase8-validate:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-tests-readme-alignment.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-tests-readme-alignment.py\n",
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
    perf_slice = read_text(root, REQUIRED_FILES["perf_slice"])
    shared_build = read_text(root, REQUIRED_FILES["shared_build"])
    makefile = read_text(root, REQUIRED_FILES["makefile"])

    for marker in TESTS_README_MARKERS:
        if marker not in tests_readme:
            missing.append(f"tests_readme:{marker}")

    for marker in PERF_SLICE_MARKERS:
        if marker not in perf_slice:
            missing.append(f"perf_slice:{marker}")

    for marker in SHARED_BUILD_MARKERS:
        if marker not in shared_build:
            missing.append(f"shared_build:{marker}")

    for marker in MAKEFILE_MARKERS:
        if marker not in makefile:
            missing.append(f"makefile:{marker}")

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
                "- zigux/tests/phase8_libbpf_segments.zig",
                "- zigux/tests/phase8_bpf_type_names.zig",
                "- zigux/tests/phase8_perf_buffer_poll.zig",
                "- scripts/zigux/validate-phase8.py",
                "- Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
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
                "- phase8-perf-buffer-poll-tests",
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

        perf_slice_path = tmp_root / REQUIRED_FILES["perf_slice"]
        original_perf_slice = perf_slice_path.read_text(encoding="utf-8")
        perf_slice_path.write_text(
            original_perf_slice.replace(
                "- zigux/tests/phase8_perf_buffer_poll.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "perf_slice_test_reference",
            tmp_root,
            "perf_slice:zigux/tests/phase8_perf_buffer_poll.zig",
        )
        perf_slice_path.write_text(original_perf_slice, encoding="utf-8")

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
            "makefile_self_test_hook",
            tmp_root,
            "makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-tests-readme-alignment.py --self-test\n",
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
            "makefile_live_hook",
            tmp_root,
            "makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-tests-readme-alignment.py\n",
        )

    print("PHASE8_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    print("PHASE8_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT=8")
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
