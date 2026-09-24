async (page) => {
  // Top-nav mega-menu triggers are plain <a href="#"> links (not button/role=tab), so the earlier
  // interactive sweep (which only targeted button/[role=tab]/[role=button]) never opened them.
  // All menu links already exist in the DOM at load (hence the original "links found" count already
  // covered them) - what toggles is the sibling .dropdown-menu panel's "show" class, not link presence.
  // Each trigger is tested against a freshly reloaded page so one panel failing to close can't
  // contaminate (block/overlay) the test of the next one. Note: "Equity" starts pre-opened by default
  // (it's the first/default segment tab), so its first click closes it - that is correct behaviour,
  // not a defect.
  // Settle first in case the site does a client-side redirect shortly after load - otherwise
  // baseUrl below could capture a pre-redirect URL that every per-trigger page.goto() then bounces
  // off of again.
  await page.waitForLoadState('networkidle', { timeout: 8000 }).catch(() => {});
  await page.waitForTimeout(1000);
  const baseUrl = page.url();
  const navTriggers = [
    { label: 'Nav: Equity', pattern: /^\s*(equity|इक्विटी)\s*$/i },
    { label: 'Nav: Derivatives', pattern: /^\s*(derivatives|डेरिवेटिव्स)\s*$/i },
    { label: 'Nav: Indices', pattern: /^\s*(indices|इंडाइसेस)\s*$/i },
    { label: 'Nav: Currency Derivatives', pattern: /currency derivatives|करेंसी डेरिवेटिव्स/i },
    { label: 'Nav: IRD', pattern: /^\s*(IRD|आईआरडी)\s*$/i },
    { label: 'Nav: Debt', pattern: /^\s*(Debt|डेट)\s*$/i },
    { label: 'Nav: SLB', pattern: /^\s*(SLB|एसएलबी)\s*$/i },
    { label: 'Nav: ETFs/Mutual Funds', pattern: /ETF|Mutual Fund|ईटीएफ|म्यूचुअल फंड/i },
    { label: 'Nav: Commodity Derivatives', pattern: /commodity derivatives|कमोडिटी डेरिवेटिव्स/i },
    { label: 'Nav: EGR', pattern: /^\s*(EGR|ईजीआर)\s*$/i },
  ];

  function hasShow(el) {
    const sib = el.nextElementSibling;
    return !!(sib && sib.classList && sib.classList.contains('show'));
  }

  const results = [];

  // Nav mega-menus: verified via the sibling .dropdown-menu's "show" class.
  for (const t of navTriggers) {
    await page.goto(baseUrl, { waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {});
    await page.waitForTimeout(4000);
    const loc = page.locator('nav a[href="#"]').filter({ hasText: t.pattern }).first();
    const exists = await loc.count().catch(() => 0);
    if (!exists) {
      results.push({ label: t.label, found: false, note: 'trigger not found' });
      continue;
    }
    const beforeShow = await loc.evaluate(hasShow).catch(() => null);
    let clickErr = '';
    try {
      await loc.scrollIntoViewIfNeeded({ timeout: 3000 });
      await loc.click({ timeout: 5000 });
    } catch (e) {
      clickErr = String(e.message || e).split('\n')[0];
    }
    await page.waitForTimeout(700);
    const afterShow = await loc.evaluate(hasShow).catch(() => null);
    const linkCount = await loc.evaluate((el) => el.nextElementSibling ? el.nextElementSibling.querySelectorAll('a[href]').length : 0).catch(() => 0);
    const toggledCorrectly = beforeShow !== afterShow; // any state flip = the toggle mechanism works
    results.push({
      label: t.label,
      found: true,
      clickError: clickErr,
      beforeShow,
      afterShow,
      toggledCorrectly,
      linksInPanel: linkCount,
    });
  }

  // Group Websites + search filter: simple button-triggered dropdowns, checked via visible-link delta.
  async function visibleHrefSet() {
    return new Set(await page.evaluate(() =>
      Array.from(document.querySelectorAll('a[href]'))
        .filter((a) => a.offsetParent !== null)
        .map((a) => a.getAttribute('href'))
    ));
  }
  const buttonTriggers = [
    { label: 'Group Websites', name: /group websites|ग्रुप वेबसाइट/i },
    { label: 'Search filter (All)', name: /^(all|सभी)$/i },
  ];
  for (const t of buttonTriggers) {
    await page.goto(baseUrl, { waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {});
    await page.waitForTimeout(4000);
    const loc = page.getByRole('button', { name: t.name });
    const exists = await loc.count().catch(() => 0);
    if (!exists) {
      results.push({ label: t.label, found: false, note: 'trigger not found' });
      continue;
    }
    const before = await visibleHrefSet();
    let clickErr = '';
    try {
      await loc.scrollIntoViewIfNeeded({ timeout: 3000 });
      await loc.click({ timeout: 5000 });
    } catch (e) {
      clickErr = String(e.message || e).split('\n')[0];
    }
    await page.waitForTimeout(700);
    const after = await visibleHrefSet();
    const revealed = [...after].filter((h) => !before.has(h));
    results.push({
      label: t.label,
      found: true,
      clickError: clickErr,
      opened: revealed.length >= 3,
      newLinksRevealed: revealed.length,
      sample: revealed.slice(0, 6),
    });
  }

  return { pageUrl: baseUrl, results };
}
