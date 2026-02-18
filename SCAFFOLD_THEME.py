#!/usr/bin/env python3
"""
WordPress Theme Scaffold Generator
Creates a minimal but complete WordPress theme structure for Carolina Panorama.
Output: theme directory with functions.php, template files, CSS/JS copied from source.
"""

import os
import shutil
from pathlib import Path

TEMPLATE = """
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

"""


def create_style_css():
    """Create theme header (style.css)."""
    return """/*
Theme Name: Carolina Panorama
Theme URI: https://example.com
Description: WordPress theme for Carolina Panorama news site
Version: 1.0.0
Author: Your Name
Author URI: https://example.com
License: GPL v2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html
Text Domain: carolina-panorama
Domain Path: /languages

This theme is designed to migrate the existing Carolina Panorama site
to WordPress while preserving widget-based architecture and API-driven content.
*/

/* Theme CSS is in css/ directory */
"""


def create_functions_php():
    """Create functions.php with enqueue hooks."""
    return """<?php
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
        filemtime( $theme_dir . '/css/carolina-panorama-global.css' )
    );

    // Global JS (loaded in footer, must run before any shortcode JS)
    wp_enqueue_script(
        'cp-global-js',
        $theme_uri . '/js/carolina-panorama-global.js',
        [],
        filemtime( $theme_dir . '/js/carolina-panorama-global.js' ),
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
        filemtime( get_template_directory() . '/css/shared-article-card-styles.css' )
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
 */
function cp_register_widget_areas() {
    register_sidebar( [
        'name'          => __( 'Primary Sidebar', 'carolina-panorama' ),
        'id'            => 'primary-sidebar',
        'description'   => __( 'Main sidebar', 'carolina-panorama' ),
        'before_widget' => '<div id="%1\\$s" class="widget %2\\$s">',
        'after_widget'  => '</div>',
        'before_title'  => '<h3 class="widget-title">',
        'after_title'   => '</h3>',
    ]);
}
add_action( 'widgets_init', 'cp_register_widget_areas' );

/**
 * Include shortcodes
 * Uncomment and add paths to generated shortcode files
 */
// require_once get_template_directory() . '/inc/shortcodes/article-detail.php';
// require_once get_template_directory() . '/inc/shortcodes/article-feed.php';
// ... etc

/**
 * Include template tags
 */
require_once get_template_directory() . '/inc/template-tags.php';
"""


def create_header_php():
    """Create header.php template."""
    return """<?php
/**
 * The header for Carolina Panorama theme
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}
?>
<!doctype html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo( 'charset' ); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="profile" href="https://gmpg.org/xfn/11">
    <?php wp_head(); ?>
</head>

<body <?php body_class(); ?>>
    <?php wp_body_open(); ?>
    <div id="page" class="site">
        <a class="skip-link screen-reader-text" href="#content"><?php _e( 'Skip to content', 'carolina-panorama' ); ?></a>

        <header id="masthead" class="site-header">
            <div class="site-branding">
                <?php
                if ( has_custom_logo() ) {
                    the_custom_logo();
                } else {
                    ?>
                    <h1 class="site-title">
                        <a href="<?php echo esc_url( home_url( '/' ) ); ?>" rel="home">
                            <?php bloginfo( 'name' ); ?>
                        </a>
                    </h1>
                    <?php
                }

                $description = get_bloginfo( 'description', 'display' );
                if ( $description ) {
                    ?>
                    <p class="site-description"><?php echo esc_html( $description ); ?></p>
                    <?php
                }
                ?>
            </div><!-- .site-branding -->

            <nav id="site-navigation" class="main-navigation">
                <button class="menu-toggle" aria-controls="primary-menu" aria-expanded="false">
                    <?php _e( 'Primary Menu', 'carolina-panorama' ); ?>
                </button>
                <?php
                wp_nav_menu( [
                    'theme_location' => 'primary',
                    'menu_id'        => 'primary-menu',
                    'depth'          => 2,
                ] );
                ?>
            </nav><!-- #site-navigation -->
        </header><!-- #masthead -->

        <main id="content" class="site-content">
"""


def create_footer_php():
    """Create footer.php template."""
    return """<?php
/**
 * The footer for Carolina Panorama theme
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}
?>

        </main><!-- #content -->

        <footer id="colophon" class="site-footer">
            <div class="site-info">
                <p>&copy; <?php echo date( 'Y' ); ?> <?php bloginfo( 'name' ); ?>. All rights reserved.</p>
            </div><!-- .site-info -->
        </footer><!-- #colophon -->
    </div><!-- #page -->

    <?php wp_footer(); ?>
</body>
</html>
"""


