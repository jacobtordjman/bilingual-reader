"""
Advanced Bilingual Reader Component
A paginated, app-like reading experience with overlay controls.
"""

import json
from typing import List, Tuple


def generate_reader_html(sentence_pairs: List[Tuple[str, str]], 
                         initial_font_size: int = 18,
                         initial_margin: int = 24,
                         initial_page: int = 0,
                         book_id: str = None,
                         supabase_url: str = "",
                         supabase_key: str = "") -> str:
    """
    Generate the complete HTML/CSS/JS for the reader.
    """
    
    # Convert sentence pairs to JSON for JavaScript
    pairs_json = json.dumps(sentence_pairs, ensure_ascii=False)
    
    html = f'''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --font-size: {initial_font_size}px;
            --margin: {initial_margin}px;
            --page-bg: #fefefe;
            --text-color: #1a1a1a;
            --english-color: #555;
            --overlay-bg: rgba(0, 0, 0, 0.85);
            --accent-color: #667eea;
            --transition-speed: 0.3s;
            --mobile-nav-height: 0px; /* Will be set to 60px on mobile */
            --vh: 1vh; /* Fallback for dynamic viewport height */
        }}
        
        html, body {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            position: fixed;
            overscroll-behavior: none;
            -webkit-overflow-scrolling: touch;
        }}
        
        body {{
            font-family: 'Georgia', 'Times New Roman', serif;
            background: var(--page-bg);
            color: var(--text-color);
            user-select: none;
            -webkit-user-select: none;
            touch-action: none;
            overflow: hidden !important;
        }}
        
        /* Reader Viewport - Fixed to prevent scroll */
        .reader-viewport {{
            width: 100vw;
            width: 100dvw;
            height: 100vh;
            height: 100dvh;
            height: calc(var(--vh, 1vh) * 100);
            position: fixed;
            top: 0;
            left: 0;
            overflow: hidden;
            overscroll-behavior: contain;
        }}
        
        /* Page Container - NO SCROLLING ALLOWED */
        .page-container {{
            width: 100%;
            height: calc(100% - var(--mobile-nav-height));
            padding: var(--margin);
            overflow: hidden !important;
            touch-action: none;
            -webkit-overflow-scrolling: none;
            overscroll-behavior: none;
            transition: opacity var(--transition-speed) ease;
        }}
        
        .page-container.transitioning {{
            opacity: 0;
        }}
        
        /* Sentence Pair Styling */
        .sentence-pair {{
            margin-bottom: 1.2em;
        }}
        
        .spanish {{
            display: block;
            font-size: var(--font-size);
            font-weight: 600;
            color: var(--text-color);
            line-height: 1.5;
            margin-bottom: 0.3em;
        }}
        
        .english {{
            display: block;
            font-size: calc(var(--font-size) * 0.85);
            font-style: italic;
            color: var(--english-color);
            line-height: 1.4;
        }}
        
        /* Navigation Zones */
        .nav-zone {{
            position: absolute;
            top: 0;
            height: calc(100% - var(--mobile-nav-height));
            width: 25%;
            z-index: 5;
            cursor: pointer;
        }}
        
        .nav-zone.left {{
            left: 0;
        }}
        
        .nav-zone.right {{
            right: 0;
        }}
        
        .nav-zone:hover {{
            background: linear-gradient(90deg, rgba(0,0,0,0.02) 0%, transparent 100%);
        }}
        
        .nav-zone.right:hover {{
            background: linear-gradient(270deg, rgba(0,0,0,0.02) 0%, transparent 100%);
        }}
        
        /* Visual Navigation Hints (Mobile) */
        .nav-hint {{
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            font-size: 32px;
            color: rgba(0, 0, 0, 0.12);
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: 6;
        }}
        
        .nav-hint.left {{
            left: 12px;
        }}
        
        .nav-hint.right {{
            right: 12px;
        }}
        
        .nav-hint.show {{
            opacity: 1;
        }}
        
        /* Center Tap Zone - for overlay toggle */
        .center-zone {{
            position: absolute;
            top: 20%;
            left: 25%;
            width: 50%;
            height: 60%;
            z-index: 4;
            cursor: pointer;
        }}
        
        /* Mobile Bottom Navigation Bar */
        .mobile-nav-bar {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            display: none; /* Hidden by default, shown on mobile */
            align-items: center;
            justify-content: space-between;
            padding: 0 16px;
            z-index: 1000;
            transition: transform 0.3s ease, opacity 0.3s ease;
            box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.2);
        }}
        
        .mobile-nav-bar.hidden {{
            transform: translateY(100%);
            opacity: 0;
        }}
        
        .mobile-nav-btn {{
            min-width: 44px;
            height: 44px;
            padding: 0 20px;
            background: rgba(255, 255, 255, 0.15);
            border: none;
            border-radius: 22px;
            color: white;
            font-size: 15px;
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all 0.2s ease;
            touch-action: manipulation;
        }}
        
        .mobile-nav-btn:active {{
            background: rgba(102, 126, 234, 0.9);
            transform: scale(0.95);
        }}
        
        .mobile-nav-btn:disabled {{
            opacity: 0.3;
            background: rgba(255, 255, 255, 0.1);
        }}
        
        .mobile-page-indicator {{
            color: white;
            font-size: 14px;
            font-weight: 500;
            opacity: 0.9;
            text-align: center;
            flex: 1;
        }}
        
        /* Overlay Controls */
        .overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 100;
            opacity: 0;
            transition: opacity var(--transition-speed) ease;
        }}
        
        .overlay.visible {{
            opacity: 1;
            pointer-events: auto;
        }}
        
        /* Top Bar */
        .top-bar {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            padding: 16px 20px;
            background: var(--overlay-bg);
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .top-bar h1 {{
            font-size: 16px;
            font-weight: 500;
            opacity: 0.9;
        }}
        
        .page-indicator {{
            font-size: 14px;
            opacity: 0.8;
        }}
        
        /* Bottom Bar */
        .bottom-bar {{
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            padding: 20px;
            background: var(--overlay-bg);
            color: white;
        }}
        
        /* Progress Slider */
        .progress-container {{
            margin-bottom: 16px;
        }}
        
        .progress-slider {{
            width: 100%;
            height: 4px;
            -webkit-appearance: none;
            appearance: none;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 2px;
            outline: none;
            cursor: pointer;
        }}
        
        .progress-slider::-webkit-slider-thumb {{
            -webkit-appearance: none;
            appearance: none;
            width: 16px;
            height: 16px;
            background: var(--accent-color);
            border-radius: 50%;
            cursor: pointer;
            transition: transform 0.2s;
        }}
        
        .progress-slider::-webkit-slider-thumb:hover {{
            transform: scale(1.2);
        }}
        
        .progress-slider::-moz-range-thumb {{
            width: 16px;
            height: 16px;
            background: var(--accent-color);
            border-radius: 50%;
            cursor: pointer;
            border: none;
        }}
        
        /* Settings Row */
        .settings-row {{
            display: flex;
            justify-content: center;
            gap: 32px;
            padding-top: 8px;
        }}
        
        .setting-group {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .setting-label {{
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            opacity: 0.7;
        }}
        
        .setting-btn {{
            width: 36px;
            height: 36px;
            border: none;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.15);
            color: white;
            font-size: 18px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s, transform 0.2s;
        }}
        
        .setting-btn:hover {{
            background: rgba(255, 255, 255, 0.25);
            transform: scale(1.1);
        }}
        
        .setting-btn:active {{
            transform: scale(0.95);
        }}
        
        .setting-value {{
            font-size: 14px;
            min-width: 40px;
            text-align: center;
        }}
        
        /* Visible Navigation Buttons (Desktop) */
        .nav-buttons {{
            position: fixed;
            bottom: 40px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 20px;
            z-index: 50;
            opacity: 0.7;
            transition: opacity 0.3s ease;
        }}
        
        .nav-buttons:hover {{
            opacity: 1;
        }}
        
        /* Hide nav buttons when overlay is visible */
        .overlay.visible ~ .nav-buttons {{
            opacity: 0;
            pointer-events: none;
        }}
        
        .nav-btn {{
            padding: 14px 32px;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            color: white;
            border: none;
            border-radius: 30px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }}
        
        .nav-btn:hover {{
            background: rgba(102, 126, 234, 0.95);
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
        }}
        
        .nav-btn:active {{
            transform: translateY(0);
        }}
        
        .nav-btn:disabled {{
            opacity: 0.3;
            cursor: not-allowed;
        }}
        
        .nav-btn:disabled:hover {{
            background: rgba(0, 0, 0, 0.8);
            transform: none;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }}
        
        /* Mobile Optimizations */
        @media (max-width: 768px) {{
            :root {{
                --font-size: 16px;
                --margin: 12px;
                --mobile-nav-height: 60px;
            }}
            
            .nav-buttons {{
                display: none;
            }}
            
            .mobile-nav-bar {{
                display: flex;
            }}
            
            .spanish {{
                font-size: var(--font-size);
            }}
            
            .english {{
                font-size: calc(var(--font-size) * 0.88);
            }}
            
            /* Larger touch targets for mobile */
            .setting-btn {{
                width: 44px;
                height: 44px;
                font-size: 20px;
            }}
            
            .nav-zone {{
                width: 30%;
            }}
            
            .center-zone {{
                left: 30%;
                width: 40%;
            }}
            
            /* Bottom bar adjustments */
            .bottom-bar {{
                padding: 16px;
                padding-bottom: calc(16px + env(safe-area-inset-bottom));
            }}
            
            .settings-row {{
                gap: 20px;
                flex-wrap: wrap;
            }}
            
            .setting-label {{
                font-size: 11px;
            }}
            
            .setting-value {{
                min-width: 50px;
                font-size: 15px;
            }}
            
            /* Top bar */
            .top-bar {{
                padding: 12px 16px;
                padding-top: max(12px, env(safe-area-inset-top));
            }}
            
            .top-bar h1 {{
                font-size: 14px;
            }}
            
            .page-indicator {{
                font-size: 12px;
            }}
            
            /* Progress slider - larger touch target */
            .progress-slider {{
                height: 6px;
            }}
            
            .progress-slider::-webkit-slider-thumb {{
                width: 20px;
                height: 20px;
            }}
            
            .progress-slider::-moz-range-thumb {{
                width: 20px;
                height: 20px;
            }}
        }}
        
        /* Very small screens (phones in portrait) */
        @media (max-width: 480px) {{
            :root {{
                --font-size: 15px;
                --margin: 10px;
            }}
            
            .sentence-pair {{
                margin-bottom: 1em;
            }}
            
            .settings-row {{
                gap: 16px;
            }}
        }}
        
        /* Landscape mobile optimization */
        @media (max-width: 896px) and (orientation: landscape) {{
            :root {{
                --margin: 10px;
                --mobile-nav-height: 50px;
            }}
            
            .mobile-nav-bar {{
                height: 50px;
                padding: 0 12px;
            }}
            
            .mobile-nav-btn {{
                height: 38px;
                min-width: 38px;
                font-size: 14px;
            }}
            
            .top-bar {{
                padding: 8px 12px;
            }}
            
            .bottom-bar {{
                padding: 12px;
            }}
            
            .settings-row {{
                gap: 16px;
            }}
            
            .setting-btn {{
                width: 32px;
                height: 32px;
            }}
        }}
        
        /* Page Turn Animation */
        @keyframes slideInLeft {{
            from {{ transform: translateX(-20px); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
        
        @keyframes slideInRight {{
            from {{ transform: translateX(20px); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
        
        .page-container.slide-left {{
            animation: slideInLeft 0.25s ease-out forwards;
        }}
        
        .page-container.slide-right {{
            animation: slideInRight 0.25s ease-out forwards;
        }}
        
        /* Loading indicator */
        .loading {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 16px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="reader-viewport" id="viewport">
        <div class="page-container" id="pageContainer">
            <div class="loading">Loading...</div>
        </div>
        
        <!-- Navigation Zones -->
        <div class="nav-zone left" id="navLeft" title="Previous page"></div>
        <div class="nav-zone right" id="navRight" title="Next page"></div>
        <div class="center-zone" id="centerZone"></div>
        
        <!-- Visual Navigation Hints (appear briefly on page turn) -->
        <div class="nav-hint left" id="navHintLeft">‹</div>
        <div class="nav-hint right" id="navHintRight">›</div>
        
        <!-- Overlay Controls -->
        <div class="overlay" id="overlay">
            <div class="top-bar">
                <h1>📚 Bilingual Reader</h1>
                <span class="page-indicator" id="pageIndicator">Page 1 of 1</span>
            </div>
            
            <div class="bottom-bar">
                <div class="progress-container">
                    <input type="range" class="progress-slider" id="progressSlider" 
                           min="0" max="100" value="0">
                </div>
                
                <div class="settings-row">
                    <div class="setting-group">
                        <span class="setting-label">Font</span>
                        <button class="setting-btn" id="fontMinus">−</button>
                        <span class="setting-value" id="fontValue">{initial_font_size}px</span>
                        <button class="setting-btn" id="fontPlus">+</button>
                    </div>
                    
                    <div class="setting-group">
                        <span class="setting-label">Margin</span>
                        <button class="setting-btn" id="marginMinus">−</button>
                        <span class="setting-value" id="marginValue">{initial_margin}px</span>
                        <button class="setting-btn" id="marginPlus">+</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Visible Navigation Buttons (Desktop) -->
        <div class="nav-buttons" id="navButtons">
            <button class="nav-btn" id="prevBtn">
                ← Previous
            </button>
            <button class="nav-btn" id="nextBtn">
                Next →
            </button>
        </div>
        
        <!-- Mobile Bottom Navigation Bar -->
        <div class="mobile-nav-bar" id="mobileNavBar">
            <button class="mobile-nav-btn" id="mobilePrevBtn">‹ Prev</button>
            <div class="mobile-page-indicator" id="mobilePageIndicator">1 / 1</div>
            <button class="mobile-nav-btn" id="mobileNextBtn">Next ›</button>
        </div>
    </div>
    
    <script>
        // Sentence pairs data
        const sentencePairs = {pairs_json};
        
        // Reader State
        const bookId = {json.dumps(book_id or 'default')};
        const localStorageKey = `bilingual_reader_page_${{bookId}}`;
        
        // Initialize Supabase Client
        const supabaseUrl = "{supabase_url}";
        const supabaseKey = "{supabase_key}";
        let supabase = null;
        
        if (supabaseUrl && supabaseKey) {{
            try {{
                supabase = window.supabase.createClient(supabaseUrl, supabaseKey);
                console.log("Supabase client initialized via CDN");
            }} catch (e) {{
                console.error("Failed to init Supabase:", e);
            }}
        }}

        // Try to load from localStorage first, then fall back to initial_page
        let savedPage = 0;
        try {{
            const saved = localStorage.getItem(localStorageKey);
            if (saved !== null) {{
                savedPage = parseInt(saved, 10);
            }}
        }} catch (e) {{
            console.warn('localStorage not available:', e);
        }}
        
        const state = {{
            currentPage: savedPage || {initial_page},
            totalPages: 1,
            pages: [],
            fontSize: {initial_font_size},
            margin: {initial_margin},
            overlayVisible: false,
            isMobile: window.innerWidth <= 768,
            navBarVisible: true,
            navTimeout: null
        }};
        
        // ... (DOM Elements and Setup ...)

        // Save current page to localStorage AND Supabase
        function saveBookmark() {{
            // 1. Local Storage (Instant)
            try {{
                localStorage.setItem(localStorageKey, state.currentPage.toString());
            }} catch (e) {{
                console.warn('Failed to save bookmark locally:', e);
            }}
            
            // 2. Supabase (Debounced/Async)
            if (supabase && bookId && bookId !== 'default') {{
                // Simple debounce/throttle could be added here, but for page turns it's likely fine
                // to just fire and forget.
                supabase
                    .from('user_books')
                    .update({{ current_page: state.currentPage }})
                    .eq('id', bookId)
                    .then(data => {{
                        if (data.error) console.warn("Bookmark sync error:", data.error);
                    }});
            }}
        }}
        
        // DOM Elements
        const viewport = document.getElementById('viewport');
        const pageContainer = document.getElementById('pageContainer');
        const overlay = document.getElementById('overlay');
        const progressSlider = document.getElementById('progressSlider');
        const pageIndicator = document.getElementById('pageIndicator');
        const fontValue = document.getElementById('fontValue');
        const marginValue = document.getElementById('marginValue');
        const mobileNavBar = document.getElementById('mobileNavBar');
        const mobilePageIndicator = document.getElementById('mobilePageIndicator');
        const navHintLeft = document.getElementById('navHintLeft');
        const navHintRight = document.getElementById('navHintRight');
        
        // Set dynamic viewport height (fixes mobile browser chrome issues)
        function setViewportHeight() {{
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${{vh}}px`);
        }}
        
        // Check if mobile
        function isMobileDevice() {{
            return window.innerWidth <= 768;
        }}
        
        // Auto-hide mobile nav bar
        function showMobileNavBar() {{
            if (!isMobileDevice()) return;
            
            mobileNavBar.classList.remove('hidden');
            state.navBarVisible = true;
            
            // Clear existing timeout
            if (state.navTimeout) {{
                clearTimeout(state.navTimeout);
            }}
            
            // Set new timeout to hide after 3 seconds
            state.navTimeout = setTimeout(() => {{
                mobileNavBar.classList.add('hidden');
                state.navBarVisible = false;
            }}, 3000);
        }}
        
        // Show navigation hint briefly
        function showNavHint(direction) {{
            if (!isMobileDevice()) return;
            
            const hint = direction === 'left' ? navHintLeft : navHintRight;
            hint.classList.add('show');
            setTimeout(() => {{
                hint.classList.remove('show');
            }}, 400);
        }}
        
        // Pagination Engine
        function paginateContent() {{
            // Calculate available height (subtract mobile nav bar if present)
            const mobileNavHeight = isMobileDevice() ? 60 : 0;
            const bufferHeight = 10; // Buffer to prevent clipping
            const containerHeight = window.innerHeight - (state.margin * 2) - mobileNavHeight - bufferHeight;
            const containerWidth = viewport.clientWidth - (state.margin * 2);
            
            // Create measurement element
            const measurer = document.createElement('div');
            measurer.style.cssText = `
                position: absolute;
                visibility: hidden;
                width: ${{containerWidth}}px;
                padding: 0;
            `;
            document.body.appendChild(measurer);
            
            state.pages = [];
            let currentPage = [];
            let currentHeight = 0;
            
            for (let i = 0; i < sentencePairs.length; i++) {{
                const pair = sentencePairs[i];
                
                // Create temp element to measure height
                const tempEl = document.createElement('div');
                tempEl.className = 'sentence-pair';
                tempEl.innerHTML = `
                    <span class="spanish" style="font-size: ${{state.fontSize}}px">${{pair[0]}}</span>
                    <span class="english" style="font-size: ${{state.fontSize * 0.85}}px">${{pair[1]}}</span>
                `;
                measurer.appendChild(tempEl);
                const pairHeight = tempEl.offsetHeight + (state.fontSize * 0.8); // margin
                measurer.removeChild(tempEl);
                
                if (currentHeight + pairHeight > containerHeight && currentPage.length > 0) {{
                    // Start new page
                    state.pages.push([...currentPage]);
                    currentPage = [i];
                    currentHeight = pairHeight;
                }} else {{
                    currentPage.push(i);
                    currentHeight += pairHeight;
                }}
            }}
            
            // Add last page
            if (currentPage.length > 0) {{
                state.pages.push(currentPage);
            }}
            
            document.body.removeChild(measurer);
            
            state.totalPages = state.pages.length || 1;
            
            // Ensure current page is valid
            if (state.currentPage >= state.totalPages) {{
                state.currentPage = state.totalPages - 1;
            }}
            
            updateUI();
            renderCurrentPage();
        }}
        
        // Render current page
        function renderCurrentPage(direction = null) {{
            if (state.pages.length === 0) {{
                pageContainer.innerHTML = '<div style="padding: 40px; text-align: center; color: #666;">No content to display</div>';
                return;
            }}
            
            const pageIndices = state.pages[state.currentPage] || [];
            let html = '';
            
            for (const idx of pageIndices) {{
                const pair = sentencePairs[idx];
                html += `
                    <div class="sentence-pair">
                        <span class="spanish">${{pair[0]}}</span>
                        <span class="english">${{pair[1]}}</span>
                    </div>
                `;
            }}
            
            // Apply transition animation
            if (direction) {{
                pageContainer.classList.add('transitioning');
                setTimeout(() => {{
                    pageContainer.innerHTML = html;
                    pageContainer.classList.remove('transitioning');
                    pageContainer.classList.add(direction === 'next' ? 'slide-left' : 'slide-right');
                    setTimeout(() => {{
                        pageContainer.classList.remove('slide-left', 'slide-right');
                    }}, 250);
                }}, 150);
            }} else {{
                pageContainer.innerHTML = html;
            }}
        }}
        
        // Update UI elements
        function updateUI() {{
            // Desktop indicators
            pageIndicator.textContent = `Page ${{state.currentPage + 1}} of ${{state.totalPages}}`;
            progressSlider.max = state.totalPages - 1;
            progressSlider.value = state.currentPage;
            fontValue.textContent = `${{state.fontSize}}px`;
            marginValue.textContent = `${{state.margin}}px`;
            
            // Mobile nav bar indicator
            mobilePageIndicator.textContent = `${{state.currentPage + 1}} / ${{state.totalPages}}`;
            
            // Update CSS variables
            document.documentElement.style.setProperty('--font-size', `${{state.fontSize}}px`);
            document.documentElement.style.setProperty('--margin', `${{state.margin}}px`);
            
            // Update navigation buttons
            updateNavButtons();
        }}
        

        
        // Navigation
        function goToPage(pageNum, direction = null) {{
            if (pageNum >= 0 && pageNum < state.totalPages) {{
                state.currentPage = pageNum;
                saveBookmark(); // Save on every page change
                updateUI();
                renderCurrentPage(direction);
                showMobileNavBar(); // Show nav bar on page change
            }}
        }}
        
        function nextPage() {{
            if (state.currentPage < state.totalPages - 1) {{
                showNavHint('right');
                goToPage(state.currentPage + 1, 'next');
            }}
        }}
        
        function prevPage() {{
            if (state.currentPage > 0) {{
                showNavHint('left');
                goToPage(state.currentPage - 1, 'prev');
            }}
        }}
        
        // Toggle overlay
        function toggleOverlay() {{
            state.overlayVisible = !state.overlayVisible;
            overlay.classList.toggle('visible', state.overlayVisible);
        }}
        
        // Font size controls
        function adjustFontSize(delta) {{
            state.fontSize = Math.max(12, Math.min(32, state.fontSize + delta));
            paginateContent();
        }}
        
        // Margin controls
        function adjustMargin(delta) {{
            state.margin = Math.max(8, Math.min(64, state.margin + delta));
            paginateContent();
        }}
        
        // Update button states
        function updateNavButtons() {{
            const prevBtn = document.getElementById('prevBtn');
            const nextBtn = document.getElementById('nextBtn');
            const mobilePrevBtn = document.getElementById('mobilePrevBtn');
            const mobileNextBtn = document.getElementById('mobileNextBtn');
            
            if (prevBtn && nextBtn) {{
                prevBtn.disabled = state.currentPage === 0;
                nextBtn.disabled = state.currentPage === state.totalPages - 1;
            }}
            
            if (mobilePrevBtn && mobileNextBtn) {{
                mobilePrevBtn.disabled = state.currentPage === 0;
                mobileNextBtn.disabled = state.currentPage === state.totalPages - 1;
            }}
        }}
        
        // Event Listeners
        document.getElementById('navLeft').addEventListener('click', prevPage);
        document.getElementById('navRight').addEventListener('click', nextPage);
        document.getElementById('centerZone').addEventListener('click', toggleOverlay);
        
        // Desktop navigation buttons
        document.getElementById('prevBtn').addEventListener('click', prevPage);
        document.getElementById('nextBtn').addEventListener('click', nextPage);
        
        // Mobile navigation buttons
        document.getElementById('mobilePrevBtn').addEventListener('click', prevPage);
        document.getElementById('mobileNextBtn').addEventListener('click', nextPage);
        
        // Tap anywhere to show mobile nav bar
        pageContainer.addEventListener('click', (e) => {{
            if (isMobileDevice() && !state.navBarVisible) {{
                showMobileNavBar();
            }}
        }});
        
        progressSlider.addEventListener('input', (e) => {{
            goToPage(parseInt(e.target.value));
        }});
        
        document.getElementById('fontMinus').addEventListener('click', () => adjustFontSize(-2));
        document.getElementById('fontPlus').addEventListener('click', () => adjustFontSize(2));
        document.getElementById('marginMinus').addEventListener('click', () => adjustMargin(-8));
        document.getElementById('marginPlus').addEventListener('click', () => adjustMargin(8));
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowLeft') prevPage();
            else if (e.key === 'ArrowRight') nextPage();
            else if (e.key === 'Escape') {{
                if (state.overlayVisible) toggleOverlay();
            }}
        }});
        
        // Handle resize and orientation change
        let resizeTimeout;
        window.addEventListener('resize', () => {{
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {{
                setViewportHeight();
                state.isMobile = isMobileDevice();
                paginateContent();
            }}, 200);
        }});
        
        // Update viewport height on orientation change
        window.addEventListener('orientationchange', () => {{
            setTimeout(() => {{
                setViewportHeight();
                paginateContent();
            }}, 100);
        }});
        
        // Touch swipe support
        let touchStartX = 0;
        viewport.addEventListener('touchstart', (e) => {{
            touchStartX = e.touches[0].clientX;
        }});
        
        viewport.addEventListener('touchend', (e) => {{
            const touchEndX = e.changedTouches[0].clientX;
            const diff = touchStartX - touchEndX;
            
            if (Math.abs(diff) > 50) {{
                if (diff > 0) nextPage();
                else prevPage();
            }}
        }});
        
        // Initialize
        document.addEventListener('DOMContentLoaded', () => {{
            setViewportHeight();
            paginateContent();
            if (isMobileDevice()) {{
                showMobileNavBar();
            }}
        }});
        
        // Also init immediately in case DOM is already ready
        if (document.readyState !== 'loading') {{
            setViewportHeight();
            paginateContent();
            if (isMobileDevice()) {{
                showMobileNavBar();
            }}
        }}
    </script>
</body>
</html>
'''
    
    return html
