# DeepSeek Harness Installer for Linux

**Punto Vuela Montejaque · Instalador independiente para Linux**

Instalador gráfico para gestionar [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) en Linux sin permisos de administrador. El instalador se distribuye como AppImage y descarga el paquete oficial `@deepseek-ai/dsh` de npm durante la instalación.

> DeepSeek Harness está en Developer Preview y puede introducir cambios incompatibles. Este proyecto no está afiliado, respaldado ni patrocinado por DeepSeek.

## Funciones

- Interfaz gráfica GTK mediante Python + Tkinter.
- Instalación, actualización, comprobación, reparación y desinstalación.
- Descarga del paquete oficial de npm; no redistribuye ni modifica DeepSeek Harness.
- Instalación por usuario, sin `sudo`, `apt`, Docker ni escritura en directorios del sistema.
- Lanzador de escritorio y comando local.
- Conserva los datos y perfiles de `~/.dsh` al actualizar y desinstalar (la eliminación de datos se ofrece como acción separada y explícita en futuras versiones).
- Comprueba Node.js y npm antes de instalar.

## Requisitos

- Linux x86_64.
- Node.js compatible con la versión publicada de `@deepseek-ai/dsh`. La documentación actual indica Node.js `^22.19.0 || >=24.0.0`; verifica la versión exigida en el paquete antes de instalar.
- npm incluido con Node.js.
- Para construir la AppImage: Ubuntu 20.04 o compatible, Python 3, Tkinter y herramientas de empaquetado de AppImage.

## Instalación

Descarga `DeepSeek-Harness-Installer-x86_64.AppImage` desde [Releases](https://github.com/Montejaque/deepseek-harness-installer-linux/releases), ejecuta:

```bash
chmod +x DeepSeek-Harness-Installer-x86_64.AppImage
./DeepSeek-Harness-Installer-x86_64.AppImage
```

La AppImage es el instalador, no contiene el programa de DeepSeek. Se requiere conexión a Internet para descargarlo desde npm.

## Ubicaciones

- Aplicación: `~/.local/opt/deepseek-harness/`
- Ejecutables: `~/.local/bin/`
- Acceso de escritorio: `~/.local/share/applications/`
- Iconos: `~/.local/share/icons/`
- Datos de usuario de DeepSeek Harness: `~/.dsh/` (no se elimina al actualizar ni al desinstalar).

## Desarrollo

Consulta [BUILD.md](BUILD.md) para compilar localmente. GitHub Actions valida el código y genera una AppImage en cada push a `main`; al publicar una etiqueta `v*`, crea una Release con el artefacto.

## Seguridad y privacidad

DeepSeek Harness es un agente que puede acceder a archivos y ejecutar herramientas dentro del espacio de trabajo configurado. Revisa la [documentación y avisos de seguridad oficiales](https://github.com/deepseek-ai/deepseek-harness) antes de usarlo. Mantén las claves API privadas. Este instalador no solicita ni transmite credenciales.

## Licencia

El instalador se publica bajo MIT. DeepSeek Harness y sus dependencias conservan sus propias licencias.
