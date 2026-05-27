#!/usr/bin/env python3
"""Fail closed on the Phase 12 virtio_scsi validator contract."""

from __future__ import annotations

import argparse
import ast
import sys
import tempfile
from pathlib import Path

VALIDATOR_PATH = Path("scripts/zigux/validate-phase12.py")

REQUIRED_VIRTIO_SCSI_CHECKERS = (
    "scripts/zigux/check-phase12-virtio-scsi-packet.py",
    "scripts/zigux/check-phase12-virtio-scsi-libbpf-boundary.py",
    "scripts/zigux/check-phase12-virtio-scsi-rollback-coverage.py",
    "scripts/zigux/check-phase12-virtio-scsi-repeated-rollback-packet.py",
)


def collect_string_assignments(module: ast.Module) -> dict[str, str]:
    values: dict[str, str] = {}
    for node in module.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        value = node.value
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            values[target.id] = value.value
    return values


def resolve_packet_checker_tuple(
    value: ast.AST, string_assignments: dict[str, str]
) -> tuple[str, ...]:
    if not isinstance(value, ast.Tuple):
        raise ValueError("PHASE12_PACKET_CHECKERS is not a tuple")

    resolved: list[str] = []
    for item in value.elts:
        if isinstance(item, ast.Constant) and isinstance(item.value, str):
            resolved.append(item.value)
            continue
        if isinstance(item, ast.Name) and item.id in string_assignments:
            resolved.append(string_assignments[item.id])
            continue
        raise ValueError(
            "PHASE12_PACKET_CHECKERS contains an unsupported entry: "
            f"{ast.dump(item, include_attributes=False)}"
        )
    return tuple(resolved)


