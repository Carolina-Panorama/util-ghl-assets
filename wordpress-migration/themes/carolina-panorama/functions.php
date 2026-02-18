<?php
/**
 * Carolina Panorama Theme Functions
 */

// Prevent direct access
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Enqueue global assets
 */
function cp_enqueue_global_assets() {
    $theme_uri = get_template_directory_uri();
    $theme_dir = get_template_directory();

    // Global CSS
    wp_enqueue_style(
        'cp-global-css',
        $theme_uri . '/css/carolina-panorama-global.css',
        [],
        '1.0.0'
    );

    // Global JS (loaded in footer, must run before any shortcode JS)
    wp_enqueue_script(
        'cp-global-js',
        $theme_uri . '/js/carolina-panorama-global.js',
        [],
        '1.0.0',
        true // Load in footer
    );

    // Pass config to JS
    wp_localize_script( 'cp-global-js', 'CarolinaPanoramaConfig', [
        'apiBaseUrl' => get_option( 'cp_api_base_url', 'https://cms.carolinapanorama.org' ),
        'siteUrl' => site_url(),
        'restUrl' => rest_url(),
    ]);
}
add_action( 'wp_enqueue_scripts', 'cp_enqueue_global_assets', 10 );

/**
 * Enqueue shared article styles (used by multiple widgets)
 */
function cp_enqueue_article_card_styles() {
    wp_enqueue_style(
        'cp-article-card-styles',
        get_template_directory_uri() . '/css/shared-article-card-styles.css',
        [],
        '1.0.0'
    );
}

/**
 * Enqueue external libraries (Algolia, Quill, YouTube, etc.)
 */
function cp_enqueue_external_libs() {
    // Algolia InstantSearch CSS
    wp_enqueue_style(
        'algolia-instantsearch-css',
        'https://cdn.jsdelivr.net/npm/instantsearch.css@7.4.5/themes/satellite-min.css',
        [],
        '7.4.5'
    );

    // Quill Rich Text Editor
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
add_action( 'wp_enqueue_scripts', 'cp_enqueue_external_libs', 11 );

/**
 * Theme supports
 */
add_theme_support( 'title-tag' );
add_theme_support( 'post-thumbnails' );
add_theme_support( 'html5', [
    'search-form',
    'comment-form',
    'comment-list',
    'gallery',
    'caption',
    'style',
    'script',
]);
add_theme_support( 'automatic-feed-links' );

/**
 * Register widget areas (sidebars)
* function cp_register_widget_areas() {
*     register_sidebar( [
*         'name'          => __( 'Primary Sidebar', 'carolina-panorama' ),
*         'id'            => 'primary-sidebar',
*         'description'   => __( 'Main sidebar', 'carolina-panorama' ),
*         'before_widget' => '<div id="%1\$s" class="widget %2\$s">',
*         'after_widget'  => '</div>',
*         'before_title'  => '<h3 class="widget-title">',
*         'after_title'   => '</h3>',
*     ]);
* }
* add_action( 'widgets_init', 'cp_register_widget_areas' );
**/

/**
 * Include shortcodes
 */
require_once get_template_directory() . '/inc/shortcodes/article_detail.php';
require_once get_template_directory() . '/inc/shortcodes/article_feed.php';
require_once get_template_directory() . '/inc/shortcodes/headlines_grid.php';
require_once get_template_directory() . '/inc/shortcodes/category_grid.php';
require_once get_template_directory() . '/inc/shortcodes/search.php';
require_once get_template_directory() . '/inc/shortcodes/trending_carousel.php';
require_once get_template_directory() . '/inc/shortcodes/article_list_feed.php';
require_once get_template_directory() . '/inc/shortcodes/file_list_preview.php';
require_once get_template_directory() . '/inc/shortcodes/classifieds_sidebar.php';
require_once get_template_directory() . '/inc/shortcodes/classifieds_search.php';
require_once get_template_directory() . '/inc/shortcodes/article_search.php';
require_once get_template_directory() . '/inc/shortcodes/nav_search.php';

/**
 * Include template tags
 */
require_once get_template_directory() . '/inc/template-tags.php';

/**
 * Include blocks
 */
require_once get_template_directory() . '/inc/blocks.php';
