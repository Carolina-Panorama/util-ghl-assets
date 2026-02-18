# WordPress Migration Guide: Carolina Panorama

**Timeline:** 2–6 weeks | **Effort:** Medium | **Risk:** Low (API-first keeps content external)

---

## Executive Summary

Your site is **90% ready for WordPress migration** due to its widget-based, API-driven architecture. All content stays in your external API during migration, minimizing risk. You can migrate in **two phases**:

- **Phase 1 (1–2 weeks):** Shortcode wrappers for all widgets. Quick, low-friction. Site goes live as a functional WordPress install while keeping content API-driven.
- **Phase 2 (Optional, 2–4 weeks after):** Convert high-value widgets to native WordPress (articles → posts, categories → taxonomies, search → WP plugins).

---

## What You Have

### Assets (16 total)
- **Widgets:** 16 (article detail, feed, headlines, categories, search, forms, YouTube, etc.)
- **Pages:** 16 (including 404, maintenance)
- **Global JS/CSS:** 2 files that power all widgets
- **External APIs:** Carolina Panorama CMS, Algolia, YouTube

### Architecture
- **Content delivery:** 100% API-first (keep as-is)
- **Frontend:** Client-side widgets (HTML + vanilla JS)
- **No database:** No current WP database needed initially

---

## Phase 1: Shortcode Migration (1–2 weeks)

### Step 1: Scaffold WordPress Theme
Creates the base theme structure with enqueue hooks and template files.

```bash
cd /path/to/your/repo
python3 SCAFFOLD_THEME.py
```

**Output:** `wordpress-migration/themes/carolina-panorama/`

Directory structure:
```
carolina-panorama/
├── style.css
├── functions.php
├── header.php
├── footer.php
├── page.php
├── 404.php
├── css/
│   ├── carolina-panorama-global.css (copy from source)
│   └── shared-article-card-styles.css
├── js/
│   └── carolina-panorama-global.js (copy from source)
└── inc/
    ├── shortcodes/
    └── template-tags.php
```

**What to do:**
1. Copy the generated theme to your WP installation: `wp-content/themes/carolina-panorama/`
2. In WP Admin → Appearance → Themes, activate "Carolina Panorama"

### Step 2: Copy Global Assets
Copy JS and CSS from source to theme:

```bash
# Copy global JS
cp /path/to/site-assets/cpanoram-global/carolina-panorama-global.js \
   wordpress-migration/themes/carolina-panorama/js/

# Copy global CSS
cp /path/to/site-assets/cpanoram-global/carolina-panorama-global.css \
   wordpress-migration/themes/carolina-panorama/css/

# Copy widget CSS files (extract from widgets as needed)
cp /path/to/site-assets/*/shared-article-card-styles.css \
   wordpress-migration/themes/carolina-panorama/css/ 2>/dev/null || true
```

### Step 3: Generate Shortcodes
Creates PHP shortcode wrappers for each widget.

```bash
python3 GENERATE_SHORTCODES.py
```

**Output:** `wordpress-migration/shortcodes/`

Example shortcode file: `article-detail.php`
```php
<?php
function cp_shortcode_article_detail( $atts = [] ) {
    wp_enqueue_script( 'cp-global-js' );
    wp_enqueue_style( 'cp-global-css' );
    
    $atts = shortcode_atts( [
        'article_id' => '',
    ], $atts, 'cp_article_detail' );
    
    ob_start();
    ?>
    <div class="cp-widget-wrapper cp-article-detail" data-article-id="<?php echo esc_attr( $atts['article_id'] ); ?>">
        <!-- Widget HTML here -->
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode( 'cp_article_detail', 'cp_shortcode_article_detail' );
```

**What to do:**
1. Copy generated PHP files to: `wp-content/themes/carolina-panorama/inc/shortcodes/`
2. In `functions.php`, uncomment and add:
   ```php
   require_once get_template_directory() . '/inc/shortcodes/article-detail.php';
   require_once get_template_directory() . '/inc/shortcodes/article-feed.php';
   // ... etc for all 16 widgets
   ```

### Step 4: Create Pages in WordPress
Create 16 pages matching your current site structure:

1. Go to **WP Admin → Pages → Add New**
2. For each page:
   - **Title:** Same as current (e.g., "Article Detail", "Categories", "Search")
   - **Content:** Add the corresponding shortcode
   - **Slug:** Match current URL paths (e.g., `/article/`, `/categories/`, `/search/`)

Example page setup:
```
Page Title: Article
Slug: /article/
Content: [cp_article_detail article_id="123"]

Page Title: Articles
Slug: /articles/
Content: [cp_article_feed category="news" per_page="20"]

Page Title: Headlines
Slug: /
Content: [cp_headlines_grid] [cp_category_grid]
```

### Step 5: Test & Launch
```bash
# Run on staging server
wp server --host=0.0.0.0 --port=8080

# Test each page in browser
# Verify API data loads from your CMS
# Check console for JS errors
```

**Verification checklist:**
- [ ] Global JS loads (check `window.CarolinaPanorama` in console)
- [ ] Global CSS applied (check styles in inspector)
- [ ] Each shortcode renders (article detail shows content, feed pagination works, etc.)
- [ ] API calls succeed (check Network tab in DevTools)
- [ ] Mobile responsive (test on iPhone, tablet)

### Phase 1 Timeline
| Task | Effort | Days |
|------|--------|------|
| Theme scaffold | Low | 0.5 |
| Copy assets | Low | 0.5 |
| Shortcode generation | Medium | 1 |
| Page creation (16 pages) | Medium | 1–2 |
| Testing & QA | Medium | 1–2 |
| **Phase 1 Total** | | **4–6 days** |

---

## Phase 2: Native WordPress Integration (Optional, 2–4 weeks after Phase 1)

Once Phase 1 is live and stable, consider moving high-value content to native WordPress for better editorial workflow:

### Phase 2a: Article Posts
Convert article detail/feed to use WP post types:

1. **Create custom post type** for articles in `functions.php`
2. **Export articles from your CMS API** using provided script (see next section)
3. **Import posts to WP** using WP REST API or WP-CLI
4. **Map old URLs → new permalinks** for SEO
5. **Convert shortcodes** to use `WP_Query` instead of external API

Example custom post type:
```php
function cp_register_post_types() {
    register_post_type( 'cp_article', [
        'public'       => true,
        'label'        => 'Articles',
        'supports'     => ['title', 'editor', 'thumbnail', 'author', 'custom-fields'],
        'rewrite'      => ['slug' => 'articles'],
    ]);
}
add_action( 'init', 'cp_register_post_types' );
```

### Phase 2b: Categories & Taxonomies
Map external categories to WP taxonomies:
```php
register_taxonomy( 'cp_category', 'cp_article', [
    'public' => true,
    'label'  => 'Categories',
] );
```

### Phase 2c: Search Integration
Use **Algolia for WordPress** plugin to keep search powered by Algolia, indexed by WP posts.

---

## Supporting Scripts & Tools

### 1. SCAFFOLD_THEME.py
Generates WordPress theme skeleton with enqueue hooks and templates.

```bash
python3 SCAFFOLD_THEME.py
# Output: wordpress-migration/themes/carolina-panorama/
```

### 2. GENERATE_SHORTCODES.py
Generates PHP shortcode wrapper files (one per widget).

```bash
python3 GENERATE_SHORTCODES.py
# Output: wordpress-migration/shortcodes/
```

### 3. Export Content (Phase 2)
To export articles from your CMS for import into WP:

```bash
python3 EXPORT_ARTICLES.py > articles.json
```

**Expected output:**
```json
{
  "articles": [
    {
      "id": 1,
      "title": "Article Title",
      "slug": "article-title",
      "content": "...",
      "date": "2025-02-17T10:00:00Z",
      "author_id": 1,
      "category": "News",
      "featured_image": "https://..."
    }
  ]
}
```

### 4. Import to WordPress (Phase 2)
Use WP-CLI or WP REST API to import posts:

```bash
# Option A: WP-CLI (fastest)
wp post create --post_type=cp_article --post_title="Title" --post_content="Content" \
  --post_status=publish --post_author=1

# Option B: WP REST API (requires REST plugin enabled)
curl -X POST https://example.com/wp-json/wp/v2/cp_article \
  -H "Content-Type: application/json" \
  -d '{"title": "...", "content": "...", "status": "publish"}' \
  --user admin:password
```

