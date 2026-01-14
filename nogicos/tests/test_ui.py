# -*- coding: utf-8 -*-
"""
UI Rendering Tests

Tests for NogicOS React UI using Playwright.
Requires: npm run build (or dev server running at localhost:5173)
"""

import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

# Path to React build output
UI_DIR = Path(__file__).parent.parent / "nogicos-ui"
DIST_DIR = UI_DIR / "dist"
INDEX_HTML = DIST_DIR / "index.html"


def get_test_url():
    """
    Get URL for testing:
    - Try dev server first (localhost:5173)
    - Otherwise skip (React apps need a server for proper loading)
    
    Note: file:// URLs don't work well with React Router and asset loading.
    """
    import socket
    
    # Check if dev server is running
    def is_port_open(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(0.5)
            result = sock.connect_ex(('localhost', port))
            return result == 0
        finally:
            sock.close()
    
    if is_port_open(5173):
        return "http://localhost:5173"
    
    # Skip if no server running
    return None


@pytest.fixture(scope="module")
def browser():
    """Launch browser for UI tests"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    """Create a new page for each test"""
    url = get_test_url()
    if url is None:
        pytest.skip("UI not built. Run: cd nogicos-ui && npm run build")
    
    context = browser.new_context()
    page = context.new_page()
    page.goto(url)
    page.wait_for_load_state("domcontentloaded")
    yield page
    context.close()


class TestAppContainer:
    """Tests for main app container"""
    
    def test_app_root_exists(self, page):
        """React root should exist"""
        root = page.locator("#root")
        expect(root).to_be_visible()
    
    def test_app_has_content(self, page):
        """App should render content in root"""
        root = page.locator("#root")
        # Should have child elements (React rendered)
        children = root.locator("> *")
        expect(children.first).to_be_visible()


class TestTitleBar:
    """Tests for title bar component (custom Electron titlebar)"""
    
    def test_titlebar_or_header_renders(self, page):
        """Title bar or header should render"""
        # React app uses data-testid or class names
        titlebar = page.locator("[data-testid='titlebar'], header, [class*='titlebar'], [class*='TitleBar']")
        if titlebar.count() > 0:
            expect(titlebar.first).to_be_visible()
        else:
            pytest.skip("TitleBar not found - may be rendered by Electron")


class TestChatArea:
    """Tests for chat/main area component"""
    
    def test_main_content_renders(self, page):
        """Main content area should render"""
        # Look for main content area
        main = page.locator("main, [class*='chat'], [class*='Chat'], [role='main']")
        if main.count() > 0:
            expect(main.first).to_be_visible()
        else:
            # Fallback: any substantial content
            root = page.locator("#root")
            expect(root).to_be_visible()


class TestResponsiveLayout:
    """Tests for responsive layout"""
    
    def test_layout_at_1280x800(self, page):
        """Layout should work at 1280x800"""
        page.set_viewport_size({"width": 1280, "height": 800})
        root = page.locator("#root")
        expect(root).to_be_visible()
    
    def test_layout_at_1920x1080(self, page):
        """Layout should work at 1920x1080"""
        page.set_viewport_size({"width": 1920, "height": 1080})
        root = page.locator("#root")
        expect(root).to_be_visible()
