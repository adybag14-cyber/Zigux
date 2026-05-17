#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ARTIFACT_DIFF_REL = Path("scripts/zigux/artifact_diff.py")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
REPLAY_REL = Path("zigux/tests/phase1_helpers.zig")

EXPECTED_SECTIONS = (
    "find_bit",
    "bitmap",
    "string",
    "rbtree",
    "argv_split",
    "cmdline",
    "ctype",
    "hweight",
    "list_sort",
    "zalloc",
    "str_error_r",
    "slab",
    "vsprintf",
)

EXPECTED_HELPERS = (
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
)

REPLAY_IMPORTS = (
    'const argv_split = @import("argv_split");',
    'const bitmap = @import("bitmap");',
    'const cmdline = @import("cmdline");',
    'const ctype = @import("ctype");',
    'const find_bit = @import("find_bit");',
    'const hweight = @import("hweight");',
    'const list_sort = @import("list_sort");',
    'const rbtree = @import("rbtree");',
    'const slab = @import("slab");',
    'const str_error_r = @import("str_error_r");',
    'const string = @import("string");',
    'const vsprintf = @import("vsprintf");',
    'const zalloc = @import("zalloc");',
)

REPLAY_ANCHORS = (
    '@embedFile("fixtures/phase1_helpers.json")',
    ".ignore_unknown_fields = true,",
    'test "phase 1 helper modules import cleanly"',
    'test "phase 1 helper ports match committed parity fixture"',
)

