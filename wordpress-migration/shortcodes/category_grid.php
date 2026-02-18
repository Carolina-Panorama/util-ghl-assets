<?php
/**
 * Shortcode: cp_category_grid
 * Widget: Category Grid
 * Auto-generated from WORDPRESS_MIGRATION_MANIFEST.json
 */

function cp_shortcode_category_grid( $atts = [], $content = null, $tag = '' ) {
    // Enqueue dependencies
    wp_enqueue_script( 'carolina_panorama_global' );

    
    // Return the widget HTML
    ob_start();
    ?>
    <div class="cp-widget-wrapper cp-widget-category_grid">
        <div id="cp-category_grid-container">
            <p style="color: #999;">Loading Category Grid...</p>
        </div>
    </div>
    <script>
        // TODO: Initialize widget with $atts data
        // Example: fetch from API using window.CarolinaPanorama utilities
        (function() {
            var container = document.getElementById('cp-category_grid-container');
            if (!container) return;
            
            // Replace this with actual widget initialization logic
            console.log('Widget category_grid initialized with:', {});
        })();
    </script>
    <?php
    return ob_get_clean();
}

// Register shortcode
add_shortcode( 'cp_category_grid', 'cp_shortcode_category_grid' );
