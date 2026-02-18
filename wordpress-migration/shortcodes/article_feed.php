<?php
/**
 * Shortcode: cp_article_feed
 * Widget: Article Feed
 * Auto-generated from WORDPRESS_MIGRATION_MANIFEST.json
 */

function cp_shortcode_article_feed( $atts = [], $content = null, $tag = '' ) {
    // Enqueue dependencies
    wp_enqueue_script( 'carolina_panorama_global' );
    wp_enqueue_style( 'shared_article_card_styles' );

    
    // Shortcode attributes with defaults
    $defaults = [
        'category' => '',
        'per_page' => 10,
        'page' => 1,
    ];
    $atts = shortcode_atts( $defaults, $atts, 'cp_article_feed' );

    // Pass attributes to JavaScript via data attributes
    $data_attrs = '';
    if ( ! empty( $atts['category'] ) ) {
        $data_attrs .= ' data-category="' . esc_attr( $atts['category'] ) . '"';
    }
    if ( ! empty( $atts['per_page'] ) ) {
        $data_attrs .= ' data-per_page="' . esc_attr( $atts['per_page'] ) . '"';
    }
    if ( ! empty( $atts['page'] ) ) {
        $data_attrs .= ' data-page="' . esc_attr( $atts['page'] ) . '"';
    }

    // Return the widget HTML
    ob_start();
    ?>
    <div class="cp-widget-wrapper cp-widget-article_feed"{ $data_attrs }>
        <div id="cp-article_feed-container">
            <p style="color: #999;">Loading Article Feed...</p>
        </div>
    </div>
    <script>
        // TODO: Initialize widget with $atts data
        // Example: fetch from API using window.CarolinaPanorama utilities
        (function() {
            var container = document.getElementById('cp-article_feed-container');
            if (!container) return;
            
            // Replace this with actual widget initialization logic
            console.log('Widget article_feed initialized with:', {});
        })();
    </script>
    <?php
    return ob_get_clean();
}

// Register shortcode
add_shortcode( 'cp_article_feed', 'cp_shortcode_article_feed' );
