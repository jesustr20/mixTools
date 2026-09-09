# AGENTS.md

Reglas para cualquier agente de código (DeepSeek vía OpenCode, u otro) que
trabaje en este repo. OpenCode lee este archivo automáticamente al arrancar.

## Antes de tocar código

1. **Usá codebase-memory-mcp primero.** Buscá/consultá el grafo del repo
   antes de abrir archivos completos. Si necesitás entender una función,
   usá `trace`/`search` del MCP, no `cat` de todo el módulo.
2. **No inventes estructura.** Si el spec de la tarea no especifica un campo,
   una librería, un estilo o un color — no lo agregues. Si hace falta,
   preguntá en el PR/commit message en vez de asumir. (Esta regla viene
   directo de cómo Jesús trabaja las conversiones de documentos: nunca
   inventar lo que no está confirmado en la fuente.)
3. **Una tarea = un issue = un módulo.** No toques archivos fuera de la
   carpeta del módulo que te asignaron (`app/tools/<módulo>/`) salvo que la
   tarea lo pida explícitamente. Si creés que hace falta tocar algo más,
   decilo en vez de hacerlo.

## Al escribir código

4. Seguí el patrón ya establecido en el módulo: `engine.py` (lógica pura,
   sin FastAPI) + `router.py` (endpoints). No mezcles las dos cosas.
5. No agregues dependencias nuevas sin decirlo explícitamente en tu resumen
   de cambios — cada `pip install` nuevo es una decisión, no un detalle.
6. Los endpoints que hacen trabajo bloqueante (subprocess, PDF, imágenes) van
   como `def`, no `async def` — así FastAPI los corre en threadpool. Ver
   `converter/router.py` como referencia de por qué.
7. Nunca borres una carpeta de trabajo temporal (`workspace`) antes de que la
   respuesta se haya enviado — usá `BackgroundTask`, no un `finally`
   inmediato. Este bug ya se cazó una vez, no lo reintroduzcas.

## Antes de terminar

8. Corré `ruff check app/` y arreglá lo que marque.
9. Si tocaste un endpoint, probalo de verdad con `curl` contra un archivo de
   prueba — no asumas que compila y ya funciona.
10. Dejá un resumen corto de qué cambiaste y por qué, no una lista de diffs.

## Si algo no está claro

No adivines. Un comentario `# TODO: confirmar con Jesús — ¿X o Y?` en el
código o una pregunta en el resumen final es mejor que una decisión
silenciosa que después hay que deshacer.
