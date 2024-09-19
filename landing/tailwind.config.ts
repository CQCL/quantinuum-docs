//@ts-ignore
import { tailwindTheme } from "@cqcl/quantinuum-ui";
import path from "path";
import { Config } from "tailwindcss";
import plugin from "tailwindcss/plugin";

const screens = {
  sm: "640px",
  // => @media (min-width: 640px) { ... }

  md: "768px",
  // => @media (min-width: 768px) { ... }

  lg: "1024px",
  // => @media (min-width: 1024px) { ... }

  xl: "1024px",
  // => @media (min-width: 1280px) { ... }

  "2xl": undefined,
} as any;
export default {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    path.join(
      path.dirname(require.resolve("@cqcl/quantinuum-ui")),
      "**/*.{js,ts,jsx,tsx,mdx}",
    ),
  ],
  theme: {
    screens,
    extend: {
      container: {
        padding: "1rem",
        screens,
      },
      animation: {
        "spin-border": "spin 8s linear reverse infinite",
      },
    },
  },
  plugins: [
    plugin(({ matchUtilities, theme }) => {
      matchUtilities(
        {
          "animation-delay": (value) => {
            return {
              "animation-delay": value,
            };
          },
        },
        {
          values: theme("transitionDelay"),
        },
      );
    }),
  ],
  presets: [tailwindTheme],
} satisfies Config;
