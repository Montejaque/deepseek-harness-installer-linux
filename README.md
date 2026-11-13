# DeepSeek Harness Installer & Updater — Punto Vuela Montejaque

Gestor gráfico para instalar, actualizar, comprobar, reparar y desinstalar **DeepSeek Harness** en Linux x86_64. Se distribuye como AppImage y realiza la instalación dentro del perfil del usuario, sin permisos root.

## Descargar

- [Última versión publicada](https://github.com/Montejaque/deepseek-harness-installer-linux/releases/latest)
- [Todas las versiones](https://github.com/Montejaque/deepseek-harness-installer-linux/releases)
- [Compilaciones de GitHub Actions](https://github.com/Montejaque/deepseek-harness-installer-linux/actions)

Descarga \`DeepSeek-Harness-Installer-x86_64.AppImage\`, permite su ejecución y abre el gestor:

\`\`\`bash
chmod +x DeepSeek-Harness-Installer-x86_64.AppImage
./DeepSeek-Harness-Installer-x86_64.AppImage
\`\`\`

## Funciones

- Consulta la última versión publicada de \`@deepseek-ai/dsh\` directamente en el registro oficial npm.
- Detecta Node.js y npm en el PATH, NVM y gestores habituales de versiones, incluso cuando la AppImage se abre desde GNOME.
- Instala y actualiza el paquete oficial en el perfil del usuario.
- Evita reinstalar si ya está instalada la última versión.
- Muestra el registro de npm en directo y el progreso de las operaciones.
- Crea el comando \`deepseek-harness\`, el icono SVG y el acceso al menú GNOME.
- Repara los accesos de terminal, icono y menú.
- Incluye una guía PDF de uso, accesible desde el botón **Ver guía de uso**.
- Desinstala solo la copia gestionada y conserva \`~/.dsh\`.

## Rutas de instalación

| Elemento | Ubicación |
|---|---|
| Aplicación y dependencias | \`~/.local/opt/deepseek-harness\` |
| Comando | \`~/.local/bin/deepseek-harness\` |
| Menú GNOME | \`~/.local/share/applications/deepseek-harness.desktop\` |
| Icono | \`~/.local/share/icons/hicolor/scalable/apps/deepseek-harness.svg\` |
| Perfiles, sesiones y configuración | \`~/.dsh\` (se conserva) |

## Requisitos

- Linux x86_64.
- Node.js 22.19.0 o superior, o Node.js 24+.
- npm compatible.
- Conexión a Internet para consultar npm e instalar el paquete.
- Entorno gráfico compatible con AppImage.

El instalador no ejecuta \`sudo\`, no instala paquetes del sistema y no modifica \`/usr\`, \`/opt\` global ni la configuración del sistema.

## Guía de uso

La guía PDF se abre desde el botón **Ver guía de uso** de la aplicación. También se genera durante la compilación en \`docs/generate_guide.py\`.

## Compilación

Consulta [BUILD.md](BUILD.md). GitHub Actions compila sobre Ubuntu 20.04 (glibc 2.31), comprueba que la ventana real se muestra y publica un Release con AppImage y SHA256.

## Fuente oficial

- Paquete npm: [@deepseek-ai/dsh](https://www.npmjs.com/package/@deepseek-ai/dsh)
- Registro npm: [registry.npmjs.org](https://registry.npmjs.org/)

## Autoría

**Desarrollador:** Francisco Javier Gallego Orellana  
**Centro:** Punto Vuela Montejaque  
Avenida Andalucía, 48 · 29360 Montejaque (Málaga)  
Teléfono: 633 402 959  
Correo: montejaque@puntosvuela.es  
Web: https://puntosvuela.es/centros/montejaque

**Identidad visual:** negro \`#171717\` y amarillo \`#F3D54E\`.  
**Licencia:** MIT.
