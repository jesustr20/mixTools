# Design tokens — MixTools

**Fuente de verdad:** `frontend-preview/index.html` (el prototipo ya aprobado
en la práctica) para colores y tipografía. Los radios y sombras se
actualizaron después (ver sección de abajo), calibrados contra los valores
reales de Ant Design (su token base `radius` es 4px, botones ~6-8px) para
que se sienta "software moderno" sin volverse un redondeo tipo pastilla.

## Colores

| Token | Hex | Uso |
|---|---|---|
| `ink` | `#1B2430` | Rail lateral, texto fuerte |
| `ink-soft` | `#2A3648` | Hover del rail |
| `paper` | `#EEF3F1` | Fondo principal |
| `paper-raised` | `#F8FAF9` | Tarjetas, chips |
| `graphite` | `#22262B` | Texto de cuerpo |
| `graphite-soft` | `#5B6570` | Texto secundario |
| `line` | `#C9CDCB` | Bordes, guías |
| `blue` | `#2F5FA3` | Acción primaria |
| `blue-dark` | `#254c85` | Hover del azul |
| `stamp` | `#B23A2E` | Éxito/confirmación — uso mínimo, no decorativo |

## Tipografía

- **UI/headings**: Archivo (600-700)
- **Cuerpo**: IBM Plex Sans (400-600)
- **Metadatos de archivo** (nombre, tamaño, tipo): IBM Plex Mono — solo
  para eso, no usar monoespaciada en otro lado

## Radios y sombras (actualizado)

- Botones y chips: `border-radius: 8px`
- Dropzone y tarjetas de resultado: `border-radius: 6px`
- Sombra sutil en botones/tarjetas: `box-shadow: 0 1px 2px rgba(27, 36, 48, 0.08)`
  — apenas perceptible, da sensación de "elevación" sin volverse pesada
- Las esquinas de registro del dropzone (`.corner`, las marcas en L) NO
  cambian — son un elemento de identidad aparte, no se redondean ni se
  quitan, conviven con el `border-radius` del contenedor

## Reglas de fidelidad

1. Ningún color nuevo sin que esté en esta tabla.
2. Las esquinas de registro del dropzone, el sello "LISTO" rotado, y el
   rail lateral oscuro se portan tal cual, no se simplifican.
3. Si algo no está claro cómo portarlo, se pregunta antes de improvisar.
