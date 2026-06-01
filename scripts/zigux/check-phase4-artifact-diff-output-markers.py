#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()


@dataclass(frozen=True)
class CheckSpec:
    name: str
    rel_path: Path
    args: tuple[str, ...]
    exact_markers: tuple[str, ...] = ()
    prefix_markers: tuple[str, ...] = ()


CHECKS = (
    CheckSpec(
        "contract_self_test",
        Path("scripts/zigux/check-artifact-diff-contract.py"),
        ("--self-test",),
        exact_markers=(
            "ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass",
            "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=24",
        ),
    ),
    CheckSpec(
        "contract_live",
        Path("scripts/zigux/check-artifact-diff-contract.py"),
        (),
        exact_markers=(
            "ARTIFACT_DIFF_CONTRACT=pass",
            "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=30",
        ),
    ),
    CheckSpec(
        "determinism_self_test",
        Path("scripts/zigux/check-phase4-artifact-diff-determinism.py"),
        ("--self-test",),
        exact_markers=(
            "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass",
            "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=12",
        ),
    ),
    CheckSpec(
        "determinism_live",
        Path("scripts/zigux/check-phase4-artifact-diff-determinism.py"),
        (),
        exact_markers=(
            "PHASE4_ARTIFACT_DIFF_DETERMINISM=pass",
            "PHASE4_ARTIFACT_DIFF_DETERMINISM_DIRECT_PACKET_MEMBERS=11",
            "PHASE4_ARTIFACT_DIFF_DETERMINISM_AUTH_MISSING_BROADER_COMPANIONS=0",
        ),
    ),
    CheckSpec(
        "validator_replays_self_test",
        Path("scripts/zigux/check-phase4-artifact-diff-validator-replays.py"),
        ("--self-test",),
        exact_markers=(
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST=pass",
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14",
        ),
    ),
    CheckSpec(
        "validator_replays_live",
        Path("scripts/zigux/check-phase4-artifact-diff-validator-replays.py"),
        (),
        exact_markers=(
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS=pass",
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT=7",
            "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT=16",
        ),
        prefix_markers=("PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MODE=",),
    ),
)

SELF_TEST_CASES = (
    "round_trip",
    "missing_target_file",
    "contract_self_test_marker_drift",
    "contract_live_marker_drift",
    "determinism_self_test_marker_drift",
    "determinism_live_marker_drift",
    "validator_replays_self_test_marker_drift",
    "validator_replays_live_marker_drift",
    "validator_replays_mode_prefix_drift",
    "command_failure_detected",
)


def run_spec(root: Path, spec: CheckSpec) -> None:
    path = root / spec.rel_path
    if not path.exists():
        raise RuntimeError(f"missing required checker target: {spec.rel_path.as_posix()}")
    completed = subprocess.run(
        [sys.executable, str(path), *spec.args],
        check=False,
        capture_output=True,
        text=True,
        cwd=root,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip()
        detail = f": {stderr}" if stderr else ""
        raise RuntimeError(f"{spec.name} exited {completed.returncode}{detail}")
    stdout = completed.stdout
    missing_exact = [marker for marker in spec.exact_markers if marker not in stdout]
    missing_prefix = [prefix for prefix in spec.prefix_markers if prefix not in stdout]
    if missing_exact or missing_prefix:
        missing = missing_exact + [f"{prefix}<value>" for prefix in missing_prefix]
        raise RuntimeError(f"{spec.name} is missing required output markers: {missing}")


def run_check(root: Path) -> int:
    for spec in CHECKS:
        run_spec(root, spec)
    print("PHASE4_ARTIFACT_DIFF_OUTPUT_MARKERS=pass")
    print(f"PHASE4_ARTIFACT_DIFF_OUTPUT_MARKERS_CHECK_COUNT={len(CHECKS)}")
    print(
        "PHASE4_ARTIFACT_DIFF_OUTPUT_MARKERS_CHECKS="
        + ",".join(spec.name for spec in CHECKS)
    )
    return 0


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_stub(
    path: Path,
    *,
    self_test_exit_code: int = 0,
    live_exit_code: int = 0,
    self_test_stdout_lines: tuple[str, ...] = (),
    live_stdout_lines: tuple[str, ...] = (),
) -> None:
    write_text(
        path,
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from __future__ import annotations",
                "import argparse",
                "import sys",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--self-test', action='store_true')",
                "args = parser.parse_args()",
                f"SELF_TEST_EXIT_CODE = {self_test_exit_code}",
                f"LIVE_EXIT_CODE = {live_exit_code}",
                f"SELF_TEST_STDOUT_LINES = {list(self_test_stdout_lines)!r}",
                f"LIVE_STDOUT_LINES = {list(live_stdout_lines)!r}",
                "lines = SELF_TEST_STDOUT_LINES if args.self_test else LIVE_STDOUT_LINES",
                "for line in lines:",
                "    print(line)",
                "raise SystemExit(SELF_TEST_EXIT_CODE if args.self_test else LIVE_EXIT_CODE)",
            ]
        )
        + "\n",
    )
    os.chmod(path, 0o755)


