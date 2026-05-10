#!/usr/bin/env python3
"""Fail-closed exact evidence checks for the Phase 6 base64 fixture packet."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
FIXTURE_PATH = Path("zigux/tests/fixtures/phase6_base64_vectors.zig")
SLICE_PATH = Path("Documentation/zigux/phase6-base64-slice.md")

COUNT_ANCHORS = {
    "standard_encode_vectors": "pub const standard_cases = [_]EncodeCase{",
    "variant_encode_vectors": "pub const variant_cases = [_]VariantCase{",
    "standard_decode_vectors": "pub const standard_decode_cases = [_]DecodeCase{",
    "variant_decode_vectors": "pub const variant_decode_cases = [_]DecodeCase{",
    "invalid_decode_vectors": "pub const invalid_decode_cases = [_]InvalidDecodeCase{",
    "perf_replay_cases": "pub const perf_cases = [_]PerfCase{",
}

REQUIRED_EXACT_CHECKS = [
    "python3 scripts/zigux/check-phase6-base64-fixture-evidence.py --self-test",
    "python3 scripts/zigux/check-phase6-base64-fixture-evidence.py",
]

REQUIRED_SLICE_SNIPPETS = [
    "- `python3 scripts/zigux/check-phase6-base64-fixture-evidence.py --self-test`",
    "- `python3 scripts/zigux/check-phase6-base64-fixture-evidence.py`",
]

PERF_PAYLOAD_KEY = "perf_payload_cases"
PERF_PAYLOAD_MARKER = "pub const perf_payload ="
PERF_CASE_FIELDS = (
    ("label", "str"),
    ("iterations", "int"),
    ("max_encode_slowdown_pct", "int"),
    ("max_decode_slowdown_pct", "int"),
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path}: {exc}") from exc


def extract_array_block(content: str, rel_path: str, anchor: str) -> str:
    start = content.find(anchor)
    if start == -1:
        raise ValidationError(f"missing expected Phase 6 base64 fixture marker in {rel_path}: {anchor}")
    end = content.find("\n};", start)
    if end == -1:
        raise ValidationError(f"unterminated Phase 6 base64 fixture block in {rel_path}: {anchor}")
    return content[start:end]


def count_zig_cases(content: str, rel_path: str, anchor: str) -> int:
    block = extract_array_block(content, rel_path, anchor)
    return len(re.findall(r"^\s*\.\{", block, flags=re.MULTILINE))


def extract_perf_case_blocks(content: str, rel_path: str) -> list[str]:
    block = extract_array_block(content, rel_path, COUNT_ANCHORS["perf_replay_cases"])
    case_blocks = re.findall(r"\.\{\n(.*?)\n\s*\},", block, flags=re.DOTALL)
    if not case_blocks:
        raise ValidationError(f"missing Phase 6 base64 perf cases in {rel_path}")
    return case_blocks


def extract_perf_case_value(case_block: str, rel_path: str, field_name: str, value_kind: str) -> str | int:
    if value_kind == "str":
        pattern = rf"\.{field_name}\s*=\s*\"([^\"]+)\""
        match = re.search(pattern, case_block)
        if not match:
            raise ValidationError(f"missing Phase 6 base64 perf field in {rel_path}: {field_name}")
        return match.group(1)
    if value_kind == "int":
        pattern = rf"\.{field_name}\s*=\s*([0-9_]+)"
        match = re.search(pattern, case_block)
        if not match:
            raise ValidationError(f"missing Phase 6 base64 perf field in {rel_path}: {field_name}")
        return int(match.group(1).replace("_", ""))
    raise AssertionError(f"unsupported value kind: {value_kind}")


def extract_perf_cases(content: str, rel_path: str) -> list[dict[str, str | int]]:
    cases: list[dict[str, str | int]] = []
    for case_block in extract_perf_case_blocks(content, rel_path):
        case: dict[str, str | int] = {}
        for field_name, value_kind in PERF_CASE_FIELDS:
            case[field_name] = extract_perf_case_value(case_block, rel_path, field_name, value_kind)
        cases.append(case)
    return cases


def validate_manifest_perf_thresholds(manifest: dict[str, object], fixture_text: str, fixture_rel: str, manifest_rel: str) -> None:
    perf_thresholds = manifest.get("perf_thresholds")
    if not isinstance(perf_thresholds, dict):
        raise ValidationError(f"missing perf_thresholds in {manifest_rel}")
    base64_thresholds = perf_thresholds.get("base64")
    if not isinstance(base64_thresholds, dict):
        raise ValidationError(f"missing perf_thresholds.base64 in {manifest_rel}")
    cases = base64_thresholds.get("cases")
    if not isinstance(cases, list):
        raise ValidationError(f"missing perf_thresholds.base64.cases in {manifest_rel}")

    actual_cases = extract_perf_cases(fixture_text, fixture_rel)
    if len(cases) != len(actual_cases):
        raise ValidationError(
            f"Phase 6 base64 perf-case count drifted between {manifest_rel} ({len(cases)}) "
            f"and {fixture_rel} ({len(actual_cases)})"
        )

    for idx, (recorded, actual) in enumerate(zip(cases, actual_cases), start=1):
        if not isinstance(recorded, dict):
            raise ValidationError(f"expected object entries in perf_thresholds.base64.cases in {manifest_rel}")
        for field_name, _value_kind in PERF_CASE_FIELDS:
            recorded_value = recorded.get(field_name)
            actual_value = actual[field_name]
            if recorded_value != actual_value:
                raise ValidationError(
                    f"Phase 6 base64 perf field drifted for case #{idx} between {manifest_rel} "
                    f"({field_name}={recorded_value!r}) and {fixture_rel} ({actual_value!r})"
                )


def validate_manifest_and_fixture(repo_root: Path) -> None:
    manifest_rel = MANIFEST_PATH.as_posix()
    fixture_rel = FIXTURE_PATH.as_posix()
    manifest = read_json(repo_root / MANIFEST_PATH)
    if not isinstance(manifest, dict):
        raise ValidationError(f"expected object in {manifest_rel}")

    determinism = manifest.get("determinism_evidence")
    if not isinstance(determinism, dict):
        raise ValidationError(f"missing determinism_evidence in {manifest_rel}")

    base64 = determinism.get("base64")
    if not isinstance(base64, dict):
        raise ValidationError(f"missing determinism_evidence.base64 in {manifest_rel}")

    fixture_text = read_text(repo_root / FIXTURE_PATH)
    for key, anchor in COUNT_ANCHORS.items():
        actual = count_zig_cases(fixture_text, fixture_rel, anchor)
        recorded = base64.get(key)
        if recorded != actual:
            raise ValidationError(
                f"Phase 6 base64 fixture count drifted between {manifest_rel} ({key}={recorded!r}) "
                f"and {fixture_rel} ({actual})"
            )

    payload_cases = base64.get(PERF_PAYLOAD_KEY)
    actual_payload_cases = fixture_text.count(PERF_PAYLOAD_MARKER)
    if payload_cases != actual_payload_cases:
        raise ValidationError(
            f"Phase 6 base64 perf payload evidence drifted between {manifest_rel} "
            f"({PERF_PAYLOAD_KEY}={payload_cases!r}) and {fixture_rel} ({actual_payload_cases})"
        )

    validate_manifest_perf_thresholds(manifest, fixture_text, fixture_rel, manifest_rel)

    exact_checks = manifest.get("exact_checks")
    if not isinstance(exact_checks, list):
        raise ValidationError(f"missing exact_checks list in {manifest_rel}")
    for check in REQUIRED_EXACT_CHECKS:
        if check not in exact_checks:
            raise ValidationError(f"missing exact check in {manifest_rel}: {check}")


def validate_slice_note(repo_root: Path) -> None:
    slice_rel = SLICE_PATH.as_posix()
    content = read_text(repo_root / SLICE_PATH)
    for snippet in REQUIRED_SLICE_SNIPPETS:
        if snippet not in content:
            raise ValidationError(f"missing expected Phase 6 base64 fixture evidence marker in {slice_rel}: {snippet}")


def run_checks(repo_root: Path) -> None:
    validate_manifest_and_fixture(repo_root)
    validate_slice_note(repo_root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_fixture_block(name: str, count: int) -> list[str]:
    lines = [name]
    for index in range(1, count + 1):
        lines.append(f'    .{{ .tag = "{index:02d}" }},')
    lines.append("};")
    return lines


def scaffold_perf_cases() -> list[str]:
    cases = [
        ("STD_PAD", 12000, 150, 325),
        ("STD_NO_PAD", 12000, 150, 325),
        ("URLSAFE_PAD", 12000, 150, 325),
        ("URLSAFE_NO_PAD", 12000, 150, 325),
    ]
    lines = [COUNT_ANCHORS["perf_replay_cases"]]
    for label, iterations, encode_pct, decode_pct in cases:
        lines.extend(
            [
                "    .{",
                f'        .label = "{label}",',
                '        .payload = perf_payload,',
                "        .padding = true,",
                '        .variant_name = "std",',
                f"        .iterations = {iterations},",
                f"        .max_encode_slowdown_pct = {encode_pct},",
                f"        .max_decode_slowdown_pct = {decode_pct},",
                "    },",
            ]
        )
    lines.append("};")
    return lines


def scaffold_repo(root: Path) -> None:
    manifest = {
        "determinism_evidence": {
            "base64": {
                "standard_encode_vectors": 22,
                "variant_encode_vectors": 4,
                "standard_decode_vectors": 22,
                "variant_decode_vectors": 4,
                "invalid_decode_vectors": 24,
                "c_parity_cases": 24,
                "perf_payload_cases": 1,
                "perf_replay_cases": 4,
            }
        },
        "perf_thresholds": {
            "base64": {
                "cases": [
                    {
                        "label": "STD_PAD",
                        "iterations": 12000,
                        "max_encode_slowdown_pct": 150,
                        "max_decode_slowdown_pct": 325,
                    },
                    {
                        "label": "STD_NO_PAD",
                        "iterations": 12000,
                        "max_encode_slowdown_pct": 150,
                        "max_decode_slowdown_pct": 325,
                    },
                    {
                        "label": "URLSAFE_PAD",
                        "iterations": 12000,
                        "max_encode_slowdown_pct": 150,
                        "max_decode_slowdown_pct": 325,
                    },
                    {
                        "label": "URLSAFE_NO_PAD",
                        "iterations": 12000,
                        "max_encode_slowdown_pct": 150,
                        "max_decode_slowdown_pct": 325,
                    },
                ]
            }
        },
        "exact_checks": list(REQUIRED_EXACT_CHECKS),
    }
    write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")

    fixture_lines: list[str] = []
    fixture_lines.extend(scaffold_fixture_block(COUNT_ANCHORS["standard_encode_vectors"], 22))
    fixture_lines.append("")
    fixture_lines.extend(scaffold_fixture_block(COUNT_ANCHORS["variant_encode_vectors"], 4))
    fixture_lines.append("")
    fixture_lines.extend(scaffold_fixture_block(COUNT_ANCHORS["standard_decode_vectors"], 22))
    fixture_lines.append("")
    fixture_lines.extend(scaffold_fixture_block(COUNT_ANCHORS["variant_decode_vectors"], 4))
    fixture_lines.append("")
    fixture_lines.extend(scaffold_fixture_block(COUNT_ANCHORS["invalid_decode_vectors"], 24))
    fixture_lines.append("")
    fixture_lines.append('pub const perf_payload = "payload";')
    fixture_lines.append("")
    fixture_lines.extend(scaffold_perf_cases())
    fixture_lines.append("")
    write(root / FIXTURE_PATH, "\n".join(fixture_lines))

    slice_lines = [
        "# Phase 6 Base64 Slice",
        "",
        "- `python3 scripts/zigux/check-phase6-base64-fixture-evidence.py --self-test`",
        "- `python3 scripts/zigux/check-phase6-base64-fixture-evidence.py`",
        "",
    ]
    write(root / SLICE_PATH, "\n".join(slice_lines))


def assert_failure(root: Path, rel_path: str, old: str, new: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    if old not in original:
        raise AssertionError(f"missing self-test marker in {rel_path}: {old}")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    try:
        run_checks(root)
    except ValidationError as exc:
        if rel_path not in str(exc):
            raise AssertionError(f"unexpected failure for {rel_path}: {exc}") from exc
    else:
        raise AssertionError(f"expected failure for {rel_path}")
    path.write_text(original, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        run_checks(root)
        assert_failure(
            root,
            MANIFEST_PATH.as_posix(),
            '"standard_encode_vectors": 22',
            '"standard_encode_vectors": 21',
        )
        assert_failure(
            root,
            MANIFEST_PATH.as_posix(),
            "check-phase6-base64-fixture-evidence.py --self-test",
            "check-phase6-base64-fixture-proof.py --self-test",
        )
        assert_failure(
            root,
            FIXTURE_PATH.as_posix(),
            '        .label = "STD_PAD",',
            '        .label = "STD_PAD_MISSING",',
        )
        assert_failure(
            root,
            FIXTURE_PATH.as_posix(),
            "        .max_decode_slowdown_pct = 325,",
            "        .max_decode_slowdown_pct = 400,",
        )
        assert_failure(
            root,
            FIXTURE_PATH.as_posix(),
            'pub const perf_payload = "payload";',
            'pub const perf_payload_missing = "payload";',
        )
        assert_failure(
            root,
            SLICE_PATH.as_posix(),
            "- `python3 scripts/zigux/check-phase6-base64-fixture-evidence.py`",
            "- `python3 scripts/zigux/check-phase6-base64-fixture-proof.py`",
        )
    print("self-test passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Path to the Zigux repository root")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checks")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return 0
    run_checks(Path(args.repo_root).resolve())
    print("Phase 6 base64 fixture evidence looks aligned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())