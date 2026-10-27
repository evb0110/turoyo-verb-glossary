import type { Directive } from 'vue'

// v-overflow-title: the element's text becomes its tooltip only while an ellipsis cuts it off,
// so tooltips appear where they explain something and nowhere else.
function titleIfClipped(event: Event) {
    const element = event.currentTarget as HTMLElement
    if (element.scrollWidth > element.clientWidth) element.title = element.textContent?.trim() || ''
    else element.removeAttribute('title')
}
const overflowTitle: Directive<HTMLElement> = {
    mounted(element) {
        element.addEventListener('mouseenter', titleIfClipped)
    },
    beforeUnmount(element) {
        element.removeEventListener('mouseenter', titleIfClipped)
    },
}
export default defineNuxtPlugin((nuxtApp) => {
    nuxtApp.vueApp.directive('overflow-title', overflowTitle)
})
