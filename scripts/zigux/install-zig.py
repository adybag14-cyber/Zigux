#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import tarfile
import tempfile
import urllib.request
import zipfile


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY = ROOT / 'scripts' / 'zigux' / 'zig-toolchain-policy.json'
INDEX_URL = 'https://ziglang.org/download/index.json'


def normalize_os(name: str) -> str:
    lowered = name.lower()
    if lowered.startswith('linux'):
        return 'linux'
    if lowered.startswith('darwin') or lowered.startswith('mac'):
        return 'macos'
    if lowered.startswith('windows'):
        return 'windows'
    raise SystemExit(f'unsupported OS for Zig installer: {name}')


def normalize_arch(name: str) -> str:
    lowered = name.lower()
    if lowered in {'amd64', 'x86_64', 'x64'}:
        return 'x86_64'
    if lowered in {'arm64', 'aarch64'}:
        return 'aarch64'
    if lowered in {'x86', 'i386', 'i686'}:
        return 'x86'
    raise SystemExit(f'unsupported architecture for Zig installer: {name}')


def parse_policy_data(raw: object) -> tuple[str, str]:
    if not isinstance(raw, dict):
        raise ValueError('toolchain policy must be a JSON object')

    channel = raw.get('channel')
    minimum_version = raw.get('minimum_version')
    if not isinstance(channel, str) or not channel:
        raise ValueError('toolchain policy must define a non-empty string channel')
    if not isinstance(minimum_version, str) or not minimum_version:
        raise ValueError('toolchain policy must define a non-empty string minimum_version')
    return channel, minimum_version


def load_policy(path: Path) -> tuple[str, str]:
    return parse_policy_data(json.loads(path.read_text(encoding='utf-8')))


def read_index() -> dict:
    with urllib.request.urlopen(INDEX_URL) as response:
        return json.load(response)


def extract_archive(archive_path: Path, dest: Path) -> Path:
    if archive_path.suffix == '.zip':
        with zipfile.ZipFile(archive_path) as zf:
            zf.extractall(dest)
    else:
        with tarfile.open(archive_path, 'r:*') as tf:
            tf.extractall(dest)

    children = [child for child in dest.iterdir() if child.is_dir()]
    if len(children) != 1:
        raise SystemExit(f'unexpected extracted layout in {dest}')
    return children[0]


def append_github_path(path: Path) -> None:
    github_path = os.environ.get('GITHUB_PATH')
    if not github_path:
        return
    with open(github_path, 'a', encoding='utf-8', newline='\n') as fh:
        fh.write(str(path.resolve()) + '\n')


def run_self_test() -> int:
    assert normalize_os('Linux') == 'linux'
    assert normalize_os('Darwin') == 'macos'
    assert normalize_os('Windows_NT') == 'windows'
    assert normalize_arch('x86_64') == 'x86_64'
    assert normalize_arch('amd64') == 'x86_64'
    assert normalize_arch('aarch64') == 'aarch64'
    assert normalize_arch('i686') == 'x86'
    assert parse_policy_data(
        {
            'channel': '0.17.0-dev.87+9b177a7d2',
            'minimum_version': '0.17.0-dev.87+9b177a7d2',
        }
    ) == ('0.17.0-dev.87+9b177a7d2', '0.17.0-dev.87+9b177a7d2')
    try:
        parse_policy_data({'channel': '', 'minimum_version': '0.17.0-dev.87+9b177a7d2'})
    except ValueError:
        pass
    else:
        raise AssertionError('expected invalid toolchain policy to fail')
    print('ZIG_INSTALL_SELF_TEST=pass')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Install Zig from the official Zig download index.')
    parser.add_argument('--channel', help='Channel or version key from ziglang.org/download/index.json')
    parser.add_argument('--policy', help='Toolchain policy JSON path. Defaults to scripts/zigux/zig-toolchain-policy.json.')
    parser.add_argument('--dest', default='.zig-toolchain', help='Install root directory')
    parser.add_argument('--system', help='Override detected OS key (linux, macos, windows)')
    parser.add_argument('--arch', help='Override detected architecture key (x86_64, aarch64, x86)')
    parser.add_argument('--resolve-only', action='store_true', help='Resolve and print the chosen archive without downloading')
    parser.add_argument('--self-test', action='store_true', help='Run built-in policy and platform parser checks.')
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    policy_path = Path(args.policy) if args.policy else DEFAULT_POLICY
    policy_channel = None
    policy_minimum_version = None
    if policy_path.exists():
        try:
            policy_channel, policy_minimum_version = load_policy(policy_path)
        except ValueError as exc:
            raise SystemExit(f'invalid toolchain policy {policy_path}: {exc}')
    elif args.policy:
        raise SystemExit(f'toolchain policy not found: {policy_path}')

    channel = args.channel or policy_channel or 'master'
    system_key = args.system or normalize_os(platform.system())
    arch_key = args.arch or normalize_arch(platform.machine())
    target_key = f'{arch_key}-{system_key}'

    index = read_index()
    if channel not in index:
        raise SystemExit(f'unknown Zig channel/version key: {channel}')
    entry = index[channel]
    if target_key not in entry:
        raise SystemExit(f'Zig download index has no target {target_key} under {channel}')

    target = entry[target_key]
    tarball_url = target['tarball']
    version = entry['version']
    if policy_minimum_version is not None and version != policy_minimum_version:
        raise SystemExit(
            f'policy version drift for {channel}: index resolved {version}, '
            f'expected {policy_minimum_version}'
        )

    print(f'ZIG_INSTALL_CHANNEL={channel}')
    print(f'ZIG_INSTALL_VERSION={version}')
    print(f'ZIG_INSTALL_TARGET={target_key}')
    print(f'ZIG_INSTALL_URL={tarball_url}')
    if policy_channel is not None:
        print(f'ZIG_INSTALL_POLICY={policy_path}')

    if args.resolve_only:
        print('ZIG_INSTALL_STATUS=resolved')
        return 0

    install_root = Path(args.dest)
    install_root.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix='zigux_install_zig_') as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        archive_name = tarball_url.rsplit('/', 1)[-1]
        archive_path = tmpdir / archive_name
        with urllib.request.urlopen(tarball_url) as response, open(archive_path, 'wb') as out:
            shutil.copyfileobj(response, out)

        extracted_root = extract_archive(archive_path, tmpdir / 'extract')
        final_root = install_root / extracted_root.name
        if final_root.exists():
            shutil.rmtree(final_root)
        shutil.copytree(extracted_root, final_root)

    bin_dir = final_root
    if (final_root / 'zig').exists() or (final_root / 'zig.exe').exists():
        bin_dir = final_root
    elif (final_root / 'bin' / 'zig').exists() or (final_root / 'bin' / 'zig.exe').exists():
        bin_dir = final_root / 'bin'
    else:
        raise SystemExit(f'could not locate zig binary in {final_root}')

    append_github_path(bin_dir)
    print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')
    print('ZIG_INSTALL_STATUS=pass')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
