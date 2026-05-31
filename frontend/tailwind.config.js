/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        "border-strong": "hsl(var(--border-strong))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        paper: "hsl(var(--paper))",
        sunken: "hsl(var(--sunken))",
        elevated: "hsl(var(--elevated))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        // Petrol scale (ADR-0010 primary).
        petrol: {
          50: "#E6F2F4",
          100: "#C2DEE3",
          200: "#94C5CD",
          300: "#5FA5B2",
          400: "#2F8497",
          500: "#15728A",
          600: "#0E5C6F",
          700: "#0B4A5A",
          800: "#093C49",
          900: "#062A33",
        },
        // Charcoal neutral with slight petrol cast (not pure gray).
        charcoal: {
          50: "#F6F8F9",
          100: "#EBEFF1",
          200: "#D4DBDF",
          300: "#A8B4BB",
          400: "#7B8A93",
          500: "#566570",
          600: "#3F4B54",
          700: "#2B343A",
          800: "#1B2226",
          900: "#0F1417",
        },
        // Status palette: caution (amber) and negative (wine) — clinical, not bright red.
        amber: {
          50: "#FFF8EB",
          100: "#FDECC8",
          500: "#D97706",
          700: "#B45309",
        },
        wine: {
          50: "#FBE9EE",
          100: "#F5C9D4",
          500: "#B91C44",
          600: "#A0173A",
          700: "#85132F",
        },
        // Status semantic shortcuts.
        affirmed: "hsl(var(--status-affirmed))",
        "affirmed-soft": "hsl(var(--status-affirmed-soft))",
        caution: "hsl(var(--status-caution))",
        "caution-soft": "hsl(var(--status-caution-soft))",
        negative: "hsl(var(--status-negative))",
        "negative-soft": "hsl(var(--status-negative-soft))",
      },
      keyframes: {
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
      },
      borderRadius: {
        // ADR-0011: clinical-sharp radius scale anchored at 2px.
        lg: "var(--radius)",
        md: "calc(var(--radius) - 1px)",
        sm: "calc(var(--radius) - 2px)",
      },
      fontFamily: {
        sans: [
          "'Inter Variable'",
          "Inter",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [],
};
