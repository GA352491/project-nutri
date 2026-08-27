import type { Meta, StoryObj } from '@storybook/vue3'
import GroceryListItem from '../components/GroceryListItem.vue'

const meta: Meta<typeof GroceryListItem> = {
 title: 'Domain/GroceryListItem',
 component: GroceryListItem,
 tags: ['autodocs'],
}
export default meta
type Story = StoryObj<typeof meta>

export const Unchecked: Story = {
 args: { name: 'Spinach', quantity: '200g', initialChecked: false },
}
export const Checked: Story = {
 args: { name: 'Paneer', quantity: '250g', initialChecked: true },
}
export const List: Story = {
 render: () => ({
 components: { GroceryListItem },
 template: `
 <div style="max-width:340px;padding:16px;background:var(--color-canvas-raised,#1e2820);border-radius:8px">
 <GroceryListItem name="Spinach" quantity="200g" />
 <GroceryListItem name="Chicken Breast" quantity="500g" />
 <GroceryListItem name="Brown Rice" quantity="1kg" :initial-checked="true" />
 <GroceryListItem name="Greek Yoghurt" quantity="2 cups" />
 <GroceryListItem name="Tomatoes" quantity="4 pcs" :initial-checked="true" />
 </div>
 `,
 }),
}
