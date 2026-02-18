<?php
/**
 * Shortcode: cp_article_search
 * Widget: Article Search
 * Auto-generated from WORDPRESS_MIGRATION_MANIFEST.json
 */

function cp_shortcode_article_search( $atts = [], $content = null, $tag = '' ) {
    // Enqueue dependencies
    wp_enqueue_script( 'instantsearch' );
    wp_enqueue_style( 'instantsearch' );

    
    // Return the widget HTML
    ob_start();
    ?>
    <div class="cp-widget-wrapper cp-widget-article_search">
        <div id="cp-article_search-container">
            <p style="color: #999;">Loading Article Search...</p>
        </div>
    </div>
    <script>
        // TODO: Initialize widget with article search
        // Example: fetch from API using window.CarolinaPanorama utilities
        (function() {
            var container = document.getElementById('cp-article_search-container');
            if (!container) return;
            
            // Replace this with actual widget initialization logic
            console.log('Widget article_search initialized');
        })();
    </script>
    <?php
    return ob_get_clean();
}

// Register shortcode
add_shortcode( 'cp_article_search', 'cp_shortcode_article_search' );
