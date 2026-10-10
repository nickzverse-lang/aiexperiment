// Bake the deck into a static, script-free HTML for Figma import (html.to.design).
// Usage: node tools/bake_figma.js <url of local deck build> <out.html>, then swap the local @font-face block for the Google Fonts link.
const { chromium } = require(process.env.PLAYWRIGHT || 'playwright');
const fs = require('fs');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto(process.argv[2], { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.evaluate(() => { document.querySelectorAll('.slide').forEach(s => s.style.zoom = 1); window.fitSlides(); });
  const res = await p.evaluate(() => {
    const out = [];
    document.querySelectorAll('.s-fit').forEach(el => {
      const before = el.getBoundingClientRect();
      const m = /scale\(([\d.]+)\)/.exec(el.style.transform); const s = m ? parseFloat(m[1]) : 1;
      const top = parseFloat(el.style.top) || 0, left = parseFloat(el.style.left) || 0;
      el.style.transform = 'none'; el.style.zoom = s; el.style.top = (top / s) + 'px'; el.style.left = (left / s) + 'px';
      const after = el.getBoundingClientRect();
      out.push([Math.round(before.width - after.width), Math.round(before.height - after.height), Math.round(before.top - after.top), Math.round(before.left - after.left)]);
    });
    document.querySelectorAll('script').forEach(s => s.remove());
    document.querySelectorAll('.slide').forEach(s => s.style.removeProperty('zoom'));
    return out;
  });
  const bad = res.filter(r => r.some(v => Math.abs(v) > 2));
  console.log('slides', res.length, 'mismatched', bad.length, JSON.stringify(bad.slice(0, 5)));
  fs.writeFileSync(process.argv[3], await p.content());
  await b.close();
})();
