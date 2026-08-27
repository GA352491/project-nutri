import type { Meta, StoryObj } from '@storybook/vue3'
import NutritionFactsBlock from '../components/NutritionFactsBlock.vue'

const meta: Meta<typeof NutritionFactsBlock> = {
 title: 'Domain/NutritionFactsBlock',
 component: NutritionFactsBlock,
 tags: ['autodocs'],
}
export default meta
type Story = StoryObj<typeof meta>

export const PalakPaneer: Story = {
 args: {
 calories: 480, protein: 22, carbs: 38, fat: 18,
 fiber: 5, sodium: 480, sugar: 6,
 },
}
export const DalTadka: Story = {
 args: {
 calories: 320, protein: 18, carbs: 42, fat: 8,
 fiber: 12, sodium: 320, sugar: 3,
 },
}
