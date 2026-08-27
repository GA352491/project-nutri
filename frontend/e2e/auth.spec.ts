import { test, expect } from '@playwright/test'

/**
 * E2E: Authentication Journey
 * Flow: Visit home → redirect to login → register new user → login → reach dashboard
 */

const UNIQUE_EMAIL = `e2e_${Date.now()}@nutriplan.test`
const PASSWORD     = 'SecurePass#1'

test.describe('Authentication', () => {
  test('redirect to /login when unauthenticated', async ({ page }) => {
    await page.goto('/')
    // App should redirect unauthenticated users to /login
    await expect(page).toHaveURL(/\/login/)
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
  })

  test('registration form validates required fields', async ({ page }) => {
    await page.goto('/register')
    // Submit empty form
    await page.getByRole('button', { name: /create account|register|sign up/i }).click()
    // Expect at least one error message
    const errors = page.locator('[role="alert"]')
    await expect(errors.first()).toBeVisible()
  })

  test('registration → login → dashboard', async ({ page }) => {
    // ── 1. Register ─────────────────────────────────────────────
    await page.goto('/register')

    await page.getByLabel(/full name/i).fill('E2E Tester')
    await page.getByLabel(/email/i).fill(UNIQUE_EMAIL)
    await page.getByLabel(/password/i).first().fill(PASSWORD)

    // Some forms have a confirm-password field
    const confirmPw = page.getByLabel(/confirm password/i)
    if (await confirmPw.isVisible()) await confirmPw.fill(PASSWORD)

    await page.getByRole('button', { name: /create account|register|sign up/i }).click()

    // After registration expect redirect to onboarding or login
    await expect(page).toHaveURL(/\/(onboarding|login|dashboard)/)

    // ── 2. Login (if redirected back to /login) ──────────────────
    if (page.url().includes('/login')) {
      await page.getByLabel(/email/i).fill(UNIQUE_EMAIL)
      await page.getByLabel(/password/i).fill(PASSWORD)
      await page.getByRole('button', { name: /log in|sign in|login/i }).click()
    }

    // ── 3. Expect dashboard or onboarding ───────────────────────
    await expect(page).toHaveURL(/\/(dashboard|today|onboarding)/, { timeout: 10_000 })
  })

  test('login shows error for wrong credentials', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel(/email/i).fill('nonexistent@nutriplan.test')
    await page.getByLabel(/password/i).fill('WrongPass#1')
    await page.getByRole('button', { name: /log in|sign in|login/i }).click()

    const error = page.locator('[role="alert"]')
    await expect(error).toBeVisible({ timeout: 8_000 })
  })
})
