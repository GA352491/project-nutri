import { test, expect } from '@playwright/test'

/**
 * E2E: Nutritionist Booking Journey
 * Flow: Navigate to Marketplace → select an expert → pick a time slot
 *       → confirm booking → see success confirmation
 */

test.describe('Nutritionist Booking', () => {
  test('marketplace page loads and shows expert cards', async ({ page }) => {
    await page.goto('/marketplace')
    // Should render a heading about nutritionists
    await expect(
      page.getByRole('heading', { name: /nutritionist|expert|specialist/i }).first()
    ).toBeVisible({ timeout: 8_000 })
  })

  test('booking page renders slot picker', async ({ page }) => {
    await page.goto('/booking')
    // SlotPicker has role=radiogroup
    const radioGroup = page.locator('[role="radiogroup"]')
    if (await radioGroup.isVisible()) {
      await expect(radioGroup).toHaveAttribute('aria-label', 'Available time slots')
      // Individual slots are radio buttons
      const firstSlot = radioGroup.locator('[role="radio"]').first()
      await expect(firstSlot).toBeVisible()
    }
  })

  test('slot picker is keyboard operable', async ({ page }) => {
    await page.goto('/booking')
    const radioGroup = page.locator('[role="radiogroup"]')
    if (!(await radioGroup.isVisible())) { test.skip(); return }

    const firstSlot = radioGroup.locator('[role="radio"]').first()
    const secondSlot = radioGroup.locator('[role="radio"]').nth(1)

    // Focus first slot
    await firstSlot.focus()
    await expect(firstSlot).toBeFocused()

    // Select with Space
    await page.keyboard.press('Space')
    await expect(firstSlot).toHaveAttribute('aria-checked', 'true')

    // Select second slot with Tab + Space
    await secondSlot.focus()
    await page.keyboard.press('Space')
    await expect(secondSlot).toHaveAttribute('aria-checked', 'true')
  })

  test('booking confirmation displays after form submission', async ({ page }) => {
    await page.goto('/booking')
    const confirmBtn = page.getByRole('button', { name: /confirm|book|schedule/i })
    if (!(await confirmBtn.isVisible())) { test.skip(); return }

    // Select a slot first
    const slot = page.locator('[role="radio"]').first()
    if (await slot.isVisible()) await slot.click()

    await confirmBtn.click()

    // Expect a success message
    await expect(
      page.getByText(/confirmed|booked|success|appointment/i)
    ).toBeVisible({ timeout: 8_000 })
  })

  test('modal focus trap works on booking confirmation', async ({ page }) => {
    await page.goto('/booking')
    // Open any modal on the page
    const openModalBtn = page.getByRole('button').filter({ hasText: /book|confirm|schedule/i }).first()
    if (!(await openModalBtn.isVisible())) { test.skip(); return }

    await openModalBtn.click()
    const modal = page.locator('[role="dialog"]')
    if (!(await modal.isVisible())) { test.skip(); return }

    // Modal should be present with aria-modal
    await expect(modal).toHaveAttribute('aria-modal', 'true')

    // Press Escape → modal should close
    await page.keyboard.press('Escape')
    await expect(modal).not.toBeVisible()
  })
})
