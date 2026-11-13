# Guía de instalación y uso — DeepSeek Harness Installer & Updater

## 1. Descargar y ejecutar el gestor

Descarga \`DeepSeek-Harness-Installer-x86_64.AppImage\` desde [GitHub Releases](https://github.com/Montejaque/deepseek-harness-installer-linux/releases/latest). En la carpeta de descarga:

\`\`\`bash
chmod +x DeepSeek-Harness-Installer-x86_64.AppImage
./DeepSeek-Harness-Installer-x86_64.AppImage
\`\`\`

No uses sudo. La AppImage contiene el gestor gráfico; el paquete DeepSeek Harness se descarga al instalar.

## 2. Requisitos de Node.js

Se requiere Node.js 22.19.0 o superior, o Node.js 24+, junto con npm. El gestor busca Node.js y npm tanto en el PATH como en instalaciones habituales de NVM, incluso cuando se abre desde el menú de aplicaciones.

## 3. Instalar o actualizar

Pulsa **Instalar / actualizar**. El gestor consulta la etiqueta latest del registro oficial npm. Si ya tienes esa versión instalada, evita repetir la descarga. Si hay una versión nueva, ejecuta npm install y muestra las líneas del proceso en el registro de operaciones.

## 4. Comprobar versiones

Pulsa **Comprobar versiones** para consultar Node.js, npm, la versión instalada y la última versión publicada en npm. La consulta al registro npm es independiente de NVM y no necesita que npm esté cargado en el PATH del escritorio.

## 5. Accesos directos e icono

El instalador crea:
- Comando de terminal: \`~/.local/bin/deepseek-harness\`
- Acceso del menú GNOME: \`~/.local/share/applications/deepseek-harness.desktop\`
- Icono SVG: \`~/.local/share/icons/hicolor/scalable/apps/deepseek-harness.svg\`

El menú inicia \`dsh web\` en un terminal. Si GNOME no muestra el acceso inmediatamente, cierra sesión y vuelve a entrar para reconstruir su catálogo.

## 6. Reparar accesos

Pulsa **Reparar acceso** para volver a crear el lanzador, el icono, el archivo .desktop y actualizar las cachés disponibles del escritorio.

## 7. Desinstalar

Pulsa **Desinstalar** y confirma. Se elimina la copia administrada y sus accesos. No se elimina \`~/.dsh\`, donde se conservan perfiles, sesiones y configuración.

## 8. Ubicaciones

- Aplicación: \`~/.local/opt/deepseek-harness\`
- Comando: \`~/.local/bin/deepseek-harness\`
- Menú GNOME: \`~/.local/share/applications/deepseek-harness.desktop\`
- Icono: \`~/.local/share/icons/hicolor/scalable/apps/deepseek-harness.svg\`
- Datos personales: \`~/.dsh\` (se conserva)

## 9. Desarrollador y contacto

**Desarrollador:** Francisco Javier Gallego Orellana  
**Centro:** Punto Vuela Montejaque  
**Dirección:** Avenida Andalucía, 48 · 29360 Montejaque (Málaga)  
**Teléfono:** 633 402 959  
**Correo:** montejaque@puntosvuela.es  
**Web:** https://puntosvuela.es/centros/montejaque

Identidad visual: negro \`#171717\` y amarillo \`#F3D54E\`.