def read_packet_checker_tuple(root: Path) -> tuple[str, ...]:
    source = (root / VALIDATOR_PATH).read_text(encoding="utf-8")
    module = ast.parse(source, filename=str(VALIDATOR_PATH))
    string_assignments = collect_string_assignments(module)
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "PHASE12_PACKET_CHECKERS":
                return resolve_packet_checker_tuple(node.value, string_assignments)
    raise ValueError("PHASE12_PACKET_CHECKERS assignment missing")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    validator = root / VALIDATOR_PATH
    if not validator.is_file():
        return [f"missing required file: {VALIDATOR_PATH}"]

    for relative_path in REQUIRED_VIRTIO_SCSI_CHECKERS:
        if not (root / relative_path).is_file():
            errors.append(f"missing required checker file: {relative_path}")

    try:
        packet_checkers = read_packet_checker_tuple(root)
    except (SyntaxError, ValueError) as exc:
        errors.append(f"validator contract parse failure: {exc}")
        return errors

    for relative_path in REQUIRED_VIRTIO_SCSI_CHECKERS:
        count = packet_checkers.count(relative_path)
        if count != 1:
            errors.append(
                "validator checker tuple drift: "
                f"{relative_path} expected once, found {count}"
            )

    positions = [
        packet_checkers.index(path)
        for path in REQUIRED_VIRTIO_SCSI_CHECKERS
        if path in packet_checkers
    ]
    if len(positions) == len(REQUIRED_VIRTIO_SCSI_CHECKERS):
        if positions != sorted(positions):
            errors.append("validator checker tuple drift: virtio_scsi checker order changed")
        if positions[-1] - positions[0] != len(REQUIRED_VIRTIO_SCSI_CHECKERS) - 1:
            errors.append(
                "validator checker tuple drift: virtio_scsi checker block is no longer contiguous"
            )

    return errors


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_fixture_root(
    root: Path, packet_checkers: tuple[str, ...], *, use_names: bool = False
) -> None:
    if use_names:
        constant_lines: list[str] = []
        tuple_lines: list[str] = []
        for index, item in enumerate(packet_checkers):
            name = f"CHECKER_{index}"
            constant_lines.append(f'{name} = "{item}"')
            tuple_lines.append(f"    {name},")
        validator_source = (
            "\n".join(constant_lines)
            + "\nPHASE12_PACKET_CHECKERS = (\n"
            + "\n".join(tuple_lines)
            + "\n)\n"
        )
    else:
        validator_source = (
            "PHASE12_PACKET_CHECKERS = (\n"
            + "".join(f'    "{item}",\n' for item in packet_checkers)
            + ")\n"
        )
    write_text(root / VALIDATOR_PATH, validator_source)
    for relative_path in REQUIRED_VIRTIO_SCSI_CHECKERS:
        write_text(root / relative_path, "#!/usr/bin/env python3\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase12-virtio-scsi-validator-") as tmp:
        root = Path(tmp)
        write_fixture_root(root, REQUIRED_VIRTIO_SCSI_CHECKERS)
        errors = validate(root)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            print("PHASE12_VIRTIO_SCSI_VALIDATOR_PACKET_SELF_TEST=fail")
            return 1

        named_root = root / "named"
        write_fixture_root(named_root, REQUIRED_VIRTIO_SCSI_CHECKERS, use_names=True)
        named_errors = validate(named_root)
        if named_errors:
            for error in named_errors:
                print(error, file=sys.stderr)
            print("PHASE12_VIRTIO_SCSI_VALIDATOR_PACKET_SELF_TEST=fail")
            return 1

        missing_root = root / "missing"
        write_fixture_root(missing_root, REQUIRED_VIRTIO_SCSI_CHECKERS[:-1])
        missing_errors = validate(missing_root)
        expected_missing = (
            "validator checker tuple drift: "
            "scripts/zigux/check-phase12-virtio-scsi-repeated-rollback-packet.py expected once, found 0"
        )
        if expected_missing not in missing_errors:
            print("self-test did not catch missing repeated-rollback checker", file=sys.stderr)
            print("PHASE12_VIRTIO_SCSI_VALIDATOR_PACKET_SELF_TEST=fail")
            return 1

        duplicate_root = root / "duplicate"
        write_fixture_root(
            duplicate_root,
            REQUIRED_VIRTIO_SCSI_CHECKERS
            + ("scripts/zigux/check-phase12-virtio-scsi-rollback-coverage.py",),
        )
        duplicate_errors = validate(duplicate_root)
        expected_duplicate = (
            "validator checker tuple drift: "
            "scripts/zigux/check-phase12-virtio-scsi-rollback-coverage.py expected once, found 2"
        )
        if expected_duplicate not in duplicate_errors:
            print("self-test did not catch duplicated rollback-coverage checker", file=sys.stderr)
            print("PHASE12_VIRTIO_SCSI_VALIDATOR_PACKET_SELF_TEST=fail")
            return 1

        order_root = root / "order"
        write_fixture_root(
            order_root,
            (
                REQUIRED_VIRTIO_SCSI_CHECKERS[1],
                REQUIRED_VIRTIO_SCSI_CHECKERS[0],
                REQUIRED_VIRTIO_SCSI_CHECKERS[2],
                REQUIRED_VIRTIO_SCSI_CHECKERS[3],
            ),
        )
        order_errors = validate(order_root)
        if "validator checker tuple drift: virtio_scsi checker order changed" not in order_errors:
            print("self-test did not catch checker order drift", file=sys.stderr)
            print("PHASE12_VIRTIO_SCSI_VALIDATOR_PACKET_SELF_TEST=fail")
            return 1

        noncontiguous_root = root / "noncontiguous"
        write_fixture_root(
            noncontiguous_root,
            (
                REQUIRED_VIRTIO_SCSI_CHECKERS[0],
                "scripts/zigux/check-build-only-phase12-surface.py",
                REQUIRED_VIRTIO_SCSI_CHECKERS[1],
                REQUIRED_VIRTIO_SCSI_CHECKERS[2],
                REQUIRED_VIRTIO_SCSI_CHECKERS[3],
            ),
        )
        noncontiguous_errors = validate(noncontiguous_root)
        if (
            "validator checker tuple drift: virtio_scsi checker block is no longer contiguous"
            not in noncontiguous_errors
        ):
            print("self-test did not catch checker contiguity drift", file=sys.stderr)
            print("PHASE12_VIRTIO_SCSI_VALIDATOR_PACKET_SELF_TEST=fail")
            return 1

    print("PHASE12_VIRTIO_SCSI_VALIDATOR_PACKET_SELF_TEST=pass")
    print("PHASE12_VIRTIO_SCSI_VALIDATOR_PACKET_SELF_TEST_CASE_COUNT=6")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = validate(Path(args.root))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("Phase 12 virtio_scsi validator packet check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
