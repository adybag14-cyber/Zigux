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


def read_packet_checker_tuple(root: Path) -> tuple[str, ...]:
    source = (root / VALIDATOR_PATH).read_text(encoding="utf-8")
    module = ast.parse(source, filename=str(VALIDATOR_PATH))
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "PHASE12_PACKET_CHECKERS":
                value = ast.literal_eval(node.value)
                if not isinstance(value, tuple):
                    raise ValueError("PHASE12_PACKET_CHECKERS is not a tuple")
                if not all(isinstance(item, str) for item in value):
                    raise ValueError("PHASE12_PACKET_CHECKERS contains a non-string entry")
                return value
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


def write_fixture_root(root: Path, packet_checkers: tuple[str, ...]) -> None:
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

    print("PHASE12_VIRTIO_SCSI_VALIDATOR_PACKET_SELF_TEST=pass")
    print("PHASE12_VIRTIO_SCSI_VALIDATOR_PACKET_SELF_TEST_CASE_COUNT=4")
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
