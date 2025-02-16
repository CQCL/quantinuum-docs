!(function () {
  'use strict'
  const e = 'data-theme-mode',
    d = (e) => {
      var d
      return (
        ('system' === e &&
          (null ===
            (d =
              null === window || void 0 === window
                ? void 0
                : window.matchMedia) || void 0 === d
            ? void 0
            : d.call(window, '(prefers-color-scheme: dark)').matches)) ||
        'dark' === e
      )
    },
    t = () => {
      const t = localStorage.getItem(e),
        o = null !== t && ['system', 'dark', 'light'].includes(t) ? t : 'dark'
      return { mode: o, isDark: d(o) }
    },
    o = () => {
      t().isDark
        ? document.documentElement.classList.add('theme-mode-dark')
        : document.documentElement.classList.remove('theme-mode-dark')
    },
    r = (e) => (
      e(),
      window.addEventListener('storage', e),
      window
        .matchMedia('(prefers-color-scheme: dark)')
        .addEventListener('change', e),
      () => {
        window.removeEventListener('storage', e),
          window
            .matchMedia('(prefers-color-scheme: dark)')
            .removeEventListener('change', e)
      }
    )
  ;(() => {
    r(o)
  })()
})()
