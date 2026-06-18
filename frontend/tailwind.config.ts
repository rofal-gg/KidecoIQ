import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        kideco: {
          50: "#f0f9f0",
          100: "#d8f0d8",
          200: "#b3e0b3",
          300: "#7cc97c",
          400: "#4daf4d",
          500: "#2d8f2d",
          600: "#1f7a1f",
          700: "#1a611a",
          800: "#184d18",
          900: "#164016",
        },
      },
    },
  },
  plugins: [],
};

export default config;
