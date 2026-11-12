"""Unit tests for Linux namespace sandbox isolation and IsolatedMiniJudge fail-closed security contracts."""
import pytest
import shutil
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

from core.isolated_judge import (
    namespace_command,
    isolation_available,
    IsolatedMiniJudge,
)
from core.mini_judge import JudgeError


class TestNamespaceCommandFlags:
    """Valida deterministicamente as flags de contenção de segurança do bubblewrap."""

    def test_mandatory_containment_flags_present(self, tmp_path):
        folder = tmp_path / "sandbox_work"
        folder.mkdir()

        with patch("shutil.which", return_value="/usr/bin/bwrap"), \
             patch("sys.platform", "linux"):
            cmd = namespace_command(str(folder), ["/usr/bin/true"], writable=False)

        # 1. Isolamento de namespaces
        assert "--unshare-all" in cmd, "Flag mandatória --unshare-all ausente"
        assert "--die-with-parent" in cmd, "Flag mandatória --die-with-parent ausente"
        assert "--new-session" in cmd, "Flag mandatória --new-session ausente"

        # 2. Remoção de capacidades do Kernel
        assert "--cap-drop" in cmd, "Flag mandatória --cap-drop ausente"
        cap_idx = cmd.index("--cap-drop")
        assert cmd[cap_idx + 1] == "ALL", "Capacidades do Kernel não foram rebaixadas com ALL"

        # 3. Limpeza de variáveis de ambiente do host
        assert "--clearenv" in cmd, "Flag mandatória --clearenv ausente"

        # 4. Sanitização de HOME e diretório de execução
        setenv_indices = [i for i, x in enumerate(cmd) if x == "--setenv"]
        home_configured = any(
            cmd[i + 1] == "HOME" and cmd[i + 2] == "/tmp" for i in setenv_indices
        )
        assert home_configured, "HOME não configurado para /tmp isolado"

        assert "--dir" in cmd, "Flag mandatória --dir /work ausente"
        dir_idx = cmd.index("--dir")
        assert cmd[dir_idx + 1] == "/work", "Diretório /work não definido"

        # 5. Limitação de processos (fork bomb mitigation)
        assert any("--nproc=32:32" in arg for arg in cmd), "Controle de limites nproc ausente"

        # 6. Modo somente leitura (writable=False)
        resolved_folder = str(folder.resolve())
        ro_bind_indices = [i for i, x in enumerate(cmd) if x == "--ro-bind"]
        is_ro_mounted = any(
            cmd[i + 1] == resolved_folder and cmd[i + 2] == "/work" for i in ro_bind_indices
        )
        assert is_ro_mounted, f"Diretório de trabalho não foi montado como --ro-bind quando writable=False: {cmd}"

    def test_writable_mode_mounts_with_bind(self, tmp_path):
        folder = tmp_path / "sandbox_writable"
        folder.mkdir()

        with patch("shutil.which", return_value="/usr/bin/bwrap"), \
             patch("sys.platform", "linux"):
            cmd = namespace_command(str(folder), ["/usr/bin/g++"], writable=True)

        resolved_folder = str(folder.resolve())
        bind_indices = [i for i, x in enumerate(cmd) if x == "--bind"]
        is_rw_mounted = any(
            cmd[i + 1] == resolved_folder and cmd[i + 2] == "/work" for i in bind_indices
        )
        assert is_rw_mounted, "Diretório não foi montado com --bind quando writable=True"

    def test_fails_closed_when_bwrap_missing(self, tmp_path):
        with patch("shutil.which", return_value=None), \
             patch("sys.platform", "linux"):
            with pytest.raises(JudgeError, match="Execução desativada: requer Linux e bubblewrap"):
                namespace_command(str(tmp_path), ["true"])

    def test_fails_closed_on_non_linux_platforms(self, tmp_path):
        with patch("shutil.which", return_value="/usr/bin/bwrap"), \
             patch("sys.platform", "darwin"):
            with pytest.raises(JudgeError, match="Execução desativada: requer Linux e bubblewrap"):
                namespace_command(str(tmp_path), ["true"])


class TestIsolatedMiniJudgeFailClosed:
    """Garante comportamento fail-closed do IsolatedMiniJudge em ausência de sandbox."""

    def test_compilation_blocked_when_isolation_unavailable(self, tmp_path):
        judge = IsolatedMiniJudge(workspace=tmp_path)

        with patch("core.isolated_judge.isolation_available", return_value=False):
            with pytest.raises(JudgeError, match="Sandbox indisponível"):
                with judge.compiled("int main() { return 0; }"):
                    pass

    def test_execution_blocked_when_isolation_unavailable(self, tmp_path):
        judge = IsolatedMiniJudge(workspace=tmp_path)
        binary_path = tmp_path / "dummy_bin"
        binary_path.touch()

        with patch("core.isolated_judge.isolation_available", return_value=False):
            with pytest.raises(JudgeError, match="Sandbox indisponível"):
                judge.execution_command(binary_path, 2.0)


class TestIsolationAvailableProbe:
    """Valida o probe de integridade do sandbox."""

    def test_probe_returns_false_when_binary_missing(self):
        isolation_available.cache_clear()
        try:
            with patch("shutil.which", return_value=None), \
                 patch("sys.platform", "linux"):
                assert isolation_available() is False
        finally:
            isolation_available.cache_clear()

    def test_probe_returns_true_when_execution_succeeds(self):
        isolation_available.cache_clear()
        mock_proc = MagicMock()
        mock_proc.returncode = 0

        try:
            with patch("shutil.which", return_value="/usr/bin/bwrap"), \
                 patch("sys.platform", "linux"), \
                 patch("subprocess.run", return_value=mock_proc):
                assert isolation_available() is True
        finally:
            isolation_available.cache_clear()
