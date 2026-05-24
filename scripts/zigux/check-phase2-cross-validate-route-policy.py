#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-contract.py"
POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"

TUPLE_RE = re.compile(
    r"EXPECTED_REQUIRED_MAKE_ROUTES\s*=\s*\(\n(?P<body>.*?)\n\)",
    re.DOTALL,
)
STRING_RE = re.compile(r'"(?P<value>[^"\n]+)"')


class DuplicateJsonKeyError(ValueError):
    pass


def reject_duplicate_object_pairs(pairs: list[tuple[object, object]]) -> dict[object, object]:
    payload: dict[object, object] = {}
    for key, value in pairs:
        if key in payload:
            raise DuplicateJsonKeyError(str(key))
        payload[key] = value
    return payload


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path), object_pairs_hook=reject_duplicate_object_pairs)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    except DuplicateJsonKeyError as exc:
        raise SystemExit(f"duplicate json key in required file: {path}: {exc}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def load_policy_routes(root: Path) -> list[str]:
    policy_path = resolve_path(root, POLICY)
    payload = read_json(policy_path)
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {policy_path}")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {policy_path}")
    routes = upgrade_policy.get("required_make_routes")
    if not isinstance(routes, list) or not routes:
        raise SystemExit(f"invalid required_make_routes in required file: {policy_path}")
    normalized: list[str] = []
    seen: set[str] = set()
    for value in routes:
        if not isinstance(value, str) or not value or value != value.strip():
            raise SystemExit(f"invalid required_make_routes in required file: {policy_path}")
        if value in seen:
            raise SystemExit(f"duplicate required_make_routes entry in required file: {policy_path}: {value}")
        normalized.append(value)
        seen.add(value)
    return normalized


def load_checker_routes(root: Path) -> list[str]:
    checker_path = resolve_path(root, CHECKER)
    text = read_text(checker_path)
    match = TUPLE_RE.search(text)
    if match is None:
        raise SystemExit(f"missing EXPECTED_REQUIRED_MAKE_ROUTES tuple in required file: {checker_path}")
    values = STRING_RE.findall(match.group("body"))
    if not values:
        raise SystemExit(f"empty EXPECTED_REQUIRED_MAKE_ROUTES tuple in required file: {checker_path}")
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            raise SystemExit(f"duplicate EXPECTED_REQUIRED_MAKE_ROUTES entry in required file: {checker_path}: {value}")
        normalized.append(value)
        seen.add(value)
    return normalized


def run_check(root: Path) -> int:
    policy_routes = load_policy_routes(root)
    checker_routes = load_checker_routes(root)
    if checker_routes != policy_routes:
        print("PHASE2_CROSS_VALIDATE_ROUTE_POLICY=fail")
        print(f"PHASE2_CROSS_VALIDATE_ROUTE_POLICY_CHECKER_ROUTES={','.join(checker_routes)}")
        print(f"PHASE2_CROSS_VALIDATE_ROUTE_POLICY_POLICY_ROUTES={','.join(policy_routes)}")
        return 1
    print("PHASE2_CROSS_VALIDATE_ROUTE_POLICY=pass")
    print(f"PHASE2_CROSS_VALIDATE_ROUTE_POLICY_ROUTE_COUNT={len(policy_routes)}")
    print(f"PHASE2_CROSS_VALIDATE_ROUTE_POLICY_ROUTES={','.join(policy_routes)}")
    return 0


def build_self_test_root(root: Path, checker_routes: list[str], policy_routes: list[str]) -> None:
    tuple_body = "\n".join(f'    "{route}",' for route in checker_routes)
    write_text(
        resolve_path(root, CHECKER),
        "\n".join(
            (
                "#!/usr/bin/env python3",
                "EXPECTED_REQUIRED_MAKE_ROUTES = (",
                tuple_body,
                ")",
                "",
            )
        ),
    )
    write_text(
        resolve_path(root, POLICY),
        json.dumps(
            {
                "upgrade_policy": {
                    "required_make_routes": policy_routes,
                }
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_validate_route_policy_") as tmp_dir:
        root = Path(tmp_dir)
        expected = [
            "phase2-toolchain",
            "phase2-tools",
            "phase2-kconfig",
            "phase2-cross",
            "phase2-genksyms",
            "phase2-fixdep",
            "phase2-validate",
        ]

        build_self_test_root(root, expected, expected)
        assert run_check(root) == 0
        checks += 1

        build_self_test_root(root, ["phase2-toolchain", "phase2-tools", "phase2-cross", "phase2-validate"], expected)
        assert run_check(root) == 1
        checks += 1

        build_self_test_root(root, ["phase2-toolchain", "phase2-tools", "phase2-kconfig", "phase2-validate", "phase2-cross", "phase2-genksyms", "phase2-fixdep"], expected)
        assert run_check(root) == 1
        checks += 1

        build_self_test_root(root, ["phase2-toolchain", "phase2-tools", "phase2-kconfig", "phase2-cross", "phase2-genksyms", "phase2-fixdep", "phase2-kconfig"], expected)
        try:
            run_check(root)
        except SystemExit as exc:
            assert "duplicate EXPECTED_REQUIRED_MAKE_ROUTES entry" in str(exc)
            checks += 1
        else:
            raise AssertionError("duplicate checker routes did not abort")

        build_self_test_root(root, expected, ["phase2-toolchain", "phase2-tools", "phase2-kconfig", "phase2-cross", "phase2-genksyms", "phase2-fixdep", "phase2-kconfig"])
        try:
            run_check(root)
        except SystemExit as exc:
            assert "duplicate required_make_routes entry" in str(exc)
            checks += 1
        else:
            raise AssertionError("duplicate policy routes did not abort")

        build_self_test_root(root, expected, expected)
        resolve_path(root, CHECKER).write_text("#!/usr/bin/env python3\n", encoding="utf-8")
        try:
            run_check(root)
        except SystemExit as exc:
            assert "missing EXPECTED_REQUIRED_MAKE_ROUTES tuple" in str(exc)
            checks += 1
        else:
            raise AssertionError("missing tuple did not abort")

        build_self_test_root(root, expected, expected)
        resolve_path(root, POLICY).write_text("{\n", encoding="utf-8")
        try:
            run_check(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
            checks += 1
        else:
            raise AssertionError("invalid policy json did not abort")

    print("PHASE2_CROSS_VALIDATE_ROUTE_POLICY_SELF_TEST=pass")
    print(f"PHASE2_CROSS_VALIDATE_ROUTE_POLICY_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 21 cross validate-contract route tuple aligned with the live Phase 2 toolchain policy."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    return run_check(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
