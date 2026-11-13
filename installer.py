#!/usr/bin/env python3
"""DeepSeek Harness Installer & Updater — Punto Vuela Montejaque."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import threading
import queue
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

APP_NAME = "DeepSeek Harness"
PACKAGE = "@deepseek-ai/dsh"
HOME = Path.home()
LOCAL = HOME / ".local"
OPT = LOCAL / "opt" / "deepseek-harness"
BIN = LOCAL / "bin"
APPS = LOCAL / "share" / "applications"
ICONS = LOCAL / "share" / "icons"
ICON = ICONS / "hicolor" / "scalable" / "apps" / "deepseek-harness.svg"
DESKTOP = APPS / "deepseek-harness.desktop"
LAUNCHER = BIN / "deepseek-harness"
DATA = HOME / ".dsh"
YELLOW = "#F3D54E"
INK = "#171717"
MUTED = "#555555"
PANEL = "#F7F7F5"
NODE_MIN = (24, 9, 0)
REGISTRY_URL = "https://registry.npmjs.org/%40deepseek-ai%2Fdsh"


def version_tuple(value: str):
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", value or "")
    return tuple(map(int, match.groups())) if match else None


def candidate_bins():
    found = []
    for item in os.environ.get("PATH", "").split(os.pathsep):
        if item:
            found.append(Path(item).expanduser())
    for pattern in (
        "~/.nvm/versions/node/*/bin",
        "~/.volta/bin",
        "~/.local/share/mise/shims",
        "~/.asdf/shims",
    ):
        paths = [Path(p).expanduser() for p in HOME.glob(pattern.replace("~/", ""))]
        paths.sort(key=lambda p: version_tuple(p.parent.name) or (0, 0, 0), reverse=True)
        found.extend(paths)
    unique = []
    seen = set()
    for path in found:
        key = str(path)
        if key not in seen and path.is_dir():
            seen.add(key)
            unique.append(path)
    return unique


def runtime_paths():
    for directory in candidate_bins():
        node, npm = directory / "node", directory / "npm"
        if node.is_file() and os.access(node, os.X_OK) and npm.is_file() and os.access(npm, os.X_OK):
            try:
                result = subprocess.run([str(node), "--version"], capture_output=True,
                                        text=True, timeout=12, check=False)
                parsed = version_tuple(result.stdout.strip())
                if result.returncode == 0 and parsed and parsed >= NODE_MIN:
                    return str(node), str(npm), directory
            except (OSError, subprocess.TimeoutExpired):
                continue
    return None, None, None


def runtime_status():
    node, npm, directory = runtime_paths()
    if not node or not npm:
        return False, ("DeepSeek Harness necesita Node.js 24.9.0 o posterior. "
                        "Se ha encontrado una versión incompatible o no se ha podido localizar npm. "
                        "Actualiza Node.js desde NVM y vuelve a comprobar.")
    try:
        version = subprocess.run([node, "--version"], capture_output=True,
                                 text=True, timeout=12, check=True).stdout.strip()
        # Ejecutar el CLI de npm con el Node absoluto evita depender del PATH
        # que GNOME entrega a procesos gráficos (NVM no siempre está cargado).
        npm_cli = str(Path(npm).resolve())
        npm_version = subprocess.run([node, npm_cli, "--version"],
                                     capture_output=True, text=True, timeout=12,
                                     check=True).stdout.strip()
        return True, f"Node.js {version} · npm {npm_version} · {directory}"
    except Exception as exc:
        return False, "No se pudo comprobar Node.js/npm: " + str(exc)


def latest_npm_version() -> str:
    request = urllib.request.Request(
        REGISTRY_URL,
        headers={"Accept": "application/vnd.npm.install-v1+json",
                 "User-Agent": "DeepSeek-Harness-Installer-Punto-Vuela/1.0"})
    with urllib.request.urlopen(request, timeout=18) as response:
        data = json.loads(response.read().decode("utf-8"))
    version = data.get("dist-tags", {}).get("latest")
    if not version:
        raise RuntimeError("El registro npm no ha devuelto la etiqueta dist-tags.latest.")
    return str(version)


def installed_version() -> str:
    package_file = OPT / "node_modules" / "@deepseek-ai" / "dsh" / "package.json"
    try:
        return str(json.loads(package_file.read_text(encoding="utf-8")).get("version", "Desconocida"))
    except (OSError, ValueError, TypeError):
        return "No instalada"


def emit(callback, kind, value):
    if callback:
        callback(kind, value)


def run_npm_install(node, npm, latest, callback):
    OPT.mkdir(parents=True, exist_ok=True)
    npm_cli = str(Path(npm).resolve())
    command = [
        node, npm_cli, "install", "--prefix", str(OPT), "--no-audit", "--no-fund",
        "--progress=false", "--prefer-offline", "--no-update-notifier",
        "--fetch-retries=2", "--fetch-timeout=120000", f"{PACKAGE}@{latest}"
    ]
    env = os.environ.copy()
    env["PATH"] = str(Path(npm).parent) + os.pathsep + str(BIN) + os.pathsep + env.get("PATH", "")
    env["npm_config_update_notifier"] = "false"
    emit(callback, "log", "Ejecutando npm install (sin auditoría ni avisos adicionales)…")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, bufsize=1, env=env)
    lines = []
    try:
        for line in iter(process.stdout.readline, ""):
            line = line.rstrip()
            if line:
                lines.append(line)
                emit(callback, "log", line)
        code = process.wait(timeout=1200)
    except Exception:
        process.kill()
        process.wait()
        raise
    if code:
        raise RuntimeError("npm install ha fallado (código " + str(code) + "). Revisa el registro.")
    return "\n".join(lines[-20:])


def write_launchers(callback=None):
    BIN.mkdir(parents=True, exist_ok=True)
    APPS.mkdir(parents=True, exist_ok=True)
    icon_dir = ICON.parent
    icon_dir.mkdir(parents=True, exist_ok=True)
    # Símbolo oficial de DeepSeek (ICON.svg, repositorio deepseek-ai).
    # Se conserva la ballena azul original; solo se adapta el lienzo al formato cuadrado de GNOME.
    ICON.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">'
        '<title>DeepSeek</title>'
        '<rect x="8" y="8" width="240" height="240" rx="52" fill="#ffffff"/>'
        '<svg x="22" y="54" width="212" height="148" viewBox="0 0 71.69 52.76">'
        '<path fill="#4d6bfe" d="M70.94 4.43c-.76-.38-1.08.33-1.53.69a4 4 0 0 0-.41.41 5.07 5.07 0 0 1-4.1 1.87 8 8 0 0 0-6.46 2.53 5.82 5.82 0 0 0-3.72-4.62 6.39 6.39 0 0 1-2.85-1.94 7.76 7.76 0 0 1-.92-2.31c-.16-.48-.32-1-.87-1.05s-.83.41-1.07.82a11 11 0 0 0-1.26 5.5 11.9 11.9 0 0 0 5.49 10.14.75.75 0 0 1 .39 1c-.25.84-.54 1.65-.79 2.49-.17.53-.41.65-1 .42a16.63 16.63 0 0 1-5.18-3.52c-2.56-2.48-4.88-5.21-7.76-7.35-.68-.5-1.36-1-2.06-1.41-2.94-2.86.39-5.2 1.16-5.48s.28-1.29-2.33-1.28-5 .88-8 2a8.23 8.23 0 0 1-1.39.41 28.67 28.67 0 0 0-8.61-.3A18.57 18.57 0 0 0 4.2 10.27C.2 15.74-.69 21.94.46 28.42a27.68 27.68 0 0 0 10 16.88 26.8 26.8 0 0 0 19.23 6.39c4.43-.25 9.36-.84 14.92-5.55a13.84 13.84 0 0 0 5.32 1.18 17.24 17.24 0 0 0 5.09-.38c2.2-.46 2.05-2.5 1.25-2.87-6.43-3-5-1.78-6.3-2.77 3.27-3.87 8.2-7.89 10.13-20.92a12.44 12.44 0 0 0 0-2.52c0-.51.1-.71.68-.76a12.55 12.55 0 0 0 4.62-1.42c4.17-2.28 5.85-6 6.25-10.51a1.57 1.57 0 0 0-.71-1.74ZM34.6 44.8c-6.24-4.9-9.27-6.52-10.52-6.45s-1 1.41-.7 2.28a8.49 8.49 0 0 0 1.11 2.21 1.14 1.14 0 0 1-.34 1.8c-2 1.24-5.5-.42-5.66-.5a26.08 26.08 0 0 1-9.87-9.88 30.15 30.15 0 0 1-3.87-13.39c-.06-1.15.28-1.56 1.42-1.77a14.31 14.31 0 0 1 4.57-.11 28.56 28.56 0 0 1 16.33 8.29 54.06 54.06 0 0 1 6.58 8.63 41.46 41.46 0 0 0 7.41 8.71 24.36 24.36 0 0 0 2.66 2c-2.88.14-6.88.19-9.61-1.97Zm3-19.23a.92.92 0 0 1 .92-.92.83.83 0 0 1 .32.06.8.8 0 0 1 .34.22.9.9 0 0 1 .25.64.92.92 0 0 1-1.83 0Zm9.29 4.76a5.27 5.27 0 0 1-1.77.48 3.75 3.75 0 0 1-2.38-.76 3.57 3.57 0 0 1-1.65-2.26 5.16 5.16 0 0 1 0-1.76 2 2 0 0 0-.71-2.17 3.1 3.1 0 0 0-2.06-.59 1.63 1.63 0 0 1-.76-.24.75.75 0 0 1-.34-1.07 3.47 3.47 0 0 1 .57-.62 3.9 3.9 0 0 1 3.43 0 10 10 0 0 1 3 2.34 18.62 18.62 0 0 1 2 2.73 10.9 10.9 0 0 1 1.33 2.53c.18.58-.07 1.11-.76 1.39Z"/>'
        '</svg></svg>',
        encoding="utf-8")
    LAUNCHER.write_text(
        '#!/bin/sh\n'
        'APP_DIR="$HOME/.local/opt/deepseek-harness"\n'
        'export PATH="$HOME/.local/bin:$PATH"\n'
        '# Las aplicaciones abiertas desde GNOME no heredan necesariamente NVM.\n'
        'if [ -s "$HOME/.nvm/nvm.sh" ]; then\n'
        '  . "$HOME/.nvm/nvm.sh" --no-use\n'
        '  if [ -f "$HOME/.nvm/alias/default" ]; then\n'
        '    nvm use --silent default >/dev/null 2>&1 || true\n'
        '  fi\n'
        'fi\n'
        '# Respaldo para instalaciones NVM sin alias default.\n'
        'if ! command -v node >/dev/null 2>&1; then\n'
        '  for NODE_BIN in "$HOME"/.nvm/versions/node/*/bin; do\n'
        '    if [ -x "$NODE_BIN/node" ]; then PATH="$NODE_BIN:$PATH"; export PATH; break; fi\n'
        '  done\n'
        'fi\n'
        'if ! command -v node >/dev/null 2>&1; then\n'
        '  echo "ERROR: No se encuentra Node.js en PATH ni en NVM."\n'
        '  printf "Pulsa Intro para cerrar esta ventana..."\n; read answer\n'
        '  exit 127\n'
        'fi\n'
        'if ! node -e \'const [a,b]=process.versions.node.split(".").map(Number); if (a < 24 || (a === 24 && b < 9)) process.exit(1)\' >/dev/null 2>&1; then\n'
        '  echo "ERROR: DeepSeek Harness necesita Node.js 24.9.0 o posterior."\n'
        '  echo "La versión detectada es: $(node --version)"\n'
        '  echo "Actualiza Node.js con NVM (por ejemplo: nvm install 24) y vuelve a abrir la aplicación."\n'
        '  printf "Pulsa Intro para cerrar esta ventana..."\n; read answer\n'
        '  exit 1\n'
        'fi\n'
        'if [ ! -x "$APP_DIR/node_modules/.bin/dsh" ]; then\n'
        '  echo "No se encuentra el ejecutable dsh. Abre DeepSeek Harness Installer y pulsa Instalar / actualizar."\n'
        '  printf "Pulsa Intro para cerrar esta ventana..."\n; read answer\n'
        '  exit 127\n'
        'fi\n'
        'cd "$HOME" || exit 1\n'
        'exec "$APP_DIR/node_modules/.bin/dsh" web "$@"\n',
        encoding="utf-8")
    LAUNCHER.chmod(0o755)
    desktop_text = (
        "[Desktop Entry]\nVersion=1.0\nType=Application\n"
        "Name=DeepSeek Harness\nName[es]=DeepSeek Harness\n"
        "GenericName=Entorno de agentes de IA\nGenericName[es]=Entorno de agentes de IA\n"
        "Comment=Entorno web de agentes de DeepSeek\n"
        f'Exec="{LAUNCHER}"\nTryExec={LAUNCHER}\nIcon={ICON}\n'
        "Terminal=true\nStartupNotify=true\n"
        "NoDisplay=false\nHidden=false\nCategories=Development;Utility;\n"
        "Keywords=deepseek;agents;ia;terminal;desarrollo;\n"
    )
    temporary = DESKTOP.with_suffix(".desktop.tmp")
    temporary.write_text(desktop_text, encoding="utf-8")
    temporary.chmod(0o755)
    os.replace(temporary, DESKTOP)
    DESKTOP.chmod(0o755)
    if not LAUNCHER.is_file() or not os.access(LAUNCHER, os.X_OK):
        raise RuntimeError("No se ha podido crear el comando de DeepSeek Harness.")
    if not ICON.is_file() or ICON.stat().st_size < 100:
        raise RuntimeError("No se ha podido instalar el icono SVG.")
    if not DESKTOP.is_file() or not os.access(DESKTOP, os.X_OK):
        raise RuntimeError("No se ha podido crear el acceso al menú.")
    validator = shutil.which("desktop-file-validate")
    if validator:
        result = subprocess.run([validator, str(DESKTOP)], capture_output=True, text=True, timeout=15)
        if result.returncode:
            raise RuntimeError("El acceso del menú no es válido: " + (result.stderr or result.stdout).strip())
    commands = [
        (["update-desktop-database", str(APPS)], "base de aplicaciones"),
        (["gtk-update-icon-cache", "-f", "-t", str(ICONS / "hicolor")], "caché de iconos"),
        (["xdg-desktop-menu", "forceupdate", "--mode", "user"], "índice del menú GNOME/XDG"),
    ]
    for command, label in commands:
        executable = shutil.which(command[0])
        if not executable:
            emit(callback, "log", "Aviso: " + command[0] + " no está disponible; se omite " + label + ".")
            continue
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
            if result.returncode == 0:
                emit(callback, "log", "Actualizado: " + label + ".")
            else:
                emit(callback, "log", "Aviso al actualizar " + label + ": " + (result.stderr or result.stdout).strip())
        except (OSError, subprocess.TimeoutExpired) as exc:
            emit(callback, "log", "Aviso al actualizar " + label + ": " + str(exc))
    emit(callback, "log", "Acceso del menú verificado: " + str(DESKTOP))
    emit(callback, "log", "Icono instalado: " + str(ICON))
    emit(callback, "log", "Si GNOME no lo muestra inmediatamente, cierra sesión y vuelve a entrar.")


class Installer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DeepSeek Harness Installer & Updater — Punto Vuela Montejaque")
        self.geometry("900x680")
        self.minsize(780, 600)
        self.configure(bg="white")
        self.events = queue.Queue()
        self.busy = False
        self.status_checking = False
        self._build()
        self.refresh_status()
        self.after(120, self._poll)

    def _build(self):
        outer = tk.Frame(self, bg="white", padx=24, pady=20)
        outer.pack(fill="both", expand=True)
        tk.Label(outer, text="DeepSeek Harness Installer & Updater", bg="white", fg=INK,
                 font=("Inter", 20, "bold")).pack(anchor="w")
        tk.Label(outer, text="Linux x64 · Sin root · Punto Vuela Montejaque",
                 bg="white", fg="#333333", font=("Inter", 9)).pack(anchor="w", pady=(3, 14))
        tk.Frame(outer, bg=YELLOW, height=5).pack(fill="x", pady=(0, 17))
        self.status_label = tk.Label(outer, text="Comprobando Node.js y npm…",
            bg="white", fg=INK, font=("Inter", 9), anchor="w")
        self.status_label.pack(fill="x", pady=(0, 5))
        self.installed_label = tk.Label(outer, text="Versión instalada: " + installed_version(),
            bg="white", fg="#333333", font=("Inter", 9), anchor="w")
        self.installed_label.pack(fill="x", pady=(0, 5))
        self.latest_label = tk.Label(outer, text="Última versión npm: consultando…",
            bg="white", fg="#333333", font=("Inter", 9), anchor="w")
        self.latest_label.pack(fill="x", pady=(0, 14))
        actions = tk.Frame(outer, bg="white")
        actions.pack(fill="x", pady=(0, 13))
        self.buttons = []
        for label, action in (
            ("Instalar / actualizar", self.install),
            ("Comprobar versiones", self.refresh_status),
            ("Reparar acceso", self.repair),
            ("Desinstalar", self.uninstall),
        ):
            button = tk.Button(actions, text=label, command=action, relief="raised", bd=1,
                font=("Inter", 9, "bold"), padx=10, pady=7, cursor="hand2")
            button.pack(side="left", padx=(0, 9))
            self.buttons.append(button)
        self.progress_label = tk.Label(outer, text="Preparado", bg="white", fg="#333333",
            font=("Inter", 8), anchor="w")
        self.progress_label.pack(fill="x", pady=(0, 4))
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("PV.Horizontal.TProgressbar", troughcolor="#E7E7E3",
            background=YELLOW, bordercolor="#D0D0CC", lightcolor=YELLOW, darkcolor=YELLOW)
        self.progress = ttk.Progressbar(outer, mode="determinate", maximum=100,
            style="PV.Horizontal.TProgressbar")
        self.progress.pack(fill="x", pady=(0, 9))
        tk.Label(outer, text="Registro de operaciones", bg="white", fg=INK,
                 font=("Inter", 9, "bold")).pack(anchor="w", pady=(0, 5))
        self.log_box = tk.Text(outer, height=12, bg=PANEL, fg=INK, insertbackground=INK,
            relief="solid", bd=1, wrap="word", font=("DejaVu Sans Mono", 8), padx=6, pady=5)
        self.log_box.pack(fill="both", expand=True)
        self.log_box.configure(state="disabled")
        footer = tk.Frame(outer, bg="white")
        footer.pack(fill="x", pady=(10, 0))
        contact = tk.Frame(footer, bg="white")
        contact.pack(side="left", fill="x", expand=True)
        tk.Label(contact, text="Desarrollador: Francisco Javier Gallego Orellana",
            bg="white", fg=INK, font=("Inter", 8, "bold")).pack(anchor="w")
        tk.Label(contact, text="Punto Vuela Montejaque · Avenida Andalucía, 48 · 29360 Montejaque (Málaga)",
            bg="white", fg="#333333", font=("Inter", 8)).pack(anchor="w", pady=(2, 0))
        tk.Label(contact, text="Teléfono: 633 402 959 · Correo: montejaque@puntosvuela.es",
            bg="white", fg="#333333", font=("Inter", 8)).pack(anchor="w")
        tk.Button(footer, text="Ver guía de uso", command=self.open_guide, relief="raised",
            bd=1, font=("Inter", 8), padx=9, pady=6, cursor="hand2").pack(side="right", anchor="s", pady=(22, 0))

    def log(self, message):
        self.events.put(("log", str(message)))

    def progress_update(self, value, message):
        self.events.put(("progress", (value, message)))

    def _poll(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "log":
                    self.log_box.configure(state="normal")
                    self.log_box.insert("end", value + "\n")
                    self.log_box.see("end")
                    self.log_box.configure(state="disabled")
                elif kind == "progress":
                    percent, message = value
                    self.progress["value"] = percent
                    self.progress_label.configure(text=f"{message} ({percent}%)")
                elif kind == "status":
                    self.status_label.configure(text=value)
                elif kind == "installed":
                    self.installed_label.configure(text="Versión instalada: " + value)
                elif kind == "latest":
                    self.latest_label.configure(text="Última versión npm: " + value)
                elif kind == "error":
                    messagebox.showerror("Error", value, parent=self)
                elif kind == "info":
                    messagebox.showinfo("DeepSeek Harness", value, parent=self)
                elif kind == "done":
                    self.busy = False
                    for button in self.buttons:
                        button.configure(state="normal")
                    self.installed_label.configure(text="Versión instalada: " + installed_version())
                    self.progress["value"] = 100
                    self.progress_label.configure(text="Proceso completado (100%)")
        except queue.Empty:
            pass
        self.after(120, self._poll)

    def _start(self, title, worker):
        if self.busy:
            return
        self.busy = True
        self.progress["value"] = 0
        self.progress_label.configure(text=title)
        for button in self.buttons:
            button.configure(state="disabled")
        self.log(title)
        def run():
            try:
                worker()
            except Exception as exc:
                self.log("ERROR: " + str(exc))
                self.events.put(("error", str(exc)))
            finally:
                self.events.put(("done", None))
        threading.Thread(target=run, daemon=True).start()

    def refresh_status(self):
        if self.status_checking or self.busy:
            return
        self.status_checking = True
        self.status_label.configure(text="Comprobando Node.js y npm…")
        self.latest_label.configure(text="Última versión npm: consultando registro oficial…")
        self.installed_label.configure(text="Versión instalada: " + installed_version())
        self.log("Comprobando requisitos y consultando registry.npmjs.org…")
        def worker():
            ok, detail = runtime_status()
            self.events.put(("status", ("✓ " if ok else "✗ ") + detail))
            try:
                latest = latest_npm_version()
                self.events.put(("latest", latest))
                self.log("Última versión publicada en npm: " + latest)
            except Exception as exc:
                self.events.put(("latest", "no disponible (" + str(exc) + ")"))
                self.log("No se pudo consultar el registro npm: " + str(exc))
            self.status_checking = False
        threading.Thread(target=worker, daemon=True).start()

    def install(self):
        def worker():
            ok, detail = runtime_status()
            self.events.put(("status", ("✓ " if ok else "✗ ") + detail))
            if not ok:
                raise RuntimeError(detail)
            node, npm, _ = runtime_paths()
            self.progress_update(5, "Consultando versión publicada en npm…")
            latest = latest_npm_version()
            self.log("Versión publicada en npm: " + latest)
            current = installed_version()
            if current == latest and (OPT / "node_modules/.bin/dsh").exists():
                self.log("Ya está instalada la última versión. No es necesario descargar de nuevo.")
                self.progress_update(90, "Comprobando accesos…")
            else:
                self.progress_update(10, "Preparando instalación…")
                run_npm_install(node, npm, latest, self._worker_event)
                self.progress_update(82, "Verificando paquete instalado…")
            package_file = OPT / "node_modules" / "@deepseek-ai" / "dsh" / "package.json"
            if not package_file.is_file() or not (OPT / "node_modules/.bin/dsh").exists():
                raise RuntimeError("npm terminó, pero no se ha encontrado el paquete y el comando dsh.")
            verified = installed_version()
            if verified != latest:
                self.log(f"Aviso: npm publica {latest}, pero el paquete instalado informa {verified}.")
            self.progress_update(90, "Creando acceso al menú e icono…")
            write_launchers(self._worker_event)
            self.progress_update(100, "Instalación verificada.")
            self.events.put(("info",
                "¡INSTALACIÓN COMPLETADA!\n\n"
                f"DeepSeek Harness {verified} ya está instalado y listo para utilizarse.\n\n"
                "¿CÓMO ABRIRLO?\n"
                "1. Pulsa «Aceptar» para cerrar este aviso.\n"
                "2. Abre el menú «Aplicaciones» de Ubuntu.\n"
                "3. Busca «DeepSeek Harness» y selecciónalo.\n\n"
                "No necesitas volver a ejecutar este instalador para abrir la aplicación.\n\n"
                "TUS DATOS\n"
                "Tus perfiles, sesiones y configuración se mantienen guardados. "
                "La instalación no ha borrado la carpeta ~/.dsh."))
        self._start("Instalando / actualizando DeepSeek Harness…", worker)

    def _worker_event(self, kind, value):
        if kind == "log":
            self.log(value)

    def repair(self):
        def worker():
            if not (OPT / "node_modules/.bin/dsh").exists():
                raise RuntimeError("DeepSeek Harness no está instalado. Usa primero Instalar / actualizar.")
            self.progress_update(30, "Recreando lanzador e icono…")
            write_launchers(self._worker_event)
            self.progress_update(100, "Accesos reparados.")
            self.events.put(("info", "Se han reparado el comando, el icono y el acceso al menú de aplicaciones."))
        self._start("Reparando accesos…", worker)

    def uninstall(self):
        if not messagebox.askyesno("Desinstalar", "Se eliminará la aplicación y sus accesos.\n\n"
            "La carpeta ~/.dsh, con perfiles, sesiones y configuración, NO se eliminará. ¿Continuar?", parent=self):
            return
        def worker():
            self.progress_update(15, "Cerrando y eliminando la aplicación…")
            # Eliminar únicamente la instalación administrada; nunca tocar ~/.dsh.
            if OPT.exists():
                shutil.rmtree(OPT)
            self.progress_update(45, "Eliminando lanzador, icono y entrada del menú…")
            removed = []
            for path in (LAUNCHER, DESKTOP, ICON):
                try:
                    if path.is_file() or path.is_symlink():
                        path.unlink()
                        removed.append(str(path))
                except OSError as exc:
                    raise RuntimeError("No se pudo eliminar " + str(path) + ": " + str(exc))
            self.log("Elementos eliminados: " + (", ".join(removed) if removed else "no había accesos previos"))
            if DATA.exists():
                self.log("Datos personales conservados: " + str(DATA))
            self.progress_update(75, "Actualizando menú e iconos…")
            for command in (["update-desktop-database", str(APPS)],
                            ["xdg-desktop-menu", "forceupdate", "--mode", "user"],
                            ["gtk-update-icon-cache", "-f", "-t", str(ICONS / "hicolor")]):
                executable = shutil.which(command[0])
                if executable:
                    subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
            self.progress_update(100, "Desinstalación completada.")
            self.log("Desinstalación completada. Los datos de ~/.dsh se han conservado.")
            self.events.put(("info", "DeepSeek Harness se ha desinstalado. ~/.dsh permanece intacta."))
        self._start("Desinstalando DeepSeek Harness…", worker)

    def open_guide(self):
        filename = "Guia-DeepSeek-Harness-Punto-Vuela-Montejaque.pdf"
        destination = LOCAL / "share" / "doc" / "deepseek-harness-installer" / filename
        bundled = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) / filename
        if not bundled.is_file():
            bundled = Path(__file__).resolve().parent / filename
        try:
            if not bundled.is_file():
                raise FileNotFoundError("No se encuentra la guía PDF incluida en el instalador.")
            destination.parent.mkdir(parents=True, exist_ok=True)
            if bundled.resolve() != destination.resolve():
                shutil.copy2(str(bundled), str(destination))
            subprocess.Popen(["xdg-open", str(destination)], stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True)
        except Exception as exc:
            messagebox.showerror("No se pudo abrir la guía", str(exc) +
                "\n\nPuedes descargarla desde GitHub Releases.", parent=self)


if __name__ == "__main__":
    if "--smoke-test" in sys.argv:
        print("DeepSeek Harness Installer: packaged runtime OK")
        raise SystemExit(0)
    Installer().mainloop()
