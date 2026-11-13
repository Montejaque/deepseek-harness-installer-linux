#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
DIST="$ROOT/dist"
APPDIR="$DIST/DeepSeekHarnessInstaller.AppDir"
mkdir -p "$DIST"

python3 -m py_compile installer.py
command -v pyinstaller >/dev/null 2>&1 || {
  echo "PyInstaller no está instalado. Ejecuta: python3 -m pip install PyInstaller==5.13.2" >&2
  exit 1
}
command -v appimagetool >/dev/null 2>&1 || {
  echo "appimagetool no está instalado. Consulta BUILD.md." >&2
  exit 1
}

rm -rf "$DIST/pyinstaller" "$DIST/work" "$APPDIR"
rm -f "$ROOT/DeepSeekHarnessInstaller.spec"
pyinstaller --clean --noconfirm --onedir --name DeepSeekHarnessInstaller \
  --hidden-import=ipaddress \
  --distpath "$DIST/pyinstaller" --workpath "$DIST/work" installer.py

# PyInstaller 5.13's bootstrap imports urllib.parse before its PYZ importer is
# active. Ensure ipaddress is also present in base_library.zip (not only PYZ).
BASE_LIBRARY="$(find "$DIST/pyinstaller/DeepSeekHarnessInstaller" -name base_library.zip -print -quit)"
if [[ -z "$BASE_LIBRARY" ]]; then
  echo "No se ha encontrado base_library.zip en el paquete PyInstaller." >&2
  exit 1
fi
python3 - "$BASE_LIBRARY" <<'PY'
import pathlib
import sys
import sysconfig
import zipfile

archive = pathlib.Path(sys.argv[1])
module = pathlib.Path(sysconfig.get_path("stdlib")) / "ipaddress.py"
if not module.is_file():
    raise SystemExit(f"No se encuentra el módulo estándar: {module}")
with zipfile.ZipFile(archive, "a", compression=zipfile.ZIP_DEFLATED) as bundle:
    if "ipaddress.py" not in bundle.namelist():
        bundle.write(module, "ipaddress.py")
with zipfile.ZipFile(archive) as bundle:
    if "ipaddress.py" not in bundle.namelist():
        raise SystemExit("ipaddress.py no se ha incluido en base_library.zip")
print(f"ipaddress añadido a {archive}")
PY

mkdir -p "$APPDIR/usr/lib" "$APPDIR/usr/share/applications" "$APPDIR/usr/share/icons/hicolor/scalable/apps"
cp -a "$DIST/pyinstaller/DeepSeekHarnessInstaller" "$APPDIR/usr/lib/"
cat > "$APPDIR/AppRun" <<'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/usr/lib/DeepSeekHarnessInstaller/DeepSeekHarnessInstaller" "$@"
EOF
chmod +x "$APPDIR/AppRun"
cat > "$APPDIR/deepseek-harness-installer.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=DeepSeek Harness Installer
Comment=Instalador de DeepSeek Harness para Linux
Exec=AppRun
Icon=deepseek-harness-installer
Terminal=false
Categories=Development;Utility;
EOF
cp "$APPDIR/deepseek-harness-installer.desktop" "$APPDIR/usr/share/applications/"
cat > "$APPDIR/deepseek-harness-installer.svg" <<'EOF'
<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">
<rect width="256" height="256" rx="52" fill="#172b55"/>
<path d="M128 38 207 83v90l-79 45-79-45V83z" fill="none" stroke="#75a7ff" stroke-width="14"/>
<path d="m78 105 50-29 50 29v49l-50 29-50-29z" fill="none" stroke="#fff" stroke-width="12"/>
<circle cx="128" cy="129" r="14" fill="#75a7ff"/>
</svg>
EOF
cp "$APPDIR/deepseek-harness-installer.svg" "$APPDIR/.DirIcon"
cp "$APPDIR/deepseek-harness-installer.svg" "$APPDIR/usr/share/icons/hicolor/scalable/apps/deepseek-harness-installer.svg"

ARCH=x86_64 APPIMAGE_EXTRACT_AND_RUN=1 appimagetool "$APPDIR" "$DIST/DeepSeek-Harness-Installer-x86_64.AppImage"
# Smoke-test the packaged executable without requiring a graphical display.
APPIMAGE_EXTRACT_AND_RUN=1 "$DIST/DeepSeek-Harness-Installer-x86_64.AppImage" --smoke-test
sha256sum "$DIST/DeepSeek-Harness-Installer-x86_64.AppImage" > "$DIST/SHA256SUMS"
