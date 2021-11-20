import * as path from 'path'
import { defineConfig } from 'vite'
import legacy from '@vitejs/plugin-legacy'

import { peerDependencies } from './package.json'

export default defineConfig(({ mode }) => {
  // Bundled mode:
  // - JS distributed via pypi. npm package and frontend js toolchain not required.
  // - All dependencies included in bundle.
  //
  // Unbundled mode:
  // - JS distributed via npm. Frontend widgets require this to be built.
  // - Some dependencies included in bundle.
  // - Some dependencies externalised (see package.json peerDependencies field)

  const isBundled = mode === 'bundled'
  const entrypoint = isBundled ? 'register.ts' : 'register.ts'

  return {
    base: '/static/',
    plugins: compact([
      isBundled && legacy({
        polyfills: false,
        targets: ['defaults', 'not IE 11']
      })
    ]),
    build: {
      emptyOutDir: true,
      rollupOptions: {
        external: isBundled ? [] : Object.keys(peerDependencies),
        output: {
          dir: isBundled ? 'static/' : 'dist/'
        },
        input: {
          main: `pyck/core/frontend/${entrypoint}`
        }
      },
      lib: isBundled ? undefined : {
        entry: path.resolve(__dirname, `pyck/core/frontend/${entrypoint}`),
        formats: isBundled ? ['cjs'] : ['es'],
        name: 'pyck',
        fileName: () => `index.js`
      },
    }
  }
})

const compact = array => array.filter(item => !!item)
