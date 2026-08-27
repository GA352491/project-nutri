import type { Meta, StoryObj } from '@storybook/vue3'
import Toast from '../components/ui/Toast.vue'

const meta: Meta<typeof Toast> = {
 title: 'Primitives/Toast',
 component: Toast,
 tags: ['autodocs'],
 argTypes: {
 type: { control: 'select', options: ['success', 'error', 'warning', 'info'] },
 message: { control: 'text' },
 },
}
export default meta
type Story = StoryObj<typeof meta>

export const Success: Story = { args: { type: 'success', message: 'Meal logged successfully!' } }
export const Error: Story = { args: { type: 'error', message: 'Failed to save plan. Please try again.' } }
export const Warning: Story = { args: { type: 'warning', message: 'You are 120 kcal above your daily goal.' } }
export const Info: Story = { args: { type: 'info', message: 'Your plan has been updated with wearable data.' } }
