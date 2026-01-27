/**
 * Carolina Panorama Global JavaScript
 * Shared utilities and functions for Carolina Panorama widgets
 */

// Initialize when DOM is ready
(function() {
    'use strict';
    
    // Utility: Format date for display
    window.CarolinaPanorama = window.CarolinaPanorama || {};
    
    window.CarolinaPanorama.formatDate = function(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };
    
    // Utility: Truncate text to specified length
    window.CarolinaPanorama.truncateText = function(text, maxLength) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength).trim() + '...';
    };
    
    // Utility: Get category class for styling
    window.CarolinaPanorama.getCategoryClass = function(category) {
        if (!category) return '';
        return category.toLowerCase().replace(/\s+/g, '-');
    };

    // Normalize and proxy image URLs via LeadConnector image proxy
    window.CarolinaPanorama.normalizeUrl = function(url) {
        if (!url) return url;
        url = String(url).trim();
        if (!/^https?:\/\//i.test(url)) url = 'https://' + url.replace(/^\/+/, '');
        url = url.replace(/^http:\/\//i, 'https://');

        // Try to decode one level of double-encoding if present
        try {
            if (/%25/.test(url)) {
                const decoded = decodeURIComponent(url);
                if (/^https?:\/\//i.test(decoded)) url = decoded;
            }
        } catch (e) {
            // ignore decode errors
        }

        return url;
    };

    window.CarolinaPanorama.proxiedLeadConnectorUrl = function(originalUrl, width = 1200) {
        if (!originalUrl) return originalUrl;
        const normalized = window.CarolinaPanorama.normalizeUrl(originalUrl);
        if (!normalized) return normalized;
        const safe = encodeURI(normalized);
        return 'https://images.leadconnectorhq.com/image/f_webp/q_80/r_' + width + '/u_' + safe;
    };
    
    // Apply color scheme to tags (covers both .blog-tag and .cp-article-tag)
    function applyTagColors(root = document) {
        const tags = root.querySelectorAll('.blog-tag, .cp-article-tag');

        tags.forEach(tag => {
            const text = (tag.textContent || '').trim().toLowerCase();

            // Reset any previously applied inline styles
            tag.style.backgroundColor = '';
            tag.style.color = '';

            // Apply colors based on category name
            if (text.includes('business')) {
                tag.style.backgroundColor = '#10b981';
                tag.style.color = '#fff';
            } else if (text.includes('politics')) {
                tag.style.backgroundColor = '#8b5cf6';
                tag.style.color = '#fff';
            } else if (text.includes('sports')) {
                tag.style.backgroundColor = '#f59e0b';
                tag.style.color = '#111';
            } else if (text.includes('education')) {
                tag.style.backgroundColor = '#06b6d4';
                tag.style.color = '#fff';
            } else if (text.includes('health')) {
                tag.style.backgroundColor = '#ec4899';
                tag.style.color = '#111';
            } else if (text.includes('local')) {
                tag.style.backgroundColor = '#3b82f6';
                tag.style.color = '#fff';
            }
            // If no match, leave defaults from CSS
        });
    }
    
    // Run on page load
    applyTagColors();

    // Re-run when content changes (for dynamic content)
    const observer = new MutationObserver(muts => {
        muts.forEach(m => {
            m.addedNodes.forEach(n => {
                if (n.nodeType === 1) applyTagColors(n);
            });
        });
    });
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    console.log('Carolina Panorama Global JS loaded');
})();
