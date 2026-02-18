<?php
/**
 * Shortcode: cp_nav_search
 * Widget: Nav Search
 * Auto-generated from WORDPRESS_MIGRATION_MANIFEST.json
 */

function cp_shortcode_nav_search( $atts = [], $content = null, $tag = '' ) {
    // Enqueue dependencies
    wp_enqueue_script( 'instantsearch' );
    wp_enqueue_style( 'instantsearch' );

    
    // Return the widget HTML
    ob_start();
    ?>
    <div class="cp-widget-wrapper cp-widget-nav_search">
        <div id="cp-nav_search-container">
            <p style="color: #999;">Loading Nav Search...</p>
        </div>
    </div>
    <script>
        // TODO: Initialize widget with nav search
        // Example: fetch from API using window.CarolinaPanorama utilities
        (function() {
            var container = document.getElementById('cp-nav_search-container');
            if (!container) return;
            
            // Replace this with actual widget initialization logic
            console.log('Widget nav_search initialized');
        })();
    </script>
    <?php
    return ob_get_clean();
}

// Register shortcode
add_shortcode( 'cp_nav_search', 'cp_shortcode_nav_search' );
