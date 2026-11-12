#!/usr/bin/env python3
"""Macro de Automação Visual e em Segundo Plano para o Antigravity IDE (via X11).

Suporta dois modos:
1. Modo Interativo: Ativa a janela e demonstra visualmente.
2. Modo Segundo Plano (--background): Envia eventos diretamente para o Window ID
   sem roubar o foco do Chrome ou mover o cursor do usuário, e captura screenshots
   silenciosamente.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

# Coordenadas relativas à janela do Antigravity/VS Code (1920x1048)
TAB_COORDINATES = {
    "integracao": (120, 355),
    "backend": (120, 395),
    "planejador": (120, 435),
    "testes": (120, 475),
    "skills": (120, 515),
    "frontend": (120, 555),
    "prompts": (120, 595),
}

INPUT_BOX = (500, 875)
REVIEW_BUTTON = (620, 688)
ACCEPT_BUTTON = (620, 715)


def find_vscode_window() -> str | None:
    try:
        res = subprocess.run(
            ["xdotool", "search", "--onlyvisible", "--name", "Visual Studio Code"],
            capture_output=True,
            text=True,
            check=False
        )
        pids = [p.strip() for p in res.stdout.splitlines() if p.strip()]
        return pids[0] if pids else None
    except Exception:
        return None


def capture_window_screenshot(win_id: str, output_path: str) -> bool:
    """Captura a janela do VS Code em segundo plano sem focar ou roubar tela."""
    try:
        subprocess.run(
            ["import", "-window", win_id, output_path],
            check=True,
            capture_output=True
        )
        return True
    except Exception as e:
        print(f"[ERRO] Falha ao capturar screenshot: {e}")
        return False


def click_tab(tab_name: str, background: bool = False) -> bool:
    coords = TAB_COORDINATES.get(tab_name.lower())
    if not coords:
        print(f"[ERRO] Aba '{tab_name}' desconhecida. Opções: {list(TAB_COORDINATES.keys())}")
        return False

    win_id = find_vscode_window()
    if not win_id:
        print("[ERRO] Janela do Antigravity não encontrada.")
        return False

    x, y = coords
    if not background:
        subprocess.run(["xdotool", "windowactivate", "--sync", win_id], check=False)
        time.sleep(0.2)
        subprocess.run(["xdotool", "mousemove", "--sync", str(x), str(y)], check=False)
        subprocess.run(["xdotool", "click", "1"], check=False)
    else:
        # Envia clique direto para a janela em background
        subprocess.run(["xdotool", "mousemove", "--window", win_id, str(x), str(y)], check=False)
        subprocess.run(["xdotool", "click", "--window", win_id, "1"], check=False)

    time.sleep(0.4)
    return True


def click_accept(background: bool = True):
    """Clica no botão de Accept / Review de alterações propostas."""
    win_id = find_vscode_window()
    if not win_id:
        return False

    x, y = ACCEPT_BUTTON
    print(f"[MACRO] Clicando em Accept/Proceed em ({x}, {y})...")
    if not background:
        subprocess.run(["xdotool", "windowactivate", "--sync", win_id], check=False)
        time.sleep(0.2)
        subprocess.run(["xdotool", "mousemove", "--sync", str(x), str(y)], check=False)
        subprocess.run(["xdotool", "click", "1"], check=False)
    else:
        subprocess.run(["xdotool", "mousemove", "--window", win_id, str(x), str(y)], check=False)
        subprocess.run(["xdotool", "click", "--window", win_id, "1"], check=False)

    time.sleep(0.5)
    return True


def type_and_send(message: str, auto_submit: bool = True, background: bool = False):
    win_id = find_vscode_window()
    if not win_id:
        return False

    ix, iy = INPUT_BOX
    if not background:
        subprocess.run(["xdotool", "windowactivate", "--sync", win_id], check=False)
        time.sleep(0.2)
        subprocess.run(["xdotool", "mousemove", "--sync", str(ix), str(iy)], check=False)
        subprocess.run(["xdotool", "click", "1"], check=False)
    else:
        subprocess.run(["xdotool", "mousemove", "--window", win_id, str(ix), str(iy)], check=False)
        subprocess.run(["xdotool", "click", "--window", win_id, "1"], check=False)

    time.sleep(0.3)
    subprocess.run(["xdotool", "key", "--window", win_id, "ctrl+a", "BackSpace"], check=False)
    time.sleep(0.2)

    subprocess.run(["xdotool", "type", "--window", win_id, "--delay", "25", message], check=False)
    time.sleep(0.3)

    if auto_submit:
        subprocess.run(["xdotool", "key", "--window", win_id, "Return"], check=False)

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Macro de Automação Visual e em Background para Antigravity")
    parser.add_argument("tab", nargs="?", default=None, choices=list(TAB_COORDINATES.keys()), help="Aba a focar")
    parser.add_argument("--msg", default=None, help="Mensagem a ser enviada no chat")
    parser.add_argument("--background", action="store_true", help="Executa silenciosamente em segundo plano sem focar")
    parser.add_argument("--accept", action="store_true", help="Clica no botão de Accept / Proceed")
    parser.add_argument("--screenshot", default=None, help="Caminho para salvar screenshot da janela em segundo plano")
    args = parser.parse_args()

    win_id = find_vscode_window()
    if not win_id:
        print("[ERRO] Janela do Antigravity não encontrada.")
        sys.exit(1)

    if args.accept:
        click_accept(background=args.background)

    if args.tab:
        click_tab(args.tab, background=args.background)
        if args.msg:
            type_and_send(args.msg, auto_submit=True, background=args.background)

    if args.screenshot:
        capture_window_screenshot(win_id, args.screenshot)
        print(f"[MACRO] Screenshot em segundo plano salvo em: {args.screenshot}")
