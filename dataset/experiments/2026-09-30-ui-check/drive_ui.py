"""Headless Edge against the local web (3100): the popup, the reminder row, the summary tab."""

import pathlib
import re
import sys

from playwright.sync_api import sync_playwright

S = pathlib.Path(__file__).parent
token = next(l.split()[1] for l in (S / "seed_out.txt").read_text(encoding="utf-8").splitlines() if l.startswith("TOKEN"))
ids = eval(next(l[4:] for l in (S / "seed_out.txt").read_text(encoding="utf-8").splitlines() if l.startswith("IDS")))
BASE = "http://localhost:3100"
shots = S / "ui_shots"
shots.mkdir(exist_ok=True)

errors: list[str] = []
with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    ctx = browser.new_context(viewport={"width": 1280, "height": 900}, locale="ko-KR")
    ctx.add_cookies([{"name": "autune_session", "value": token, "domain": "localhost", "path": "/"}])
    page = ctx.new_page()
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)

    page.goto(f"{BASE}/meetings/{ids['this']}/actions", wait_until="networkidle", timeout=120_000)
    dialog = page.get_by_role("dialog", name="지난 회의 미완료 액션")
    dialog.wait_for(timeout=60_000)
    page.screenshot(path=str(shots / "1_popup.png"))
    print("popup text:", re.sub(r"\s+", " ", dialog.inner_text())[:400])
    dialog.get_by_role("button", name="확인").click()
    page.wait_for_timeout(500)
    page.screenshot(path=str(shots / "2_reminder.png"))
    print("reminder visible:", page.get_by_text("지난 회의에서 넘어온 미완료 액션 3건").first.is_visible())

    page.reload(wait_until="networkidle")
    page.wait_for_timeout(1500)
    print("popup after reload (should be False):", page.get_by_role("dialog").count() > 0)

    page.goto(f"{BASE}/meetings/{ids['this']}/summary", wait_until="networkidle", timeout=120_000)
    page.get_by_text("개요").first.wait_for(timeout=60_000)
    page.screenshot(path=str(shots / "3_summary.png"), full_page=True)
    print("tabs:", [t.inner_text() for t in page.get_by_role("link").all() if t.inner_text() in ("요약", "전사", "액션", "갭", "컨텍스트")])
    page.get_by_role("textbox").fill("다음 회의 전에 배포 일정 다시 확인 (2차)")
    page.get_by_role("button", name="저장").click()
    page.get_by_text("마지막 저장").wait_for(timeout=30_000)
    page.screenshot(path=str(shots / "4_memo_saved.png"), full_page=True)
    page.reload(wait_until="networkidle")
    page.get_by_text("개요").first.wait_for(timeout=60_000)
    print("memo after reload:", page.get_by_role("textbox").input_value())
    browser.close()

print("console errors:", errors[:5] if errors else "none")
sys.exit(0)
