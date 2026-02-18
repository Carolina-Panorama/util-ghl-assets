<?php
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
