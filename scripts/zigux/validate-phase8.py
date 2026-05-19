#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from dataclasses import dataclass
from pathlib import Path


def _default_root() -> Path:
    resolved = Path(__file__).resolve()
    if len(resolved.parents) >= 3:
        return resolved.parents[2]
    return resolved.parent


ROOT = _default_root()

REQUIRED_FILES = (
    Path(".github/workflows/zigux-bootstrap.yml"),
    Path("Documentation/zigux/README.md"),
    Path("Documentation/zigux/phase8-libbpf-segment-survey.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("scripts/zigux/README.md"),
    Path("zigux/Makefile"),
    Path("zigux/tests/README.md"),
    Path("zigux/tests/phase8_exec_cmd.zig"),
    Path("zigux/tests/phase8_file_path_handle_bridge.zig"),
    Path("zigux/tests/phase8_libbpf_segments.zig"),
    Path("zigux/tests/phase8_perf_buffer_poll.zig"),
)

ROUTE_FILES = (
    Path("zigux/tests/phase8_exec_cmd_only_build.zig"),
    Path("zigux/tests/phase8_file_path_handle_bridge_only_build.zig"),
    Path("zigux/tests/phase8_libbpf_segments_only_build.zig"),
    Path("zigux/tests/phase8_perf_buffer_poll_only_build.zig"),
    Path("zigux/tests/phase8_build.zig"),
)

EXEC_CMD_NOTE_CANDIDATES = (
    Path("Documentation/zigux/phase8-exec-cmd-slice.md"),
    Path("Documentation/zigux/phase8-exec-cmd-repo-reality-note.md"),
)

FILE_MARKERS: dict[Path, tuple[str, ...]] = {
    Path("zigux/Makefile"): (
        "phase8-validate:",
        "scripts/zigux/validate-phase8.py",
        "phase8-exec-cmd-test:",
        "phase8-file-path-handle-bridge-test:",
        "phase8-libbpf-segments-test:",
        "phase8-perf-buffer-poll-test:",
        "phase8-test:",
    ),
    Path(".github/workflows/zigux-bootstrap.yml"): (
        "Validate Phase 8 tooling routes",
        "make -C zigux phase8-validate",
        "Run focused Phase 8 exec-cmd tests",
        "Run Phase 8 tooling tests",
    ),
    Path("Documentation/zigux/README.md"): (
        "Phase 8 notes",
        "scripts/zigux/validate-phase8.py",
        "tools/lib/subcmd/exec-cmd.zig",
        "tools/lib/bpf/zigux_segments/verify.zig",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        "zigux/tests/phase8_file_path_handle_bridge.zig",
        "zigux/tests/phase8_libbpf_segments.zig",
        "zigux/tests/phase8_perf_buffer_poll.zig",
    ),
    Path("Documentation/zigux/phase8-libbpf-segment-survey.md"): (
        "survey checkpoint: refreshed against current `master` readback on",
        "tools/lib/bpf/zigux_segments/verify.zig",
        "tools/lib/bpf/zigux_segments/cpu_mask.zig",
        "tools/lib/bpf/zigux_segments/logging.zig",
        "tools/lib/bpf/zigux_segments/type_names.zig",
        "tools/lib/bpf/zigux_segments/pin_path.zig",
        "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        "tools/lib/bpf/zigux_segments/manifest.json",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        "tools/lib/bpf/zigux_segments/online_cpu_routing.zig",
        "zigux/tests/phase8_build.zig",
        "zigux/tests/phase8_libbpf_segments.zig",
        "verify.zig` now directly imports `cpu_mask.zig`, `logging.zig`, `perf_buffer_poll.zig`, `pin_path.zig`, and `type_names.zig`",
        "the roadmap still calls for segmented libbpf delivery under `tools/lib/bpf/zigux_segments/`",
        "the shared bridge-boundary note, review checklist, and tests-root guide remain useful reminder surfaces",
    ),
    Path("Documentation/zigux/review-checklist.md"): (
        "if the change touches the parked Phase 8 `exec-cmd` packet",
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`make -C zigux phase8-exec-cmd-test`",
        "`make -C zigux phase8-validate`",
        "separate `kernel/workqueue.c` Phase 14 boundary-study target",
    ),
    Path("scripts/zigux/README.md"): (
        "## Phase 8",
        "scripts/zigux/validate-phase8.py",
        "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
        "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
        "zigux/tests/phase8_file_path_handle_bridge.zig",
        "zigux/tests/phase8_file_path_handle_bridge_only_build.zig",
        "zigux/tests/phase8_perf_buffer_poll.zig",
        "make -C zigux phase8-file-path-handle-bridge-test",
        "make -C zigux phase8-perf-buffer-poll-test",
        "make -C zigux phase8-validate",
    ),
    Path("zigux/tests/README.md"): (
        "scripts/zigux/validate-phase8.py",
        "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
        "`zigux/tests/phase8_file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`zigux/tests/phase8_perf_buffer_poll.zig`",
        "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
        "make -C zigux phase8-validate",
        "make -C zigux phase8-exec-cmd-test",
        "make -C zigux phase8-file-path-handle-bridge-test",
        "make -C zigux phase8-perf-buffer-poll-test",
    ),
    Path("zigux/tests/phase8_exec_cmd.zig"): (
        "phase 8 exec-cmd checklist hook keeps the parked deferred-exec packet explicit",
        "Documentation/zigux/review-checklist.md",
        "make -C zigux phase8-exec-cmd-test",
        "make -C zigux phase8-validate",
        "kernel/workqueue.c",
    ),
    Path("zigux/tests/phase8_perf_buffer_poll.zig"): (
        "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
        "zigux/tests/README.md",
        "scripts/zigux/README.md",
        "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    ),
}


@dataclass
class ValidationResult:
    missing_files: list[str]
    missing_markers: list[str]
    exec_cmd_note: str | None


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _find_exec_cmd_note(root: Path) -> str | None:
    for candidate in EXEC_CMD_NOTE_CANDIDATES:
        if (root / candidate).exists():
            return candidate.as_posix()
    return None


def _collect_missing_markers(root: Path) -> list[str]:
    missing_markers: list[str] = []
    for relative_path, markers in FILE_MARKERS.items():
        path = root / relative_path
        if not path.exists():
            continue
        text = _read(path)
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{relative_path}:{marker}")
    return missing_markers


def validate_root(root: Path) -> ValidationResult:
    missing_files = [
        path.as_posix()
        for path in (*REQUIRED_FILES, *ROUTE_FILES)
        if not (root / path).exists()
    ]

    exec_cmd_note = _find_exec_cmd_note(root)
    if exec_cmd_note is None:
        missing_files.append("Documentation/zigux/phase8-exec-cmd-slice.md|Documentation/zigux/phase8-exec-cmd-repo-reality-note.md")

    missing_markers = _collect_missing_markers(root)
    return ValidationResult(
        missing_files=missing_files,
        missing_markers=missing_markers,
        exec_cmd_note=exec_cmd_note,
    )


def emit_result(result: ValidationResult) -> int:
    if result.missing_files or result.missing_markers:
        print("PHASE8_VALIDATION=fail")
        if result.missing_files:
            print("PHASE8_MISSING_FILES_START")
            for item in result.missing_files:
                print(item)
            print("PHASE8_MISSING_FILES_END")
        if result.missing_markers:
            print("PHASE8_MISSING_MARKERS_START")
            for item in result.missing_markers:
                print(item)
            print("PHASE8_MISSING_MARKERS_END")
        return 1

    print("PHASE8_VALIDATION=pass")
    print(f"PHASE8_SHARED_FILE_COUNT={len(REQUIRED_FILES) + len(ROUTE_FILES) + 1}")
    print(f"PHASE8_MARKER_COUNT={sum(len(markers) for markers in FILE_MARKERS.values())}")
    print(f"PHASE8_EXEC_CMD_NOTE={result.exec_cmd_note}")
    return 0


def _passing_fixture(root: Path) -> None:
    _write(
        root / "zigux/Makefile",
        "\n".join(
            (
                "phase8-validate:",
                "\tpython3 scripts/zigux/validate-phase8.py",
                "phase8-exec-cmd-test:",
                "phase8-file-path-handle-bridge-test:",
                "phase8-libbpf-segments-test:",
                "phase8-perf-buffer-poll-test:",
                "phase8-test:",
            )
        ),
    )
    _write(
        root / ".github/workflows/zigux-bootstrap.yml",
        "\n".join(
            (
                "Validate Phase 8 tooling routes",
                "make -C zigux phase8-validate",
                "Run focused Phase 8 exec-cmd tests",
                "Run Phase 8 tooling tests",
            )
        ),
    )
    _write(
        root / "Documentation/zigux/README.md",
        "\n".join(
            (
                "Phase 8 notes",
                "scripts/zigux/validate-phase8.py",
                "tools/lib/subcmd/exec-cmd.zig",
                "tools/lib/bpf/zigux_segments/verify.zig",
                "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
                "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
                "zigux/tests/phase8_file_path_handle_bridge.zig",
                "zigux/tests/phase8_libbpf_segments.zig",
                "zigux/tests/phase8_perf_buffer_poll.zig",
            )
        ),
    )
    _write(
        root / "Documentation/zigux/phase8-libbpf-segment-survey.md",
        "\n".join(
            (
                "survey checkpoint: refreshed against current `master` readback on 2026-05-19",
                "tools/lib/bpf/zigux_segments/verify.zig",
                "tools/lib/bpf/zigux_segments/cpu_mask.zig",
                "tools/lib/bpf/zigux_segments/logging.zig",
                "tools/lib/bpf/zigux_segments/type_names.zig",
                "tools/lib/bpf/zigux_segments/pin_path.zig",
                "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
                "tools/lib/bpf/zigux_segments/manifest.json",
                "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
                "tools/lib/bpf/zigux_segments/online_cpu_routing.zig",
                "zigux/tests/phase8_build.zig",
                "zigux/tests/phase8_libbpf_segments.zig",
                "verify.zig` now directly imports `cpu_mask.zig`, `logging.zig`, `perf_buffer_poll.zig`, `pin_path.zig`, and `type_names.zig`",
                "the roadmap still calls for segmented libbpf delivery under `tools/lib/bpf/zigux_segments/`",
                "the shared bridge-boundary note, review checklist, and tests-root guide remain useful reminder surfaces",
            )
        ),
    )
    _write(
        root / "Documentation/zigux/review-checklist.md",
        "\n".join(
            (
                "if the change touches the parked Phase 8 `exec-cmd` packet",
                "`zigux/tests/phase8_exec_cmd.zig`",
                "`make -C zigux phase8-exec-cmd-test`",
                "`make -C zigux phase8-validate`",
                "separate `kernel/workqueue.c` Phase 14 boundary-study target",
            )
        ),
    )
    _write(
        root / "Documentation/zigux/phase8-exec-cmd-repo-reality-note.md",
        "current parked deferred-exec repo-reality note",
    )
    _write(
        root / "scripts/zigux/README.md",
        "\n".join(
            (
                "## Phase 8",
                "scripts/zigux/validate-phase8.py",
                "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
                "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
                "zigux/tests/phase8_file_path_handle_bridge.zig",
                "zigux/tests/phase8_file_path_handle_bridge_only_build.zig",
                "zigux/tests/phase8_perf_buffer_poll.zig",
                "make -C zigux phase8-file-path-handle-bridge-test",
                "make -C zigux phase8-perf-buffer-poll-test",
                "make -C zigux phase8-validate",
            )
        ),
    )
    _write(
        root / "zigux/tests/README.md",
        "\n".join(
            (
                "scripts/zigux/validate-phase8.py",
                "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
                "`zigux/tests/phase8_file_path_handle_bridge.zig`",
                "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
                "`zigux/tests/phase8_perf_buffer_poll.zig`",
                "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
                "make -C zigux phase8-validate",
                "make -C zigux phase8-exec-cmd-test",
                "make -C zigux phase8-file-path-handle-bridge-test",
                "make -C zigux phase8-perf-buffer-poll-test",
            )
        ),
    )
    _write(
        root / "zigux/tests/phase8_exec_cmd.zig",
        "\n".join(
            (
                "phase 8 exec-cmd checklist hook keeps the parked deferred-exec packet explicit",
                "Documentation/zigux/review-checklist.md",
                "make -C zigux phase8-exec-cmd-test",
                "make -C zigux phase8-validate",
                "kernel/workqueue.c",
            )
        ),
    )
    _write(
        root / "zigux/tests/phase8_file_path_handle_bridge.zig",
        "phase8 file-path-handle bridge reminder surface",
    )
    _write(
        root / "zigux/tests/phase8_libbpf_segments.zig",
        "phase8 libbpf segment reminder surface",
    )
    _write(
        root / "zigux/tests/phase8_perf_buffer_poll.zig",
        "\n".join(
            (
                "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
                "zigux/tests/README.md",
                "scripts/zigux/README.md",
                "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
            )
        ),
    )
    _write(root / "zigux/tests/phase8_exec_cmd_only_build.zig", "exec cmd build shard")
    _write(
        root / "zigux/tests/phase8_file_path_handle_bridge_only_build.zig",
        "file-path-handle bridge build shard",
    )
    _write(root / "zigux/tests/phase8_libbpf_segments_only_build.zig", "libbpf segment verify shard")
    _write(root / "zigux/tests/phase8_perf_buffer_poll_only_build.zig", "perf buffer poll shard")
    _write(root / "zigux/tests/phase8_build.zig", "phase8 aggregate build shard")


def _self_test_case_count() -> int:
    return 13


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase8-validate-selftest-") as tmp:
        root = Path(tmp)

        _passing_fixture(root)
        passing = validate_root(root)
        if passing.missing_files or passing.missing_markers:
            raise AssertionError("expected passing fixture to validate")

        broken_route = root / "zigux/tests/phase8_build.zig"
        broken_route.unlink()
        failing_route = validate_root(root)
        if "zigux/tests/phase8_build.zig" not in failing_route.missing_files:
            raise AssertionError("expected missing route file to be reported")
        _write(broken_route, "phase8 aggregate build shard")

        scripts_readme = root / "scripts/zigux/README.md"
        original_scripts_readme = _read(scripts_readme)
        scripts_readme.write_text("## Phase 8\nmake -C zigux phase8-validate\n", encoding="utf-8")
        failing_marker = validate_root(root)
        expected_marker = "scripts/zigux/README.md:scripts/zigux/validate-phase8.py"
        if expected_marker not in failing_marker.missing_markers:
            raise AssertionError("expected missing scripts-root validator marker to be reported")
        scripts_readme.write_text(original_scripts_readme, encoding="utf-8")

        exec_note = root / "Documentation/zigux/phase8-exec-cmd-repo-reality-note.md"
        exec_note.unlink()
        missing_note = validate_root(root)
        expected_note = "Documentation/zigux/phase8-exec-cmd-slice.md|Documentation/zigux/phase8-exec-cmd-repo-reality-note.md"
        if expected_note not in missing_note.missing_files:
            raise AssertionError("expected missing exec-cmd note candidate to be reported")
        _write(exec_note, "current parked deferred-exec repo-reality note")

        makefile = root / "zigux/Makefile"
        original_makefile = _read(makefile)
        makefile.write_text(
            original_makefile.replace("phase8-libbpf-segments-test:\n", "", 1),
            encoding="utf-8",
        )
        missing_libbpf_route = validate_root(root)
        expected_libbpf_route = "zigux/Makefile:phase8-libbpf-segments-test:"
        if expected_libbpf_route not in missing_libbpf_route.missing_markers:
            raise AssertionError("expected missing libbpf make route marker to be reported")
        makefile.write_text(original_makefile, encoding="utf-8")

        survey = root / "Documentation/zigux/phase8-libbpf-segment-survey.md"
        original_survey = _read(survey)
        survey.write_text(
            original_survey.replace(
                "tools/lib/bpf/zigux_segments/online_cpu_routing.zig",
                "tools/lib/bpf/zigux_segments/offline_cpu_routing.zig",
                1,
            ),
            encoding="utf-8",
        )
        missing_survey_marker = validate_root(root)
        expected_survey_marker = (
            "Documentation/zigux/phase8-libbpf-segment-survey.md:"
            "tools/lib/bpf/zigux_segments/online_cpu_routing.zig"
        )
        if expected_survey_marker not in missing_survey_marker.missing_markers:
            raise AssertionError("expected missing libbpf survey marker to be reported")
        survey.write_text(original_survey, encoding="utf-8")

        bridge_test = root / "zigux/tests/phase8_file_path_handle_bridge.zig"
        bridge_test.unlink()
        missing_bridge_test = validate_root(root)
        if "zigux/tests/phase8_file_path_handle_bridge.zig" not in missing_bridge_test.missing_files:
            raise AssertionError("expected missing bridge replay file to be reported")
        _write(bridge_test, "phase8 file-path-handle bridge reminder surface")

        bridge_build = root / "zigux/tests/phase8_file_path_handle_bridge_only_build.zig"
        bridge_build.unlink()
        missing_bridge_build = validate_root(root)
        if "zigux/tests/phase8_file_path_handle_bridge_only_build.zig" not in missing_bridge_build.missing_files:
            raise AssertionError("expected missing bridge build shard to be reported")
        _write(bridge_build, "file-path-handle bridge build shard")

        makefile.write_text(
            original_makefile.replace("phase8-file-path-handle-bridge-test:\n", "", 1),
            encoding="utf-8",
        )
        missing_bridge_route = validate_root(root)
        expected_bridge_route = "zigux/Makefile:phase8-file-path-handle-bridge-test:"
        if expected_bridge_route not in missing_bridge_route.missing_markers:
            raise AssertionError("expected missing bridge make route marker to be reported")
        makefile.write_text(original_makefile, encoding="utf-8")

        tests_readme = root / "zigux/tests/README.md"
        original_tests_readme = _read(tests_readme)
        tests_readme.write_text(
            original_tests_readme.replace("make -C zigux phase8-file-path-handle-bridge-test", "", 1),
            encoding="utf-8",
        )
        missing_tests_bridge_marker = validate_root(root)
        expected_tests_bridge_marker = (
            "zigux/tests/README.md:make -C zigux phase8-file-path-handle-bridge-test"
        )
        if expected_tests_bridge_marker not in missing_tests_bridge_marker.missing_markers:
            raise AssertionError("expected missing tests-root bridge route marker to be reported")
        tests_readme.write_text(original_tests_readme, encoding="utf-8")

        perf_poll_test = root / "zigux/tests/phase8_perf_buffer_poll.zig"
        perf_poll_test.unlink()
        missing_perf_poll_test = validate_root(root)
        if "zigux/tests/phase8_perf_buffer_poll.zig" not in missing_perf_poll_test.missing_files:
            raise AssertionError("expected missing perf-buffer-poll replay file to be reported")
        _write(
            perf_poll_test,
            "\n".join(
                (
                    "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
                    "zigux/tests/README.md",
                    "scripts/zigux/README.md",
                    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
                )
            ),
        )

        scripts_readme.write_text(
            original_scripts_readme.replace("scripts/zigux/check-phase8-perf-buffer-poll-gate.py\n", "", 1),
            encoding="utf-8",
        )
        missing_perf_poll_scripts_marker = validate_root(root)
        expected_perf_poll_scripts_marker = (
            "scripts/zigux/README.md:scripts/zigux/check-phase8-perf-buffer-poll-gate.py"
        )
        if expected_perf_poll_scripts_marker not in missing_perf_poll_scripts_marker.missing_markers:
            raise AssertionError("expected missing scripts-root perf-buffer-poll marker to be reported")
        scripts_readme.write_text(original_scripts_readme, encoding="utf-8")

        tests_readme.write_text(
            original_tests_readme.replace("`zigux/tests/phase8_perf_buffer_poll.zig`\n", "", 1),
            encoding="utf-8",
        )
        missing_perf_poll_tests_marker = validate_root(root)
        expected_perf_poll_tests_marker = (
            "zigux/tests/README.md:`zigux/tests/phase8_perf_buffer_poll.zig`"
        )
        if expected_perf_poll_tests_marker not in missing_perf_poll_tests_marker.missing_markers:
            raise AssertionError("expected missing tests-root perf-buffer-poll marker to be reported")
        tests_readme.write_text(original_tests_readme, encoding="utf-8")

        original_perf_poll_test = _read(perf_poll_test)
        perf_poll_test.write_text(
            original_perf_poll_test.replace(
                "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing_perf_poll_replay_marker = validate_root(root)
        expected_perf_poll_replay_marker = (
            "zigux/tests/phase8_perf_buffer_poll.zig:tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"
        )
        if expected_perf_poll_replay_marker not in missing_perf_poll_replay_marker.missing_markers:
            raise AssertionError("expected missing perf-buffer-poll replay marker to be reported")

    print("PHASE8_VALIDATE_SELF_TEST=pass")
    print(f"PHASE8_VALIDATE_SELF_TEST_CASE_COUNT={_self_test_case_count()}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    return emit_result(validate_root(args.root))


if __name__ == "__main__":
    raise SystemExit(main())