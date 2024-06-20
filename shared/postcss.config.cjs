module.exports = {
    plugins: {
      'postcss-import': {},
      'tailwindcss/nesting': {},
      tailwindcss: {},
      autoprefixer: {},
      'postcss-prefix-selector': {
        prefix: '.use-tailwind',
      },
    },
  }
  