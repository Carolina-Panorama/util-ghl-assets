<?php
/**
 * The template for displaying 404 pages
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

get_header();
?>

<div class="error-404">
    <div class="error-wrapper">
        <h1><?php _e( 'Oops! That page can&rsquo;t be found.', 'carolina-panorama' ); ?></h1>
        <p><?php _e( 'The page you are looking for doesn&rsquo;t exist or has been moved.', 'carolina-panorama' ); ?></p>
        <p><a href="<?php echo esc_url( home_url( '/' ) ); ?>" class="button"><?php _e( 'Go Home', 'carolina-panorama' ); ?></a></p>
    </div>
</div>

<?php get_footer(); ?>
