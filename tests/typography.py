"""Verify actual rendered fonts, expanded math, narrow layouts, zoom, and no-JS.

Computed font-family declarations alone can pass even when fonts never load.
Chromium's CSS domain reports which font actually rendered each selected node.
"""
from pathlib import Path
import json
import os
import sys
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
BASE=(sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8086').rstrip('/')+'/'
OUT=ROOT/'test-results/typography';OUT.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    options={'headless':True,'args':['--no-sandbox']}
    candidates=sorted(Path('/root/.cache/ms-playwright').glob('chromium-*/chrome-linux64/chrome'))
    if os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE'):
        options['executable_path']=os.environ['PLAYWRIGHT_CHROMIUM_EXECUTABLE']
    elif candidates:
        options['executable_path']=str(candidates[-1])
    browser=p.chromium.launch(**options)
    page=browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('response',lambda r:errors.append(f'{r.status} {r.url}') if r.status>=400 else None)
    page.goto(BASE,wait_until='networkidle')
    page.evaluate('''async () => {document.querySelectorAll('details').forEach(d=>d.open=true);await document.fonts.ready;}''')
    assert page.locator('.katex-error').count()==0
    count=page.locator('.katex').count()
    assert count>=60, count
    assert page.locator('.katex math').count()==count
    assert page.locator('math-inline, math-block').count()==0
    assert page.locator('.article-body sub').count()==0, 'Hand-built subscripts remain'
    session=page.context.new_cdp_session(page)
    session.send('DOM.enable');session.send('CSS.enable')
    root=session.send('DOM.getDocument')['root']['nodeId']
    font_report={}
    for role,selector,expected in [('prose','.article-body .lead','Lato'),('code','pre code','DejaVu Sans Mono'),('math','.math-inline .katex-html .mathnormal','KaTeX_Math')]:
        node=session.send('DOM.querySelector',{'nodeId':root,'selector':selector})['nodeId']
        fonts=session.send('CSS.getPlatformFontsForNode',{'nodeId':node})['fonts']
        font_report[role]=fonts
        assert any(expected in f['familyName'] and f['isCustomFont'] and f['glyphCount']>0 for f in fonts),(role,fonts)
    for width in [1440,768,390,320]:
        page.set_viewport_size({'width':width,'height':1000})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Expanded content overflows at {width}'
        assert page.evaluate('''() => [...document.querySelectorAll('.math-display')].every(e=>e.scrollWidth<=e.clientWidth+1 || getComputedStyle(e).overflowX==='auto')''')
        page.locator('.projection-equations').screenshot(path=str(OUT/f'equations-{width}.png'))
        page.locator('#backward details').first.screenshot(path=str(OUT/f'backward-math-{width}.png'))
    page.set_viewport_size({'width':1440,'height':1000})
    page.locator('.code-figure').screenshot(path=str(OUT/'code.png'))
    page.locator('#planner').screenshot(path=str(OUT/'planner-chapter.png'))
    page.evaluate("document.documentElement.style.zoom='200%'")
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Overflow at 200% zoom'
    page.locator('.projection-equations').screenshot(path=str(OUT/'equations-zoom-200.png'))
    nojs=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
    fallback=nojs.new_page();fallback.goto(BASE,wait_until='networkidle')
    assert fallback.locator('.katex').count()==count+fallback.locator('noscript .katex').count()
    assert fallback.locator('.projection-equations').is_visible()
    # The browser exposes real mathematical structure, not a string of fake subscripts.
    assert fallback.locator('math mfrac').count()>0
    assert fallback.locator('math msub, math msup, math msubsup').count()>0
    fallback.locator('.projection-equations').screenshot(path=str(OUT/'no-js-math.png'))
    assert not errors,errors
    (OUT/'font-report.json').write_text(json.dumps({'expressions':count,'fonts':font_report,'checks':['expanded details at 320/390/768/1440 px','200% zoom','static MathML without JavaScript']},indent=2))
    print(json.dumps({'result':'PASS','expressions':count,'fonts':{k:[f['familyName'] for f in v] for k,v in font_report.items()}},indent=2))
    browser.close()
