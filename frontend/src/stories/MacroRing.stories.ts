import type { Meta, StoryObj } from '@storybook/vue3'
import MacroRing from '../components/MacroRing.vue'

const meta: Meta<typeof MacroRing> = {
 title: 'Domain/MacroRing',
 component: MacroRing,
 tags: ['autodocs'],
 argTypes: {
 totalKcal: { control: { type: 'range', min: 0, max: 3000, step: 50 } },
 targetKcal: { control: { type: 'range', min: 500, max: 4000, step: 50 } },
 },
}
export default meta
type Story = StoryObj<typeof meta>

const legendSlot = `
 <template #legend>
 <div style="display:flex;flex-direction:column;gap:4px">
 <div> Protein <strong>142 g</strong></div>
 <div> Carbs <strong>210 g</strong></div>
 <div> Fat <strong>68 g</strong></div>
 </div>
 </template>`

export const OnTrack: Story = {
 args: { totalKcal: 1200, targetKcal: 2000 },
 render: (args) => ({ components: { MacroRing }, setup: () => ({ args }), template: `<MacroRing v-bind="args">${legendSlot}</MacroRing>` }),
}

export const NearlyFull: Story = {
 args: { totalKcal: 1920, targetKcal: 2000 },
 render: (args) => ({ components: { MacroRing }, setup: () => ({ args }), template: `<MacroRing v-bind="args">${legendSlot}</MacroRing>` }),
}

export const Over: Story = {
 args: { totalKcal: 2300, targetKcal: 2000 },
 render: (args) => ({ components: { MacroRing }, setup: () => ({ args }), template: `<MacroRing v-bind="args">${legendSlot}</MacroRing>` }),
}

export const Empty: Story = {
 args: { totalKcal: 0, targetKcal: 2000 },
 render: (args) => ({ components: { MacroRing }, setup: () => ({ args }), template: `<MacroRing v-bind="args">${legendSlot}</MacroRing>` }),
}
