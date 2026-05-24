#!/usr/bin/env python3
"""Check the current Phase 1 parity gate still matches the committed blocker packet."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PARITY_REL = Path("scripts/zigux/check-phase1-parity.py")
BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")

EXPECTED_REQUIRED_FILES = (
    PARITY_REL.as_posix(),
    BLOCKERS_REL.as_posix(),
    FIXTURE_REL.as_posix(),
)

EXPECTED_FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
EXPECTED_HARNESS_REL = Path("zigux/tests/fixtures/phase1_helpers_c_harness.c")
EXPECTED_ARTIFACT_DIFF_REL = Path("scripts/zigux/artifact_diff.py")

EXPECTED_SOURCE_RELS = (
    EXPECTED_HARNESS_REL.as_posix(),
    "tools/lib/argv_split.c",
    "tools/lib/bitmap.c",
    "tools/lib/cmdline.c",
    "tools/lib/ctype.c",
    "tools/lib/find_bit.c",
    "tools/lib/hweight.c",
    "tools/lib/list_sort.c",
    "tools/lib/slab.c",
    "tools/lib/str_error_r.c",
    "tools/lib/string.c",
    "tools/lib/rbtree.c",
    "tools/lib/vsprintf.c",
    "tools/lib/zalloc.c",
)

EXPECTED_MISSING_INPUT_ISSUES = tuple(
    f"missing:{path}"
    for path in (
        "tools/lib/argv_split.c",
        "tools/lib/bitmap.c",
        "tools/lib/cmdline.c",
        "tools/lib/ctype.c",
        "tools/lib/find_bit.c",
        "tools/lib/hweight.c",
        "tools/lib/list_sort.c",
        "tools/lib/slab.c",
        "tools/lib/str_error_r.c",
        "tools/lib/string.c",
        "tools/lib/rbtree.c",
        "tools/lib/vsprintf.c",
        "tools/lib/zalloc.c",
    )
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

EXPECTED_REPLAY_BLOCKER = {
    "id": "phase1_helpers_zig_slab_zero_after_kmalloc",
    "kind": "fixture_mismatch",
    "path": "tools/lib/slab.zig",
    "field": "slab.zero_after_kmalloc",
    "expected": True,
    "actual": False,
}

EXPECTED_C_HARNESS = {
    "path": "zigux/tests/fixtures/phase1_helpers_c_harness.c",
    "state": "blocked",
    "helper_count": len(EXPECTED_HELPERS),
    "helpers": list(EXPECTED_HELPERS),
    "blocker_id": "phase1_helpers_c_harness_missing_c_sources",
}


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def load_module(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())


def eval_literalish(node: ast.AST, env: dict[str, object]) -> object:
    if isinstance(node, ast.Name):
        if node.id not in env:
            raise ValueError(f"unresolved name: {node.id}")
        return env[node.id]
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "Path"
        and len(node.args) == 1
        and not node.keywords
    ):
        return Path(ast.literal_eval(node.args[0]))
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "json"
        and node.func.attr == "loads"
        and len(node.args) == 1
        and not node.keywords
    ):
        return json.loads(ast.literal_eval(node.args[0]))
    if isinstance(node, ast.List):
        return [eval_literalish(item, env) for item in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(eval_literalish(item, env) for item in node.elts)
    if isinstance(node, ast.Dict):
        return {
            ast.literal_eval(key): eval_literalish(value, env)
            for key, value in zip(node.keys, node.values, strict=True)
        }
    return ast.literal_eval(node)


def find_literal(module: ast.Module, name: str) -> object | None:
    env: dict[str, object] = {}
    for node in module.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        try:
            value = eval_literalish(node.value, env)
        except (ValueError, SyntaxError):
            if target.id == name:
                return None
            continue
        env[target.id] = value
        if target.id == name:
            return value
    return None


def extract_fail_block(output: str) -> tuple[str, ...]:
    lines = output.splitlines()
    try:
        start = lines.index("PHASE1_PARITY_INPUT_ISSUES_START")
        end = lines.index("PHASE1_PARITY_INPUT_ISSUES_END")
    except ValueError:
        return ()
    return tuple(lines[start + 1 : end])


def validate_current_run(root: Path) -> list[str]:
    proc = subprocess.run(
        [sys.executable, str(root / PARITY_REL)],
        check=False,
        capture_output=True,
        text=True,
        cwd=root,
    )

    issues: list[str] = []
    if proc.returncode != 1:
        issues.append(f"phase1_parity_returncode:expected=1:actual={proc.returncode}")

    stdout_lines = proc.stdout.splitlines()
    if not stdout_lines or stdout_lines[0] != "PHASE1_PARITY=fail":
        actual = stdout_lines[0] if stdout_lines else ""
        issues.append(f"phase1_parity_status:expected='PHASE1_PARITY=fail':actual={actual!r}")

    missing = extract_fail_block(proc.stdout)
    if missing != EXPECTED_MISSING_INPUT_ISSUES:
        issues.append(
            f"phase1_parity_missing_input_issues:expected={EXPECTED_MISSING_INPUT_ISSUES!r}:actual={missing!r}"
        )

    forbidden_markers = (
        "PHASE1_PARITY_OUTPUT_ISSUES_START",
        "PHASE1_PARITY_KEY_ISSUES_START",
        "PHASE1_PARITY=pass",
    )
    for marker in forbidden_markers:
        if marker in proc.stdout:
            issues.append(f"phase1_parity_unexpected_marker:{marker}")

    if proc.stderr:
        issues.append(f"phase1_parity_stderr:expected='':actual={proc.stderr.strip()!r}")

    return issues


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path in EXPECTED_REQUIRED_FILES:
        if not (root / relative_path).is_file():
            issues.append(f"missing_file:{relative_path}")
    if issues:
        return issues

    module = load_module(root / PARITY_REL)
    fixture_rel = find_literal(module, "FIXTURE_REL")
    harness_rel = find_literal(module, "HARNESS_REL")
    artifact_diff_rel = find_literal(module, "ARTIFACT_DIFF_REL")
    source_rels = find_literal(module, "SOURCE_RELS")
    required_parity_keys = find_literal(module, "REQUIRED_PARITY_KEYS")
    expected_self_test_output = find_literal(module, "EXPECTED_SELF_TEST_OUTPUT")

    if fixture_rel != EXPECTED_FIXTURE_REL:
        issues.append(
            f"fixture_rel:expected={EXPECTED_FIXTURE_REL!r}:actual={fixture_rel!r}"
        )
    if harness_rel != EXPECTED_HARNESS_REL:
        issues.append(
            f"harness_rel:expected={EXPECTED_HARNESS_REL!r}:actual={harness_rel!r}"
        )
    if artifact_diff_rel != EXPECTED_ARTIFACT_DIFF_REL:
        issues.append(
            f"artifact_diff_rel:expected={EXPECTED_ARTIFACT_DIFF_REL!r}:actual={artifact_diff_rel!r}"
        )
    if tuple(path.as_posix() for path in source_rels or ()) != EXPECTED_SOURCE_RELS:
        actual = tuple(path.as_posix() for path in source_rels or ())
        issues.append(
            f"source_rels:expected={EXPECTED_SOURCE_RELS!r}:actual={actual!r}"
        )

    if not isinstance(required_parity_keys, dict):
        issues.append(
            f"required_parity_keys_type:expected='dict':actual={type(required_parity_keys).__name__!r}"
        )
    else:
        slab_keys = tuple(required_parity_keys.get("slab", ()))
        if "zero_after_kmalloc" not in slab_keys:
            issues.append(
                f"required_parity_keys:slab:missing='zero_after_kmalloc':actual={slab_keys!r}"
            )
        if isinstance(expected_self_test_output, dict) and tuple(required_parity_keys.keys()) != tuple(
            expected_self_test_output.keys()
        ):
            issues.append(
                "required_parity_keys_sections:"
                f"expected={tuple(expected_self_test_output.keys())!r}:actual={tuple(required_parity_keys.keys())!r}"
            )

    if not isinstance(expected_self_test_output, dict):
        issues.append(
            f"expected_self_test_output_type:expected='dict':actual={type(expected_self_test_output).__name__!r}"
        )
    else:
        slab = expected_self_test_output.get("slab")
        if not isinstance(slab, dict):
            issues.append(f"expected_self_test_output:slab_type:actual={type(slab).__name__!r}")
        else:
            if slab.get("zero_after_kmalloc") is not True:
                issues.append(
                    f"expected_self_test_output:slab.zero_after_kmalloc:expected=True:actual={slab.get('zero_after_kmalloc')!r}"
                )

    blockers = load_json(root / BLOCKERS_REL)
    fixture = load_json(root / FIXTURE_REL)
    if not isinstance(blockers, dict) or not isinstance(fixture, dict):
        return issues + ["blocker_or_fixture_packet_type_drift"]

    replay = blockers.get("replay")
    if not isinstance(replay, dict):
        issues.append(f"replay_type:expected='dict':actual={type(replay).__name__!r}")
    else:
        blockers_list = replay.get("blockers")
        if not isinstance(blockers_list, list) or len(blockers_list) != 1:
            issues.append(f"replay_blockers_shape:actual={blockers_list!r}")
        else:
            blocker = blockers_list[0]
            if not isinstance(blocker, dict):
                issues.append(f"replay_blocker_type:actual={type(blocker).__name__!r}")
            else:
                for key, expected in EXPECTED_REPLAY_BLOCKER.items():
                    if blocker.get(key) != expected:
                        issues.append(
                            f"replay_blocker:{key}:expected={expected!r}:actual={blocker.get(key)!r}"
                        )

    c_harness = blockers.get("c_harness")
    if not isinstance(c_harness, dict):
        issues.append(f"c_harness_type:expected='dict':actual={type(c_harness).__name__!r}")
    else:
        for key, expected in EXPECTED_C_HARNESS.items():
            if c_harness.get(key) != expected:
                issues.append(
                    f"c_harness:{key}:expected={expected!r}:actual={c_harness.get(key)!r}"
                )

    slab = fixture.get("slab")
    if not isinstance(slab, dict):
        issues.append(f"fixture:slab_type:expected='dict':actual={type(slab).__name__!r}")
    else:
        if slab.get("zero_after_kmalloc") is not True:
            issues.append(
                f"fixture:slab.zero_after_kmalloc:expected=True:actual={slab.get('zero_after_kmalloc')!r}"
            )

    issues.extend(validate_current_run(root))
    return issues


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    parity_script = f"""#!/usr/bin/env python3
from pathlib import Path
import sys
FIXTURE_REL = Path({EXPECTED_FIXTURE_REL.as_posix()!r})
HARNESS_REL = Path({EXPECTED_HARNESS_REL.as_posix()!r})
ARTIFACT_DIFF_REL = Path({EXPECTED_ARTIFACT_DIFF_REL.as_posix()!r})
EXPECTED_SELF_TEST_OUTPUT = {{\"slab\": {{\"zero_after_kmalloc\": True}}, \"bitmap\": {{}}, \"find_bit\": {{}}, \"string\": {{}}, \"rbtree\": {{}}, \"argv_split\": {{}}, \"cmdline\": {{}}, \"ctype\": {{}}, \"hweight\": {{}}, \"list_sort\": {{}}, \"zalloc\": {{}}, \"str_error_r\": {{}}, \"vsprintf\": {{}}}}
SOURCE_RELS = [{", ".join(f"Path({item!r})" for item in EXPECTED_SOURCE_RELS)}]
REQUIRED_PARITY_KEYS = {{
    \"slab\": (\"null_without_reclaim\", \"alloc_count_after_kmalloc\", \"zero_after_kmalloc\"),
    \"bitmap\": (),
    \"find_bit\": (),
    \"string\": (),
    \"rbtree\": (),
    \"argv_split\": (),
    \"cmdline\": (),
    \"ctype\": (),
    \"hweight\": (),
    \"list_sort\": (),
    \"zalloc\": (),
    \"str_error_r\": (),
    \"vsprintf\": (),
}}
if __name__ == \"__main__\":
    print(\"PHASE1_PARITY=fail\")
    print(\"PHASE1_PARITY_INPUT_ISSUES_START\")
"""
    parity_script += "\n".join(f'    print({line!r})' for line in EXPECTED_MISSING_INPUT_ISSUES)
    parity_script += """
    print("PHASE1_PARITY_INPUT_ISSUES_END")
    raise SystemExit(1)
"""
    write_text(root / PARITY_REL, parity_script)

    write_text(
        root / BLOCKERS_REL,
        json.dumps(
            {
                "replay": {"blockers": [EXPECTED_REPLAY_BLOCKER]},
                "c_harness": EXPECTED_C_HARNESS,
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / FIXTURE_REL,
        json.dumps({"slab": {"zero_after_kmalloc": True}}, indent=2) + "\n",
    )


def mutate_json(path: Path, mutate) -> None:
    payload = load_json(path)
    assert isinstance(payload, dict)
    mutate(payload)
    write_text(path, json.dumps(payload, indent=2) + "\n")


def run_self_test() -> int:
    cases = (
        ("success", None, False),
        (
            "fixture_rel_drift",
            lambda root: write_text(
                root / PARITY_REL,
                (root / PARITY_REL).read_text(encoding="utf-8").replace(
                    EXPECTED_FIXTURE_REL.as_posix(), "zigux/tests/fixtures/drift.json", 1
                ),
            ),
            True,
        ),
        (
            "source_list_drift",
            lambda root: write_text(
                root / PARITY_REL,
                (root / PARITY_REL).read_text(encoding="utf-8").replace(
                    "tools/lib/slab.c", "tools/lib/slab.cc", 1
                ),
            ),
            True,
        ),
        (
            "blocked_field_drift",
            lambda root: mutate_json(
                root / BLOCKERS_REL,
                lambda payload: payload["replay"]["blockers"][0].__setitem__(  # type: ignore[index]
                    "field", "slab.drift"
                ),
            ),
            True,
        ),
        (
            "fixture_value_drift",
            lambda root: mutate_json(
                root / FIXTURE_REL,
                lambda payload: payload["slab"].__setitem__("zero_after_kmalloc", False),  # type: ignore[index]
            ),
            True,
        ),
        (
            "runtime_output_drift",
            lambda root: write_text(
                root / PARITY_REL,
                (root / PARITY_REL).read_text(encoding="utf-8").replace(
                    EXPECTED_MISSING_INPUT_ISSUES[-1],
                    "missing:tools/lib/zalloc.cc",
                    1,
                ),
            ),
            True,
        ),
    )

    for case_name, mutate, should_fail in cases:
        with tempfile.TemporaryDirectory(prefix="phase1_parity_blocker_contract_") as tmpdir:
            sample_root = Path(tmpdir)
            build_sample_root(sample_root)
            if mutate is not None:
                mutate(sample_root)
            issues = collect_issues(sample_root)
            if should_fail and not issues:
                raise AssertionError(f"{case_name}: expected failure")
            if not should_fail and issues:
                raise AssertionError(f"{case_name}: unexpected issues: {issues}")

    print("PHASE1_PARITY_BLOCKER_CONTRACT_SELF_TEST=pass")
    print(f"PHASE1_PARITY_BLOCKER_CONTRACT_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = Path(args.root).resolve() if args.root else ROOT
    issues = collect_issues(root)
    if issues:
        print("PHASE1_PARITY_BLOCKER_CONTRACT=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE1_PARITY_BLOCKER_CONTRACT=pass")
    print(f"PHASE1_PARITY_BLOCKER_CONTRACT_REQUIRED_FILE_COUNT={len(EXPECTED_REQUIRED_FILES)}")
    print(f"PHASE1_PARITY_BLOCKER_CONTRACT_SOURCE_REL_COUNT={len(EXPECTED_SOURCE_RELS)}")
    print(f"PHASE1_PARITY_BLOCKER_CONTRACT_MISSING_INPUT_COUNT={len(EXPECTED_MISSING_INPUT_ISSUES)}")
    print(
        f"PHASE1_PARITY_BLOCKER_CONTRACT_BLOCKED_FIELD={EXPECTED_REPLAY_BLOCKER['field']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
