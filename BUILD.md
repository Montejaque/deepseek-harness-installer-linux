# Construcción de la AppImage

La AppImage se compila en Ubuntu 20.04 (glibc 2.31) para mantener compatibilidad con el Ubuntu 20.04 del entorno de Punto Vuela.

## Requisitos para compilar localmente

- Python 3 y Tkinter
- PyInstaller 5.13.2
- appimagetool de AppImageKit

```bash
python3 -m pip install 'PyInstaller==5.13.2'
# Instala/descarga appimagetool en PATH
chmod +x build.sh
./build.sh
```

El resultado es `dist/DeepSeek-Harness-Installer-x86_64.AppImage`.

## Portabilidad

PyInstaller empaqueta el intérprete Python, Tk/Tcl y las dependencias de la interfaz dentro del AppDir. La construcción debe realizarse en Ubuntu 20.04 o una base compatible; no compiles en una distribución más nueva si necesitas glibc 2.31.

La AppImage no contiene DeepSeek Harness: descarga el paquete oficial `@deepseek-ai/dsh` desde npm cuando el usuario pulsa Instalar / actualizar. Se necesita Node.js compatible y conexión a Internet en el equipo de destino.

## CI y Releases

Cada push a `main` y cada etiqueta `v*` ejecutan validación y compilación. Los pushes generan un artefacto descargable desde GitHub Actions. Al crear una Release basada en una etiqueta `v*`, el workflow adjunta la AppImage y su SHA256 automáticamente.