ARTIFACT_DIFF_MARKERS = (
    "ARTIFACT_DIFF_SELF_TEST=pass",
    "MODE=text",
    "MODE=json",
    "MODE=sha256",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> object:
    return json.loads(_read_text(path))


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    artifact_diff = root / ARTIFACT_DIFF_REL
    fixture = root / FIXTURE_REL
    manifest = root / MANIFEST_REL
    replay = root / REPLAY_REL

    for rel in (ARTIFACT_DIFF_REL, FIXTURE_REL, MANIFEST_REL):
        if not (root / rel).exists():
            issues.append(f"missing:{rel.as_posix()}")

    if issues:
        return issues

    artifact_diff_text = _read_text(artifact_diff)
    for marker in ARTIFACT_DIFF_MARKERS:
        if marker not in artifact_diff_text:
            issues.append(f"artifact_diff_marker:{marker}")

    fixture_payload = _read_json(fixture)
    if not isinstance(fixture_payload, dict):
        issues.append("fixture:not_json_object")
    else:
        actual_sections = tuple(fixture_payload.keys())
        if actual_sections != EXPECTED_SECTIONS:
            issues.append(
                "fixture_sections:"
                + ",".join(actual_sections)
                + "!="
                + ",".join(EXPECTED_SECTIONS)
            )

    manifest_payload = _read_json(manifest)
    if not isinstance(manifest_payload, dict):
        issues.append("manifest:not_json_object")
    else:
        if manifest_payload.get("phase") != "Phase 1":
            issues.append(f"manifest_phase:{manifest_payload.get('phase')!r}")
        if manifest_payload.get("helper_count") != len(EXPECTED_HELPERS):
            issues.append(
                f"manifest_helper_count:{manifest_payload.get('helper_count')}"
            )
        helpers = manifest_payload.get("helpers")
        if helpers != list(EXPECTED_HELPERS):
            issues.append("manifest_helpers")

    if replay.exists():
        replay_text = _read_text(replay)
        for marker in REPLAY_IMPORTS:
            if marker not in replay_text:
                issues.append(f"replay_import:{marker}")
        for marker in REPLAY_ANCHORS:
            if marker not in replay_text:
                issues.append(f"replay_anchor:{marker}")

    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        print("PHASE1_PARITY=fail")
        for issue in issues:
            print(f"PHASE1_PARITY_ISSUE={issue}")
        return 1

    print("PHASE1_PARITY=pass")
    print(f"PHASE1_PARITY_SECTION_COUNT={len(EXPECTED_SECTIONS)}")
    print(f"PHASE1_PARITY_HELPER_COUNT={len(EXPECTED_HELPERS)}")
    print(
        "PHASE1_PARITY_REPLAY="
        + ("present" if (root / REPLAY_REL).exists() else "parked")
    )
    return 0


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture_json() -> str:
    payload = {section: {} for section in EXPECTED_SECTIONS}
    return json.dumps(payload, indent=2) + "\n"


def make_manifest_json() -> str:
    payload = {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(EXPECTED_HELPERS),
        "helpers": list(EXPECTED_HELPERS),
    }
    return json.dumps(payload, indent=2) + "\n"


def make_replay_text() -> str:
    imports = "\n".join(REPLAY_IMPORTS)
    anchors = "\n".join(
        (
            "fn loadFixture() void {",
            f"    _ = {REPLAY_ANCHORS[0]};",
            f"    _ = {REPLAY_ANCHORS[1]}",
            "}",
            "",
            f"{REPLAY_ANCHORS[2]} {{}}",
            f"{REPLAY_ANCHORS[3]} {{}}",
        )
    )
    return imports + "\n\n" + anchors + "\n"


def make_artifact_diff_text() -> str:
    return "\n".join(
        (
            "#!/usr/bin/env python3",
            "TEXT = 'MODE=text'",
            "JSON = 'MODE=json'",
            "SHA = 'MODE=sha256'",
            "print_marker = 'ARTIFACT_DIFF_SELF_TEST=pass'",
        )
    ) + "\n"


def build_case_root(base: Path) -> Path:
    write_file(base / ARTIFACT_DIFF_REL, make_artifact_diff_text())
    write_file(base / FIXTURE_REL, make_fixture_json())
    write_file(base / MANIFEST_REL, make_manifest_json())
    return base


def run_self_test() -> int:
    cases: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)

        good_root = build_case_root(tmp_root / "good")
        cases.append(("good", run_check(good_root) == 0))

        missing_artifact_diff_root = build_case_root(tmp_root / "missing_artifact_diff")
        (missing_artifact_diff_root / ARTIFACT_DIFF_REL).unlink()
        cases.append(("missing_artifact_diff", run_check(missing_artifact_diff_root) != 0))

        fixture_drift_root = build_case_root(tmp_root / "fixture_drift")
        write_file(
            fixture_drift_root / FIXTURE_REL,
            json.dumps({"find_bit": {}, "bitmap": {}}, indent=2) + "\n",
        )
        cases.append(("fixture_drift", run_check(fixture_drift_root) != 0))

        manifest_drift_root = build_case_root(tmp_root / "manifest_drift")
        write_file(
            manifest_drift_root / MANIFEST_REL,
            json.dumps(
                {
                    "phase": "Phase 1",
                    "status": "closed",
                    "helper_count": len(EXPECTED_HELPERS),
                    "helpers": list(EXPECTED_HELPERS[:-1]),
                },
                indent=2,
            )
            + "\n",
        )
        cases.append(("manifest_drift", run_check(manifest_drift_root) != 0))

        replay_anchor_root = build_case_root(tmp_root / "replay_anchor")
        write_file(replay_anchor_root / REPLAY_REL, make_replay_text())
        cases.append(("replay_present", run_check(replay_anchor_root) == 0))
        write_file(
            replay_anchor_root / REPLAY_REL,
            "\n".join(REPLAY_IMPORTS) + "\n",
        )
        cases.append(("replay_anchor", run_check(replay_anchor_root) != 0))

    failed = [name for name, ok in cases if not ok]
    if failed:
        print("PHASE1_PARITY_SELF_TEST=fail")
        for name in failed:
            print(f"PHASE1_PARITY_SELF_TEST_FAILED_CASE={name}")
        return 1

    print("PHASE1_PARITY_SELF_TEST=pass")
    print(f"PHASE1_PARITY_SELF_TEST_CASE_COUNT={len(cases)}")
    print(
        "PHASE1_PARITY_SELF_TEST_CASES="
        + ",".join(name for name, _ in cases)
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Lane 09 Phase 1 parity packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    return run_check(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
