/**
 * PostCSS Configuration.
 * 
 * Tailwind CSS v4 moved its PostCSS plugin to a separate @tailwindcss/postcss package.
 * This is a breaking change from v3 where 'tailwindcss' was used directly as a plugin.
 */
export default {
  plugins: {
    '@tailwindcss/postcss': {},
    autoprefixer: {},
  },
}
