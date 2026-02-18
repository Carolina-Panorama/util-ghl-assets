<?php
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
