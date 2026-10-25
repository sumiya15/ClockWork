export default [{
  ignores: ['dist/**', 'node_modules/**'],
}, {
  files: ['**/*.{js,jsx}'],
  languageOptions: {
    ecmaVersion: 'latest', sourceType: 'module',
    parserOptions: { ecmaFeatures: { jsx: true } },
    globals: { document: 'readonly', fetch: 'readonly', window: 'readonly', AbortController: 'readonly' },
  },
  rules: {
    'no-unused-vars': ['error', { varsIgnorePattern: '^[A-Z]', argsIgnorePattern: '^_' }],
    'no-undef': 'error', 'no-constant-condition': 'error', 'eqeqeq': 'error',
  },
}];
