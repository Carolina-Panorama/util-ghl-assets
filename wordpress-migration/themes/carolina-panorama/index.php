<?php
/**
 * The main template file
 * This is the most generic template file in a WordPress theme
 * and one of the two required files for a theme (the other being style.css).
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

get_header();
?>

<div class="index-wrapper">
    <?php
    if ( have_posts() ) {
        while ( have_posts() ) {
            the_post();
            ?>
            <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
                <header class="entry-header">
                    <?php the_title( '<h1 class="entry-title">', '</h1>' ); ?>
                </header><!-- .entry-header -->

                <div class="entry-content">
                    <?php the_excerpt(); ?>
                </div><!-- .entry-content -->
            </article><!-- #post-<?php the_ID(); ?> -->
            <?php
        }

        // Pagination
        the_posts_pagination( [
            'prev_text' => __( 'Prev', 'carolina-panorama' ),
            'next_text' => __( 'Next', 'carolina-panorama' ),
        ] );
    } else {
        ?>
        <p><?php _e( 'No posts found.', 'carolina-panorama' ); ?></p>
        <?php
    }
    ?>
</div><!-- .index-wrapper -->

<?php get_footer(); ?>
