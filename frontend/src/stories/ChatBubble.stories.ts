import type { Meta, StoryObj } from '@storybook/vue3'
import ChatBubble from '../components/ChatBubble.vue'

const meta: Meta<typeof ChatBubble> = {
 title: 'Domain/ChatBubble',
 component: ChatBubble,
 tags: ['autodocs'],
 argTypes: {
 senderType: { control: 'select', options: ['ai', 'human', 'user'] },
 },
}
export default meta
type Story = StoryObj<typeof meta>

export const AiMessage: Story = {
 args: { senderType: 'ai', senderName: 'NutriBot', message: 'Based on your TDEE of 2,100 kcal I\'ve updated your plan with higher protein for fat loss.' },
}
export const HumanMessage: Story = {
 args: { senderType: 'human', senderName: 'Dr. Priya', message: 'Great progress! Keep up the 150g protein target and try to get more sleep.' },
}
export const UserMessage: Story = {
 args: { senderType: 'user', message: 'Can I swap the evening snack for a banana?' },
}

export const Conversation: Story = {
 render: () => ({
 components: { ChatBubble },
 template: `
 <div style="max-width:480px;padding:16px">
 <ChatBubble sender-type="ai" sender-name="NutriBot" message="Good morning! Your plan is ready for today." />
 <ChatBubble sender-type="user" message="Can I swap dinner for something lighter?" />
 <ChatBubble sender-type="ai" sender-name="NutriBot" message="Sure! I replaced Butter Chicken with Dal Soup — saves 220 kcal." />
 </div>
 `,
 }),
}
