# Construcción de la AppImage

## Entorno

La construcción está pensada para Linux x86_64 y debe ejecutarse en Ubuntu 20.04 para maximizar la compatibilidad con glibc 2.31. Requiere Python 3, Tkinter, `appimagetool` y FUSE en el sistema anfitrión donde se ejecute la AppImage.

## Construcción local

```bash
python3 -m py_compile installer.py
./build.sh
```

El resultado se genera en `dist/DeepSeek-Harness-Installer-x86_64.AppImage`.

## Nota importante sobre dependencias

Esta primera versión es un prototipo funcional de interfaz y gestión npm: la AppImage depende de Python 3 y Tkinter del sistema anfitrión. Para una distribución autocontenida al estilo de los instaladores anteriores, la siguiente iteración debe incorporar un runtime Python/Tk compatible dentro del AppDir y validar AppImage en Ubuntu 20.04 sin dependencias preinstaladas. No se debe anunciar como completamente autocontenida hasta superar esa prueba.
