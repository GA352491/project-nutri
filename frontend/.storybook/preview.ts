import type { Preview } from '@storybook/vue3'
import '../src/index.css'

const preview: Preview = {
  parameters: {
    backgrounds: {
      default: 'dark',
      values: [
        { name: 'dark', value: '#111714' },
        { name: 'light', value: '#f5f7f5' },
      ],
    },
    controls: { matchers: { color: /(background|color)$/i, date: /Date$/ } },
    a11y: {
      // axe-core config — test all rules
      config: {},
      options: { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa'] } },
    },
  },
}

export default preview
