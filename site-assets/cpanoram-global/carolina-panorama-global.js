/**
 * Carolina Panorama Global JavaScript
 * Shared utilities and functions for Carolina Panorama widgets
 */

// Initialize when DOM is ready
(function() {
    'use strict';
    
    // Utility: Format date for display
    window.CarolinaPanorama = window.CarolinaPanorama || {};

    // Base URL for Carolina Panorama CMS public API
    // Can be overridden by setting window.CarolinaPanorama.API_BASE_URL before this script runs
    window.CarolinaPanorama.API_BASE_URL = window.CarolinaPanorama.API_BASE_URL || 'https://cms.carolinapanorama.org';
    
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

    // Article image fallback: replace broken/missing images with a styled placeholder
    (function() {
    function createImgPlaceholder(alt) {
        const div = document.createElement('div');
        div.className = 'img-placeholder';
        div.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="3" y="3" width="18" height="18" rx="4" fill="#e2e8f0"/><path d="M8 13l2.5 3.5L15 11l4 6H5l3-4z" fill="#94a3b8"/></svg>
        <span>No Image</span>
        `;
        if (alt) div.title = alt;
        return div;
    }
    function handleImgError(e) {
        const img = e.target;
        if (!img.classList.contains('img-placeholder')) {
        const alt = img.alt || '';
        const ph = createImgPlaceholder(alt);
        ph.style.width = img.width ? img.width + 'px' : '';
        ph.style.height = img.height ? img.height + 'px' : '';
        img.replaceWith(ph);
        }
    }
    document.addEventListener('DOMContentLoaded', function() {
        document.querySelectorAll('img.cp-article-image').forEach(img => {
        img.addEventListener('error', handleImgError);
        // If already broken (cached 404), trigger error
        if (!img.complete || img.naturalWidth === 0) {
            handleImgError({ target: img });
        }
        });
    });
    })();


    window.CarolinaPanorama.proxiedLeadConnectorUrl = function(originalUrl, width = 1200) {
        if (!originalUrl) return originalUrl;
        if((new URL(originalUrl)).hostname != "storage.googleapis.com") return originalUrl;  // Only proxy GHL storage URLs;
        const normalized = window.CarolinaPanorama.normalizeUrl(originalUrl);
        if (!normalized) return normalized;
        const safe = encodeURI(normalized);
        return 'https://images.leadconnectorhq.com/image/f_webp/q_80/r_' + width + '/u_' + safe;
    };
    
    /**
     * Fetch metadata for a single article URL by scraping meta tags and common selectors.
     * Returns an object with url, title, description, image, author, date, categories.
     */
    window.CarolinaPanorama.fetchArticleMetadata = async function(url) {
        try {
            const response = await fetch(url);
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            const getMetaContent = (property) => {
                const ogTag = doc.querySelector(`meta[property="${property}"]`);
                const nameTag = doc.querySelector(`meta[name="${property}"]`);
                return ogTag?.content || nameTag?.content || '';
            };

            const title = getMetaContent('og:title') ||
                getMetaContent('twitter:title') ||
                doc.querySelector('title')?.textContent ||
                'Article';

            const description = getMetaContent('og:description') ||
                getMetaContent('twitter:description') ||
                getMetaContent('description') ||
                '';

            const image = getMetaContent('og:image') ||
                getMetaContent('twitter:image') ||
                'https://storage.googleapis.com/msgsndr/9Iv8kFcMiUgScXzMPv23/media/697bd8644d56831c95c3248d.svg';

            const authorElement = doc.querySelector('.blog-author-name, [itemprop="author"]');
            const author = authorElement?.textContent?.trim() || 'Carolina Panorama';

            let dateStr = doc.querySelector('.blog-date')?.textContent?.trim();
            if (!dateStr) {
                const dateElement = doc.querySelector('[itemprop="datePublished"], time');
                dateStr = dateElement?.getAttribute('datetime') || dateElement?.textContent;
            }
            const date = dateStr ? new Date(dateStr) : new Date();

            const categoryElements = doc.querySelectorAll('.blog-category, [rel="category tag"]');
            const categories = Array.from(categoryElements)
                .map(el => el.textContent.trim().replace(/^\|\s*/, ''))
                .filter(Boolean);

            return {
                url: url,
                title: title,
                description: description,
                image: image,
                author: author,
                date: date,
                categories: categories.length > 0 ? categories : ['News']
            };
        } catch (error) {
            console.error('Error fetching article metadata:', error);
            return null;
        }
    };

    // proxiedLeadConnectorUrl already present as window.CarolinaPanorama.proxiedLeadConnectorUrl
    /**
     * Fetch articles from Carolina Panorama CMS public API and map to metadata objects.
     * This preserves the original return shape expected by existing widgets.
     * @param {Object} params - { limit, offset, categoryUrlSlug, tag }
     * @returns {Promise<Array>} Array of article metadata objects
     */
    window.CarolinaPanorama.fetchArticlesFromBackend = async function({
        limit = 10,
        offset = 0,
        categoryUrlSlug = null,
        tag = null
    } = {}) {
        const apiBase = window.CarolinaPanorama.API_BASE_URL || 'https://domain.org';
        const perPage = limit;
        const page = Math.floor(offset / perPage) + 1;

        const params = new URLSearchParams();
        params.set('page', String(page));
        params.set('per_page', String(perPage));

        if (categoryUrlSlug) {
            // For now, treat the slug as the category name; if your
            // routes use pretty slugs, ensure the backend accepts this
            // value or update to resolve via /api/public/categories.
            params.set('category', categoryUrlSlug);
        }
        if (tag) {
            params.set('tag', tag);
        }

        const url = `${apiBase}/api/public/articles?${params.toString()}`;
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`CMS fetch failed: ${response.status}`);
            const json = await response.json();
            if (!json.success || !Array.isArray(json.data)) return [];

            return json.data.map(article => ({
                url: article.url || (article.slug ? `/post/${article.slug}` : ''),
                title: article.title,
                description: article.excerpt || '',
                image: article.featured_image,
                author: article.author && article.author.name ? article.author.name : 'Unknown',
                date: article.publish_date,
                categories: Array.isArray(article.categories) && article.categories.length > 0
                    ? article.categories.map(cat => cat.name)
                    : ['News']
            }));
        } catch (error) {
            console.error('Error fetching articles from CMS:', error);
            return [];
        }
    };
    console.log('Carolina Panorama Global JS loaded');

    // Wait for Broadstreet JS library to load, then insert the ad zone
    (function loadBroadstreetAndSignalReady() {
    var bsScript = document.createElement('script');
    bsScript.src = 'https://cdn.broadstreetads.com/init-2.min.js';
    bsScript.onload = function() {
        if (window.broadstreet) {
        broadstreet.watch({ networkId: 10001 });
        document.dispatchEvent(new Event('broadstreet:ready'));
        }
    };
    document.head.appendChild(bsScript);
    })();   
})();

