import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        okj: {
          "bg-deep": "#17233D",
          surface: "#1B2740",
          card: "#202E4D",
          "card-border": "#2C3A5C",
          gold: "#D3A85C",
          parchment: "#EDE4D3",
          "parchment-text": "#3A2E1C",
          terracotta: "#C1694A",
          "text-primary": "#F3EDE0",
          "text-secondary": "#9BA6C4",
          "text-muted": "#6B7694",
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "Fraunces", "serif"],
        body: ["var(--font-body)", "Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
