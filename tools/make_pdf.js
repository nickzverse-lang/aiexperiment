// Export the project book to PDF with real 3D and local fonts.
// 1. python3 tools/build_book.py --local <deps> <dir>/local-body.html   (deps: npm folder with three + @fontsource fonts)
// 2. wrap it in a document, serve "/" over http (module scripts need http), then:
//    node tools/make_pdf.js http://127.0.0.1:8765/<dir>/local.html docs/bluprint-project-book.pdf
const { chromium } = require(process.env.PLAYWRIGHT || 'playwright');

(async () => {
  const [url, out] = process.argv.slice(2);
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1320, height: 1868 }, reducedMotion: 'reduce' });
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.waitForFunction(() => document.getElementById('stage').classList.contains('ready'), null, { timeout: 60000 });
  await page.evaluate(() => { document.documentElement.classList.add('pdf'); dispatchEvent(new Event('resize')); });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(800);
  await page.pdf({ path: out, width: '1320px', height: '1868px', printBackground: true });
  await browser.close();
  console.log('wrote', out);
})();
