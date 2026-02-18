#!/usr/bin/env python3
"""
WordPress Widget Shortcode Generator
Generates PHP shortcode wrapper boilerplate for all Carolina Panorama widgets.
Output: PHP files ready to be included in WordPress theme functions.php or custom plugin.
"""

import json
import os
from pathlib import Path

# Widget manifest (simplified version for script generation)
WIDGETS = [
    {
        "name": "article_detail",
        "title": "Article Detail",
        "file": "site-feed-widgets/article-detail-widget.html",
        "shortcode": "cp_article_detail",
        "attrs": [
            {"name": "article_id", "type": "int", "required": True, "description": "Article ID from CMS API"},
        ],
        "js_deps": ["carolina-panorama-global.js"],
        "css": ["article-detail-styles (inline in HTML)"],
    },
    {
        "name": "article_feed",
        "title": "Article Feed",
        "file": "site-feed-widgets/article-feed-widget.html",
        "shortcode": "cp_article_feed",
        "attrs": [
            {"name": "category", "type": "string", "required": False, "description": "Category slug"},
            {"name": "per_page", "type": "int", "required": False, "default": 10, "description": "Articles per page"},
            {"name": "page", "type": "int", "required": False, "default": 1, "description": "Page number"},
        ],
        "js_deps": ["carolina-panorama-global.js"],
        "css": ["shared-article-card-styles.css"],
    },
    {
        "name": "headlines_grid",
        "title": "Headlines Grid",
        "file": "site-home-widgets/headlines-grid-v2.html",
        "shortcode": "cp_headlines_grid",
        "attrs": [],
        "js_deps": ["carolina-panorama-global.js"],
        "css": ["shared-article-card-styles.css"],
    },
    {
        "name": "category_grid",
        "title": "Category Grid",
        "file": "site-home-widgets/category-grid-widget.html",
        "shortcode": "cp_category_grid",
        "attrs": [],
        "js_deps": ["carolina-panorama-global.js"],
        "css": [],
    },
    {
        "name": "search",
        "title": "Search Widget",
        "file": "search-assets/search-widget.html",
        "shortcode": "cp_search",
        "attrs": [],
        "js_deps": ["instantsearch.js"],
        "css": ["instantsearch.css"],
    },
]


def generate_shortcode_php(widget):
    """Generate PHP shortcode handler for a widget."""
    shortcode_name = widget["shortcode"].replace("cp_", "")
    php_class_name = "".join(word.capitalize() for word in shortcode_name.split("_"))

    # Build attributes array
    attrs_php = ""
    if widget["attrs"]:
        attrs_php = "    // Shortcode attributes with defaults\n"
        attrs_php += "    $defaults = [\n"
        for attr in widget["attrs"]:
            default = attr.get("default", "''")
            attrs_php += f"        '{attr['name']}' => {default},\n"
        attrs_php += "    ];\n"
        attrs_php += "    $atts = shortcode_atts( $defaults, $atts, '{widget['shortcode']}' );\n\n"

    # Build JS/CSS enqueue
    enqueue_code = ""
    for js in widget["js_deps"]:
        js_handle = js.replace(".js", "").replace("-", "_")
        enqueue_code += f"    wp_enqueue_script( '{js_handle}' );\n"
    for css in widget["css"]:
        css_handle = css.replace(".css", "").replace("-", "_")
        enqueue_code += f"    wp_enqueue_style( '{css_handle}' );\n"

    # Sanitize shortcode attrs for safe JS
    sanitize_code = ""
    if widget["attrs"]:
        sanitize_code = "    // Pass attributes to JavaScript via data attributes\n"
        sanitize_code += "    $data_attrs = '';\n"
        for attr in widget["attrs"]:
            sanitize_code += f"    if ( ! empty( $atts['{attr['name']}'] ) ) {{\n"
            sanitize_code += f"        $data_attrs .= ' data-{attr['name']}=\"' . esc_attr( $atts['{attr['name']}'] ) . '\"';\n"
            sanitize_code += "    }\n"
        sanitize_code += "\n"

    php_template = f'''<?php
/**
 * Shortcode: {widget['shortcode']}
 * Widget: {widget['title']}
 * Auto-generated from WORDPRESS_MIGRATION_MANIFEST.json
 */

function cp_shortcode_{shortcode_name}( $atts = [], $content = null, $tag = '' ) {{
    // Enqueue dependencies
{enqueue_code}
    
{attrs_php}{sanitize_code}    // Return the widget HTML
    ob_start();
    ?>
    <div class="cp-widget-wrapper cp-widget-{shortcode_name}"{{ $data_attrs }}>
        <div id="cp-{shortcode_name}-container">
            <p style="color: #999;">Loading {widget['title']}...</p>
        </div>
    </div>
    <script>
        // TODO: Initialize widget with $atts data
        // Example: fetch from API using window.CarolinaPanorama utilities
        (function() {{
            var container = document.getElementById('cp-{shortcode_name}-container');
            if (!container) return;
            
            // Replace this with actual widget initialization logic
            console.log('Widget {shortcode_name} initialized with:', {{}});
        }})();
    </script>
    <?php
    return ob_get_clean();
}}

// Register shortcode
add_shortcode( '{widget['shortcode']}', 'cp_shortcode_{shortcode_name}' );
'''

    return php_template


