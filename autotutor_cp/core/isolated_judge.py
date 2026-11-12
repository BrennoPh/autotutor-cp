"""Fail-closed Linux namespaces for compilation and execution of untrusted C++.

No host home, credentials, network, devices or writable system paths are mounted.
This is a restricted local prototype, not a claim of audited multi-tenant security.
"""
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
import os,shutil,subprocess,sys,tempfile
from config import WORKSPACE,MAX_SOURCE_BYTES,OUTPUT_LIMIT_BYTES,MEMORY_LIMIT_MB,COMPILE_TIMEOUT_SEC
from core.mini_judge import MiniJudge,JudgeError

def namespace_command(folder,command,writable=False):
    executable=shutil.which('bwrap')
    if sys.platform!='linux' or not executable:raise JudgeError('Execução desativada: requer Linux e bubblewrap funcional.')
    args=[executable,'--unshare-all','--die-with-parent','--new-session','--cap-drop','ALL','--clearenv',
          '--setenv','PATH','/usr/bin:/bin','--setenv','LANG','C.UTF-8','--setenv','HOME','/tmp']
    for path in ('/usr','/lib','/lib64','/bin'):
        if Path(path).exists():args+=['--ro-bind',path,path]
    args+=['--proc','/proc','--dev','/dev','--tmpfs','/tmp','--dir','/work',
           '--bind' if writable else '--ro-bind',str(Path(folder).resolve()),'/work','--chdir','/work','--',
           '/usr/bin/prlimit','--nproc=32:32','--',*command]
    return args

@lru_cache(maxsize=1)
def isolation_available():
    if sys.platform!='linux' or not shutil.which('bwrap'):return False
    try:
        with tempfile.TemporaryDirectory(prefix='autotutor-sandbox-probe-') as folder:
            p=subprocess.run(namespace_command(folder,['/usr/bin/true']),capture_output=True,timeout=4)
            return p.returncode==0
    except (OSError,subprocess.TimeoutExpired,JudgeError):return False

class IsolatedMiniJudge(MiniJudge):
    @contextmanager
    def compiled(self,source):
        if not isolation_available():raise JudgeError('Sandbox indisponível; código gerado não será compilado nem executado no host.')
        if not isinstance(source,str) or len(source.encode())>MAX_SOURCE_BYTES:raise JudgeError('Fonte ausente ou excede 100 KB.')
        compiler=shutil.which('g++')
        if not compiler:raise JudgeError('g++ indisponível.')
        with tempfile.TemporaryDirectory(prefix='isolated_',dir=self.workspace) as folder:
            Path(folder,'main.cpp').write_text(source)
            cmd=namespace_command(folder,[compiler,'-O2','-std=c++17','/work/main.cpp','-o','/work/main'],True)
            cmd=[sys.executable,str(Path(__file__).with_name('runner.py')),str(COMPILE_TIMEOUT_SEC),'768',str(OUTPUT_LIMIT_BYTES),*cmd]
            with tempfile.TemporaryFile() as output:
                process=subprocess.Popen(cmd,stdout=output,stderr=output,start_new_session=True)
                try:process.wait(timeout=COMPILE_TIMEOUT_SEC)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid,9);process.wait();raise JudgeError('Compilação isolada excedeu o tempo.')
                output.seek(0);message=output.read(16000).decode(errors='replace')
            if process.returncode:raise JudgeError('Compilação isolada falhou: '+message)
            yield Path(folder,'main')

    def execution_command(self,binary,time_limit_sec):
        if not isolation_available():raise JudgeError('Sandbox indisponível; execução bloqueada.')
        cmd=namespace_command(binary.parent,['/work/'+binary.name])
        return [sys.executable,str(Path(__file__).with_name('runner.py')),str(time_limit_sec),str(MEMORY_LIMIT_MB),str(OUTPUT_LIMIT_BYTES),*cmd]
