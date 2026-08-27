import { test, expect } from '@playwright/test'

/**
 * Complete E2E Suite: Full Patient, Provider & Admin Journeys
 */

test.describe('NutriPlan Comprehensive Journeys', () => {

  test('Patient Journey: Login → Dashboard → Food Photo Scanner → Video Room', async ({ page }) => {
    // 1. Visit Login
    await page.goto('/login')

    // 2. Patient Login via Quick Switcher
    await page.getByRole('button', { name: /Patient/i }).click()
    await page.getByRole('button', { name: /Sign in/i }).click()

    // 3. Lands on Dashboard
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 })
    await expect(page.getByRole('heading', { name: 'Today' })).toBeVisible()

    // 4. Navigate to Food Diary
    await page.goto('/diary')
    await expect(page.getByRole('heading', { name: /Food Diary/i })).toBeVisible()

    // 5. Open AI Photo Scan Modal
    const photoBtn = page.getByRole('button', { name: /AI Photo Scan/i })
    await expect(photoBtn).toBeVisible()
    await photoBtn.click()

    // Expect scanner modal
    await expect(page.getByText(/AI Food Camera & Macro Scanner/i)).toBeVisible()

    // 6. Navigate to Video Consultation Room
    await page.goto('/consultation/test-session-01?provider=Dr.+Sneha+Roy')
    await expect(page.getByText('LIVE', { exact: true })).toBeVisible()
    await expect(page.getByText(/Live Clinical Notes/i)).toBeVisible()
  })

  test('Nutritionist Journey: Expert Dashboard → Settings & Availability', async ({ page }) => {
    await page.goto('/login')
    await page.getByRole('button', { name: /Expert \/ Nutritionist/i }).click()
    await page.getByRole('button', { name: /Sign in/i }).click()

    await expect(page).toHaveURL(/\/expert/, { timeout: 10000 })
    
    // Visit Expert Settings
    await page.goto('/expert/settings')
    await expect(page.getByText(/Doctor Profile & Bio/i)).toBeVisible()
    await expect(page.getByText(/Certificates & Credentials/i)).toBeVisible()
    await expect(page.getByText(/Working Hours & Calendar/i)).toBeVisible()
  })

  test('Admin Journey: Overview → Verified Nutritionists Management', async ({ page }) => {
    await page.goto('/login')
    await page.getByRole('button', { name: /Admin/i }).click()
    await page.getByRole('button', { name: /Sign in/i }).click()

    await expect(page).toHaveURL(/\/admin/, { timeout: 10000 })

    // Inspect Nutritionists Queue
    await page.goto('/admin/nutritionists')
    await expect(page.getByText(/Experts Queue & Credential Verification/i)).toBeVisible()
  })

})
