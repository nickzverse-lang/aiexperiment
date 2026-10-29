// Capture screens, states and components of the BLUPRINT dashboard for the case study (wireframes → hi-fi, design system,
// wireflows, usability). Usage: node tools/cs/shoot_dashboard.js <dashboard.html> <v1-dark.html> <out dir>
const { chromium } = require(process.env.PLAYWRIGHT || 'playwright');
const path = require('path');

(async () => {
  const [dash, v1, out] = process.argv.slice(2);
  const f = (n) => path.join(out, n + '.jpg');
  const shot = { type: 'jpeg', quality: 84 };
  const b = await chromium.launch();

  async function page(file, w, h, dpr) {
    const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: dpr, reducedMotion: 'reduce' });
    await p.goto('file://' + path.resolve(file));
    await p.evaluate(() => document.fonts.ready);
    await p.addStyleTag({ content: '.store{position:relative!important}' });
    return p;
  }
  async function el(p, sel, name, opts = {}) {
    const h = await p.$(sel);
    if (!h) { console.log('missing', sel); return; }
    await h.scrollIntoViewIfNeeded();
    await h.screenshot({ path: f(name), ...shot, ...opts });
  }
  async function clipOf(p, sel, name, maxH, pad = 0) {
    // page coordinates (fullPage clips ignore the current scroll position)
    const r = await p.$eval(sel, (el) => { const b = el.getBoundingClientRect(); return { x: b.left + scrollX, y: b.top + scrollY, width: b.width, height: b.height }; });
    await p.screenshot({ path: f(name), ...shot, fullPage: true, clip: { x: r.x - pad, y: r.y - pad, width: r.width + pad * 2, height: Math.min(maxH || r.height, r.height) + pad * 2 } });
  }

  // ---------- desktop screens
  let p = await page(dash, 1440, 900, 1);
  await p.screenshot({ path: f('d-top'), ...shot });
  await clipOf(p, '#overview .wrap', 'd-overview', 1180);
  await el(p, '#overview .grid', 'd-top10');
  await clipOf(p, '#working .wrap', 'd-working', 1150);
  await clipOf(p, '#avoid .wrap', 'd-avoid', 760);
  await clipOf(p, '#ideas .ideas', 'd-ideas-grid', 760);
  await clipOf(p, '#hashtags .wrap', 'd-hashtags', 1000);
  await clipOf(p, '#posting .wrap', 'd-posting', 1100);
  await clipOf(p, '#audience .wrap', 'd-audience', 900);
  await clipOf(p, '#ideas .wrap', 'd-ideas', 1150);
  await clipOf(p, '#calendar .wrap', 'd-calendar', 900);
  await el(p, '.foot', 'd-footer');
  await p.screenshot({ path: f('d-full'), ...shot, quality: 70, fullPage: true });
  // states
  const bar = await p.$('#overview .hb');
  await bar.scrollIntoViewIfNeeded(); await bar.hover(); await p.waitForTimeout(150);
  const r = await (await p.$('#overview .grid')).boundingBox();
  await p.screenshot({ path: f('s-tooltip'), ...shot, clip: { x: r.x, y: r.y - 10, width: r.width * .62, height: 420 } });
  await p.mouse.move(5, 5);
  await p.click('.filters button[data-f="Reel"]');
  await clipOf(p, '#calendar .wrap', 's-filter', 760);
  await p.click('.filters button[data-f="All"]');
  await p.evaluate(() => { document.querySelector('details.all').open = true; });
  await clipOf(p, 'details.all', 's-table', 520);
  await p.close();

  // sticky header with an active tab (real sticky behaviour)
  p = await b.newPage({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
  await p.goto('file://' + path.resolve(dash)); await p.evaluate(() => document.fonts.ready);
  await p.evaluate(() => document.getElementById('hashtags').scrollIntoView()); await p.waitForTimeout(400);
  await p.screenshot({ path: f('s-sticky'), ...shot });
  await p.close();

  // ---------- components (2x)
  p = await page(dash, 1440, 900, 2);
  await el(p, '.announce', 'c-ticker', { clip: undefined });
  await el(p, '.demo', 'c-demo');
  await el(p, '.store-top', 'c-header');
  await el(p, '.cats', 'c-tabs');
  await el(p, '.ctas', 'c-ctas');
  await el(p, '.store-top .r', 'c-actions');
  await el(p, '.kp', 'c-kp');
  await el(p, '.kp.best', 'c-kp-best');
  await el(p, '.idea', 'c-idea-dark');
  await el(p, '.idea:nth-child(2)', 'c-idea');
  await el(p, '#working .grid .panel', 'c-bars');
  await el(p, '.card.win', 'c-card-win');
  await el(p, '.card.bad', 'c-card-bad');
  await el(p, '.heat', 'c-heat');
  await el(p, '.sched', 'c-sched');
  await el(p, '.filters', 'c-filters');
  await el(p, '.cloud', 'c-cloud');
  await el(p, '.plist li', 'c-post');
  await el(p, '.pill', 'c-pill');
  await el(p, '#calendar tbody tr.k-idea', 'c-row');
  await el(p, '.hooks', 'c-table');
  await p.close();

  // ---------- mobile (390 x 844, 2x)
  p = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, reducedMotion: 'reduce', isMobile: true, hasTouch: true });
  await p.goto('file://' + path.resolve(dash)); await p.evaluate(() => document.fonts.ready);
  const mob = async (sel, name, dy = -60) => {
    await p.evaluate(([s, d]) => { const e = s ? document.querySelector(s) : null; window.scrollTo(0, e ? e.getBoundingClientRect().top + scrollY + d : 0); }, [sel, dy]);
    await p.waitForTimeout(250); await p.screenshot({ path: f(name), ...shot });
  };
  await mob(null, 'm-top');
  await mob('.kpis', 'm-kpis', -120);
  await mob('#overview .grid', 'm-bars', -110);
  await mob('.heat', 'm-heat', -150);
  await mob('.ideas', 'm-ideas', -110);
  await mob('.filters', 'm-calendar', -110);
  await p.close();

  // ---------- version 1 (dark) for the usability rounds
  p = await b.newPage({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
  await p.goto('file://' + path.resolve(v1)); await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: f('v1-top'), ...shot });
  const cr = await p.$eval('#calendar', (el) => { const b = el.getBoundingClientRect(); return { x: b.left + scrollX, y: b.top + scrollY, width: b.width }; });
  await p.screenshot({ path: f('v1-calendar'), ...shot, fullPage: true, clip: { x: cr.x, y: cr.y, width: cr.width, height: 760 } });
  await p.close();
  p = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, reducedMotion: 'reduce', isMobile: true });
  await p.goto('file://' + path.resolve(v1)); await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: f('v1-mobile'), ...shot });
  await p.close();
  await b.close();
  console.log('done');
})();
