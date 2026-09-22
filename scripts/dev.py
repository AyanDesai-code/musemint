#!/usr/bin/env python3
"""Dependency-free local tooling; no application build is implied."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def run(*args):
    subprocess.run(args, cwd=ROOT, check=True)


def compose(*args):
    if not (ROOT / '.env').is_file():
        raise RuntimeError('Missing .env; run python3 scripts/dev.py setup')
    run('docker', 'compose', '--env-file', '.env', '-f', 'compose.yaml', *args)


def setup():
    target = ROOT / '.env'
    try:
        with target.open('x', encoding='utf-8') as output:
            output.write((ROOT / '.env.example').read_text(encoding='utf-8'))
        target.chmod(0o600)
        print('Created .env with disposable local defaults.')
    except FileExistsError:
        print('Kept existing .env unchanged.')


def chain_ready():
    request = Request('http://127.0.0.1:8545', data=json.dumps({
        'jsonrpc': '2.0', 'id': 1, 'method': 'eth_chainId', 'params': []
    }).encode(), headers={'Content-Type': 'application/json'})
    with urlopen(request, timeout=2) as response:
        result = json.load(response)
    if result.get('result') != '0x7a69':
        raise ValueError('Local RPC must report chain ID 31337')


def smoke():
    # Temporary table verifies SQL writes without touching application data.
    compose('exec', '-T', 'db', 'psql', '-U', 'musemint', '-d', 'musemint',
            '-v', 'ON_ERROR_STOP=1', '-c',
            'BEGIN; CREATE TEMP TABLE dev_smoke (id integer PRIMARY KEY); '
            'INSERT INTO dev_smoke VALUES (1); SELECT * FROM dev_smoke; ROLLBACK;')
    for attempt in range(30):
        try:
            chain_ready()
            print('PostgreSQL read/write and local EVM chain ID checks passed.')
            return
        except (URLError, OSError, ValueError):
            if attempt == 29:
                raise RuntimeError('Local EVM did not become ready on port 8545') from None
            time.sleep(1)


def build():
    run(sys.executable, '-m', 'compileall', '-q', 'scripts', 'tests')


def test():
    run(sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=[
        'setup', 'doctor', 'build', 'test', 'check', 'up', 'down', 'status', 'smoke'])
    args = parser.parse_args(argv)
    try:
        if args.command == 'setup':
            setup()
        elif args.command == 'doctor':
            if sys.version_info < (3, 12):
                raise RuntimeError('Python 3.12 or newer required; CI uses 3.12')
            for tool in ('git', 'docker'):
                if shutil.which(tool) is None:
                    raise RuntimeError(f'Install {tool} before starting local services')
            run('docker', 'compose', 'version')
            run('docker', 'info', '--format', '{{.ServerVersion}}')
            print('Local prerequisites available.')
        elif args.command == 'build':
            build()
        elif args.command == 'test':
            test()
        elif args.command == 'check':
            build()
            test()
            run(sys.executable, 'scripts/check_docs.py')
            run('git', 'diff', '--check')
            run('git', 'diff', '--cached', '--check')
        elif args.command == 'up':
            compose('up', '-d', '--wait', '--wait-timeout', '90')
            smoke()
        elif args.command == 'down':
            compose('down')  # Deliberately retain the database volume.
        elif args.command == 'status':
            compose('ps')
        elif args.command == 'smoke':
            smoke()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f'dev: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
