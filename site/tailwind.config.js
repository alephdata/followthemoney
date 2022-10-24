module.exports = {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  plugins: [require('@tailwindcss/typography')],
  theme: {
    extend: {
      typography: (theme) => ({
        DEFAULT: {
          css: {
            code: {
              background: theme('colors.gray.200'),
              color: 'inherit',
              padding: theme('space.1'),
              fontWeight: theme('fontWeight.normal'),
              borderRadius: theme('borderRadius.md'),
            },
            'code::before': {
              content: 'none',
            },
            'code::after': {
              content: 'none',
            },
            'pre code': {
              background: 'transparent',
            }
          },
        },

        invert: {
          css: {
            code: {
              background: theme('colors.gray.800'),
            },
            'pre code': {
              background: 'transparent',
            }
          },
        },
      }),
    },
  },
};
