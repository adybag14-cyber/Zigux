#!/usr/bin/env python3
"""Guard the Phase 6 runtime-task, poll, and event-loop boundary packet."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SURVEY_DOC = Path("Documentation/zigux/phase6-runtime-task-poll-event-loop-gap-survey.md")
SURVEY_CHECKER = Path("scripts/zigux/check-phase6-runtime-task-poll-event-loop-gap-survey.py")
HELPER_EVIDENCE_MANIFEST = Path("zigux/tests/phase6_helper_evidence_manifest.json")
HELPER_PARITY_MANIFEST = Path("zigux/tests/phase6_helper_parity_manifest.json")
HELPER_EVIDENCE_CATALOG = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")
HELPER_PARITY_CATALOG = Path("Documentation/zigux/phase6-helper-parity-catalog.md")

EXPECTED_ROADMAP_ANCHORS = [
    "lib/base64.c",
    "lib/bsearch.c",
    "lib/checksum.c",
    "lib/hexdump.c",
]
EXPECTED_HELPER_KEYS = ["base64", "bsearch", "checksum", "hexdump"]
FORBIDDEN_RUNTIME_HELPER_MARKERS = [
    "runtime-task",
    "runtime_task",
    "event-loop",
    "event_loop",
    "process.poll",
    "acp.sessions.events",
    "tasks.events",
    "tasks.get",
]
SURVEY_REQUIRED_SNIPPETS = [
    "# Phase 6 Runtime Task, Poll, And Event-Loop Gap Survey",
    "The truthful Phase 6 product scope is still the four helper anchors above",
    "task receipt orchestration",
    "polling-based runtime update delivery",
    "process lifecycle polling",
    "scheduler dispatch, wake, or timer-loop ownership",
]
EVIDENCE_CATALOG_REQUIRED_SNIPPETS = [
    "- roadmap-backed helper anchors:",
    "- `lib/base64.c`",
    "- `lib/bsearch.c`",
    "- `lib/checksum.c`",
    "- `lib/hexdump.c`",
]
PARITY_CATALOG_REQUIRED_SNIPPETS = [
    "| `base64` | `lib/base64.c` | `lib/base64.zig` |",
    "| `bsearch` | `lib/bsearch.c` | `lib/bsearch.zig` |",
    "| `checksum` | `lib/checksum.c` | `lib/checksum.zig` |",
    "| `hexdump` | `lib/hexdump.c` | `lib/hexdump.zig` |",
]

SELF_TEST_CASE_COUNT = 11


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def read_json(path: Path) -> dict[str, object]:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path.as_posix()}: {exc}") from exc


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(f"missing expected marker in {path.as_posix()}: {snippet}")


def require_list(manifest: dict[str, object], field_name: str) -> list[object]:
    value = manifest.get(field_name)
    if not isinstance(value, list):
        raise ValidationError(f"{field_name} missing or not a list")
    return value


def require_manifest_shape(manifest: dict[str, object], manifest_name: str) -> None:
    anchors = manifest.get("roadmap_anchors")
    if anchors != EXPECTED_ROADMAP_ANCHORS:
        raise ValidationError(f"{manifest_name} roadmap_anchors drift")

    helpers = require_list(manifest, "helpers")
    helper_keys: list[str] = []
    for helper in helpers:
        if not isinstance(helper, dict):
            raise ValidationError(f"{manifest_name} helper entry is not an object")
        key = helper.get("key")
        if not isinstance(key, str):
            raise ValidationError(f"{manifest_name} helper key missing")
        helper_keys.append(key)
        lower_key = key.lower()
        if any(marker in lower_key for marker in FORBIDDEN_RUNTIME_HELPER_MARKERS):
            raise ValidationError(f"{manifest_name} widened into runtime helper key: {key}")
        checker_surfaces = helper.get("checker_surfaces")
        if isinstance(checker_surfaces, list):
            for surface in checker_surfaces:
                if isinstance(surface, str) and surface == SURVEY_CHECKER.as_posix():
                    raise ValidationError(
                        f"{manifest_name} incorrectly classified survey checker as helper-local evidence"
                    )
    if helper_keys != EXPECTED_HELPER_KEYS:
        raise ValidationError(f"{manifest_name} helper key roster drift")


def require_catalog_boundary(path: Path) -> None:
    content = read_text(path)
    if "runtime task, polling, and event-loop" in content.lower():
        raise ValidationError(
            f"{path.as_posix()} widened into runtime-task boundary text instead of helper packet truth"
        )


def run_gap_checker(root: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(root / SURVEY_CHECKER), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise ValidationError(f"{SURVEY_CHECKER.as_posix()} failed: {detail}")


def validate(root: Path) -> None:
    require_snippets(root / SURVEY_DOC, SURVEY_REQUIRED_SNIPPETS)
    require_snippets(root / HELPER_EVIDENCE_CATALOG, EVIDENCE_CATALOG_REQUIRED_SNIPPETS)
    require_snippets(root / HELPER_PARITY_CATALOG, PARITY_CATALOG_REQUIRED_SNIPPETS)

    helper_evidence_manifest = read_json(root / HELPER_EVIDENCE_MANIFEST)
    helper_parity_manifest = read_json(root / HELPER_PARITY_MANIFEST)
    require_manifest_shape(helper_evidence_manifest, "phase6 helper evidence manifest")
    require_manifest_shape(helper_parity_manifest, "phase6 helper parity manifest")

    require_catalog_boundary(root / HELPER_EVIDENCE_CATALOG)
    require_catalog_boundary(root / HELPER_PARITY_CATALOG)
    run_gap_checker(root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_gap_checker_stub() -> str:
    return """#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()

