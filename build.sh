#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
APP="DeepSeekHarnessInstaller"
DIST="$ROOT/dist"
mkdir -p "$DIST"
python3 -m py_compile installer.py
command -v appimagetool >/dev/null 2>&1 || {
  echo "appimagetool no está instalado. Consulta BUILD.md." >&2
  exit 1
}
rm -rf "$DIST/$APP.AppDir"
mkdir -p "$DIST/$APP.AppDir/usr/bin" "$DIST/$APP.AppDir/usr/share/applications"
cp installer.py "$DIST/$APP.AppDir/usr/bin/installer.py"
cat > "$DIST/$APP.AppDir/AppRun" <<'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
exec python3 "$HERE/usr/bin/installer.py" "$@"
EOF
chmod +x "$DIST/$APP.AppDir/AppRun"
cat > "$DIST/$APP.AppDir/deepseek-harness-installer.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=DeepSeek Harness Installer
Comment=Instalador de DeepSeek Harness para Linux
Exec=AppRun
Terminal=false
Categories=Development;Utility;
EOF
cp "$DIST/$APP.AppDir/deepseek-harness-installer.desktop" "$DIST/$APP.AppDir/usr/share/applications/"
cat > "$DIST/$APP.AppDir/deepseek-harness-installer.svg" <<'EOF'
<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">
<rect width="256" height="256" rx="52" fill="#172b55"/>
<path d="M128 38 207 83v90l-79 45-79-45V83z" fill="none" stroke="#75a7ff" stroke-width="14"/>
<path d="m78 105 50-29 50 29v49l-50 29-50-29z" fill="none" stroke="#fff" stroke-width="12"/>
<circle cx="128" cy="129" r="14" fill="#75a7ff"/>
</svg>
EOF
cp "$DIST/$APP.AppDir/deepseek-harness-installer.svg" "$DIST/$APP.AppDir/.DirIcon"
ARCH=x86_64 appimagetool "$DIST/$APP.AppDir" "$DIST/DeepSeek-Harness-Installer-x86_64.AppImage"
sha256sum "$DIST/DeepSeek-Harness-Installer-x86_64.AppImage" > "$DIST/SHA256SUMS"
