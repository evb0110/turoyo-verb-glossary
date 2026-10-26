// Keyboard shortcuts must not fire while someone types in a field.
export function isEditableTarget(target: EventTarget | null) {
    return target instanceof HTMLElement
        && (target.isContentEditable || ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName))
}
