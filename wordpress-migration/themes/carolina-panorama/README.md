
# WordPress Theme Scaffold

This script generates a minimal WordPress theme tailored for the Carolina Panorama migration.

## What it does:

1. Creates `wp-content/themes/carolina-panorama/` directory
2. Copies global JS and CSS from source
3. Generates `functions.php` with enqueue code
4. Creates template files (header.php, footer.php, single.php, page.php, etc.)
5. Sets up directory structure for shortcodes and widget-specific assets

## File structure:

```
carolina-panorama/
├── functions.php
├── style.css (theme header)
├── header.php
├── footer.php
├── page.php (static pages)
├── single.php (single post - for future native post types)
├── search.php
├── 404.php
├── js/
│   └── carolina-panorama-global.js (copied from source)
├── css/
│   ├── carolina-panorama-global.css (copied from source)
│   └── shared-article-card-styles.css (extracted from widgets)
├── inc/
│   ├── shortcodes/
│   │   ├── article-detail.php
│   │   ├── article-feed.php
│   │   ├── headlines-grid.php
│   │   ├── category-grid.php
│   │   └── ... (one per widget)
│   └── template-tags.php (helper functions)
└── README.md
```

## How to use:

1. Run: `python3 SCAFFOLD_THEME.py`
2. Copy generated `carolina-panorama/` to your WP installation: `wp-content/themes/`
3. In WP Admin: Appearance → Themes → Activate "Carolina Panorama"
4. Go to Appearance → Customizer to configure logo, colors, etc.
5. Create 16 pages (or import pages from old site if available)
6. Add shortcodes to page content

## Next: Shortcodes

After theme scaffold is active, run `GENERATE_SHORTCODES.py` to create shortcode PHP files,
then include them in functions.php.

## Customization

- `style.css`: Modify theme metadata (author, version, URI, etc.)
- `functions.php`: Add custom hooks, filters, admin settings
- `css/`: Add theme-specific overrides or new styles
- `inc/shortcodes/`: Modify shortcode handlers to match your API schema

