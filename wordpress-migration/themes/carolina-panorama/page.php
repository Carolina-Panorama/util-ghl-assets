<?php
/**
 * The template for displaying pages
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

get_header();
?>

<div class="page-wrapper">
    <?php
    while ( have_posts() ) {
        the_post();
        ?>
        <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
            <div class="entry-content">
                <?php
                the_content();
                wp_link_pages( [
                    'before' => '<div class="page-links">' . esc_html__( 'Pages:', 'carolina-panorama' ),
                    'after'  => '</div>',
                ] );
                ?>
            </div><!-- .entry-content -->
        </article><!-- #post-<?php the_ID(); ?> -->
        <?php
    }
    ?>
</div><!-- .page-wrapper -->

<?php get_footer(); ?>
