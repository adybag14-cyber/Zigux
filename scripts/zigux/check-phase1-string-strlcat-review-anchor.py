#!/usr/bin/env python3
"""Guard the Phase 1 string strlcat review-anchor mapping."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parent

STRING_HELPER_REL = Path("tools/lib/string.zig")
STRING_MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
STRING_REVIEW_PACKET_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")

LIVE_HELPER_ANCHOR = 'test "strlcat appends only the C-string prefix from embedded-NUL sources"'
LEGACY_REVIEW_ANCHOR = 'test "strlcat appends within the destination size and reports the attempted length"'
MANIFEST_STRING_PATH = ("review_anchors", "tools/lib/string.zig")
EQUIVALENT_MAP_SNIPPET = (
    "EXPECTED_HELPER_SOURCE_EQUIVALENT_ANCHORS = {\n"
    "    'test \"strlcat appends within the destination size and reports the attempted length\"': (\n"
    "        'test \"strlcat appends only the C-string prefix from embedded-NUL sources\"'\n"
    "    ),\n"
    "}\n"
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def load_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def load_manifest(root: Path) -> dict[str, object]:
    return json.loads(load_text(root, STRING_MANIFEST_REL))


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in (STRING_HELPER_REL, STRING_MANIFEST_REL, STRING_REVIEW_PACKET_REL):
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, STRING_HELPER_REL)
    review_packet_text = load_text(root, STRING_REVIEW_PACKET_REL)
    try:
        manifest = load_manifest(root)
    except json.JSONDecodeError as exc:
        return [f"manifest:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]

    helper_anchors = nested_value(manifest, MANIFEST_STRING_PATH + ("helper_test_anchors",))
    strlcat_review_anchors = nested_value(manifest, MANIFEST_STRING_PATH + ("strlcat_review_anchors",))
    strlcat_review_summary = nested_value(manifest, MANIFEST_STRING_PATH + ("strlcat_review_summary",))

    if helper_text.count(LIVE_HELPER_ANCHOR) != 1:
        failures.append(
            f"helper_anchor:expected=1:actual={helper_text.count(LIVE_HELPER_ANCHOR)}"
        )
    if helper_text.count(LEGACY_REVIEW_ANCHOR) != 0:
        failures.append(
            f"helper_legacy_anchor:expected=0:actual={helper_text.count(LEGACY_REVIEW_ANCHOR)}"
        )

    if not isinstance(helper_anchors, list) or LEGACY_REVIEW_ANCHOR not in helper_anchors:
        failures.append("manifest_helper_test_anchors:missing_legacy_strlcat_anchor")
    if not isinstance(strlcat_review_anchors, list) or LEGACY_REVIEW_ANCHOR not in strlcat_review_anchors:
        failures.append("manifest_strlcat_review_anchors:missing_legacy_strlcat_anchor")
    if not isinstance(strlcat_review_summary, str) or "shared Phase 1 replay still does not carry dedicated strlcat() fixture keys" not in strlcat_review_summary:
        failures.append("manifest_strlcat_review_summary:missing_fixture_gap_wording")

    if review_packet_text.count(EQUIVALENT_MAP_SNIPPET) != 1:
        failures.append(
            f"review_packet_equivalent_map:expected=1:actual={review_packet_text.count(EQUIVALENT_MAP_SNIPPET)}"
        )
    if review_packet_text.count(LIVE_HELPER_ANCHOR) < 1:
        failures.append("review_packet_live_anchor:missing")
    if review_packet_text.count(LEGACY_REVIEW_ANCHOR) < 2:
        failures.append("review_packet_legacy_anchor:expected_at_least=2")

    return failures


def write_file(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_file(
        root,
        STRING_HELPER_REL,
        "\n".join(
            [
                "const std = @import(\"std\");",
                "",
                LIVE_HELPER_ANCHOR,
                "",
            ]
        ),
    )
    write_file(
        root,
        STRING_MANIFEST_REL,
        json.dumps(
            {
                "review_anchors": {
                    "tools/lib/string.zig": {
                        "helper_test_anchors": [LEGACY_REVIEW_ANCHOR],
                        "strlcat_review_anchors": [LEGACY_REVIEW_ANCHOR],
                        "strlcat_review_summary": (
                            "helper-local strlcat truncation and destination-boundary anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated strlcat() fixture keys, so append length reporting, truncation with a preserved terminator slot, unterminated-destination handling, and zero-length destination behavior remain review-visible at the helper surface"
                        ),
                    }
                }
            },
            indent=2,
        )
        + "\n",
    )
    write_file(
        root,
        STRING_REVIEW_PACKET_REL,
        "\n".join(
            [
                EQUIVALENT_MAP_SNIPPET.rstrip(),
                "",
                f"EXPECTED_HELPER_TEST_ANCHORS = ['{LEGACY_REVIEW_ANCHOR}']",
                f"EXPECTED_STRING_PACKET = {{'strlcat_review_anchors': ['{LEGACY_REVIEW_ANCHOR}']}}",
                f"# {LIVE_HELPER_ANCHOR}",
                "",
            ]
        ),
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_string_strlcat_anchor_") as tmp_dir:
        root = Path(tmp_dir)

        if "missing_file:tools/lib/string.zig" not in collect_failures(root):
            raise SystemExit("phase1-string-strlcat-anchor:self-test:missing_helper")

        build_sample_repo(root)
        if collect_failures(root):
            raise SystemExit("phase1-string-strlcat-anchor:self-test:baseline")

        write_file(root, STRING_HELPER_REL, "const std = @import(\"std\");\n")
        if "helper_anchor:expected=1:actual=0" not in collect_failures(root):
            raise SystemExit("phase1-string-strlcat-anchor:self-test:live_anchor_missing")

        build_sample_repo(root)
        manifest = load_manifest(root)
        manifest["review_anchors"]["tools/lib/string.zig"]["strlcat_review_anchors"] = []
        write_file(root, STRING_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        if "manifest_strlcat_review_anchors:missing_legacy_strlcat_anchor" not in collect_failures(root):
            raise SystemExit("phase1-string-strlcat-anchor:self-test:manifest_anchor_missing")

        build_sample_repo(root)
        write_file(root, STRING_REVIEW_PACKET_REL, "# drift\n")
        if "review_packet_equivalent_map:expected=1:actual=0" not in collect_failures(root):
            raise SystemExit("phase1-string-strlcat-anchor:self-test:equivalent_map_missing")

    print("PHASE1_STRING_STRLCAT_REVIEW_ANCHOR_SELF_TEST=pass")
    print("PHASE1_STRING_STRLCAT_REVIEW_ANCHOR_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("phase1-string-strlcat-review-anchor:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
