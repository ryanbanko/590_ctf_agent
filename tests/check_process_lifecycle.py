"""Explicit generic Docker diagnostic: no dataset, model, task code or answers."""

import argparse
import json
from pathlib import Path
import subprocess
import time
from types import SimpleNamespace
import uuid

from ctf_agent.challenge import challenge_target
from ctf_agent.docker import docker


CHILD = """import os, resource, signal, sys, time
resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
mode = sys.argv[1]
if mode.startswith('orphan'):
    if os.fork():
        os._exit(0)
    time.sleep(0.4)
print('synthetic-child mode=%s pid=%s ppid=%s' % (mode, os.getpid(), os.getppid()),
      file=sys.stderr, flush=True)
if mode.endswith('signal'):
    os.kill(os.getpid(), signal.SIGSEGV)
"""

CLIENT = """import json, socket, time
rows = []
for number in range(5):
    row = {'number': number + 1}
    try:
        with socket.create_connection(('listener', 8000), 2) as sock:
            row['connected'] = True
            sock.settimeout(2)
            row['eof'] = not sock.recv(1)
    except OSError as error:
        row.update(connected=False, error_type=type(error).__name__, errno=error.errno)
    rows.append(row)
    time.sleep(0.7)
    if not row['connected']:
        break
print(json.dumps(rows))
"""

LIMITS = """import json, pathlib, resource
print(json.dumps({'cgroups': {name: pathlib.Path('/sys/fs/cgroup/' + name).read_text().strip()
    for name in ['memory.max', 'memory.swap.max', 'pids.max', 'cpu.max']},
    'rlimits': {name: resource.getrlimit(getattr(resource, name))
    for name in ['RLIMIT_NOFILE', 'RLIMIT_NPROC', 'RLIMIT_AS']}}))
"""


def inspect_limits(container):
    info = json.loads(docker('inspect', container))[0]
    keys = ['Memory', 'MemorySwap', 'MemoryReservation', 'NanoCpus', 'CpuQuota',
            'CpuPeriod', 'CpusetCpus', 'PidsLimit', 'Ulimits', 'CapAdd', 'CapDrop',
            'SecurityOpt', 'ReadonlyRootfs', 'Privileged', 'Init', 'RestartPolicy']
    return {'host_config': {key: info['HostConfig'].get(key) for key in keys},
            'inside': json.loads(docker('exec', container, 'python', '-I', '-c', LIMITS))}


def state(container):
    info = json.loads(docker('inspect', container))[0]
    return {key: info['State'][key] for key in ['Status', 'Running', 'ExitCode', 'OOMKilled']}


def compare_launcher(image, platform, directory):
    supplied = {'services': {'listener': {'image': image, 'platform': platform,
                 'command': ['python', '-c', 'import time; time.sleep(120)'],
                 'networks': {'ctfnet': {}}}}, 'networks': {'ctfnet': {}}}
    source = directory / 'synthetic-source'
    source.mkdir()
    compose_file = source / 'docker-compose.yml'
    compose_file.write_text(json.dumps(supplied))
    project = 'ctf590-process-direct-' + uuid.uuid4().hex[:8]
    args = ('compose', '-p', project, '-f', str(compose_file.resolve()))
    try:
        docker(*args, 'up', '-d', '--pull', 'never', timeout=30)
        container = docker(*args, 'ps', '-q', 'listener')
        direct = inspect_limits(container)
    finally:
        docker(*args, 'down', '--volumes', '--timeout', '1', timeout=15)
    synthetic = SimpleNamespace(container=True, challenge_dir=source,
                                server_name='listener', port=8000, challenge={})
    with challenge_target(synthetic, directory / 'launcher-target') as target:
        launched = inspect_limits(target['container'])
    return {'direct_compose': direct, 'project_launcher': launched,
            'equal': direct == launched, 'cleanup_errors': target['cleanup_errors']}


