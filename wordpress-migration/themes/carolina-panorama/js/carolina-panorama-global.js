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
    
    // Utility: Debounce function to limit rate of function calls
    window.CarolinaPanorama.debounce = function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };
    
    // Add preconnect hints for performance
    (function addPreconnects() {
        const domains = [
            'https://cms.carolinapanorama.org',
            'https://api.carolinapanorama.com',
            'https://storage.googleapis.com',
            'https://images.leadconnectorhq.com'
        ];
        
        domains.forEach(domain => {
            const link = document.createElement('link');
            link.rel = 'preconnect';
            link.href = domain;
            link.crossOrigin = 'anonymous';
            document.head.appendChild(link);
        });
    })();
    
    // Utility: Get category class for styling
    window.CarolinaPanorama.getCategoryClass = function(category) {
        if (!category) return '';
        return category.toLowerCase().replace(/\s+/g, '-');
    };

    // Category cache and utilities
    let categoriesCache = null;
    let categoriesFetchPromise = null;
    const CACHE_KEY = 'cp_categories_cache';
    const CACHE_DURATION = 30 * 60 * 1000; // 30 minutes

    // Fetch and cache categories from CMS with localStorage persistence
    window.CarolinaPanorama.fetchCategories = async function(forceRefresh = false) {
        // Check memory cache first
        if (categoriesCache && !forceRefresh) {
            return categoriesCache;
        }
        
        // Check localStorage cache
        if (!forceRefresh) {
            try {
                const cached = localStorage.getItem(CACHE_KEY);
                if (cached) {
                    const { data, timestamp } = JSON.parse(cached);
                    const age = Date.now() - timestamp;
                    
                    if (age < CACHE_DURATION) {
                        categoriesCache = data;
                        console.log('[CarolinaPanorama] Loaded', data.length, 'categories from localStorage cache');
                        return categoriesCache;
                    } else {
                        localStorage.removeItem(CACHE_KEY);
                    }
                }
            } catch (e) {
                console.warn('[CarolinaPanorama] Failed to read localStorage cache:', e);
            }
        }
        
        // If already fetching, return the existing promise
        if (categoriesFetchPromise) {
            return categoriesFetchPromise;
        }
        
        categoriesFetchPromise = (async () => {
            try {
                const apiBase = window.CarolinaPanorama.API_BASE_URL || 'https://cms.carolinapanorama.org';
                const response = await fetch(`${apiBase}/api/public/categories`);
                const data = await response.json();
                
                if (data.success && data.data) {
                    categoriesCache = data.data;
                    
                    // Store in localStorage
                    try {
                        localStorage.setItem(CACHE_KEY, JSON.stringify({
                            data: categoriesCache,
                            timestamp: Date.now()
                        }));
                    } catch (e) {
                        console.warn('[CarolinaPanorama] Failed to cache in localStorage:', e);
                    }
                    
                    console.log('[CarolinaPanorama] Fetched and cached', categoriesCache.length, 'categories');
                    return categoriesCache;
                }
                
                return [];
            } catch (error) {
                console.error('[CarolinaPanorama] Failed to fetch categories:', error);
                return [];
            } finally {
                categoriesFetchPromise = null;
            }
        })();
        
        return categoriesFetchPromise;
    };

    // Get category details by name
    window.CarolinaPanorama.getCategoryByName = async function(categoryName) {
        if (!categoryName) return null;
        
        const categories = await window.CarolinaPanorama.fetchCategories();
        const normalized = categoryName.toLowerCase().trim();
        
        return categories.find(cat => 
            cat.name.toLowerCase() === normalized
        ) || null;
    };

    // Get inline style for category tag with color from CMS
    window.CarolinaPanorama.getCategoryStyle = async function(categoryName) {
        const category = await window.CarolinaPanorama.getCategoryByName(categoryName);
        
        if (category && category.color_code) {
            return `background-color: ${category.color_code} !important;`;
        }
        
        // Fallback to default blue
        return 'background-color: #3b82f6 !important;';
    };

    // Extract keywords from text (simple implementation)
    window.CarolinaPanorama.extractKeywords = function(text, maxKeywords = 5) {
        if (!text) return '';
        
        // Common words to exclude
        const stopWords = new Set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'it', 'its', 'their', 'them', 'they']);
        
        // Extract words, filter stop words, get most meaningful ones
        const words = text.toLowerCase()
            .replace(/[^\w\s]/g, ' ')
            .split(/\s+/)
            .filter(word => word.length > 3 && !stopWords.has(word));
        
        // Count word frequency
        const wordCount = {};
        words.forEach(word => {
            wordCount[word] = (wordCount[word] || 0) + 1;
        });
        
        // Sort by frequency and take top N
        return Object.entries(wordCount)
            .sort((a, b) => b[1] - a[1])
            .slice(0, maxKeywords)
            .map(([word]) => word)
            .join(', ');
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
                author: article.author && article.author.name ? article.author.name : '',
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
    /**
     * SEO Meta Tag Injection Utilities
     * Update page meta tags for SEO (title, description, keywords, og tags)
     */
    window.CarolinaPanorama.setPageMeta = function({
        title = '',
        description = '',
        keywords = '',
        image = '',
        url = '',
        type = 'website'
    } = {}) {
        // Update document title
        if (title) {
            document.title = title;
        }
        
        // Helper to set or update a meta tag
        function setMeta(selector, content) {
            if (!content) return;
            let tag = document.querySelector(selector);
            if (!tag) {
                const [attr, value] = selector.match(/\[(.+)="(.+)"\]/)?.[0]?.replace(/[\[\]]/g, '').split('=') || [];
                if (attr && value) {
                    tag = document.createElement('meta');
                    tag.setAttribute(attr, value.replace(/"/g, ''));
                    document.head.appendChild(tag);
                }
            }
            if (tag) tag.setAttribute('content', content);
        }
        
        // Standard meta tags
        if (description) {
            setMeta('meta[name="description"]', description);
        }
        if (keywords) {
            setMeta('meta[name="keywords"]', keywords);
        }
        
        // Open Graph tags
        if (title) {
            setMeta('meta[property="og:title"]', title);
        }
        if (description) {
            setMeta('meta[property="og:description"]', description);
        }
        if (image) {
            setMeta('meta[property="og:image"]', image);
        }
        if (url) {
            setMeta('meta[property="og:url"]', url);
        }
        if (type) {
            setMeta('meta[property="og:type"]', type);
        }
        
        // Twitter Card tags
        setMeta('meta[name="twitter:card"]', 'summary_large_image');
        if (title) {
            setMeta('meta[name="twitter:title"]', title);
        }
        if (description) {
            setMeta('meta[name="twitter:description"]', description);
        }
        if (image) {
            setMeta('meta[name="twitter:image"]', image);
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

    // ========================================
    // IN-STORY AD INJECTION
    // ========================================
    // BroadStreet handles all other ad types (pop-ups, sticky notes, etc.) through their dashboard.
    // We only need to inject in-story ads programmatically since they need to appear mid-article.

    /**
     * Inject in-story ad into article content
     * Finds a good midpoint in the article and inserts the ad zone
     */
    function injectInstoryAd() {
        const articleBody = document.getElementById('cp-article-body');
        
        if (!articleBody) {
            return; // Not an article page, skip
        }

        // Get all paragraphs in the article
        const paragraphs = articleBody.querySelectorAll('p');
        
        if (paragraphs.length < 3) {
            console.log('[CP Ads] Article too short for in-story ad');
            return;
        }

        // Find a good insertion point (roughly 40-50% through the article)
        const insertionIndex = Math.floor(paragraphs.length * 0.45);
        const targetParagraph = paragraphs[insertionIndex];

        // Create the ad container
        const adContainer = document.createElement('div');
        adContainer.className = 'ad-zone-instory';
        adContainer.innerHTML = '<broadstreet-zone zone-id="179415" uri-keywords="true" soft-keywords="true"></broadstreet-zone>';

        // Insert after the target paragraph
        targetParagraph.parentNode.insertBefore(adContainer, targetParagraph.nextSibling);
        
        console.log('[CP Ads] In-story ad injected after paragraph', insertionIndex + 1);
    }

    // Auto-inject in-story ad when article content loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(injectInstoryAd, 500); // Brief delay for article content to render
        });
    } else {
        setTimeout(injectInstoryAd, 500);
    }

})();

