#!/usr/bin/env python3
"""Check that the shared Phase 10 churn filter matches the live input packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path(__file__).resolve().parent

INPUT_PACKET_PATH = Path("scripts/zigux/check-phase10-input-packet.py")
SHARED_FILTER_PATH = Path("scripts/zigux/check-phase10-tests-readme-core-surfaces.py")
COMPANION_PATH = Path("Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")

LIVE_INPUT_PACKET_MARKERS = (
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    '"id": "phase10-virtio-input-teardown-preflight-helper"',
)

SHARED_FILTER_REQUIRED_MARKERS = (
    "`drivers/virtio/virtio_input_teardown_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_teardown_preflight.zig`",
    "queue-callback-preflight, registration-preflight, teardown-preflight, status-drain, and teardown-observation replays explicit here",
    "keep `zigux/tests/phase10_virtio_ring.zig` explicit as the returned broader ring companion now that exact direct-path readback rematerializes it too.",
)

SHARED_FILTER_FORBIDDEN_MARKERS = (
    "while exact direct-path readback in this runtime still misses it",
    "queue-callback-preflight, registration-preflight, teardown-observation, and status-drain replays explicit here",
)

COMPANION_REQUIRED_MARKERS = (
    "`drivers/virtio/virtio_input_teardown_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_teardown_preflight.zig`",
    "keep `zigux/tests/phase10_virtio_ring.zig` explicit as the returned broader ring companion now that exact direct-path readback rematerializes it too.",
)

TESTS_README_REQUIRED_MARKERS = (
    "`drivers/virtio/virtio_input_teardown_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_teardown_preflight.zig`",
    "queue-callback-preflight, registration-preflight, teardown-preflight, status-drain, and teardown-observation replays explicit here",
)

SCRIPTS_README_REQUIRED_MARKERS = (
    "`drivers/virtio/virtio_input_teardown_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_teardown_preflight.zig`",
)


def read_text(root: Path, rel_path: Path) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def require_markers(problems: list[str], label: str, text: str, markers: tuple[str, ...]) -> None:
    for marker in markers:
        if marker not in text:
            problems.append(f"{label}:missing:{marker}")


def forbid_markers(problems: list[str], label: str, text: str, markers: tuple[str, ...]) -> None:
    for marker in markers:
        if marker in text:
            problems.append(f"{label}:forbidden:{marker}")


def validate(root: Path) -> tuple[list[str], list[str]]:
    tracked_paths = (
        INPUT_PACKET_PATH,
        SHARED_FILTER_PATH,
        COMPANION_PATH,
        TESTS_README_PATH,
        SCRIPTS_README_PATH,
    )
    missing_files = [str(path) for path in tracked_paths if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    problems: list[str] = []
    input_packet = read_text(root, INPUT_PACKET_PATH)
    shared_filter = read_text(root, SHARED_FILTER_PATH)
    companion = read_text(root, COMPANION_PATH)
    tests_readme = read_text(root, TESTS_README_PATH)
    scripts_readme = read_text(root, SCRIPTS_README_PATH)

    require_markers(problems, "input_packet", input_packet, LIVE_INPUT_PACKET_MARKERS)
    require_markers(problems, "shared_filter", shared_filter, SHARED_FILTER_REQUIRED_MARKERS)
    forbid_markers(problems, "shared_filter", shared_filter, SHARED_FILTER_FORBIDDEN_MARKERS)
    require_markers(problems, "companion", companion, COMPANION_REQUIRED_MARKERS)
    require_markers(problems, "tests_readme", tests_readme, TESTS_README_REQUIRED_MARKERS)
    require_markers(problems, "scripts_readme", scripts_readme, SCRIPTS_README_REQUIRED_MARKERS)

    return [], problems


def write_text(root: Path, rel_path: Path, content: str) -> None:
    target = root / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def write_fixture(root: Path) -> None:
    write_text(
        root,
        INPUT_PACKET_PATH,
        "\n".join(LIVE_INPUT_PACKET_MARKERS) + "\n",
    )
    write_text(
        root,
        SHARED_FILTER_PATH,
        "\n".join(SHARED_FILTER_REQUIRED_MARKERS) + "\n",
    )
    write_text(
        root,
        COMPANION_PATH,
        "\n".join(COMPANION_REQUIRED_MARKERS) + "\n",
    )
    write_text(
        root,
        TESTS_README_PATH,
        "\n".join(TESTS_README_REQUIRED_MARKERS) + "\n",
    )
    write_text(
        root,
        SCRIPTS_README_PATH,
        "\n".join(SCRIPTS_README_REQUIRED_MARKERS) + "\n",
    )


def expect_problem(root: Path, rel_path: Path, old: str, new: str, expected: str) -> None:
    target = root / rel_path
    original = target.read_text(encoding="utf-8")
    target.write_text(original.replace(old, new, 1), encoding="utf-8")
    missing_files, problems = validate(root)
    if missing_files:
        raise SystemExit(f"unexpected_missing_files:{','.join(missing_files)}")
    if expected not in problems:
        actual = ",".join(problems) if problems else "none"
        raise SystemExit(f"expected={expected}:actual={actual}")
    target.write_text(original, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_shared_churn_filter_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, problems = validate(root)
        if missing_files or problems:
            raise SystemExit(
                "baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"problems={','.join(problems) if problems else 'none'}"
            )

        expect_problem(
            root,
            INPUT_PACKET_PATH,
            "drivers/virtio/virtio_input_teardown_preflight.zig",
            "drivers/virtio/virtio_input_teardown_preflight_missing.zig",
            "input_packet:missing:drivers/virtio/virtio_input_teardown_preflight.zig",
        )
        expect_problem(
            root,
            SHARED_FILTER_PATH,
            "`drivers/virtio/virtio_input_teardown_preflight.zig`",
            "`drivers/virtio/virtio_input_teardown_preflight_missing.zig`",
            "shared_filter:missing:`drivers/virtio/virtio_input_teardown_preflight.zig`",
        )
        expect_problem(
            root,
            SHARED_FILTER_PATH,
            "keep `zigux/tests/phase10_virtio_ring.zig` explicit as the returned broader ring companion now that exact direct-path readback rematerializes it too.",
            "keep `zigux/tests/phase10_virtio_ring.zig` explicit as the returned broader ring companion while exact direct-path readback in this runtime still misses it.",
            "shared_filter:forbidden:while exact direct-path readback in this runtime still misses it",
        )
        expect_problem(
            root,
            TESTS_README_PATH,
            "`zigux/tests/phase10_virtio_input_teardown_preflight.zig`",
            "`zigux/tests/phase10_virtio_input_teardown_preflight_missing.zig`",
            "tests_readme:missing:`zigux/tests/phase10_virtio_input_teardown_preflight.zig`",
        )
        expect_problem(
            root,
            COMPANION_PATH,
            "keep `zigux/tests/phase10_virtio_ring.zig` explicit as the returned broader ring companion now that exact direct-path readback rematerializes it too.",
            "keep `zigux/tests/phase10_virtio_ring.zig` explicit as the returned broader ring companion while exact direct-path readback in this runtime still misses it.",
            "companion:missing:keep `zigux/tests/phase10_virtio_ring.zig` explicit as the returned broader ring companion now that exact direct-path readback rematerializes it too.",
        )
        expect_problem(
            root,
            SCRIPTS_README_PATH,
            "`drivers/virtio/virtio_input_teardown_preflight.zig`",
            "`drivers/virtio/virtio_input_teardown_preflight_missing.zig`",
            "scripts_readme:missing:`drivers/virtio/virtio_input_teardown_preflight.zig`",
        )

    print("PHASE10_SHARED_CHURN_FILTER_SELF_TEST=pass")
    print("PHASE10_SHARED_CHURN_FILTER_SELF_TEST_CASE_COUNT=6")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that the shared Phase 10 churn filter keeps teardown-preflight anchors and current ring-readback wording aligned."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, problems = validate(args.root)
    if missing_files:
        print("PHASE10_SHARED_CHURN_FILTER=fail")
        print("MISSING_PHASE10_SHARED_CHURN_FILTER_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_SHARED_CHURN_FILTER_FILES_END")
        return 1

    if problems:
        print("PHASE10_SHARED_CHURN_FILTER=fail")
        print("PHASE10_SHARED_CHURN_FILTER_PROBLEMS_START")
        for item in problems:
            print(item)
        print("PHASE10_SHARED_CHURN_FILTER_PROBLEMS_END")
        return 1

    print("PHASE10_SHARED_CHURN_FILTER=pass")
    print("PHASE10_SHARED_CHURN_FILTER_REQUIRED_FILE_COUNT=5")
    print(
        "PHASE10_SHARED_CHURN_FILTER_REQUIRED_MARKER_COUNT="
        f"{len(LIVE_INPUT_PACKET_MARKERS) + len(SHARED_FILTER_REQUIRED_MARKERS) + len(COMPANION_REQUIRED_MARKERS) + len(TESTS_README_REQUIRED_MARKERS) + len(SCRIPTS_README_REQUIRED_MARKERS)}"
    )
    print(
        "PHASE10_SHARED_CHURN_FILTER_FORBIDDEN_MARKER_COUNT="
        f"{len(SHARED_FILTER_FORBIDDEN_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
