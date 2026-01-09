const path = require('path');

module.exports = {
  content: [
      // Absolute paths from project root (assuming build runs from theme/static_src)
      '../../core/templates/**/*.html',
      '../templates/**/*.html',
      '../../templates/**/*.html',
  ],
  darkMode: 'class',
  safelist: [
    'flex-col',
    'min-h-screen',
    'w-full',
    'flex-grow',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}