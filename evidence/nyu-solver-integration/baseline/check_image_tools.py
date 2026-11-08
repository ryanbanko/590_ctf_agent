"""Explicit image-evaluation checks; not part of default toolkit requirements.

Run this file explicitly with pytest and --ctf-config for the candidate image.
Only benign synthetic programs are analyzed; no benchmark files are loaded.
"""

import json

import pytest

from .test_controls import python_command

pytestmark = pytest.mark.docker


def test_supplied_sudo_cannot_elevate(attempt):
    assert attempt['call_tool']('run_command', {'command': 'command -v sudo'})['stdout'].strip()
    result = attempt['call_tool']('run_command', {'command': 'sudo -n id'})
    assert result['exit_code'] != 0 and 'uid=0' not in result['stdout'], result
    assert attempt['call_tool']('run_command', {'command': 'id -u'})['stdout'].strip() == '1000'


def test_sage_arithmetic_and_linear_algebra(attempt):
    result = attempt['call_tool']('run_command', {
        'command': 'sage -c "assert list(factor(360)) == [(2,3),(3,2),(5,1)]; '
                   'assert matrix(QQ,[[1,2],[3,4]]).det() == -2; print(\'sage-ok\')"'})
    assert result['exit_code'] == 0 and 'sage-ok' in result['stdout'], result


def test_multilib_compilation_and_execution(attempt):
    result = attempt['call_tool']('run_command', python_command('''
import pathlib, subprocess
pathlib.Path('benign32.c').write_text('int main(void){return 0;}')
subprocess.run(['gcc','-m32','-o','benign32','benign32.c'],check=True)
assert pathlib.Path('benign32').read_bytes()[:5]==b'\\x7fELF\\x01'
subprocess.run(['./benign32'],check=True)
print('multilib-ok')
'''))
    assert result['exit_code'] == 0 and result['stdout'].strip() == 'multilib-ok', result


def test_radare2_binary_analysis(attempt):
    result = attempt['call_tool']('run_command', python_command('''
import json, pathlib, subprocess
pathlib.Path('benign.c').write_text('int choose(int x){return x==7?42:0;} int main(void){return 0;}')
subprocess.run(['gcc','-O0','-o','benign','benign.c'],check=True)
output=subprocess.check_output(['radare2','-2','-q','-c','aaa;aflj','benign'],text=True)
functions=json.loads(output)
assert any(f['name']=='main' or f['name'].endswith('.main') for f in functions)
print(json.dumps({'function_count':len(functions),'main_found':True}))
'''))
    assert result['exit_code'] == 0, result
    assert json.loads(result['stdout'])['main_found']


def test_angr_symbolic_function(attempt):
    result = attempt['call_tool']('run_command', python_command('''
import angr, claripy, json, pathlib, subprocess
pathlib.Path('benign.c').write_text('int choose(int x){return x==7?42:0;} int main(void){return 0;}')
subprocess.run(['gcc','-O0','-fno-pie','-no-pie','-o','benign','benign.c'],check=True)
project=angr.Project('benign',auto_load_libs=False)
value=claripy.BVS('value',32)
state=project.factory.call_state(project.loader.find_symbol('choose').rebased_addr,value,
    ret_addr=0xdeadbeef,prototype='int choose(int)',
    add_options={angr.options.ZERO_FILL_UNCONSTRAINED_REGISTERS,
                 angr.options.ZERO_FILL_UNCONSTRAINED_MEMORY})
simulation=project.factory.simgr(state)
simulation.explore(find=lambda s: s.addr==0xdeadbeef and
    s.solver.satisfiable(extra_constraints=[s.regs.eax==42]))
assert simulation.found
found=simulation.found[0]; found.solver.add(found.regs.eax==42)
assert found.solver.eval(value)==7
print(json.dumps({'angr':angr.__version__,'symbolic_result':7}))
'''))
    assert result['exit_code'] == 0, result
    assert json.loads(result['stdout'])['symbolic_result'] == 7
