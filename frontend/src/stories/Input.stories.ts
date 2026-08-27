import type { Meta, StoryObj } from '@storybook/vue3'
import { ref } from 'vue'
import Input from '../components/ui/Input.vue'

const meta: Meta<typeof Input> = {
 title: 'Primitives/Input',
 component: Input,
 tags: ['autodocs'],
 argTypes: { type: { control: 'select', options: ['text', 'email', 'password', 'number', 'tel'] } },
}
export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
 args: { label: 'Email address', placeholder: 'you@example.com', type: 'email', id: 'story-email' },
}
export const WithError: Story = {
 args: { label: 'Email address', placeholder: 'you@example.com', type: 'email', error: 'Please enter a valid email', id: 'story-email-err' },
}
export const WithHint: Story = {
 args: { label: 'Daily calorie target', placeholder: '2000', type: 'number', hint: 'We calculate this from your TDEE', id: 'story-kcal' },
}
export const Required: Story = {
 args: { label: 'Full name', placeholder: 'Anish Ganga', required: true, id: 'story-name' },
}
export const Disabled: Story = {
 args: { label: 'Phone (read-only)', modelValue: '+91 98765 43210', disabled: true, id: 'story-phone' },
}
export const Password: Story = {
 render: () => ({
 components: { Input },
 setup: () => { const v = ref(''); return { v } },
 template: '<Input label="Password" type="password" placeholder="Min 8 chars" v-model="v" id="story-pw" />',
 }),
}
