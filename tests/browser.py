"""Browser smoke test. Accepts a local or deployed GitHub Pages base URL."""
from pathlib import Path
import os
import sys
from urllib.parse import urljoin, urlparse, unquote
from urllib.request import urlopen
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
base = (sys.argv[1] if len(sys.argv)>1 else "http://localhost:8080").rstrip("/") + "/"
out = ROOT / "test-results"
out.mkdir(exist_ok=True)
with sync_playwright() as p:
    override = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
    bundled = list(Path("/root/.cache/ms-playwright").glob("chromium-*/chrome-linux64/chrome"))
    options = {"headless": True, "args": ["--no-sandbox"]}
    if override:
        options["executable_path"] = override
    elif bundled:
        options["executable_path"] = str(sorted(bundled)[-1])
    browser = p.chromium.launch(**options)
    context = browser.new_context(viewport={"width":1440,"height":1000}, reduced_motion="reduce")
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("response", lambda r: errors.append(f"HTTP {r.status}: {r.url}") if r.status>=400 else None)
    documents = {}
    for route in ["", "storyboard.html"]:
        response = page.goto(urljoin(base,route), wait_until="networkidle")
        assert response.status == 200
        assert page.locator("h1").count() == 1
        assert page.locator("main").count() == 1
        for width in [1440, 768, 390, 320]:
            page.set_viewport_size({"width":width,"height":1000})
            assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), f"Overflow on {route} at {width}"
        # Verify every same-origin link and fragment, even on a project subpath.
        links = page.locator("a[href]").evaluate_all("els => els.map(e=>e.href)")
        for link in set(links):
            parsed = urlparse(link)
            if parsed.netloc != urlparse(base).netloc:
                continue
            target = link.split("#")[0]
            if target not in documents:
                # urllib honors standard HTTPS_PROXY settings in remote workspaces.
                with urlopen(target, timeout=30) as result:
                    assert result.status == 200, f"Broken internal link: {link}"
                    documents[target] = result.read().decode("utf-8")
            if parsed.fragment:
                assert f'id="{unquote(parsed.fragment)}"' in documents[target], f"Missing fragment: {link}"
    page.set_viewport_size({"width":1440,"height":1000})
    page.goto(base, wait_until="networkidle")
    assert page.locator("#max-load").inner_text() == "24 → 12"
    # The user's typography requirement: prose, code, and math have separate faces.
    font_roles = page.evaluate("""() => [
      getComputedStyle(document.querySelector('.article-body p')).fontFamily,
      getComputedStyle(document.querySelector('pre code')).fontFamily,
      getComputedStyle(document.querySelector('.katex-html .mathnormal')).fontFamily
    ]""")
    assert len(set(font_roles)) == 3, font_roles
    page.evaluate("() => document.fonts.load('15px \"DejaVu Code\"')")
    page.evaluate("() => document.fonts.load('17px Lato')")
    page.locator("#replica-budget").select_option("0")
    assert page.locator("#max-load").inner_text() == "24 → 24"
    assert page.locator("#replica-count").inner_text() == "0"
    page.locator("#reset-planner").click()
    page.locator("#training-mode").check()
    assert page.locator("#replica-count").inner_text() == "0"
    page.locator("#hot-load").fill("96")
    assert int(page.locator("#replica-count").inner_text()) > 0
    assert page.locator("#block-total").inner_text() == "120"
    page.locator("#reset-planner").click()
    page.locator("#hot-load").focus()
    page.keyboard.press("ArrowRight")
    assert page.locator("#hot-value").inner_text() == "28"
    page.locator("#reset-planner").click()
    for video in page.locator("video").all():
        video.evaluate("v => {v.muted=true; v.load();}")
        video.evaluate("v => new Promise((resolve,reject)=>{if(v.readyState>=2)return resolve();v.addEventListener('loadeddata',resolve,{once:true});v.addEventListener('error',()=>reject(new Error('Video decode failed')),{once:true});})")
        assert video.evaluate("v => v.videoWidth") == 1920
        assert 20 < video.evaluate("v => v.duration") < 40
        video.evaluate("v => v.play()")
        page.wait_for_timeout(250)
        assert video.evaluate("v => v.currentTime") > 0
        video.evaluate("v => {v.pause();v.currentTime=0;}")
    page.evaluate("window.scrollTo(0,0)")
    page.screenshot(path=str(out/"desktop.png"))
    page.locator("#planner-lab").screenshot(path=str(out/"planner-desktop.png"))
    page.locator(".code-figure").screenshot(path=str(out/"code-desktop.png"))
    page.set_viewport_size({"width":390,"height":844})
    page.evaluate("window.scrollTo(0,0)")
    page.screenshot(path=str(out/"mobile.png"))
    page.locator("#planner-lab").screenshot(path=str(out/"planner-mobile.png"))
    # Text and native disclosure widgets remain usable with JavaScript disabled.
    nojs = browser.new_context(java_script_enabled=False, viewport={"width":390,"height":844})
    fallback = nojs.new_page()
    fallback.goto(base)
    assert fallback.locator("#backward h2").inner_text() == "Bring every partial to the table."
    fallback.locator(".transcript summary").first.click()
    assert fallback.locator(".transcript").first.get_attribute("open") is not None
    assert fallback.locator("noscript").inner_text().startswith("The interactive model")
    assert not errors, errors
    browser.close()
print("PASS: desktop/mobile, links, conservation UI, keyboard, video decoding, no-JS reading, and zero browser errors")
