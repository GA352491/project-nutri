import type { Meta, StoryObj } from '@storybook/vue3'
import Skeleton from '../components/ui/Skeleton.vue'

const meta: Meta<typeof Skeleton> = {
 title: 'Primitives/Skeleton',
 component: Skeleton,
 tags: ['autodocs'],
 argTypes: {
 variant: { control: 'select', options: ['text', 'rect', 'circle', 'card'] },
 width: { control: 'text' },
 height: { control: 'text' },
 },
}
export default meta
type Story = StoryObj<typeof meta>

export const Text: Story = { args: { variant: 'text', width: '220px' } }
export const Rect: Story = { args: { variant: 'rect', width: '100%', height: '120px' } }
export const Circle: Story = { args: { variant: 'circle', width: '56px', height: '56px' } }
export const Card: Story = { args: { variant: 'card', width: '100%', height: '80px' } }
export const MealCardLoad: Story = {
 render: () => ({
 components: { Skeleton },
 template: `
 <div style="max-width:360px;display:flex;flex-direction:column;gap:8px">
 <Skeleton variant="card" height="68px" />
 <Skeleton variant="card" height="68px" />
 <Skeleton variant="card" height="68px" />
 </div>
 `,
 }),
}
