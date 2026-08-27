import type { Meta, StoryObj } from '@storybook/vue3'
import ActivityBanner from '../components/ActivityBanner.vue'

const meta: Meta<typeof ActivityBanner> = {
 title: 'Domain/ActivityBanner',
 component: ActivityBanner,
 tags: ['autodocs'],
}
export default meta
type Story = StoryObj<typeof meta>

export const WearableSync: Story = {
 args: {
 title: ' Activity Detected',
 description: 'Your Apple Watch logged 8,400 steps. Add 320 kcal to today\'s budget?',
 acceptText: 'Add Calories',
 dismissText: 'Keep original',
 },
}

export const CalorieAdjust: Story = {
 args: {
 title: ' High activity day',
 description: 'You burned 680 kcal in your workout. We\'ve added a high-protein snack to your plan.',
 acceptText: 'Accept snack',
 dismissText: 'Skip',
 },
}
