#!/usr/bin/env python3
"""Guard review-status wording for the Phase 2 cross-target fixture."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
MAKEFILE = ROOT / "zigux" / "Makefile"
ROUTE = "make -C zigux phase2-cross"
MAKE_TARGET = "phase2-cross:"
MODE_STATUS = {
    "archive_required": "pinned bootstrap archive",
    "route_contract_only": "route contract only",
}
EXPECTED_SELF_TEST_CASE_COUNT = 8


def text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def load(path: Path) -> object:
    return json.loads(text(path))


def at(root: Path, path: Path) -> Path:
    return root / path.relative_to(ROOT)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def archive_scope(root: Path) -> list[str]:
    payload = load(at(root, POLICY))
    if not isinstance(payload, dict) or not isinstance(payload.get("upgrade_policy"), dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {at(root, POLICY)}")
    values = payload["upgrade_policy"].get("archive_target_scope")
    if not isinstance(values, list) or not values:
        raise SystemExit(f"invalid archive_target_scope in required file: {at(root, POLICY)}")
    seen: set[str] = set()
    normalized: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(f"invalid archive_target_scope in required file: {at(root, POLICY)}")
        target = value.strip()
        if target in seen:
            raise SystemExit(f"duplicate archive_target_scope entry in required file: {at(root, POLICY)}")
        seen.add(target)
        normalized.append(target)
    return normalized


def issues(root: Path) -> list[tuple[str, str]]:
    scope = archive_scope(root)
    scope_set = set(scope)
    fixture = load(at(root, FIXTURE))
    makefile = text(at(root, MAKEFILE))
    out: list[tuple[str, str]] = []
    if not any(line.strip() == MAKE_TARGET for line in makefile.splitlines()):
        out.append(("MISSING_PHASE2_CROSS_TARGET", MAKE_TARGET))
    if not isinstance(fixture, dict):
        return [("INVALID_CROSS_TARGET_FIXTURE", type(fixture).__name__)]
    if fixture.get("route") != ROUTE:
        out.append(("INVALID_FIXTURE_ROUTE", str(fixture.get("route"))))
    if fixture.get("archive_target_scope") != scope:
        out.append(("ARCHIVE_SCOPE_MISMATCH", ",".join(scope)))
    entries = fixture.get("cross_targets")
    if not isinstance(entries, list) or not entries:
        return out + [("INVALID_CROSS_TARGETS", type(entries).__name__)]
    seen: set[str] = set()
    archive_required: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            out.append(("INVALID_CROSS_TARGET_ENTRY", f"index={index}"))
            continue
        target = entry.get("target")
        mode = entry.get("validation_mode")
        status = entry.get("review_status")
        if not isinstance(target, str) or not target.strip():
            out.append(("INVALID_CROSS_TARGET_ENTRY", f"index={index}:target"))
            continue
        target = target.strip()
        if target in seen:
            out.append(("DUPLICATE_CROSS_TARGET", target))
        seen.add(target)
        if entry.get("route") != ROUTE:
            out.append(("INVALID_CROSS_TARGET_ROUTE", target))
        if mode not in MODE_STATUS:
            out.append(("INVALID_VALIDATION_MODE", target))
            continue
        if status != MODE_STATUS[mode]:
            out.append(("INVALID_REVIEW_STATUS", f"{target}:{status!r}"))
        if mode == "archive_required":
            archive_required.add(target)
            if target not in scope_set:
                out.append(("ARCHIVE_REQUIRED_TARGET_NOT_PINNED", target))
        elif target in scope_set:
            out.append(("PINNED_TARGET_NOT_ARCHIVE_REQUIRED", target))
    if archive_required != scope_set:
        out.append(("ARCHIVE_REQUIRED_TARGET_SET_MISMATCH", ",".join(sorted(archive_required))))
    return out


def seed(root: Path) -> None:
    write(at(root, POLICY), '{"upgrade_policy":{"archive_target_scope":["x86_64-linux"]}}\n')
    write(at(root, MAKEFILE), f"{MAKE_TARGET}\n")
    write(
        at(root, FIXTURE),
        json.dumps(
            {
                "route": ROUTE,
                "archive_target_scope": ["x86_64-linux"],
                "cross_targets": [
                    {"target": "x86_64-linux", "review_status": "pinned bootstrap archive", "validation_mode": "archive_required", "route": ROUTE},
                    {"target": "aarch64-linux", "review_status": "route contract only", "validation_mode": "route_contract_only", "route": ROUTE},
                ],
            },
            indent=2,
        )
        + "\n",
    )


def mutate(root: Path, fn) -> None:
    path = at(root, FIXTURE)
    payload = load(path)
    fn(payload)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def self_test() -> int:
    checks = 0
    cases = (
        (lambda p: p["cross_targets"][0].update(review_status="route contract only"), ("INVALID_REVIEW_STATUS", "x86_64-linux:'route contract only'")),
        (lambda p: p["cross_targets"][0].update(validation_mode="route_contract_only"), ("PINNED_TARGET_NOT_ARCHIVE_REQUIRED", "x86_64-linux")),
        (lambda p: p["cross_targets"][1].update(validation_mode="archive_required"), ("ARCHIVE_REQUIRED_TARGET_NOT_PINNED", "aarch64-linux")),
        (lambda p: p.update(archive_target_scope=["aarch64-linux"]), ("ARCHIVE_SCOPE_MISMATCH", "x86_64-linux")),
        (lambda p: p["cross_targets"].append(dict(p["cross_targets"][0])), ("DUPLICATE_CROSS_TARGET", "x86_64-linux")),
        (lambda p: p["cross_targets"][1].update(route="make -C zigux phase2"), ("INVALID_CROSS_TARGET_ROUTE", "aarch64-linux")),
    )
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_review_status_") as tmp:
        root = Path(tmp)
        seed(root)
        assert issues(root) == []
        checks += 1
        for fn, expected in cases:
            seed(root)
            mutate(root, fn)
            assert expected in issues(root)
            checks += 1
        seed(root)
        at(root, MAKEFILE).write_text("phase2:\n", encoding="utf-8")
        assert ("MISSING_PHASE2_CROSS_TARGET", MAKE_TARGET) in issues(root)
        checks += 1
    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_REVIEW_STATUS_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_REVIEW_STATUS_CONTRACT_SELF_TEST_CASE_COUNT={checks}")
    return 0


def emit(found: list[tuple[str, str]]) -> int:
    print("PHASE2_CROSS_REVIEW_STATUS_CONTRACT=fail")
    for code, value in found:
        print(f"{code}: {value}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    root = args.root.resolve()
    found = issues(root)
    if found:
        return emit(found)
    entries = load(at(root, FIXTURE))["cross_targets"]
    print("PHASE2_CROSS_REVIEW_STATUS_CONTRACT=pass")
    print(f"PHASE2_CROSS_REVIEW_STATUS_CONTRACT_TARGET_COUNT={len(entries)}")
    print(f"PHASE2_CROSS_REVIEW_STATUS_CONTRACT_ARCHIVE_SCOPE_COUNT={len(archive_scope(root))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