def generate_functions_php():
    """Generate enqueue code for functions.php."""
    enqueue_template = '''<?php
/**
 * Carolina Panorama WordPress Theme Functions
 * Auto-generated enqueue code for global assets and shortcodes
 */

// Enqueue global assets
function cp_enqueue_global_assets() {
    // Global CSS
    wp_enqueue_style(
        'cp-global-css',
        get_template_directory_uri() . '/css/carolina-panorama-global.css',
        [],
        filemtime( get_template_directory() . '/css/carolina-panorama-global.css' )
    );

    // Global JS (must be loaded before widgets)
    wp_enqueue_script(
        'cp-global-js',
        get_template_directory_uri() . '/js/carolina-panorama-global.js',
        [],
        filemtime( get_template_directory() . '/js/carolina-panorama-global.js' ),
        true // Load in footer
    );

    // Optional: Set global API base URL (can override in child theme or settings)
    wp_localize_script( 'cp-global-js', 'CarolinaPanoramaConfig', [
        'apiBaseUrl' => get_option( 'cp_api_base_url', 'https://cms.carolinapanorama.org' ),
        'siteUrl' => site_url(),
    ]);
}
add_action( 'wp_enqueue_scripts', 'cp_enqueue_global_assets' );

// Widget-specific styles (loaded on-demand by shortcodes)
function cp_enqueue_article_card_styles() {
    wp_enqueue_style(
        'cp-article-card-styles',
        get_template_directory_uri() . '/css/shared-article-card-styles.css',
        [],
        filemtime( get_template_directory() . '/css/shared-article-card-styles.css' )
    );
}

// External libraries (Algolia, YouTube, etc.)
function cp_enqueue_external_libs() {
    // Algolia InstantSearch CSS
    wp_enqueue_style(
        'algolia-instantsearch-css',
        'https://cdn.jsdelivr.net/npm/instantsearch.css@7.4.5/themes/satellite-min.css',
        [],
        '7.4.5'
    );

    // Algolia InstantSearch JS
    wp_enqueue_script(
        'instantsearch-js',
        'https://cdn.jsdelivr.net/npm/instantsearch.js@4.33.0/umd/index.umd.production.min.js',
        [],
        '4.33.0',
        true
    );

    // Quill Rich Text Editor (for forms)
    wp_enqueue_style(
        'quill-snow-css',
        'https://cdn.quilljs.com/1.3.6/quill.snow.css',
        [],
        '1.3.6'
    );

    wp_enqueue_script(
        'quill-js',
        'https://cdn.quilljs.com/1.3.6/quill.min.js',
        [],
        '1.3.6',
        true
    );
}
add_action( 'wp_enqueue_scripts', 'cp_enqueue_external_libs' );

// TODO: Include shortcode handlers
// require_once get_template_directory() . '/inc/shortcodes/article-detail.php';
// require_once get_template_directory() . '/inc/shortcodes/article-feed.php';
// ... (add all shortcodes)
'''
    return enqueue_template


def main():
    """Generate all shortcode PHP files."""
    output_dir = Path("wordpress-migration/shortcodes")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating shortcode wrappers in: {output_dir}")

    for widget in WIDGETS:
        php_code = generate_shortcode_php(widget)
        filename = f"{widget['name']}.php"
        filepath = output_dir / filename
        
        with open(filepath, "w") as f:
            f.write(php_code)
        
        print(f"  ✓ Created {filename}")

    # Generate functions.php template
    functions_php = generate_functions_php()
    with open(output_dir / "functions-template.php", "w") as f:
        f.write(functions_php)
    print(f"  ✓ Created functions-template.php")

    # Generate manifest of all shortcodes
    shortcodes_manifest = {
        "shortcodes": [
            {
                "shortcode": w["shortcode"],
                "title": w["title"],
                "file": str(output_dir / f"{w['name']}.php"),
                "attributes": w["attrs"],
            }
            for w in WIDGETS
        ]
    }

    with open(output_dir / "SHORTCODES_MANIFEST.json", "w") as f:
        json.dump(shortcodes_manifest, f, indent=2)
    print(f"  ✓ Created SHORTCODES_MANIFEST.json")

    print("\nNext steps:")
    print("1. Copy these PHP files to: wp-content/themes/your-theme/inc/shortcodes/")
    print("2. Include them in functions.php using require_once")
    print("3. Enqueue theme JS/CSS and external libraries (see functions-template.php)")
    print("4. Create 16 WP pages and add shortcodes to page content")
    print("5. Test each shortcode in the WP editor\n")


if __name__ == "__main__":
    main()
