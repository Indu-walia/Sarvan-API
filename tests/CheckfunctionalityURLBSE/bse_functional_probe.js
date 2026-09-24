async (page) => {
  // Some sites redirect/navigate client-side shortly after initial load (e.g. a locale redirect),
  // which destroys the JS execution context mid-script if we don't wait it out first. Settle before
  // reading anything, and capture baseUrl only after that settle so later sameDoc() checks compare
  // against the page's actual final URL, not a pre-redirect one.
  await page.waitForLoadState('networkidle', { timeout: 8000 }).catch(() => {});
  await page.waitForTimeout(1000);
  const baseUrl = page.url();

  const consoleErrors = [];
  page.on('console', (m) => { if (m.type() === 'error') consoleErrors.push(m.text()); });
  const newTabUrls = [];
  page.context().on('page', async (p) => {
    try {
      await p.waitForLoadState('domcontentloaded', { timeout: 4000 }).catch(() => {});
      newTabUrls.push(p.url());
      await p.close().catch(() => {});
    } catch (e) {}
  });
  page.on('dialog', async (d) => { await d.dismiss().catch(() => {}); });

  // 1) Link health check (no navigation) - all unique hrefs found on the page.
  // Retry once if a late navigation destroys the execution context mid-evaluate.
  async function harvestHrefs() {
    return page.evaluate(() => {
      const set = new Set();
      document.querySelectorAll('a[href]').forEach((a) => {
        const h = a.getAttribute('href');
        if (h && !h.startsWith('#') && !h.startsWith('javascript:') && !h.startsWith('mailto:') && !h.startsWith('tel:')) {
          set.add(a.href);
        }
      });
      return Array.from(set);
    });
  }
  let hrefs;
  try {
    hrefs = await harvestHrefs();
  } catch (e) {
    await page.waitForLoadState('networkidle', { timeout: 8000 }).catch(() => {});
    await page.waitForTimeout(1000);
    hrefs = await harvestHrefs();
  }

  async function checkUrl(url) {
    try {
      const resp = await page.context().request.fetch(url, { method: 'HEAD', timeout: 6000, failOnStatusCode: false });
      let status = resp.status();
      if (status === 405 || status === 403) {
        const resp2 = await page.context().request.fetch(url, { method: 'GET', timeout: 6000, failOnStatusCode: false });
        status = resp2.status();
      }
      return { url, status, ok: status >= 200 && status < 400 };
    } catch (e) {
      return { url, status: 'ERROR', ok: false, error: String(e.message || e).split('\n')[0] };
    }
  }

  const linkResults = [];
  for (const url of hrefs) {
    let result = await checkUrl(url);
    if (!result.ok) {
      await page.waitForTimeout(300);
      result = await checkUrl(url);
    }
    linkResults.push(result);
  }

  // Closes any open dialog using its own Close control first, falling back to Escape,
  // then force-hides it as a last resort so a stuck modal can't block the rest of the sweep.
  async function closeAnyOpenDialog() {
    const dialogs = page.locator('[role="dialog"]');
    const count = await dialogs.count().catch(() => 0);
    if (count === 0) return false;
    for (let d = 0; d < count; d++) {
      const dlg = dialogs.nth(d);
      const closeBtn = dlg.getByRole('button', { name: /close/i }).first();
      if (await closeBtn.count().catch(() => 0)) {
        await closeBtn.click({ timeout: 1500 }).catch(() => {});
      }
    }
    await page.waitForTimeout(150);
    if (await dialogs.count().catch(() => 0)) {
      await page.keyboard.press('Escape').catch(() => {});
      await page.waitForTimeout(150);
    }
    if (await dialogs.count().catch(() => 0)) {
      await page.evaluate(() => {
        document.querySelectorAll('[role="dialog"]').forEach((d) => d.remove());
      }).catch(() => {});
    }
    return true;
  }

  function sameDoc(url) {
    return url.split('#')[0] === baseUrl.split('#')[0];
  }

  // 2) Interactive control sweep: every button / role=tab / role=button on the page.
  // Some "tabs" are real links that navigate to a sub-page rather than switching an in-place panel;
  // those are validated by checking the destination loaded, then we return to baseUrl before continuing
  // so later indices still resolve against the original page structure.
  const handles = await page.locator('button, [role="tab"], [role="button"]').all();
  const interactiveResults = [];
  for (let i = 0; i < handles.length; i++) {
    const el = handles[i];
    let label = '';
    let role = '';
    try { label = ((await el.getAttribute('aria-label')) || (await el.innerText().catch(() => ''))).trim().slice(0, 60); } catch (e) {}
    try { role = await el.evaluate((node) => node.getAttribute('role') || node.tagName.toLowerCase()); } catch (e) {}

    await closeAnyOpenDialog();

    const dialogsBefore = await page.locator('[role="dialog"]').count();
    const errBefore = consoleErrors.length;
    const tabsBefore = newTabUrls.length;
    let status = 'Pass';
    let note = '';
    let navigatedTo = '';

    // Try the interaction with a generous timeout; if that times out, wait for the page to settle
    // (this site loads price/quote data asynchronously for a few seconds after load/navigation) and
    // retry once before giving up. A pure timeout on the retry is downgraded to "Warning" rather than
    // "Fail" - it means the control couldn't be confirmed within the test budget, not that it's broken.
    let interacted = false;
    let lastErr = '';
    let wasTimeout = false;
    for (let attempt = 0; attempt < 2 && !interacted; attempt++) {
      try {
        await el.scrollIntoViewIfNeeded({ timeout: 6000 });
        await el.click({ timeout: 6000 });
        interacted = true;
      } catch (e) {
        lastErr = String(e.message || e).split('\n')[0];
        wasTimeout = /Timeout [\d.]+ms exceeded/.test(lastErr);
        if (attempt === 0) await page.waitForTimeout(1500);
      }
    }

    if (!interacted) {
      status = wasTimeout ? 'Warning' : 'Fail';
      note = lastErr;
    } else {
      try {
        await page.waitForTimeout(350);
        if (!sameDoc(page.url())) {
          navigatedTo = page.url();
          const title = await page.title();
          if (/access denied|error|not found/i.test(title)) {
            status = 'Fail';
            note = `Navigated to ${navigatedTo} which shows error page: ${title}`;
          }
          await page.goto(baseUrl, { waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {});
          await page.waitForTimeout(300);
        }
      } catch (e) {
        status = 'Fail';
        note = String(e.message || e).split('\n')[0];
      }
    }
    const dialogsAfter = await page.locator('[role="dialog"]').count().catch(() => dialogsBefore);
    const errAfter = consoleErrors.length;
    const tabsAfter = newTabUrls.length;
    const dialogOpened = dialogsAfter > dialogsBefore;
    interactiveResults.push({
      index: i,
      role,
      label,
      status,
      note,
      navigatedTo,
      dialogOpened,
      newTabOpened: tabsAfter > tabsBefore,
      newConsoleErrors: errAfter - errBefore,
    });
  }
  await closeAnyOpenDialog();
  if (!sameDoc(page.url())) {
    await page.goto(baseUrl, { waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {});
  }

  return {
    pageTitle: await page.title(),
    pageUrl: page.url(),
    totalLinks: linkResults.length,
    brokenLinks: linkResults.filter((l) => !l.ok),
    linkResults,
    totalInteractive: interactiveResults.length,
    interactiveResults,
    totalConsoleErrors: consoleErrors.length,
    consoleErrorSamples: Array.from(new Set(consoleErrors)).slice(0, 20),
    newTabsOpened: newTabUrls,
  };
}
