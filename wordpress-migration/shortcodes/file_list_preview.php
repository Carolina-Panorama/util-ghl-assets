<?php
/**
 * Shortcode: cp_file_list_preview
 * Widget: File List Preview
 * Auto-generated from WORDPRESS_MIGRATION_MANIFEST.json
 */

function cp_shortcode_file_list_preview( $atts = [], $content = null, $tag = '' ) {
    // Enqueue dependencies
    wp_enqueue_script( 'carolina_panorama_global' );

    
    // Return the widget HTML
    ob_start();
    ?>
    <div class="cp-widget-wrapper cp-widget-file_list_preview">
        <div id="cp-file_list_preview-container">
            <p style="color: #999;">Loading File List Preview...</p>
        </div>
    </div>
    <script>
        // TODO: Initialize widget with file list
        // Example: fetch from API using window.CarolinaPanorama utilities
        (function() {
            var container = document.getElementById('cp-file_list_preview-container');
            if (!container) return;
            
            // Replace this with actual widget initialization logic
            console.log('Widget file_list_preview initialized');
        })();
    </script>
    <?php
    return ob_get_clean();
}

// Register shortcode
add_shortcode( 'cp_file_list_preview', 'cp_shortcode_file_list_preview' );
