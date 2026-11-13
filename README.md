# DeepSeek Harness Installer for Linux

**Punto Vuela Montejaque · Instalador independiente para Linux**

Instalador gráfico para gestionar [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) en Linux sin permisos de administrador. Se distribuye como AppImage y descarga el paquete oficial `@deepseek-ai/dsh` de npm durante la instalación.

> DeepSeek Harness está en Developer Preview. Este proyecto es independiente y no está afiliado, respaldado ni patrocinado por DeepSeek.

## Funciones

- Interfaz gráfica Python/Tkinter empaquetada con PyInstaller.
- Instalar, actualizar, comprobar, reparar lanzadores y desinstalar.
- Descarga del paquete oficial npm; no redistribuye ni modifica DeepSeek Harness.
- Instalación por usuario, sin sudo, apt, Docker ni escritura en directorios del sistema.
- Acceso directo de escritorio y comando local.
- Conserva los datos de `~/.dsh` al actualizar y desinstalar.

## Requisitos del equipo

- Linux x86_64.
- Node.js compatible con la versión publicada de `@deepseek-ai/dsh` y npm.
- Conexión a Internet para instalar o actualizar.
- Para ejecutar AppImage en sistemas sin FUSE disponible, prueba `--appimage-extract-and-run`.

Comprueba siempre el requisito de Node.js en la [documentación oficial](https://github.com/deepseek-ai/deepseek-harness).

## Descarga y uso

Descarga `DeepSeek-Harness-Installer-x86_64.AppImage` desde [Releases](https://github.com/Montejaque/deepseek-harness-installer-linux/releases) o desde el artefacto de la última ejecución de [GitHub Actions](https://github.com/Montejaque/deepseek-harness-installer-linux/actions).

```bash
chmod +x DeepSeek-Harness-Installer-x86_64.AppImage
./DeepSeek-Harness-Installer-x86_64.AppImage
```

## Ubicaciones

- Aplicación: `~/.local/opt/deepseek-harness/`
- Ejecutables: `~/.local/bin/`
- Acceso de escritorio: `~/.local/share/applications/`
- Datos de DeepSeek Harness: `~/.dsh/` (no se elimina al actualizar ni al desinstalar).

## Desarrollo

Consulta [BUILD.md](BUILD.md). GitHub Actions compila dentro de Ubuntu 20.04 (glibc 2.31) y comprueba que aparece la ventana real del instalador antes de publicar el artefacto. Cada push a `main` publica una compilación preliminar; no se considera estable hasta superar también las pruebas de instalación y ejecución del paquete npm en un equipo de destino.

## Seguridad

DeepSeek Harness puede acceder a archivos y ejecutar herramientas en el espacio de trabajo. Revisa la documentación oficial y protege tus claves API. Este instalador no solicita ni transmite credenciales.

## Licencia

El instalador se publica bajo MIT. DeepSeek Harness y sus dependencias conservan sus propias licencias.
