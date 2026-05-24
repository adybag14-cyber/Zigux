#!/usr/bin/env python3
"""Guard the current Phase 6 checksum and hexdump perf-marker packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
CATALOG_PATH = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")
SURVEY_PATH = Path("Documentation/zigux/phase6-perf-gate-survey.md")
EVIDENCE_MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")
PARITY_MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
MAKEFILE_PATH = Path("zigux/Makefile")
CHECKER_PATH = Path("scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py")

REQUIRED_SCRIPTS_SNIPPETS = [
    "## Phase 6",
    "`zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`",
    "`make -C zigux phase6-checksum-perf`",
    "`zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig`",
    "`make -C zigux phase6-hexdump-perf`",
]

REQUIRED_CATALOG_SNIPPETS = [
    "checksum keeps a dedicated helper-vs-reference slowdown gate in `zigux/tests/phase6_checksum_perf.zig`",
    "- `checksum` keeps a dedicated helper-vs-reference slowdown gate in `zigux/tests/phase6_checksum_perf.zig`, with the committed payload threshold matrix (`64B`, `1501B`) and the `checksum.ipFastCsum` IPv4 fast-path matrix (`IPV4_20B`, `IPV4_20B_UPDATED`, `IPV4_24B`, `IPV4_60B`) still owned by `zigux/tests/fixtures/phase6_checksum_vectors.zig`; the shared replay packet exposes that packet through `zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig`, `make -C zigux phase6-checksum-perf-matrix-test`, `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-perf`.",
    "hexdump keeps a dedicated slowdown gate in `zigux/tests/phase6_hexdump_perf.zig`",
    "- `make -C zigux phase6-checksum-perf`",
    "- `python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py`",
    "- `make -C zigux phase6-hexdump-perf`",
]

REQUIRED_SURVEY_SNIPPETS = [
    "`64B` at `iterations = 200_000` with `max_slowdown_pct = 150`",
    "`1501B` at `iterations = 12_000` with `max_slowdown_pct = 150`",
    "`IPV4_20B` with `iterations = 600_000` and `max_slowdown_pct = 100`",
    "`IPV4_20B_UPDATED` with `iterations = 600_000` and `max_slowdown_pct = 100`",
    "`IPV4_24B` with `iterations = 500_000` and `max_slowdown_pct = 100`",
    "`IPV4_60B` with `iterations = 250_000` and `max_slowdown_pct = 100`",
    "`16B-plain-g1` at `reps = 40_000` with `max_slowdown_pct = 175`",
    "`32B-ascii-g2` at `reps = 10_000` with `max_slowdown_pct = 550`",
    "`16B-ascii-g4` at `reps = 20_000` with `max_slowdown_pct = 550`",
    "`16B-ascii-g8` at `reps = 20_000` with `max_slowdown_pct = 600`",
]

REQUIRED_MAKEFILE_SNIPPETS = [
    "phase6-checksum-perf:",
    "phase6-hexdump-review:",
    "phase6-hexdump-perf-matrix-test:",
    "phase6-hexdump-perf:",
    "phase6-perf: phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf phase6-hexdump-review phase6-hexdump-perf-matrix-test phase6-hexdump-perf",
]

REQUIRED_EVIDENCE_REPLAYS = [
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf",
    "python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py",
    "zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-review",
    "zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-perf-matrix-test",
    "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-perf",
]

REQUIRED_DIRECT_READBACK_COMPANION = CHECKER_PATH.as_posix()
REQUIRED_CHECKSUM_CHECKER_SURFACES = [
    "scripts/zigux/check-phase6-checksum-corpus-evidence.py",
    "scripts/zigux/check-phase6-checksum-c-parity.py",
]
REQUIRED_HEXDUMP_CHECKER_SURFACES = [
    "scripts/zigux/check-phase6-hexdump-packet.py",
    "scripts/zigux/check-phase6-hexdump-route.py",
]
EXPECTED_CHECKSUM_EVIDENCE_ROUTES = [
    "zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf-matrix-test",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf",
    "make -C zigux phase6-perf",
]
EXPECTED_HEXDUMP_EVIDENCE_ROUTES = [
    "zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-review",
    "zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-perf-matrix-test",
    "zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-test",
    "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-perf",
]
EXPECTED_CHECKSUM_PARITY_ROUTES = [
    "make -C zigux phase6-checksum-perf-matrix-test",
    "make -C zigux phase6-checksum-perf",
    "make -C zigux phase6-perf",
]
EXPECTED_HEXDUMP_PARITY_ROUTES = [
    "make -C zigux phase6-hexdump-review",
    "make -C zigux phase6-hexdump-perf-matrix-test",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-perf",
]
EXPECTED_HEXDUMP_PERF_MATRIX_PREFLIGHT = "zigux/tests/phase6_hexdump_perf_matrix.zig"
EXPECTED_SURVEYED_HEAD = "current-master-readback-2026-05-24"
EXPECTED_CHECKSUM_CASES = {
    "64B": {"iterations": 200000, "max_slowdown_pct": 150},
    "1501B": {"iterations": 12000, "max_slowdown_pct": 150},
}
EXPECTED_CHECKSUM_IPV4_FAST_PATH_CASES = {
    "IPV4_20B": {"iterations": 600000, "max_slowdown_pct": 100},
    "IPV4_20B_UPDATED": {"iterations": 600000, "max_slowdown_pct": 100},
    "IPV4_24B": {"iterations": 500000, "max_slowdown_pct": 100},
    "IPV4_60B": {"iterations": 250000, "max_slowdown_pct": 100},
}
EXPECTED_CHECKSUM_IPV4_FAST_PATH_LABELS = ["IPV4_20B", "IPV4_20B_UPDATED", "IPV4_24B", "IPV4_60B"]
EXPECTED_HEXDUMP_CASES = {
    "16B-plain-g1": {"reps": 40000, "max_slowdown_pct": 175},
    "32B-ascii-g2": {"reps": 10000, "max_slowdown_pct": 550},
    "16B-ascii-g4": {"reps": 20000, "max_slowdown_pct": 550},
    "16B-ascii-g8": {"reps": 20000, "max_slowdown_pct": 600},
}

SELF_TEST_CASE_COUNT = 12


class ValidationError(RuntimeError):
    """Raised when the Phase 6 perf packet drifts."""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(
                f"missing expected Phase 6 perf marker in {path.as_posix()}: {snippet}"
            )


def load_manifest(path: Path) -> dict[str, object]:
    try:
        parsed = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path.as_posix()}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValidationError(f"manifest root is not an object: {path.as_posix()}")
    return parsed


def get_helper(manifest: dict[str, object], key: str) -> dict[str, object]:
    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError(f"manifest helpers[] missing for {key}")
    for helper in helpers:
        if isinstance(helper, dict) and helper.get("key") == key:
            return helper
    raise ValidationError(f"missing helper row in manifest: {key}")


def validate_case_matrix(name: str, cases: object, expected: dict[str, dict[str, int]]) -> None:
    if not isinstance(cases, list):
        raise ValidationError(f"{name} perf cases missing")
    by_label: dict[str, dict[str, object]] = {}
    for case in cases:
        if not isinstance(case, dict):
            raise ValidationError(f"{name} perf case entry is not an object")
        label = case.get("label")
        if not isinstance(label, str):
            raise ValidationError(f"{name} perf case label missing")
        by_label[label] = case
    if set(by_label) != set(expected):
        raise ValidationError(f"{name} perf case drift: {sorted(by_label)}")
    for label, fields in expected.items():
        for field, value in fields.items():
            if by_label[label].get(field) != value:
                raise ValidationError(f"{name} {label} {field} drifted")


def require_checker_surfaces(helper: dict[str, object], key: str, expected_surfaces: list[str]) -> None:
    checker_surfaces = helper.get("checker_surfaces")
    if checker_surfaces != expected_surfaces:
        raise ValidationError(f"{key} checker surface drifted")


def require_routes(name: str, routes: object, expected_routes: list[str]) -> None:
    if routes != expected_routes:
        raise ValidationError(f"{name} rerun routes drifted")


def validate_evidence_manifest(path: Path) -> None:
    manifest = load_manifest(path)
    if manifest.get("packet") != "phase6-helper-evidence":
        raise ValidationError(f"unexpected packet id in {path.as_posix()}")
    if manifest.get("phase") != "Phase 6":
        raise ValidationError(f"unexpected phase id in {path.as_posix()}")
    if manifest.get("surveyed_head") != EXPECTED_SURVEYED_HEAD:
        raise ValidationError("helper-evidence surveyed_head drifted")

    companions = manifest.get("current_direct_readback_companions")
    if not isinstance(companions, list) or REQUIRED_DIRECT_READBACK_COMPANION not in companions:
        raise ValidationError(f"missing direct readback companion in {path.as_posix()}: {REQUIRED_DIRECT_READBACK_COMPANION}")

    inventory = manifest.get("current_shared_replay_inventory")
    if not isinstance(inventory, list):
        raise ValidationError("current_shared_replay_inventory is missing")
    for replay in REQUIRED_EVIDENCE_REPLAYS:
        if replay not in inventory:
            raise ValidationError(f"missing shared replay inventory marker in {path.as_posix()}: {replay}")

    checksum = get_helper(manifest, "checksum")
    hexdump = get_helper(manifest, "hexdump")

    if checksum.get("dedicated_slowdown_replay") != "zigux/tests/phase6_checksum_perf.zig":
        raise ValidationError("checksum dedicated_slowdown_replay drifted")
    if hexdump.get("dedicated_slowdown_replay") != "zigux/tests/phase6_hexdump_perf.zig":
        raise ValidationError("hexdump dedicated_slowdown_replay drifted")

    require_checker_surfaces(checksum, "checksum", REQUIRED_CHECKSUM_CHECKER_SURFACES)
    require_checker_surfaces(hexdump, "hexdump", REQUIRED_HEXDUMP_CHECKER_SURFACES)

    checksum_perf = checksum.get("current_perf_evidence")
    hexdump_perf = hexdump.get("current_perf_evidence")
    if not isinstance(checksum_perf, dict):
        raise ValidationError("checksum current_perf_evidence missing")
    if not isinstance(hexdump_perf, dict):
        raise ValidationError("hexdump current_perf_evidence missing")

    validate_case_matrix("checksum evidence", checksum_perf.get("cases"), EXPECTED_CHECKSUM_CASES)
    if checksum_perf.get("payload_case_labels") != list(EXPECTED_CHECKSUM_CASES):
        raise ValidationError("checksum evidence payload_case_labels drifted")
    validate_case_matrix(
        "checksum evidence ipv4 fast path",
        checksum_perf.get("ipv4_fast_path_cases"),
        EXPECTED_CHECKSUM_IPV4_FAST_PATH_CASES,
    )
    if checksum_perf.get("ipv4_fast_path_case_labels") != EXPECTED_CHECKSUM_IPV4_FAST_PATH_LABELS:
        raise ValidationError("checksum evidence ipv4_fast_path_case_labels drifted")
    require_routes(
        "checksum evidence",
        checksum_perf.get("linux_style_rerun_routes"),
        EXPECTED_CHECKSUM_EVIDENCE_ROUTES,
    )

    validate_case_matrix("hexdump evidence", hexdump_perf.get("cases"), EXPECTED_HEXDUMP_CASES)
    require_routes(
        "hexdump evidence",
        hexdump_perf.get("linux_style_rerun_routes"),
        EXPECTED_HEXDUMP_EVIDENCE_ROUTES,
    )


def validate_parity_manifest(path: Path) -> None:
    manifest = load_manifest(path)
    if manifest.get("packet") != "phase6-helper-parity":
        raise ValidationError(f"unexpected packet id in {path.as_posix()}")
    if manifest.get("phase") != "Phase 6":
        raise ValidationError(f"unexpected phase id in {path.as_posix()}")
    if manifest.get("surveyed_head") != EXPECTED_SURVEYED_HEAD:
        raise ValidationError("helper-parity surveyed_head drifted")

    checksum = get_helper(manifest, "checksum")
    hexdump = get_helper(manifest, "hexdump")
    require_checker_surfaces(checksum, "checksum", REQUIRED_CHECKSUM_CHECKER_SURFACES)
    require_checker_surfaces(hexdump, "hexdump", REQUIRED_HEXDUMP_CHECKER_SURFACES)
    if hexdump.get("perf_matrix_preflight") != EXPECTED_HEXDUMP_PERF_MATRIX_PREFLIGHT:
        raise ValidationError("hexdump perf_matrix_preflight drifted")

    checksum_perf = checksum.get("current_perf_evidence")
    hexdump_perf = hexdump.get("current_perf_evidence")
    if not isinstance(checksum_perf, dict):
        raise ValidationError("checksum current_perf_evidence missing")
    if not isinstance(hexdump_perf, dict):
        raise ValidationError("hexdump current_perf_evidence missing")

    validate_case_matrix("checksum", checksum_perf.get("cases"), EXPECTED_CHECKSUM_CASES)
    if checksum_perf.get("payload_case_labels") != list(EXPECTED_CHECKSUM_CASES):
        raise ValidationError("checksum payload_case_labels drifted")
    if checksum_perf.get("ipv4_fast_path_case_labels") != EXPECTED_CHECKSUM_IPV4_FAST_PATH_LABELS:
        raise ValidationError("checksum ipv4_fast_path_case_labels drifted")
    require_routes(
        "checksum parity",
        checksum_perf.get("linux_style_rerun_routes"),
        EXPECTED_CHECKSUM_PARITY_ROUTES,
    )

    validate_case_matrix("hexdump", hexdump_perf.get("cases"), EXPECTED_HEXDUMP_CASES)
    require_routes(
        "hexdump parity",
        hexdump_perf.get("linux_style_rerun_routes"),
        EXPECTED_HEXDUMP_PARITY_ROUTES,
    )


def validate(repo_root: Path) -> None:
    require_snippets(repo_root / SCRIPTS_README_PATH, REQUIRED_SCRIPTS_SNIPPETS)
    require_snippets(repo_root / CATALOG_PATH, REQUIRED_CATALOG_SNIPPETS)
    require_snippets(repo_root / SURVEY_PATH, REQUIRED_SURVEY_SNIPPETS)
    require_snippets(repo_root / MAKEFILE_PATH, REQUIRED_MAKEFILE_SNIPPETS)
    validate_evidence_manifest(repo_root / EVIDENCE_MANIFEST_PATH)
    validate_parity_manifest(repo_root / PARITY_MANIFEST_PATH)


def scaffold_repo(root: Path) -> None:
    write_text(root / SCRIPTS_README_PATH, "\n".join(REQUIRED_SCRIPTS_SNIPPETS) + "\n")
    write_text(root / CATALOG_PATH, "\n".join(REQUIRED_CATALOG_SNIPPETS) + "\n")
    write_text(root / SURVEY_PATH, "\n".join(REQUIRED_SURVEY_SNIPPETS) + "\n")
    write_text(root / MAKEFILE_PATH, "\n".join(REQUIRED_MAKEFILE_SNIPPETS) + "\n")
    write_text(
        root / EVIDENCE_MANIFEST_PATH,
        json.dumps(
            {
                "packet": "phase6-helper-evidence",
                "phase": "Phase 6",
                "surveyed_head": EXPECTED_SURVEYED_HEAD,
                "current_direct_readback_companions": [REQUIRED_DIRECT_READBACK_COMPANION],
                "current_shared_replay_inventory": REQUIRED_EVIDENCE_REPLAYS,
                "helpers": [
                    {
                        "key": "checksum",
                        "dedicated_slowdown_replay": "zigux/tests/phase6_checksum_perf.zig",
                        "checker_surfaces": REQUIRED_CHECKSUM_CHECKER_SURFACES,
                        "current_perf_evidence": {
                            "cases": [
                                {"label": "64B", "iterations": 200000, "max_slowdown_pct": 150},
                                {"label": "1501B", "iterations": 12000, "max_slowdown_pct": 150},
                            ],
                            "payload_case_labels": ["64B", "1501B"],
                            "ipv4_fast_path_cases": [
                                {"label": "IPV4_20B", "iterations": 600000, "max_slowdown_pct": 100},
                                {"label": "IPV4_20B_UPDATED", "iterations": 600000, "max_slowdown_pct": 100},
                                {"label": "IPV4_24B", "iterations": 500000, "max_slowdown_pct": 100},
                                {"label": "IPV4_60B", "iterations": 250000, "max_slowdown_pct": 100},
                            ],
                            "ipv4_fast_path_case_labels": EXPECTED_CHECKSUM_IPV4_FAST_PATH_LABELS,
                            "linux_style_rerun_routes": EXPECTED_CHECKSUM_EVIDENCE_ROUTES,
                        },
                    },
                    {
                        "key": "hexdump",
                        "dedicated_slowdown_replay": "zigux/tests/phase6_hexdump_perf.zig",
                        "checker_surfaces": REQUIRED_HEXDUMP_CHECKER_SURFACES,
                        "current_perf_evidence": {
                            "cases": [
                                {"label": "16B-plain-g1", "reps": 40000, "max_slowdown_pct": 175},
                                {"label": "32B-ascii-g2", "reps": 10000, "max_slowdown_pct": 550},
                                {"label": "16B-ascii-g4", "reps": 20000, "max_slowdown_pct": 550},
                                {"label": "16B-ascii-g8", "reps": 20000, "max_slowdown_pct": 600},
                            ],
                            "linux_style_rerun_routes": EXPECTED_HEXDUMP_EVIDENCE_ROUTES,
                        },
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / PARITY_MANIFEST_PATH,
        json.dumps(
            {
                "packet": "phase6-helper-parity",
                "phase": "Phase 6",
                "surveyed_head": EXPECTED_SURVEYED_HEAD,
                "helpers": [
                    {
                        "key": "checksum",
                        "checker_surfaces": REQUIRED_CHECKSUM_CHECKER_SURFACES,
                        "current_perf_evidence": {
                            "cases": [
                                {"label": "64B", "iterations": 200000, "max_slowdown_pct": 150},
                                {"label": "1501B", "iterations": 12000, "max_slowdown_pct": 150},
                            ],
                            "payload_case_labels": ["64B", "1501B"],
                            "ipv4_fast_path_case_labels": EXPECTED_CHECKSUM_IPV4_FAST_PATH_LABELS,
                            "linux_style_rerun_routes": EXPECTED_CHECKSUM_PARITY_ROUTES,
                        },
                    },
                    {
                        "key": "hexdump",
                        "checker_surfaces": REQUIRED_HEXDUMP_CHECKER_SURFACES,
                        "perf_matrix_preflight": EXPECTED_HEXDUMP_PERF_MATRIX_PREFLIGHT,
                        "current_perf_evidence": {
                            "cases": [
                                {"label": "16B-plain-g1", "reps": 40000, "max_slowdown_pct": 175},
                                {"label": "32B-ascii-g2", "reps": 10000, "max_slowdown_pct": 550},
                                {"label": "16B-ascii-g4", "reps": 20000, "max_slowdown_pct": 550},
                                {"label": "16B-ascii-g8", "reps": 20000, "max_slowdown_pct": 600},
                            ],
                            "linux_style_rerun_routes": EXPECTED_HEXDUMP_PARITY_ROUTES,
                        },
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )


def mutate_text(path: Path, old: str, new: str) -> None:
    write_text(path, read_text(path).replace(old, new, 1))


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_checksum_hexdump_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        cases = [
            (SCRIPTS_README_PATH, "`make -C zigux phase6-checksum-perf`", "`make -C zigux phase6-checksum-test`", "phase6-checksum-perf"),
            (CATALOG_PATH, "- `python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py`", "- `python3 scripts/zigux/check-phase6-checksum-c-parity.py`", "check-phase6-checksum-hexdump-perf-markers.py"),
            (SURVEY_PATH, "`16B-ascii-g8` at `reps = 20_000` with `max_slowdown_pct = 600`", "`16B-ascii-g8` at `reps = 20_000` with `max_slowdown_pct = 650`", "16B-ascii-g8"),
            (MAKEFILE_PATH, "phase6-hexdump-perf:", "phase6-hexdump-test:", "phase6-hexdump-perf:"),
            (EVIDENCE_MANIFEST_PATH, '"surveyed_head": "current-master-readback-2026-05-24"', '"surveyed_head": "current-master-readback-2026-05-21"', "helper-evidence surveyed_head drifted"),
            (EVIDENCE_MANIFEST_PATH, '"dedicated_slowdown_replay": "zigux/tests/phase6_checksum_perf.zig"', '"dedicated_slowdown_replay": "zigux/tests/phase6_checksum.zig"', "checksum dedicated_slowdown_replay drifted"),
            (EVIDENCE_MANIFEST_PATH, '"zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig"', '"zig build phase6-checksum-test --build-file zigux/tests/phase6_build.zig"', "checksum evidence rerun routes drifted"),
            (EVIDENCE_MANIFEST_PATH, '"zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig"', '"zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig"', "hexdump evidence rerun routes drifted"),
            (EVIDENCE_MANIFEST_PATH, '"zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe"', '"zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig"', "hexdump evidence rerun routes drifted"),
            (PARITY_MANIFEST_PATH, '"perf_matrix_preflight": "zigux/tests/phase6_hexdump_perf_matrix.zig"', '"perf_matrix_preflight": "zigux/tests/phase6_hexdump_perf.zig"', "hexdump perf_matrix_preflight drifted"),
            (PARITY_MANIFEST_PATH, '"make -C zigux phase6-perf"', '"make -C zigux phase6-checksum-test"', "checksum parity rerun routes drifted"),
            (PARITY_MANIFEST_PATH, '"scripts/zigux/check-phase6-hexdump-route.py"', '"scripts/zigux/check-phase6-hexdump-review.py"', "hexdump checker surface drifted"),
        ]

        cases_run = 0
        for rel_path, old, new, expected in cases:
            mutate_text(root / rel_path, old, new)
            try:
                validate(root)
            except ValidationError as exc:
                if expected not in str(exc):
                    raise AssertionError(f"expected {expected!r} in {str(exc)!r}") from exc
            else:
                raise AssertionError(f"expected validation failure for {rel_path.as_posix()}")
            scaffold_repo(root)
            cases_run += 1

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")

    print("PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS_SELF_TEST=pass")
    print(f"PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0
    try:
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS=fail: {exc}")
        return 1
    print("PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
