import path from 'path'
import { Config } from 'tailwindcss'
import plugin from 'tailwindcss/plugin'
import { tailwindTheme } from '@cqcl/quantinuum-ui'
export default {
    content: [
        './src/**/*.{js,ts,jsx,tsx,mdx,html}',
        path.join(
          path.dirname(require.resolve('@cqcl/quantinuum-ui')),
          '**/*.{js,ts,jsx,tsx,mdx}'
        ),
    ],
    theme: {
      extend: {
        screens: {
          wide: '1600px',
        },
        fontFamily: {
          'inter': ['Inter', 'sans-serif'],
        },
      },
    },
    plugins: [
        plugin(({ matchUtilities, theme }) => {
          matchUtilities(
            {
              'animation-delay': (value) => {
                return {
                  'animation-delay': value,
                }
              },
            },
            {
              values: theme('transitionDelay'),
            }
          )
        }),
      ],
      presets: [tailwindTheme]
} satisfies Config