def make_fixture(root: Path) -> None:
    make_stub(
        root / Path("scripts/zigux/check-artifact-diff-contract.py"),
        self_test_stdout_lines=CHECKS[0].exact_markers,
        live_stdout_lines=CHECKS[1].exact_markers,
    )
    make_stub(
        root / Path("scripts/zigux/check-phase4-artifact-diff-determinism.py"),
        self_test_stdout_lines=CHECKS[2].exact_markers,
        live_stdout_lines=CHECKS[3].exact_markers,
    )
    make_stub(
        root / Path("scripts/zigux/check-phase4-artifact-diff-validator-replays.py"),
        self_test_stdout_lines=CHECKS[4].exact_markers,
        live_stdout_lines=CHECKS[5].exact_markers
        + tuple(prefix + "validator_present" for prefix in CHECKS[5].prefix_markers),
    )


def expect_failure(root: Path, label: str) -> str:
    try:
        run_check(root)
    except RuntimeError:
        return label
    raise AssertionError(f"expected {label} to fail")


def run_self_test() -> int:
    covered: list[str] = []
    with tempfile.TemporaryDirectory(prefix="phase4_artifact_diff_output_markers_") as tmp_dir:
        root = Path(tmp_dir)

        make_fixture(root)
        if run_check(root) != 0:
            raise AssertionError("round_trip")
        covered.append("round_trip")

        make_fixture(root)
        (root / CHECKS[0].rel_path).unlink()
        covered.append(expect_failure(root, "missing_target_file"))

        make_fixture(root)
        make_stub(
            root / CHECKS[0].rel_path,
            self_test_stdout_lines=("ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass",),
            live_stdout_lines=CHECKS[1].exact_markers,
        )
        covered.append(expect_failure(root, "contract_self_test_marker_drift"))

        make_fixture(root)
        make_stub(
            root / CHECKS[1].rel_path,
            self_test_stdout_lines=CHECKS[0].exact_markers,
            live_stdout_lines=("ARTIFACT_DIFF_CONTRACT=pass",),
        )
        covered.append(expect_failure(root, "contract_live_marker_drift"))

        make_fixture(root)
        make_stub(
            root / CHECKS[2].rel_path,
            self_test_stdout_lines=("PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass",),
            live_stdout_lines=CHECKS[3].exact_markers,
        )
        covered.append(expect_failure(root, "determinism_self_test_marker_drift"))

        make_fixture(root)
        make_stub(
            root / CHECKS[3].rel_path,
            self_test_stdout_lines=CHECKS[2].exact_markers,
            live_stdout_lines=("PHASE4_ARTIFACT_DIFF_DETERMINISM=pass",),
        )
        covered.append(expect_failure(root, "determinism_live_marker_drift"))

        make_fixture(root)
        make_stub(
            root / CHECKS[4].rel_path,
            self_test_stdout_lines=("PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST=pass",),
            live_stdout_lines=CHECKS[5].exact_markers
            + tuple(prefix + "validator_present" for prefix in CHECKS[5].prefix_markers),
        )
        covered.append(expect_failure(root, "validator_replays_self_test_marker_drift"))

        make_fixture(root)
        make_stub(
            root / CHECKS[5].rel_path,
            self_test_stdout_lines=CHECKS[4].exact_markers,
            live_stdout_lines=(
                "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS=pass",
                "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MODE=validator_present",
                "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT=7",
            ),
        )
        covered.append(expect_failure(root, "validator_replays_live_marker_drift"))

        make_fixture(root)
        make_stub(
            root / CHECKS[5].rel_path,
            self_test_stdout_lines=CHECKS[4].exact_markers,
            live_stdout_lines=(
                "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS=pass",
                "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT=7",
                "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT=16",
            ),
        )
        covered.append(expect_failure(root, "validator_replays_mode_prefix_drift"))

        make_fixture(root)
        make_stub(
            root / CHECKS[3].rel_path,
            self_test_stdout_lines=CHECKS[2].exact_markers,
            live_exit_code=1,
        )
        covered.append(expect_failure(root, "command_failure_detected"))

    if tuple(covered) != SELF_TEST_CASES:
        raise AssertionError(f"self-test catalog drifted: {covered}")

    print("PHASE4_ARTIFACT_DIFF_OUTPUT_MARKERS_SELF_TEST=pass")
    print(f"PHASE4_ARTIFACT_DIFF_OUTPUT_MARKERS_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    print(
        "PHASE4_ARTIFACT_DIFF_OUTPUT_MARKERS_SELF_TEST_CASES="
        + ",".join(SELF_TEST_CASES)
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the Phase 4 artifact-diff contract, determinism, and "
            "validator-replay scripts keep publishing the output markers relied on "
            "by broader validation and review surfaces."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    try:
        return run_check(args.root.resolve())
    except RuntimeError as exc:
        print(f"PHASE4_ARTIFACT_DIFF_OUTPUT_MARKERS=fail: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
