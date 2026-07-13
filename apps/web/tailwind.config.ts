import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#08090F",
        surface: "#0F1219",
        border: "#1C2133",
        orange: "#FF5F1F",
        teal: "#00C896",
        blue: "#3B82F6",
        yellow: "#F5B642",
        red: "#FF4757",
        txt: "#DDE3F0",
        txt2: "#8A97B4",
      },
      fontFamily: {
        display: ["Space Grotesk", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
