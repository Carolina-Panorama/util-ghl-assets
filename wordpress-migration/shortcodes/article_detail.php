<?php
/**
 * Shortcode: cp_article_detail
 * Widget: Article Detail
 * Auto-generated from WORDPRESS_MIGRATION_MANIFEST.json
 */

function cp_shortcode_article_detail( $atts = [], $content = null, $tag = '' ) {
    // Enqueue dependencies
    wp_enqueue_script( 'carolina_panorama_global' );
    wp_enqueue_style( 'article_detail_styles (inline in HTML)' );

    
    // Shortcode attributes with defaults
    $defaults = [
        'article_id' => '',
    ];
    $atts = shortcode_atts( $defaults, $atts, 'cp_article_detail' );

    // Pass attributes to JavaScript via data attributes
    $data_attrs = '';
    if ( ! empty( $atts['article_id'] ) ) {
        $data_attrs .= ' data-article_id="' . esc_attr( $atts['article_id'] ) . '"';
    }

    // Return the widget HTML
    ob_start();
    ?>
    <div class="cp-widget-wrapper cp-widget-article_detail" <?php echo $data_attrs; ?>>
        <div id="cp-article_detail-container">
            <p style="color: #999;">Loading Article Detail...</p>
        </div>
    </div>
    <script>
        // TODO: Initialize widget with $atts data
        // Example: fetch from API using window.CarolinaPanorama utilities
        (function() {
            var container = document.getElementById('cp-article_detail-container');
            if (!container) return;
            
            // Replace this with actual widget initialization logic
            console.log('Widget article_detail initialized with:', {});
        })();
    </script>
    <?php
    return ob_get_clean();
}

// Register shortcode
add_shortcode( 'cp_article_detail', 'cp_shortcode_article_detail' );
