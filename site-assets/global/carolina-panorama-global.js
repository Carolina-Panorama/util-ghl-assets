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
                'https://via.placeholder.com/400x200';

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
     * Fetch articles from backend API and map to metadata objects.
     * @param {Object} params - { limit, offset, categoryUrlSlug }
     * @returns {Promise<Array>} Array of article metadata objects
     */
    window.CarolinaPanorama.fetchArticlesFromBackend = async function({
        limit = 10,
        offset = 0,
        categoryUrlSlug = null,
        tag = null,
        locationId = '9Iv8kFcMiUgScXzMPv23',
        blogId = 'iWSdkAQOuuRNrWiAHku1'
    } = {}) {
        const baseUrl = 'https://backend.leadconnectorhq.com/blogs/posts/list';
        const params = [
            `locationId=${encodeURIComponent(locationId)}`,
            `blogId=${encodeURIComponent(blogId)}`,
            `limit=${encodeURIComponent(limit)}`,
            `offset=${encodeURIComponent(offset)}`
        ];
        // Only one of tag or categoryUrlSlug can be used
        if (tag && !categoryUrlSlug) {
            // If tag is an array, join with comma, else use as is
            const tagValue = Array.isArray(tag) ? tag.join(',') : tag;
            params.push(`tag=${encodeURIComponent(tagValue)}`);
        } else if (categoryUrlSlug && !tag) {
            params.push(`categoryUrlSlug=${encodeURIComponent(categoryUrlSlug)}`);
        }
        const url = `${baseUrl}?${params.join('&')}`;
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`Backend fetch failed: ${response.status}`);
            const data = await response.json();
            if (!data.blogPosts || !Array.isArray(data.blogPosts)) return [];
            return data.blogPosts.map(post => ({
                url: post.canonicalLink || (post.urlSlug ? `/post/${post.urlSlug}` : ''),
                title: post.title,
                description: post.description,
                image: post.imageUrl,
                author: post.author?.name || 'Unknown',
                date: post.publishedAt,
                categories: Array.isArray(post.categories) && post.categories.length > 0
                    ? post.categories.map(cat => cat.label)
                    : ['News']
            }));
        } catch (error) {
            console.error('Error fetching articles from backend:', error);
            return [];
        }
    };
    console.log('Carolina Panorama Global JS loaded');
})();