def create_page_php():
    """Create page.php template (for pages and shortcodes)."""
    return """<?php
/**
 * The template for displaying pages
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

get_header();
?>

<div class="page-wrapper">
    <?php
    while ( have_posts() ) {
        the_post();
        ?>
        <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
            <div class="entry-content">
                <?php
                the_content();
                wp_link_pages( [
                    'before' => '<div class="page-links">' . esc_html__( 'Pages:', 'carolina-panorama' ),
                    'after'  => '</div>',
                ] );
                ?>
            </div><!-- .entry-content -->
        </article><!-- #post-<?php the_ID(); ?> -->
        <?php
    }
    ?>
</div><!-- .page-wrapper -->

<?php get_footer(); ?>
"""


def create_404_php():
    """Create 404.php template."""
    return """<?php
/**
 * The template for displaying 404 pages
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

get_header();
?>

<div class="error-404">
    <div class="error-wrapper">
        <h1><?php _e( 'Oops! That page can&rsquo;t be found.', 'carolina-panorama' ); ?></h1>
        <p><?php _e( 'The page you are looking for doesn&rsquo;t exist or has been moved.', 'carolina-panorama' ); ?></p>
        <p><a href="<?php echo esc_url( home_url( '/' ) ); ?>" class="button"><?php _e( 'Go Home', 'carolina-panorama' ); ?></a></p>
    </div>
</div>

<?php get_footer(); ?>
"""


def create_template_tags():
    """Create inc/template-tags.php."""
    return """<?php
/**
 * Template tags for Carolina Panorama theme
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Get API base URL (with fallback)
 */
function cp_get_api_url() {
    return get_option( 'cp_api_base_url', 'https://cms.carolinapanorama.org' );
}

/**
 * Echo breadcrumbs (basic implementation)
 */
function cp_breadcrumbs() {
    if ( is_home() ) {
        return;
    }

    echo '<div class="breadcrumbs">';
    echo '<a href="' . esc_url( home_url() ) . '">Home</a> / ';

    if ( is_category() || is_single() ) {
        the_category( ', ' );
        if ( is_single() ) {
            echo ' / ' . get_the_title();
        }
    } elseif ( is_page() ) {
        echo get_the_title();
    }

    echo '</div>';
}

/**
 * Get featured image with fallback
 */
function cp_get_featured_image( $post_id = null, $size = 'post-thumbnail' ) {
    if ( ! $post_id ) {
        $post_id = get_the_ID();
    }

    if ( has_post_thumbnail( $post_id ) ) {
        return get_the_post_thumbnail_url( $post_id, $size );
    }

    // Return placeholder or external image URL if no WP thumbnail
    return '';
}
"""


def main():
    """Generate theme scaffold."""
    theme_dir = Path("wordpress-migration/themes/carolina-panorama")
    theme_dir.mkdir(parents=True, exist_ok=True)

    print(f"Scaffolding WordPress theme in: {theme_dir}")

    # Create directories
    dirs = [
        theme_dir / "css",
        theme_dir / "js",
        theme_dir / "inc" / "shortcodes",
        theme_dir / "inc" / "template-parts",
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Created {d.relative_to(theme_dir.parent.parent)}/")

    # Create files
    files = {
        "style.css": create_style_css(),
        "functions.php": create_functions_php(),
        "header.php": create_header_php(),
        "footer.php": create_footer_php(),
        "page.php": create_page_php(),
        "404.php": create_404_php(),
        "inc/template-tags.php": create_template_tags(),
        "README.md": TEMPLATE,
    }

    for filename, content in files.items():
        filepath = theme_dir / filename
        filepath.write_text(content)
        print(f"  ✓ Created {filename}")

    # TODO: Copy CSS/JS from source (we'll do this in next step with actual file paths)

    print("\nTheme scaffold created!")
    print(f"  Theme directory: {theme_dir}")
    print("\nNext steps:")
    print("1. Copy global CSS/JS from source to theme/css and theme/js")
    print("2. Run GENERATE_SHORTCODES.py to create shortcode files")
    print("3. Copy theme to wp-content/themes/ in your WP installation")
    print("4. Activate theme in WP Admin")
    print("5. Create 16 pages and add shortcodes\n")


if __name__ == "__main__":
    main()
