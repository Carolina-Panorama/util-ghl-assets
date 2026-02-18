<?php
/**
 * Shortcode: cp_search
 * Widget: Search Widget
 * Auto-generated from WORDPRESS_MIGRATION_MANIFEST.json
 */

function cp_shortcode_search( $atts = [], $content = null, $tag = '' ) {
    // Enqueue dependencies
    wp_enqueue_script( 'instantsearch' );
    wp_enqueue_style( 'instantsearch' );

    
    // Return the widget HTML
    ob_start();
    ?>
    <div class="cp-widget-wrapper cp-widget-search">
        <div id="cp-search-container">
            <p style="color: #999;">Loading Search Widget...</p>
        </div>
    </div>
    <script>
        // TODO: Initialize widget with $atts data
        // Example: fetch from API using window.CarolinaPanorama utilities
        (function() {
            var container = document.getElementById('cp-search-container');
            if (!container) return;
            
            // Replace this with actual widget initialization logic
            console.log('Widget search initialized with:', {});
        })();
    </script>
    <?php
    return ob_get_clean();
}

// Register shortcode
add_shortcode( 'cp_search', 'cp_shortcode_search' );
