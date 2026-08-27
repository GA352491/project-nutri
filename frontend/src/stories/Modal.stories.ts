import type { Meta, StoryObj } from '@storybook/vue3'
import { ref } from 'vue'
import Modal from '../components/ui/Modal.vue'
import Button from '../components/ui/Button.vue'

const meta: Meta<typeof Modal> = {
 title: 'Primitives/Modal',
 component: Modal,
 tags: ['autodocs'],
 argTypes: { size: { control: 'select', options: ['sm', 'md', 'lg'] } },
}
export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
 render: () => ({
 components: { Modal, Button },
 setup: () => { const open = ref(false); return { open } },
 template: `
 <div>
 <Button @click="open = true">Open Modal</Button>
 <Modal v-model="open" title="Confirm your plan">
 <p style="color:var(--color-ink,#e2e8e2)">Your meal plan will be regenerated using the Llama 3 engine. This may take a few seconds.</p>
 <template #footer>
 <Button variant="ghost" @click="open = false">Cancel</Button>
 <Button @click="open = false">Regenerate</Button>
 </template>
 </Modal>
 </div>
 `,
 }),
}

export const Small: Story = {
 render: () => ({
 components: { Modal, Button },
 setup: () => { const open = ref(true); return { open } },
 template: `
 <div>
 <Button @click="open = true">Open Small</Button>
 <Modal v-model="open" title="Quick note" size="sm">
 <p style="color:var(--color-ink,#e2e8e2)">Meal logged successfully!</p>
 </Modal>
 </div>
 `,
 }),
}