def main() -> int:
    _ = parse_args()
    print("PHASE6_RUNTIME_TASK_POLL_EVENT_LOOP_GAP_SURVEY=pass")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
"""


def scaffold(root: Path) -> None:
    write(root / SURVEY_DOC, "\n".join(SURVEY_REQUIRED_SNIPPETS) + "\n")
    write(root / SURVEY_CHECKER, make_gap_checker_stub())
    write(
        root / HELPER_EVIDENCE_MANIFEST,
        json.dumps(
            {
                "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
                "helpers": [
                    {"key": "base64", "checker_surfaces": ["scripts/zigux/check-phase6-base64-c-parity.py"]},
                    {"key": "bsearch", "checker_surfaces": ["scripts/zigux/check-phase6-bsearch-c-parity.py"]},
                    {"key": "checksum", "checker_surfaces": ["scripts/zigux/check-phase6-checksum-c-parity.py"]},
                    {"key": "hexdump", "checker_surfaces": ["scripts/zigux/check-phase6-hexdump-packet.py"]},
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / HELPER_PARITY_MANIFEST,
        json.dumps(
            {
                "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
                "helpers": [
                    {"key": "base64", "checker_surfaces": ["scripts/zigux/check-phase6-base64-c-parity.py"]},
                    {"key": "bsearch", "checker_surfaces": ["scripts/zigux/check-phase6-bsearch-c-parity.py"]},
                    {"key": "checksum", "checker_surfaces": ["scripts/zigux/check-phase6-checksum-c-parity.py"]},
                    {"key": "hexdump", "checker_surfaces": ["scripts/zigux/check-phase6-hexdump-packet.py"]},
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write(root / HELPER_EVIDENCE_CATALOG, "\n".join(EVIDENCE_CATALOG_REQUIRED_SNIPPETS) + "\n")
    write(root / HELPER_PARITY_CATALOG, "\n".join(PARITY_CATALOG_REQUIRED_SNIPPETS) + "\n")


def expect_failure(root: Path, mutate) -> None:
    mutate()
    try:
        validate(root)
    except ValidationError:
        return
    raise AssertionError("expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_p6_runtime_packet_") as tmpdir:
        root = Path(tmpdir)
        scaffold(root)
        validate(root)

        cases_run = 0

        def reset() -> None:
            scaffold(root)

        def run_case(mutator) -> None:
            nonlocal cases_run
            reset()
            expect_failure(root, mutator)
            cases_run += 1

        run_case(lambda: (root / SURVEY_DOC).unlink())
        run_case(lambda: write(root / SURVEY_DOC, read_text(root / SURVEY_DOC).replace(SURVEY_REQUIRED_SNIPPETS[1] + "\n", "", 1)))
        run_case(lambda: (root / SURVEY_CHECKER).unlink())
        run_case(lambda: write(root / SURVEY_CHECKER, "#!/usr/bin/env python3\nraise SystemExit(1)\n"))
        run_case(
            lambda: write(
                root / HELPER_EVIDENCE_MANIFEST,
                json.dumps({"roadmap_anchors": ["lib/base64.c"], "helpers": []}, indent=2) + "\n",
            )
        )
        run_case(
            lambda: write(
                root / HELPER_EVIDENCE_MANIFEST,
                json.dumps(
                    {
                        "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
                        "helpers": [{"key": "runtime-task"}],
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        run_case(
            lambda: write(
                root / HELPER_PARITY_MANIFEST,
                json.dumps(
                    {
                        "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
                        "helpers": [
                            {"key": "base64"},
                            {"key": "bsearch"},
                            {"key": "checksum"},
                            {"key": "hexdump"},
                            {"key": "event-loop"},
                        ],
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        run_case(lambda: write(root / HELPER_EVIDENCE_CATALOG, "runtime task, polling, and event-loop\n"))
        run_case(lambda: write(root / HELPER_PARITY_CATALOG, "runtime task, polling, and event-loop\n"))
        run_case(lambda: write(root / HELPER_PARITY_CATALOG, "\n".join(PARITY_CATALOG_REQUIRED_SNIPPETS[:-1]) + "\n"))
        run_case(lambda: write(root / HELPER_EVIDENCE_CATALOG, "\n".join(EVIDENCE_CATALOG_REQUIRED_SNIPPETS[:-1]) + "\n"))

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} self-test cases, ran {cases_run}")

    print("PHASE6_RUNTIME_TASK_POLL_EVENT_LOOP_SHARED_PACKET_SELF_TEST=pass")
    print(f"PHASE6_RUNTIME_TASK_POLL_EVENT_LOOP_SHARED_PACKET_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.write_sample_root is not None:
        scaffold(args.write_sample_root)
        print(f"PHASE6_RUNTIME_TASK_POLL_EVENT_LOOP_SHARED_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0
    if args.self_test:
        run_self_test()
        return 0
    try:
        validate(args.root)
    except ValidationError as exc:
        print(f"PHASE6_RUNTIME_TASK_POLL_EVENT_LOOP_SHARED_PACKET=fail: {exc}")
        return 1
    print("PHASE6_RUNTIME_TASK_POLL_EVENT_LOOP_SHARED_PACKET=pass")
    print(f"PHASE6_RUNTIME_TASK_POLL_EVENT_LOOP_SHARED_PACKET_MARKER_COUNT={len(SURVEY_REQUIRED_SNIPPETS) + len(EVIDENCE_CATALOG_REQUIRED_SNIPPETS) + len(PARITY_CATALOG_REQUIRED_SNIPPETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
