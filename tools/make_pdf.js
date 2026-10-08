// Export the project book or the deck to PDF with local fonts (and real 3D for the book).
// 1. python3 tools/build_book.py --local <deps> <dir>/book.html   or   python3 tools/build_deck.py --local <deps> <dir>/deck.html
//    (deps: an npm folder with three@0.160.0 and the @fontsource Archivo, Geist Sans and Geist Mono packages)
// 2. wrap the output in a document, serve "/" over http (module scripts need http), then:
//    node tools/make_pdf.js <url> <out.pdf> [width height]      book: 1320 1868 (default), deck: 1920 1080
const { chromium } = require(process.env.PLAYWRIGHT || 'playwright');

(async () => {
  const [url, out, w = '1320', h = '1868'] = process.argv.slice(2);
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: +w, height: +h }, reducedMotion: 'reduce' });
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.documentElement.classList.add('pdf'));
  if (await page.$('#stage')) {
    await page.waitForFunction(() => document.getElementById('stage').classList.contains('ready'), null, { timeout: 60000 });
    await page.evaluate(() => dispatchEvent(new Event('resize')));
  }
  await page.emulateMedia({ media: 'print' });
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => { document.querySelectorAll('.slide').forEach(s => { s.style.zoom = 1; }); window.fitSlides && window.fitSlides(); });
  await page.waitForTimeout(800);
  await page.pdf({ path: out, width: w + 'px', height: h + 'px', printBackground: true });
  await browser.close();
  console.log('wrote', out);
})();
