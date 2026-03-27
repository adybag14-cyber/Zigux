#!/usr/bin/env python3
import argparse
import shutil
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description='Check local Zig toolchain availability for Zigux bootstrap work.')
    parser.add_argument('--min-version', default='0.16.0', help='Minimum recommended Zig version string.')
    parser.add_argument('--allow-missing', action='store_true', help='Return success when zig is unavailable.')
    args = parser.parse_args()

    zig = shutil.which('zig')
    if zig is None:
        message = 'zig not found on PATH'
        if args.allow_missing:
            print(f'ZIG_TOOLCHAIN_STATUS=missing')
            print(f'ZIG_TOOLCHAIN_NOTE={message}')
            return 0
        print(message, file=sys.stderr)
        return 1

    result = subprocess.run([zig, 'version'], capture_output=True, text=True, check=True)
    version = result.stdout.strip()
    print(f'ZIG_TOOLCHAIN_STATUS=present')
    print(f'ZIG_TOOLCHAIN_PATH={zig}')
    print(f'ZIG_TOOLCHAIN_VERSION={version}')
    print(f'ZIG_TOOLCHAIN_MIN_RECOMMENDED={args.min_version}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
