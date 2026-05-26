#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
KCONFIG_BRIDGE_CHECKER = ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py"
CASES_PATH = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json"
CONF_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json"

REQUIRED_BRIDGE_MARKERS = (
    'if "seed" in case:',
    'if "probability" in case:',
    "cmd.append(f\"seed={case['seed']}\")",
    "cmd.append(f\"probability={case['probability']}\")",
)

EXPECTED_RANDCONFIG_CASE = {
    "name": "randconfig",
    "seed": "0xC0FFEE",
    "probability": "15:25",
    "expected": "randconfig_expected.json",
}

EXPECTED_MANIFEST_PACKET = ["randconfig_expected.json"]
SELF_TEST_CASE_COUNT = 9


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> object:
    return json.loads(read_text(path))


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    bridge_text = read_text(resolve_path(root, KCONFIG_BRIDGE_CHECKER))
    for marker in REQUIRED_BRIDGE_MARKERS:
        count = count_exact_lines(bridge_text, marker)
        if count == 0:
            issues.append(("MISSING_BRIDGE_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_BRIDGE_MARKER", f"{marker}:count={count}"))

    cases_payload = read_json(resolve_path(root, CASES_PATH))
    if not isinstance(cases_payload, dict):
        issues.append(("INVALID_CASES_PAYLOAD", type(cases_payload).__name__))
        return issues

    conf_cases = cases_payload.get("conf_cases")
    if not isinstance(conf_cases, list):
        issues.append(("INVALID_CONF_CASES_PAYLOAD", type(conf_cases).__name__))
        return issues

    randconfig_cases = [case for case in conf_cases if isinstance(case, dict) and case.get("name") == EXPECTED_RANDCONFIG_CASE["name"]]
    if len(randconfig_cases) != 1:
        issues.append(("RANDCONFIG_CASE_COUNT_MISMATCH", f"actual={len(randconfig_cases)}:expected=1"))
    else:
        randconfig_case = randconfig_cases[0]
        for field, expected_value in EXPECTED_RANDCONFIG_CASE.items():
            actual_value = randconfig_case.get(field)
            if actual_value != expected_value:
                issues.append(
                    (
                        "RANDCONFIG_CASE_FIELD_MISMATCH",
                        f"{field}:actual={actual_value!r}:expected={expected_value!r}",
                    )
                )

    manifest_payload = read_json(resolve_path(root, CONF_MANIFEST))
    if not isinstance(manifest_payload, dict):
        issues.append(("INVALID_CONF_MANIFEST_PAYLOAD", type(manifest_payload).__name__))
        return issues

    randconfig_env_packet = manifest_payload.get("randconfig_env_packet")
    if randconfig_env_packet != EXPECTED_MANIFEST_PACKET:
        issues.append(
            (
                "RANDCONFIG_ENV_PACKET_MISMATCH",
                f"actual={randconfig_env_packet!r}:expected={EXPECTED_MANIFEST_PACKET!r}",
            )
        )

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_KCONFIG_RANDCONFIG_ENV_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, KCONFIG_BRIDGE_CHECKER), "\n".join(REQUIRED_BRIDGE_MARKERS) + "\n")
    write_text(
        resolve_path(root, CASES_PATH),
        json.dumps(
            {
                "conf_cases": [
                    {
                        "name": "randconfig",
                        "mode": "randconfig",
                        "kconfig": "Kconfig",
                        "config": "rand/.config",
                        "arch": "x86_64",
                        "allconfig": "",
                        "seed": "0xC0FFEE",
                        "probability": "15:25",
                        "expected": "randconfig_expected.json",
                    }
                ]
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve_path(root, CONF_MANIFEST),
        json.dumps({"randconfig_env_packet": EXPECTED_MANIFEST_PACKET}, indent=2) + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_kconfig_randconfig_env_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        bridge_path = resolve_path(root, KCONFIG_BRIDGE_CHECKER)
        write_text(bridge_path, read_text(bridge_path).replace(REQUIRED_BRIDGE_MARKERS[0] + "\n", "", 1))
        assert ("MISSING_BRIDGE_MARKER", REQUIRED_BRIDGE_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        bridge_path = resolve_path(root, KCONFIG_BRIDGE_CHECKER)
        write_text(bridge_path, read_text(bridge_path) + REQUIRED_BRIDGE_MARKERS[-1] + "\n")
        assert ("DUPLICATE_BRIDGE_MARKER", REQUIRED_BRIDGE_MARKERS[-1] + ":count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        cases_path = resolve_path(root, CASES_PATH)
        payload = read_json(cases_path)
        assert isinstance(payload, dict)
        payload["conf_cases"][0].pop("seed")
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        assert any(code == "RANDCONFIG_CASE_FIELD_MISMATCH" and value.startswith("seed:") for code, value in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        cases_path = resolve_path(root, CASES_PATH)
        payload = read_json(cases_path)
        assert isinstance(payload, dict)
        payload["conf_cases"][0]["probability"] = "20:30"
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        assert any(code == "RANDCONFIG_CASE_FIELD_MISMATCH" and value.startswith("probability:") for code, value in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        cases_path = resolve_path(root, CASES_PATH)
        payload = read_json(cases_path)
        assert isinstance(payload, dict)
        payload["conf_cases"].append(dict(payload["conf_cases"][0]))
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        assert ("RANDCONFIG_CASE_COUNT_MISMATCH", "actual=2:expected=1") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve_path(root, CONF_MANIFEST)
        write_text(manifest_path, json.dumps({"randconfig_env_packet": []}, indent=2) + "\n")
        assert any(code == "RANDCONFIG_ENV_PACKET_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        write_text(resolve_path(root, CASES_PATH), "[]\n")
        assert ("INVALID_CASES_PAYLOAD", "list") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(resolve_path(root, CONF_MANIFEST), "[]\n")
        assert ("INVALID_CONF_MANIFEST_PAYLOAD", "list") in collect_issues(root)
        checks_run += 1

    if checks_run != SELF_TEST_CASE_COUNT:
        print("PHASE2_KCONFIG_RANDCONFIG_ENV_PACKET_SELF_TEST=fail")
        print(f"PHASE2_KCONFIG_RANDCONFIG_ENV_PACKET_SELF_TEST_CASE_COUNT_ACTUAL={checks_run}")
        print(f"PHASE2_KCONFIG_RANDCONFIG_ENV_PACKET_SELF_TEST_CASE_COUNT_EXPECTED={SELF_TEST_CASE_COUNT}")
        return 1

    print("PHASE2_KCONFIG_RANDCONFIG_ENV_PACKET_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_RANDCONFIG_ENV_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Phase 2 kconfig randconfig seed/probability packet against the live bridge contract."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_KCONFIG_RANDCONFIG_ENV_PACKET=pass")
    print(f"PHASE2_KCONFIG_RANDCONFIG_ENV_MARKER_COUNT={len(REQUIRED_BRIDGE_MARKERS)}")
    print(f"PHASE2_KCONFIG_RANDCONFIG_ENV_EXPECTED_PACKET_COUNT={len(EXPECTED_MANIFEST_PACKET)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
