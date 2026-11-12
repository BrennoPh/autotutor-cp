"""Deterministic local C++ judge. Resource limits are NOT a security sandbox."""
from contextlib import contextmanager
from pathlib import Path
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time

from config import (WORKSPACE, TIME_LIMIT_SEC, COMPILE_TIMEOUT_SEC,
                    MEMORY_LIMIT_MB, OUTPUT_LIMIT_BYTES, MAX_SOURCE_BYTES, MAX_TESTS)


def normalize_output(value):
    return '\n'.join(line.rstrip() for line in value.replace('\r\n', '\n').splitlines()).rstrip()


class JudgeError(RuntimeError):
    """Infrastructure or compilation failure during reference validation."""


class MiniJudge:
    def __init__(self, workspace=WORKSPACE):
        self.workspace = Path(workspace).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)

    def execution_command(self,binary,time_limit_sec):
        command=[str(binary)]
        if os.name=='posix':
            command=[sys.executable,str(Path(__file__).with_name('runner.py')),
                     str(time_limit_sec),str(MEMORY_LIMIT_MB),str(OUTPUT_LIMIT_BYTES),str(binary)]
        return command

    @contextmanager
    def compiled(self, source):
        if not isinstance(source, str) or len(source.encode()) > MAX_SOURCE_BYTES:
            raise JudgeError('Fonte ausente ou excede 100 KB.')
        compiler = shutil.which('g++')
        if compiler is None:
            raise JudgeError('g++ não encontrado no PATH. Instale GCC/MinGW e reinicie o terminal.')
        with tempfile.TemporaryDirectory(prefix='judge_', dir=self.workspace) as folder:
            src = Path(folder) / 'main.cpp'
            binary = Path(folder) / ('main.exe' if os.name == 'nt' else 'main')
            src.write_text(source, encoding='utf-8')
            try:
                result = subprocess.run([compiler, '-O2', '-std=c++17', str(src), '-o', str(binary)],
                                        capture_output=True, text=True, errors='replace',
                                        timeout=COMPILE_TIMEOUT_SEC, cwd=folder)
            except subprocess.TimeoutExpired as exc:
                raise JudgeError('Compilação excedeu o limite de tempo.') from exc
            except OSError as exc:
                raise JudgeError(f'Falha ao iniciar compilador: {exc}') from exc
            if result.returncode:
                raise JudgeError(result.stderr[:16000])
            yield binary

    def execute(self, binary, input_data, time_limit_sec=TIME_LIMIT_SEC):
        if not 0 < time_limit_sec <= 10:
            raise ValueError('Limite de tempo deve estar entre 0 e 10 segundos.')
        command = self.execution_command(binary,time_limit_sec)
        start = time.perf_counter()
        with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr,
                                       cwd=binary.parent, start_new_session=(os.name == 'posix'))
            verdict = 'AC'
            try:
                process.communicate(input_data.encode(), timeout=time_limit_sec)
                if process.returncode != 0:
                    verdict = 'RE'
            except subprocess.TimeoutExpired:
                verdict = 'TLE'
            finally:
                if os.name == 'posix':
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        process.poll()
                elif process.poll() is None:
                    process.kill()
                process.wait()
            elapsed = (time.perf_counter() - start) * 1000
            stdout.seek(0)
            stderr.seek(0)
            output = stdout.read(OUTPUT_LIMIT_BYTES + 1)
            error = stderr.read(OUTPUT_LIMIT_BYTES + 1)
            if len(output) > OUTPUT_LIMIT_BYTES or len(error) > OUTPUT_LIMIT_BYTES:
                verdict = 'RE'
                error = b'Limite de saida excedido.'
            elif verdict == 'RE' and (b'std::bad_alloc' in error or b'MemoryError' in error or b'out of memory' in error.lower()):
                verdict = 'MLE'
            return {'verdict': verdict, 'actual_output': output[:OUTPUT_LIMIT_BYTES].decode(errors='replace'),
                    'stderr': error[:16000].decode(errors='replace'), 'execution_time_ms': round(elapsed, 3)}

    def judge(self, source_code, test_cases, time_limit_sec=TIME_LIMIT_SEC):
        if not test_cases or len(test_cases) > MAX_TESTS:
            raise ValueError(f'Forneça de 1 a {MAX_TESTS} testes; conjunto vazio não pode receber AC.')
        results = []
        try:
            with self.compiled(source_code) as binary:
                for index, case in enumerate(test_cases, 1):
                    result = self.execute(binary, case['input'], time_limit_sec)
                    result.update(test_id=index, input=case['input'], expected_output=case['expected_output'],
                                  strategy=case.get('strategy', 'base'))
                    if result['verdict'] == 'AC' and normalize_output(result['actual_output']) != normalize_output(case['expected_output']):
                        result['verdict'] = 'WA'
                    results.append(result)
                    if result['verdict'] != 'AC':
                        return {'verdict': result['verdict'], 'tests': results, 'failed_test': result,
                                'message': result['stderr']}
        except JudgeError as exc:
            return {'verdict': 'CE', 'message': str(exc), 'tests': results, 'failed_test': None}
        return {'verdict': 'AC', 'tests': results, 'failed_test': None, 'message': 'Todos os testes passaram.'}
