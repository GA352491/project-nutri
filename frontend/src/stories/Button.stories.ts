import type { Meta, StoryObj } from '@storybook/vue3'
import Button from '../components/ui/Button.vue'

const meta: Meta<typeof Button> = {
 title: 'Primitives/Button',
 component: Button,
 tags: ['autodocs'],
 argTypes: {
 variant: { control: 'select', options: ['primary', 'secondary', 'outline', 'danger', 'ghost'] },
 size: { control: 'select', options: ['sm', 'md', 'lg'] },
 disabled: { control: 'boolean' },
 loading: { control: 'boolean' },
 },
}
export default meta
type Story = StoryObj<typeof meta>

export const Primary: Story = {
 args: { variant: 'primary', size: 'md', disabled: false, loading: false },
 render: (args) => ({ components: { Button }, setup: () => ({ args }), template: '<Button v-bind="args">Save Plan</Button>' }),
}

export const Secondary: Story = {
 args: { variant: 'secondary' },
 render: (args) => ({ components: { Button }, setup: () => ({ args }), template: '<Button v-bind="args">Cancel</Button>' }),
}

export const Outline: Story = {
 args: { variant: 'outline' },
 render: (args) => ({ components: { Button }, setup: () => ({ args }), template: '<Button v-bind="args">View Details</Button>' }),
}

export const Danger: Story = {
 args: { variant: 'danger' },
 render: (args) => ({ components: { Button }, setup: () => ({ args }), template: '<Button v-bind="args">Delete Recipe</Button>' }),
}

export const Ghost: Story = {
 args: { variant: 'ghost' },
 render: (args) => ({ components: { Button }, setup: () => ({ args }), template: '<Button v-bind="args">Skip for now</Button>' }),
}

export const Loading: Story = {
 args: { variant: 'primary', loading: true },
 render: (args) => ({ components: { Button }, setup: () => ({ args }), template: '<Button v-bind="args">Saving…</Button>' }),
}

export const Disabled: Story = {
 args: { variant: 'primary', disabled: true },
 render: (args) => ({ components: { Button }, setup: () => ({ args }), template: '<Button v-bind="args">Unavailable</Button>' }),
}

export const Small: Story = {
 args: { variant: 'primary', size: 'sm' },
 render: (args) => ({ components: { Button }, setup: () => ({ args }), template: '<Button v-bind="args">Log Meal</Button>' }),
}

export const Large: Story = {
 args: { variant: 'primary', size: 'lg' },
 render: (args) => ({ components: { Button }, setup: () => ({ args }), template: '<Button v-bind="args">Get My Plan</Button>' }),
}
