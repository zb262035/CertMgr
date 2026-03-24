"""Playwright UI test for CertMgr certificate functionality."""
import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), 'screenshots')
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

async def test_certificates():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        errors = []
        page.on("console", lambda msg: errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None)

        print("1. 打开登录页...")
        await page.goto("http://localhost:5002/auth/login")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "01_login.png"))

        print("2. 登录...")
        await page.fill('input[name="email"]', "admin@example.com")
        await page.fill('input[name="password"]', "admin123")
        await page.click('input[type="submit"]')
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "02_after_login.png"))
        print(f"   登录后当前URL: {page.url}")

        print("3. 进入证书列表...")
        await page.goto("http://localhost:5002/certificates/")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "03_certs_list.png"))

        # 检查是否有控制台错误
        if errors:
            print(f"   ⚠️ Console 错误: {errors}")
            errors.clear()
        else:
            print("   ✅ 无 Console 错误")

        print("4. 测试搜索功能...")
        await page.fill('#search-input', "证书")
        await page.click('#filter-btn')
        await page.wait_for_timeout(1000)
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "04_search.png"))

        print("5. 测试点击卡片...")
        cards = await page.query_selector_all('.view-cert-btn')
        print(f"   找到 {len(cards)} 个证书卡片")

        if cards:
            await cards[0].click()
            await page.wait_for_load_state("networkidle")
            await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "05_detail.png"))
            print(f"   点击后URL: {page.url}")

            if "/certificates/" in page.url and "/detail" not in page.url:
                # 检查是否成功跳转到详情页
                title = await page.text_content('h4')
                print(f"   ✅ 证书详情: {title}")
            else:
                print(f"   ⚠️ 跳转结果: {page.url}")

        print("6. 测试上传页面...")
        await page.goto("http://localhost:5002/certificates/upload")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "06_upload.png"))

        # 检查动态字段是否显示
        type_select = await page.query_selector('#certificate_type_id')
        if type_select:
            await type_select.select_option(index=1)
            await page.wait_for_timeout(500)
            await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "07_upload_type.png"))
            dynamic_fields = await page.query_selector('#dynamic-fields-container')
            if dynamic_fields:
                style = await dynamic_fields.get_attribute('style')
                if 'none' not in style:
                    print("   ✅ 动态字段容器显示正常")
                else:
                    print("   ⚠️ 动态字段容器被隐藏")

        print("7. 测试统计页面...")
        await page.goto("http://localhost:5002/admin/statistics")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "08_stats.png"))

        # 截图已完成
        print("\n📸 截图已保存到 tests/screenshots/:")
        print("  - 01_login.png")
        print("  - 02_after_login.png")
        print("  - 03_certs_list.png")
        print("  - 04_search.png")
        print("  - 05_detail.png")
        print("  - 06_upload.png")
        print("  - 07_upload_type.png")
        print("  - 08_stats.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_certificates())
