import type { Meta, StoryObj } from '@storybook/vue3'
import Chip from '../components/ui/Chip.vue'

const meta: Meta<typeof Chip> = {
 title: 'Primitives/Chip',
 component: Chip,
 tags: ['autodocs'],
 argTypes: {
 variant: { control: 'select', options: ['default', 'selected', 'success', 'warning', 'danger'] },
 removable: { control: 'boolean' },
 clickable: { control: 'boolean' },
 },
}
export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = { args: { label: 'Vegetarian' } }
export const Selected: Story = { args: { label: 'Vegetarian', variant: 'selected' } }
export const Removable: Story = { args: { label: 'Gluten-free', removable: true } }
export const DietaryTags: Story = {
 render: () => ({
 components: { Chip },
 template: `
 <div style="display:flex;flex-wrap:wrap;gap:8px">
 <Chip label="Vegetarian" variant="selected" />
 <Chip label="Gluten-free" />
 <Chip label="Low-sodium" />
 <Chip label="Diabetic-friendly" variant="success" />
 <Chip label="High-fat" variant="warning" />
 </div>
 `,
 }),
}
