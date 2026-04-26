import os
import time
from playwright.sync_api import sync_playwright

path_dir = r"C:\Users\Amirthesh\Desktop\New folder\Dental_Demand_Platform"
os.chdir(path_dir)

def main():
    print("Starting Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720})

        print("Capturing MVP Dashboard...")
        mvp_url = f"file:///{path_dir.replace(chr(92), '/')}/mvp.html"
        page.goto(mvp_url)
        page.wait_for_timeout(2000)
        page.screenshot(path="mvp_highres.png")

        print("Capturing Phase 2 Dashboard...")
        index_url = f"file:///{path_dir.replace(chr(92), '/')}/index.html"
        page.goto(index_url)
        page.wait_for_timeout(2000)
        
        # Click the nav item for Phase 2
        try:
            page.locator("button[data-view='phase2']").click()
            page.wait_for_timeout(1000)
            print("Successfully transitioned to Phase 2.")
        except Exception as e:
            print(f"Warning: Could not click Phase 2: {e}")
            
        page.screenshot(path="phase2_highres.png")

        print("Updating HTML presentation...")
        with open("presentation.html", "r", encoding="utf-8") as f:
            html = f.read()
        
        html = html.replace("mvp_dashboard_1774049133650.png", "mvp_highres.png")
        html = html.replace("dental_platform_mockup_1774048622777.png", "phase2_highres.png")

        with open("presentation.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("Rendering PDF...")
        pres_url = f"file:///{path_dir.replace(chr(92), '/')}/presentation.html"
        page.goto(pres_url)
        page.wait_for_timeout(2000)

        # Print layout matches the CSS 1280x720 exactly
        page.pdf(
            path="presentation.pdf",
            width="1280px",
            height="720px",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}
        )

        browser.close()
        print("Successfully generated presentation.pdf!")

if __name__ == "__main__":
    main()
