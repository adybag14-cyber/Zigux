#!/usr/bin/env python3
"""Guard the current Phase 6 runtime command and environment boundary survey."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SURVEY_PATH = Path("Documentation/zigux/phase6-runtime-command-environment-gap-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")

EXPECTED_PACKET = "phase6-helper-evidence"
EXPECTED_PHASE = "Phase 6"
EXPECTED_LANE_SCOPE = "shared helper-evidence rows and machine-readable manifest only"
EXPECTED_SURVEYED_HEAD = "current-master-readback-2026-05-22"
EXPECTED_SURVEY_COMPANION = "Documentation/zigux/phase6-runtime-command-environment-gap-survey.md"
EXPECTED_HELPER_ANCHORS = ["lib/base64.c", "lib/bsearch.c", "lib/checksum.c", "lib/hexdump.c"]
EXPECTED_SURVEY_SNIPPETS = [
    "# Phase 6 Runtime Command And Environment Gap Survey",
    "That is a runtime command substrate, not a Phase 6 leaf-helper replay.",
    "That is session and command-routing behavior, not helper-only Phase 6 evidence.",
    "These are environment-plumbing and orchestrator-state surfaces.",
    "A fresh current-master reread on 2026-05-27 did not change that boundary.",
    "Do not use it to claim that Zigux Phase 6 has already landed:",
    "- shell execution semantics",
    "- TTY session control",
    "- runtime RPC/session control",
    "- persisted workspace or app-runtime environment orchestration",
]
SELF_TEST_CASE_COUNT = 5


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def read_json(path: Path) -> dict[str, object]:
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path.as_posix()}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError(f"manifest root is not an object: {path.as_posix()}")
    return data


def require_snippets(content: str, path: Path, snippets: list[str]) -> None:
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(f"missing expected Phase 6 marker in {path.as_posix()}: {snippet}")


def validate(repo_root: Path) -> None:
    survey = read_text(repo_root / SURVEY_PATH)
    require_snippets(survey, SURVEY_PATH, EXPECTED_SURVEY_SNIPPETS)

    manifest = read_json(repo_root / MANIFEST_PATH)
    if manifest.get("packet") != EXPECTED_PACKET:
        raise ValidationError("phase6 helper evidence packet drift")
    if manifest.get("phase") != EXPECTED_PHASE:
        raise ValidationError("phase6 helper evidence phase drift")
    if manifest.get("lane_scope") != EXPECTED_LANE_SCOPE:
        raise ValidationError("phase6 helper evidence lane scope drift")
    if manifest.get("surveyed_head") != EXPECTED_SURVEYED_HEAD:
        raise ValidationError("phase6 helper evidence surveyed_head drift")
    if manifest.get("roadmap_anchors") != EXPECTED_HELPER_ANCHORS:
        raise ValidationError("phase6 helper evidence roadmap anchor drift")

    companions = manifest.get("current_direct_readback_companions")
    if not isinstance(companions, list):
        raise ValidationError("phase6 helper evidence direct-readback companions missing")
    if EXPECTED_SURVEY_COMPANION not in companions:
        raise ValidationError("phase6 runtime command/environment survey companion missing")

    gaps = manifest.get("current_repo_reality_gaps")
    if gaps != []:
        raise ValidationError("phase6 helper evidence repo-reality gaps drift")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / SURVEY_PATH, "\n".join(EXPECTED_SURVEY_SNIPPETS) + "\n")
    write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "packet": EXPECTED_PACKET,
                "phase": EXPECTED_PHASE,
                "surveyed_head": EXPECTED_SURVEYED_HEAD,
                "lane_scope": EXPECTED_LANE_SCOPE,
                "current_direct_readback_companions": [EXPECTED_SURVEY_COMPANION],
                "roadmap_anchors": EXPECTED_HELPER_ANCHORS,
                "current_repo_reality_gaps": [],
            },
            indent=2,
        )
        + "\n",
    )


def expect_failure(fn) -> None:
    try:
        fn()
    except ValidationError:
        return
    raise AssertionError("expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_runtime_cmd_env_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        def reset() -> None:
            scaffold_repo(root)

        def expect_mutation(mutator) -> None:
            nonlocal cases_run
            reset()
            mutator()
            expect_failure(lambda: validate(root))
            cases_run += 1

        cases_run = 0
        expect_mutation(
            lambda: write(
                root / MANIFEST_PATH,
                json.dumps(
                    {
                        **read_json(root / MANIFEST_PATH),
                        "current_direct_readback_companions": [],
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        expect_mutation(
            lambda: write(
                root / MANIFEST_PATH,
                json.dumps(
                    {
                        **read_json(root / MANIFEST_PATH),
                        "phase": "Phase 7",
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        expect_mutation(
            lambda: write(
                root / MANIFEST_PATH,
                json.dumps(
                    {
                        **read_json(root / MANIFEST_PATH),
                        "current_repo_reality_gaps": [EXPECTED_SURVEY_COMPANION],
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        expect_mutation(
            lambda: write(
                root / SURVEY_PATH,
                read_text(root / SURVEY_PATH).replace(
                    "That is a runtime command substrate, not a Phase 6 leaf-helper replay.\n",
                    "",
                    1,
                ),
            )
        )
        expect_mutation(
            lambda: write(
                root / SURVEY_PATH,
                read_text(root / SURVEY_PATH).replace(
                    "- persisted workspace or app-runtime environment orchestration\n",
                    "",
                    1,
                ),
            )
        )
        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")
    print("PHASE6_RUNTIME_COMMAND_ENVIRONMENT_GAP_SURVEY_SELF_TEST=pass")
    print(f"PHASE6_RUNTIME_COMMAND_ENVIRONMENT_GAP_SURVEY_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0
    try:
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE6_RUNTIME_COMMAND_ENVIRONMENT_GAP_SURVEY=fail: {exc}")
        return 1
    print("PHASE6_RUNTIME_COMMAND_ENVIRONMENT_GAP_SURVEY=pass")
    print("PHASE6_RUNTIME_COMMAND_ENVIRONMENT_GAP_SURVEY_CLAIM_BLOCK_COUNT=4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
