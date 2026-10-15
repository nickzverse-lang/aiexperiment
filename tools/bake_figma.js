// Bake the deck or the case study into a static, script-free HTML for Figma import (html.to.design).
// Usage: node tools/bake_figma.js <url of local build> <out.html> [width height]
//   deck: 1920 1080 (default)   case study: 297mm 210mm
// Scaled content is converted from transform to zoom, scripts are removed and the local @font-face block
// is swapped for the Google Fonts link, so the file opens anywhere.
const { chromium } = require(process.env.PLAYWRIGHT || 'playwright');
const fs = require('fs');
const FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
  + '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap">';
(async () => {
  const [url, out, w = '1920', h = '1080'] = process.argv.slice(2);
  const px = v => /mm$/.test(v) ? Math.round(parseFloat(v) * 96 / 25.4) : +v;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: px(w), height: px(h) } });
  await p.goto(url, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.evaluate(() => { document.documentElement.classList.add('pdf'); document.querySelectorAll('.slide').forEach(s => s.style.zoom = 1); window.fitSlides(); });
  const res = await p.evaluate((fonts) => {
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
    document.documentElement.classList.remove('pdf');
    document.querySelectorAll('style').forEach(st => {
      if (st.textContent.includes('@font-face') && st.textContent.includes('node_modules')) st.outerHTML = fonts;
    });
    return out;
  }, FONTS);
  const bad = res.filter(r => r.some(v => Math.abs(v) > 2));
  console.log('fitted blocks', res.length, 'mismatched', bad.length, JSON.stringify(bad.slice(0, 5)));
  const html = await p.content();
  if (html.includes('node_modules')) console.warn('warning: local paths left in output');
  fs.writeFileSync(out, html);
  await b.close();
})();
