/**
 * Reordenamiento de listas por id (usado por el drag-and-drop de Unir PDFs).
 *
 * Función pura, sin dependencia de React ni de dnd-kit, para poder testearla
 * aislada: dado el array de items, el id del elemento arrastrado y el id del
 * elemento sobre el que se suelta, devuelve un array nuevo con el elemento
 * movido a la posición del destino.
 */
export function reorderById<T extends { id: string }>(
  items: T[],
  activeId: string,
  overId: string,
): T[] {
  const oldIndex = items.findIndex((item) => item.id === activeId)
  const newIndex = items.findIndex((item) => item.id === overId)

  if (oldIndex === -1 || newIndex === -1 || oldIndex === newIndex) return items

  const next = items.slice()
  const [moved] = next.splice(oldIndex, 1)
  next.splice(newIndex, 0, moved)
  return next
}