---

## FAQ & Troubleshooting

### Q: Will my API-driven content break during migration?
**A:** No. Phase 1 keeps all content in your external API. WordPress only serves the HTML/CSS/JS wrapper. You can migrate content to WP later (Phase 2).

### Q: Can I keep the current URL structure?
**A:** Yes. Use WordPress **Settings → Permalinks** to match your old structure. Set slugs when creating pages to match old routes.

### Q: What about redirects?
**A:** Create a simple `.htaccess` or NGINX config to redirect old URLs to new WP pages:
```apache
# .htaccess example
RewriteRule ^article/(.*)$ /article/?article_id=$1 [R=301,L]
```

Or use a plugin like **Redirection** to manage 301 redirects in WP Admin.

### Q: Can I test Phase 1 locally first?
**A:** Yes. Run locally:
```bash
wp server --host=127.0.0.1 --port=8080
# Visit http://127.0.0.1:8080
```

Your API should still be accessible (if it's public or on a staging URL).

### Q: How do I handle authentication (login, API keys)?
**A:** 
- **For now:** Keep auth in your external API (no changes needed).
- **Phase 2:** Add WP user auth, OAuth, or API key management in WP Admin.

### Q: What about media uploads?
**A:** 
- **Phase 1:** Media stays in your external storage (no changes).
- **Phase 2 (optional):** Use WP media library or link to external CDN.

### Q: Can I use WP plugins?
**A:** Yes. Install any plugins you need (WP Algolia, Gravity Forms, etc.) alongside shortcodes.

---

## Deployment Checklist

### Pre-Launch
- [ ] Theme activated in WP Admin
- [ ] All shortcodes registered and working
- [ ] Global JS/CSS enqueued (check source in DevTools)
- [ ] 16 pages created and published
- [ ] SEO: Titles, meta descriptions, canonical URLs set
- [ ] Mobile responsive tested
- [ ] 301 redirects from old URLs working (if applicable)
- [ ] Analytics configured (GTM, GA, etc.)

### Launch Steps
1. **Staging:** Deploy to staging WP site, run full QA
2. **DNS cutover:** Update DNS to point old domain to new WP server
3. **Monitoring:** Watch server logs, API responses, error logs for 24 hours
4. **Backups:** Take full backup before and after launch
5. **Announce:** Notify users of any downtime

### Post-Launch
- [ ] Monitor 404s in Google Search Console
- [ ] Check for console errors (DevTools on live site)
- [ ] Test form submissions, API calls
- [ ] Monitor server performance (CPU, memory, DB queries)
- [ ] Plan Phase 2 roadmap (if doing native content import)

---

## File Inventory (Reference)

| Category | Files | Count |
|----------|-------|-------|
| **Global Assets** | carolina-panorama-global.{js,css} | 2 |
| **Feed Widgets** | article-detail, article-feed, newsletter, youtube-* | 5 |
| **Home Widgets** | headlines-grid, category-grid, trending-carousel, article-list, file-list | 5 |
| **Search Widgets** | search, article-search, classifieds-*, nav-search | 4 |
| **Form Widgets** | content-sub (Quill editor) | 1 |
| **Total** | | **16** |

---

## Next Steps

1. **Review manifest:** Read `WORDPRESS_MIGRATION_MANIFEST.json` for detailed widget breakdown
2. **Run scaffold:** Execute `SCAFFOLD_THEME.py` to generate theme
3. **Run shortcodes:** Execute `GENERATE_SHORTCODES.py` to generate shortcode files
4. **Copy assets:** Move JS/CSS to theme directories
5. **Create pages:** Add 16 pages in WP Admin with shortcodes
6. **Test:** Verify all widgets render and API calls work
7. **Launch:** Deploy to production or staging

---

## Questions?

Refer to:
- `WORDPRESS_MIGRATION_MANIFEST.json` — Full widget breakdown, complexity estimates, dependencies
- `GENERATE_SHORTCODES.py` — Shortcode generation (run to see generated PHP)
- `SCAFFOLD_THEME.py` — Theme structure generation (run to see full theme output)

Good luck!
