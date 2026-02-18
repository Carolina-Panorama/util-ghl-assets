<?php
/**
 * Register Gutenberg Blocks for Carolina Panorama Widgets
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Register block category for CP widgets
 */
function cp_register_block_category( $categories ) {
    return array_merge(
        $categories,
        [
            [
                'slug'  => 'cp-widgets',
                'title' => __( 'Carolina Panorama', 'carolina-panorama' ),
                'icon'  => 'newspaper',
            ],
        ]
    );
}
add_filter( 'block_categories_all', 'cp_register_block_category', 10, 2 );

/**
 * Register all CP blocks
 */
function cp_register_blocks() {
    $blocks = [
        [
            'name'        => 'cp/article-detail',
            'title'       => 'Article Detail',
            'description' => 'Display a single article with full content',
            'icon'        => 'text',
        ],
        [
            'name'        => 'cp/article-feed',
            'title'       => 'Article Feed',
            'description' => 'Display a paginated list of articles',
            'icon'        => 'list-view',
        ],
        [
            'name'        => 'cp/headlines-grid',
            'title'       => 'Headlines Grid',
            'description' => 'Display featured articles in a grid layout',
            'icon'        => 'grid',
        ],
        [
            'name'        => 'cp/category-grid',
            'title'       => 'Category Grid',
            'description' => 'Display all categories as navigation',
            'icon'        => 'grid',
        ],
        [
            'name'        => 'cp/search',
            'title'       => 'Search Widget',
            'description' => 'Full-text search with Algolia',
            'icon'        => 'search',
        ],
        [
            'name'        => 'cp/trending-carousel',
            'title'       => 'Trending Carousel',
            'description' => 'Display trending articles in a carousel',
            'icon'        => 'slides',
        ],
        [
            'name'        => 'cp/article-list-feed',
            'title'       => 'Article List Feed',
            'description' => 'Display articles in a vertical list',
            'icon'        => 'list-view',
        ],
        [
            'name'        => 'cp/file-list-preview',
            'title'       => 'File List Preview',
            'description' => 'Display a collapsible file list',
            'icon'        => 'media-document',
        ],
    ];

    foreach ( $blocks as $block ) {
        register_block_type(
            $block['name'],
            [
                'title'             => $block['title'],
                'description'       => $block['description'],
                'category'          => 'cp-widgets',
                'icon'              => $block['icon'],
                'render_callback'   => function() use ( $block ) {
                    return cp_render_block( $block['name'] );
                },
            ]
        );
    }
}
add_action( 'init', 'cp_register_blocks' );

/**
 * Render a block using its corresponding shortcode
 */
function cp_render_block( $block_name ) {
    // Map block names to shortcode names
    $shortcode_map = [
        'cp/article-detail'      => 'cp_article_detail',
        'cp/article-feed'        => 'cp_article_feed',
        'cp/headlines-grid'      => 'cp_headlines_grid',
        'cp/category-grid'       => 'cp_category_grid',
        'cp/search'              => 'cp_search',
        'cp/trending-carousel'   => 'cp_trending_carousel',
        'cp/article-list-feed'   => 'cp_article_list_feed',
        'cp/file-list-preview'   => 'cp_file_list_preview',
    ];

    if ( ! isset( $shortcode_map[ $block_name ] ) ) {
        return '<p>Unknown widget: ' . esc_html( $block_name ) . '</p>';
    }

    $shortcode = $shortcode_map[ $block_name ];
    return do_shortcode( '[' . $shortcode . ']' );
}

