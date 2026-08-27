import type { Meta, StoryObj } from '@storybook/vue3'
import MealCard from '../components/MealCard.vue'

const meta: Meta<typeof MealCard> = {
 title: 'Domain/MealCard',
 component: MealCard,
 tags: ['autodocs'],
 argTypes: {
 statusType: { control: 'select', options: ['success', 'warning', 'danger', undefined] },
 },
}
export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
 args: { title: 'Palak Paneer', macros: '480 kcal · P 22g · C 38g · F 18g' },
}

export const WithSuccessBadge: Story = {
 args: { title: 'Dal Tadka', macros: '320 kcal · P 18g · C 42g · F 8g', statusType: 'success', statusText: 'High protein' },
}

export const WithWarningBadge: Story = {
 args: { title: 'Biryani', macros: '720 kcal · P 28g · C 95g · F 22g', statusType: 'warning', statusText: 'High carbs' },
}

export const WithDangerBadge: Story = {
 args: { title: 'Fried Samosa', macros: '560 kcal · P 8g · C 48g · F 36g', statusType: 'danger', statusText: 'High fat' },
}

export const AlreadyLogged: Story = {
 args: { title: 'Masala Oats', macros: '260 kcal · P 9g · C 44g · F 5g', isLogged: true },
}
