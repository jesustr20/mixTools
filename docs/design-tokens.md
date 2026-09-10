# Design tokens — MixTools

**Fuente de verdad:** `frontend-preview/index.html` (el prototipo ya aprobado
en la práctica). Estos valores están copiados literal de ahí — no
reinterpretados. Cuando se porte a React/Tailwind, van directo al
`tailwind.config.js`, no se "recrean" a ojo.

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

## Radios y espaciado

- `radius`: 3px
- Sin `box-shadow` decorativo — bordes de 1px, no sombras difusas

## Reglas de fidelidad

1. Ningún color nuevo sin que esté en esta tabla.
2. Las esquinas de registro del dropzone, el sello "LISTO" rotado, y el
   rail lateral oscuro se portan tal cual, no se simplifican.
3. Si algo no está claro cómo portarlo, se pregunta antes de improvisar.
