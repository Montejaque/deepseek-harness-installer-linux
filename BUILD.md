# Compilación del AppImage

El proyecto se compila en Ubuntu 20.04 para mantener compatibilidad con sistemas Linux x86_64 que utilizan glibc 2.31.

## Dependencias de compilación

- Python 3
- Tkinter y Tcl/Tk
- PyInstaller 5.13.2
- ReportLab
- appimagetool
- Xvfb (para la prueba de la interfaz gráfica)

En el contenedor de Ubuntu 20.04 utilizado por GitHub Actions se instalan las dependencias automáticamente. Para una compilación local, instala PyInstaller y ReportLab en el entorno de Python disponible y proporciona \`appimagetool\` en el PATH.

## Generar el AppImage

\`\`\`bash
python3 -m pip install PyInstaller==5.13.2 reportlab
chmod +x build.sh
./build.sh
\`\`\`

El resultado se guarda en:

- \`dist/DeepSeek-Harness-Installer-x86_64.AppImage\`
- \`dist/SHA256SUMS\`
- \`dist/Guia-DeepSeek-Harness-Punto-Vuela-Montejaque.pdf\`

El PDF se incorpora a la AppImage y se abre desde el botón **Ver guía de uso**.

## Comprobaciones

El workflow valida la sintaxis Python y Bash, genera la guía, compila el AppImage, comprueba que la ventana gráfica real aparece mediante Xvfb, verifica el tipo de archivo y valida SHA256 antes de publicar.

La aplicación final debe probarse también en una sesión gráfica Linux real. La compilación automatizada no sustituye la validación funcional de la instalación npm en el equipo de destino.
