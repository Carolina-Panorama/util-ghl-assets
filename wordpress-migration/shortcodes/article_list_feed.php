<?php
/**
 * Shortcode: cp_article_list_feed
 * Widget: Article List Feed
 * Auto-generated from WORDPRESS_MIGRATION_MANIFEST.json
 */

function cp_shortcode_article_list_feed( $atts = [], $content = null, $tag = '' ) {
    // Enqueue dependencies
    wp_enqueue_script( 'carolina_panorama_global' );
    wp_enqueue_style( 'shared_article_card_styles' );

    
    $defaults = [
        'category' => '',
        'per_page' => 10,
        'page' => 1,
    ];
    $atts = shortcode_atts( $defaults, $atts, 'cp_article_list_feed' );

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
    <div class="cp-widget-wrapper cp-widget-article_list_feed" <?php echo $data_attrs; ?>>
        <div id="cp-article_list_feed-container">
            <p style="color: #999;">Loading Article List Feed...</p>
        </div>
    </div>
    <script>
        // TODO: Initialize widget with article list
        // Example: fetch from API using window.CarolinaPanorama utilities
        (function() {
            var container = document.getElementById('cp-article_list_feed-container');
            if (!container) return;
            
            // Replace this with actual widget initialization logic
            console.log('Widget article_list_feed initialized');
        })();
    </script>
    <?php
    return ob_get_clean();
}

// Register shortcode
add_shortcode( 'cp_article_list_feed', 'cp_shortcode_article_list_feed' );
