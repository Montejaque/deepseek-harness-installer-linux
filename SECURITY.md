# Seguridad

- Este instalador descarga exclusivamente el paquete publicado `@deepseek-ai/dsh` desde el registro npm configurado en npm.
- No solicita ni almacena claves API.
- No requiere privilegios root y no debe ejecutarse con `sudo`.
- Los datos de usuario se mantienen en `~/.dsh` y no se eliminan al desinstalar el paquete.
- DeepSeek Harness puede leer y modificar los archivos del espacio de trabajo y ejecutar herramientas. Revisa los permisos y avisos de seguridad del proyecto oficial antes de usarlo.
- El software oficial está en Developer Preview; confirma las versiones y notas de publicación antes de actualizar.
- Informa de vulnerabilidades de este instalador mediante GitHub Security Advisories del repositorio.