def check_case(image, platform, network, mode, init, fork_listener=True):
    name = 'ctf590-process-case-' + uuid.uuid4().hex[:8]
    client = name + '-client'
    result = {'mode': mode, 'init': init, 'platform': platform, 'fork_listener': fork_listener}
    try:
        docker('run', '-d', '--pull', 'never', '--platform', platform, '--name', name,
               '--network', network, '--network-alias', 'listener',
               *(['--init'] if init else []), image,
               'socat', 'TCP-LISTEN:8000,reuseaddr' + (',fork' if fork_listener else ''),
               'EXEC:python /synthetic-child.py ' + mode)
        result['effective_limits'] = inspect_limits(name)
        time.sleep(0.3)
        docker('create', '--pull', 'never', '--platform', platform, '--name', client,
               '--network', network, '--init', '--user', '1000', '--cap-drop', 'ALL',
               '--cap-add', 'CHOWN', '--security-opt', 'no-new-privileges=true',
               '--memory', '1024m', '--memory-swap', '1024m', '--pids-limit', '64',
               '--cpus', '1', image, 'python', '-I', '-c', CLIENT)
        result['probes'] = json.loads(docker('start', '-a', client, timeout=20))
        result['end'] = state(name)
        logs = subprocess.run(['docker', 'logs', name], capture_output=True,
                              text=True, timeout=5, check=True)
        result['generic_logs'] = (logs.stdout + logs.stderr).splitlines()
        return result
    finally:
        docker('rm', '-f', client, name, timeout=15)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--platform', choices=['linux/arm64', 'linux/amd64'], default='linux/arm64')
    parser.add_argument('--output', type=Path, default=Path('runs/process-lifecycle'))
    parser.add_argument('--one-shot-control', action='store_true',
                        help='Only compare deliberately one-connection listeners with/without init')
    args = parser.parse_args()
    directory = args.output / (args.platform.split('/')[-1] + '-' + uuid.uuid4().hex[:8])
    directory.mkdir(parents=True)
    image = 'ctf590-process-diagnostic:' + directory.name
    network = 'ctf590-process-network-' + uuid.uuid4().hex[:8]
    report = {'kind': 'generic_process_diagnostic', 'platform': args.platform,
              'model_calls': 0, 'challenge_code_used': False, 'cases': []}
    context = directory / 'build'
    context.mkdir()
    (context / 'synthetic-child.py').write_text(CHILD)
    (context / 'Dockerfile').write_text('FROM python:3.13.2-slim-bookworm\n'
        'RUN apt-get update && apt-get install -y --no-install-recommends socat '
        '&& rm -rf /var/lib/apt/lists/*\n'
        'COPY synthetic-child.py /synthetic-child.py\n')
    try:
        build = subprocess.run(['docker', 'build', '--platform', args.platform,
                                '-t', image, str(context)], capture_output=True, text=True, timeout=240)
        (directory / 'build.log').write_text(build.stdout + build.stderr)
        build.check_returncode()
        info = json.loads(docker('image', 'inspect', image))[0]
        report.update(image_id=info['Id'], image_architecture=info['Architecture'])
        report['socat_version'] = docker('run', '--rm', '--network', 'none', '--platform',
                                         args.platform, image, 'socat', '-V').splitlines()[:4]
        if not args.one_shot_control:
            report['launcher_comparison'] = compare_launcher(image, args.platform, directory)
            print(json.dumps({'launcher_limits_equal': report['launcher_comparison']['equal']}), flush=True)
        docker('network', 'create', network)
        cases = ([('attached-signal', False), ('attached-signal', True)] if args.one_shot_control
                 else [('attached', False), ('attached-signal', False),
                       ('orphan', False), ('orphan-signal', False), ('orphan-signal', True)])
        for mode, init in cases:
            row = check_case(image, args.platform, network, mode, init,
                             fork_listener=not args.one_shot_control)
            report['cases'].append(row)
            print(json.dumps({'mode': mode, 'init': init, 'end': row['end'],
                              'connections': row['probes']}), flush=True)
    except BaseException as error:
        report['error_type'] = type(error).__name__
        raise
    finally:
        cleanup = subprocess.run(['docker', 'network', 'rm', network], capture_output=True, text=True)
        report['network_cleanup'] = cleanup.returncode == 0 or 'not found' in cleanup.stderr
        cleanup = subprocess.run(['docker', 'image', 'rm', image], capture_output=True, text=True)
        report['image_cleanup'] = cleanup.returncode == 0 or 'No such image' in cleanup.stderr
        (directory / 'check.json').write_text(json.dumps(report, indent=2) + '\n')
        print('Diagnostic records: ' + str(directory), flush=True)


if __name__ == '__main__':
    main()
