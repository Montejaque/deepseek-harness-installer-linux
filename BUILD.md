# Compilación y publicación de DeepSeek Harness Installer

El proyecto se compila sobre Ubuntu 20.04 (glibc 2.31) para mantener compatibilidad con Linux x86_64.

## Dependencias de compilación

- Python 3, Tkinter y Tcl/Tk
- PyInstaller 5.13.2
- ReportLab
- appimagetool
- Xvfb, xauth y xdotool para las pruebas de interfaz

En GitHub Actions se instalan automáticamente dentro del contenedor Ubuntu 20.04. Para una compilación local, instala PyInstaller y ReportLab en tu entorno Python y proporciona `appimagetool` en el PATH.

## Generar la AppImage

```bash
python3 -m pip install PyInstaller==5.13.2 reportlab
chmod +x build.sh
./build.sh
```

Los artefactos se generan en `dist/`:

- `DeepSeek-Harness-Installer-x86_64.AppImage`
- `SHA256SUMS`
- `Guia-DeepSeek-Harness-Punto-Vuela-Montejaque.pdf`

La guía PDF se incorpora a la AppImage y se abre desde **Ver guía de uso**.

## Runtime de usuario

La AppImage no incluye una copia estática de Node.js. En la primera instalación, el gestor consulta el índice oficial de Node.js, descarga la última versión LTS 24 compatible con el requisito mínimo 24.9.0, verifica el SHA256 publicado por nodejs.org y la instala en:

`~/.local/opt/deepseek-harness/runtime/node`

El npm incluido en esa distribución se utiliza para instalar `@deepseek-ai/dsh`. No se modifica Node.js del sistema ni se necesita NVM, sudo o acceso de administrador. Se requiere conexión a Internet durante la preparación del runtime y la instalación del paquete.

## Lanzador GNOME

El acceso del menú ejecuta `~/.local/bin/deepseek-harness`. El lanzador:

1. Usa exclusivamente el Node.js privado.
2. Comprueba el puerto TCP `127.0.0.1:3080`.
3. Si ya existe un servidor, abre la instancia existente en el navegador.
4. Si no existe, inicia `dsh web`, espera a que el puerto esté disponible y abre la interfaz.
5. Si falla, muestra un diagnóstico y conserva el registro en `~/.local/state/deepseek-harness/launcher.log`.

Los diagnósticos propios de Harness se guardan en `~/.dsh/logs/`. No se finalizan procesos externos automáticamente.

## Comprobaciones de CI

El workflow valida sintaxis Python y Bash, prueba la selección de la etiqueta npm `next` (con alternativa `latest`), comprueba que el runtime se prepara aunque no exista Node.js en el PATH, construye la AppImage en Ubuntu 20.04, verifica la ventana gráfica real mediante Xvfb y valida el archivo y su SHA256.

La prueba automatizada de ventana no sustituye la comprobación funcional de instalación y arranque en un escritorio Linux real.

## Publicación

Los cambios en `main` ejecutan validación, compilación y publicación. Las versiones estables se publican como releases normales, no como prereleases. Cada artefacto incluye su suma SHA256.
