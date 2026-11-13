#!/usr/bin/env python3
"""DeepSeek Harness Installer - user-scoped Linux GUI installer."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path

APP_NAME = "DeepSeek Harness"
PACKAGE = "@deepseek-ai/dsh"
HOME = Path.home()
OPT = HOME / ".local/opt/deepseek-harness"
BIN = HOME / ".local/bin"
APPS = HOME / ".local/share/applications"
ICONS = HOME / ".local/share/icons"
DATA = HOME / ".dsh"
NODE_MIN = (22, 19, 0)
PORT = 3080


def run_cmd(args: list[str], timeout: int = 900) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PATH"] = f"{BIN}:{Path(shutil.which('node') or '/usr/bin/node').parent}:{env.get('PATH','')}"
    return subprocess.run(args, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, env=env, timeout=timeout)


def version_tuple(value: str) -> tuple[int, int, int] | None:
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", value)
    return tuple(map(int, match.groups())) if match else None


def check_runtime() -> tuple[bool, str]:
    node, npm = shutil.which("node"), shutil.which("npm")
    if not node or not npm:
        return False, "No se encuentra Node.js o npm en PATH. Instala Node.js en tu usuario y vuelve a intentarlo."
    try:
        version = run_cmd([node, "--version"], timeout=15).stdout.strip()
        parsed = version_tuple(version)
        if not parsed or not (parsed >= NODE_MIN or parsed[0] >= 24):
            return False, f"Node.js {version} no cumple el requisito mínimo comprobado (22.19.0 o 24+). Revisa los requisitos actuales del paquete oficial."
        return True, f"Node.js {version} · npm disponible"
    except Exception as exc:
        return False, f"No se pudo comprobar Node.js: {exc}"


def npm_latest() -> str:
    npm = shutil.which("npm")
    result = run_cmd([npm, "view", PACKAGE, "version"], timeout=60)
    if result.returncode:
        raise RuntimeError(result.stdout.strip() or "No se pudo consultar npm.")
    return result.stdout.strip().splitlines()[-1]


def installed_version() -> str:
    pkg = OPT / "node_modules" / "@deepseek-ai" / "dsh" / "package.json"
    if not pkg.exists():
        return "No instalado"
    try:
        import json
        return json.loads(pkg.read_text(encoding="utf-8")).get("version", "Desconocida")
    except Exception:
        return "Instalado (versión desconocida)"


def write_launchers() -> None:
    BIN.mkdir(parents=True, exist_ok=True)
    APPS.mkdir(parents=True, exist_ok=True)
    launcher = BIN / "deepseek-harness"
    launcher.write_text(
        "#!/bin/sh\n"
        "APP_DIR=\"$HOME/.local/opt/deepseek-harness\"\n"
        "export PATH=\"$HOME/.local/bin:$PATH\"\n"
        "cd \"$HOME\" || exit 1\n"
        "exec \"$APP_DIR/node_modules/.bin/dsh\" web \"$@\"\n",
        encoding="utf-8")
    launcher.chmod(0o755)
    desktop = APPS / "deepseek-harness.desktop"
    desktop.write_text(
        "[Desktop Entry]\nType=Application\nName=DeepSeek Harness\n"
        "Comment=Entorno de agentes de DeepSeek\n"
        "Exec=" + str(launcher) + "\nTerminal=true\nCategories=Development;Utility;\n"
        "StartupNotify=false\n",
        encoding="utf-8")
    desktop.chmod(0o644)


class Installer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DeepSeek Harness · Instalador")
        self.geometry("720x560")
        self.minsize(650, 500)
        self.configure(bg="#f4f6fa")
        self.busy = False
        self._build()
        self.refresh_status()

    def _build(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#f4f6fa")
        style.configure("TLabel", background="#f4f6fa", foreground="#172033", font=("Inter", 10))
        style.configure("Title.TLabel", font=("Inter", 21, "bold"), foreground="#101828")
        style.configure("Sub.TLabel", foreground="#596579")
        style.configure("TButton", font=("Inter", 10, "bold"), padding=10)
        style.configure("Action.TButton", background="#2457d6", foreground="white")
        outer = ttk.Frame(self, padding=26)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="DEEPSEEK HARNESS", style="Title.TLabel").pack(anchor="w")
        ttk.Label(outer, text="Instalador independiente para Linux · Sin permisos root",
                  style="Sub.TLabel").pack(anchor="w", pady=(5, 18))
        status = ttk.LabelFrame(outer, text=" Estado del sistema ", padding=14)
        status.pack(fill="x")
        self.runtime_var = tk.StringVar(value="Comprobando Node.js…")
        self.installed_var = tk.StringVar(value="Versión instalada: consultando…")
        self.latest_var = tk.StringVar(value="Última versión npm: no consultada")
        ttk.Label(status, textvariable=self.runtime_var).pack(anchor="w")
        ttk.Label(status, textvariable=self.installed_var).pack(anchor="w", pady=(7, 0))
        ttk.Label(status, textvariable=self.latest_var).pack(anchor="w", pady=(7, 0))
        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=18)
        self.install_btn = ttk.Button(actions, text="Instalar / actualizar", style="Action.TButton",
                                       command=self.install)
        self.install_btn.pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Comprobar versiones", command=self.refresh_status).pack(side="left", padx=4)
        ttk.Button(actions, text="Reparar lanzador", command=self.repair).pack(side="left", padx=4)
        ttk.Button(actions, text="Desinstalar", command=self.uninstall).pack(side="left", padx=4)
        ttk.Label(outer, text="Registro de operaciones").pack(anchor="w")
        self.log = tk.Text(outer, height=13, bg="#101828", fg="#e7edf7",
                           insertbackground="white", relief="flat", font=("DejaVu Sans Mono", 9),
                           wrap="word")
        self.log.pack(fill="both", expand=True, pady=(7, 0))
        self.progress = ttk.Progressbar(outer, mode="indeterminate")
        self.progress.pack(fill="x", pady=(10, 0))
        ttk.Label(outer, text="DeepSeek Harness es software en Developer Preview. Revisa sus permisos y protege tus claves API.",
                  style="Sub.TLabel", wraplength=650).pack(anchor="w", pady=(12, 0))

    def log_msg(self, message: str):
        self.after(0, lambda: (self.log.insert("end", message.rstrip() + "\n"),
                               self.log.see("end")))

    def task(self, title: str, function):
        if self.busy:
            return
        self.busy = True
        self.progress.start(12)
        self.install_btn.configure(state="disabled")
        self.log_msg(title)
        def worker():
            try:
                function()
            except Exception as exc:
                self.log_msg("ERROR: " + str(exc))
                self.after(0, lambda: messagebox.showerror("Error", str(exc)))
            finally:
                self.after(0, self._done)
        threading.Thread(target=worker, daemon=True).start()

    def _done(self):
        self.progress.stop()
        self.install_btn.configure(state="normal")
        self.busy = False
        self.refresh_labels()

    def refresh_labels(self):
        self.installed_var.set("Versión instalada: " + installed_version())

    def refresh_status(self):
        ok, text = check_runtime()
        self.runtime_var.set(("✓ " if ok else "✗ ") + text)
        self.refresh_labels()
        self.log_msg(text)

    def install(self):
        def work():
            ok, text = check_runtime()
            self.log_msg(text)
            if not ok:
                raise RuntimeError(text)
            latest = npm_latest()
            self.log_msg(f"Versión publicada en npm: {latest}")
            OPT.mkdir(parents=True, exist_ok=True)
            npm = shutil.which("npm")
            result = run_cmd([npm, "install", "--prefix", str(OPT), "--no-audit", "--no-fund",
                              f"{PACKAGE}@latest"], timeout=1200)
            self.log_msg(result.stdout)
            if result.returncode:
                raise RuntimeError("Falló la instalación npm. Consulta el registro.")
            write_launchers()
            self.log_msg("Instalación completada. Ejecuta 'deepseek-harness' o abre el menú de aplicaciones.")
            self.after(0, lambda: messagebox.showinfo("Instalación completada",
                f"DeepSeek Harness {installed_version()} instalado para tu usuario.\n\n"
                "La configuración y los datos de ~/.dsh se conservan independientemente." ))
        self.task("Instalando / actualizando DeepSeek Harness desde npm oficial…", work)

    def repair(self):
        def work():
            if not (OPT / "node_modules/.bin/dsh").exists():
                raise RuntimeError("DeepSeek Harness no está instalado. Usa primero Instalar / actualizar.")
            write_launchers()
            self.log_msg("Lanzador y acceso de escritorio reparados.")
        self.task("Reparando lanzadores…", work)

    def uninstall(self):
        if not messagebox.askyesno("Desinstalar", "Se eliminará el paquete instalado y sus lanzadores.\n\n"
            "Tus perfiles, sesiones y configuración de ~/.dsh NO se eliminarán. ¿Continuar?"):
            return
        def work():
            shutil.rmtree(OPT, ignore_errors=True)
            for path in (BIN / "deepseek-harness", APPS / "deepseek-harness.desktop"):
                try:
                    path.unlink(missing_ok=True)
                except OSError as exc:
                    self.log_msg(f"No se pudo eliminar {path}: {exc}")
            self.log_msg("Desinstalación completada. Los datos de ~/.dsh se han conservado.")
        self.task("Desinstalando…", work)


if __name__ == "__main__":
    Installer().mainloop()
