#!/usr/bin/env python3
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verify = load("verify-kernel-packages").verify
check = load("check-media-boot").check
SHA = "1" * 40


class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for profile in ("allmodconfig", "allyesconfig"):
            name = f"linux-zigux-{profile}-7.3-1-x86_64.pkg.tar.zst"
            release = f"7.3.0-zigux-{profile}-g{SHA[:12]}"
            (self.root / name).write_bytes(profile.encode())
            (self.root / f"kernel-release-{profile}.txt").write_text(release)
            (self.root / f"QEMU_KERNEL_RESULT-{profile}").write_text("success\n")
            (self.root / f"kernel-source-{profile}.json").write_text(json.dumps({
                "profile": profile, "source_sha": SHA, "package": name,
                "kernel_release": release, "direct_boot_passed": True,
                "package_sha256": hashlib.sha256(profile.encode()).hexdigest(),
            }))

    def test_matching_packages_pass(self):
        self.assertEqual(len(verify(self.root, SHA)), 2)

    def test_stale_source_is_rejected(self):
        with self.assertRaises(ValueError):
            verify(self.root, "2" * 40)

    def test_tampered_package_is_rejected(self):
        next(self.root.glob("*.pkg.tar.zst")).write_bytes(b"modified")
        with self.assertRaises(ValueError):
            verify(self.root, SHA)

    def test_failed_kernel_smoke_is_rejected(self):
        (self.root / "QEMU_KERNEL_RESULT-allmodconfig").write_text("failed")
        with self.assertRaises(ValueError):
            verify(self.root, SHA)

    def test_extra_package_is_rejected(self):
        (self.root / "linux-zigux-stale.pkg.tar.zst").write_bytes(b"stale")
        with self.assertRaises(ValueError):
            verify(self.root, SHA)

    def test_missing_provenance_is_rejected(self):
        (self.root / "kernel-source-allmodconfig.json").unlink()
        with self.assertRaises(FileNotFoundError):
            verify(self.root, SHA)

    def test_boot_marker_requires_correct_kernel(self):
        release = f"7.3.0-zigux-allmodconfig-g{SHA[:12]}"
        check(f"ZIGUX_CACHYOS_KERNEL={release}\nZIGUX_CACHYOS_MEDIA_BOOT_OK", release)
        for log in ("ZIGUX_CACHYOS_MEDIA_BOOT_OK",
                    "ZIGUX_CACHYOS_KERNEL=6.18.50-cachyos-lts\nZIGUX_CACHYOS_MEDIA_BOOT_OK",
                    f"ZIGUX_CACHYOS_KERNEL={release}"):
            with self.subTest(log=log), self.assertRaises(ValueError):
                check(log, release)


if __name__ == "__main__":
    unittest.main()
