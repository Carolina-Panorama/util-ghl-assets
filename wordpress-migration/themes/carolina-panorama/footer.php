<?php
/**
 * The footer for Carolina Panorama theme
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}
?>

        </main><!-- #content -->

        <footer id="colophon" class="site-footer">

            <!-- ===== Row 1: CTA / Advertising ===== -->
            <div class="footer-cta">
                <div class="footer-inner">
                    <h2 class="footer-cta-heading">Want to work with us?</h2>
                    <p class="footer-cta-text">Looking to reach a passionate and engaged audience? Partner with us to share your brand&rsquo;s story where it matters most. We offer a range of advertising options to fit your goals and budget.</p>
                    <p class="footer-cta-text">Get in touch through our advertising inquiry form to learn more:</p>
                    <a href="<?php echo esc_url( home_url( '/contact' ) ); ?>" class="footer-cta-btn">CONTACT US</a>
                </div>
                <div class="footer-inner"><hr class="footer-divider"></div>
            </div>

            <!-- ===== Row 2: 4-column links ===== -->
            <div class="footer-links">
                <div class="footer-inner footer-grid">

                    <div class="footer-col">
                        <h3 class="footer-col-heading">COMPANY</h3>
                        <ul>
                            <li><a href="<?php echo esc_url( home_url( '/about' ) ); ?>">About Us</a></li>
                            <li><a href="<?php echo esc_url( home_url( '/our-team' ) ); ?>">Our Team</a></li>
                            <li><a href="<?php echo esc_url( home_url( '/location' ) ); ?>">Our Location</a></li>
                            <li><a href="<?php echo esc_url( home_url( '/careers' ) ); ?>">Careers</a></li>
                        </ul>
                    </div>

                    <div class="footer-col">
                        <h3 class="footer-col-heading">CUSTOMER CARE</h3>
                        <ul>
                            <li><a href="<?php echo esc_url( home_url( '/contact' ) ); ?>">Contact Us</a></li>
                            <li><a href="<?php echo esc_url( home_url( '/support' ) ); ?>">Support</a></li>
                        </ul>
                    </div>

                    <div class="footer-col">
                        <h3 class="footer-col-heading">LEGAL</h3>
                        <ul>
                            <li><a href="<?php echo esc_url( home_url( '/terms-of-use' ) ); ?>">Terms of Use</a></li>
                            <li><a href="<?php echo esc_url( home_url( '/privacy-policy' ) ); ?>">Privacy Policy</a></li>
                            <li><a href="<?php echo esc_url( home_url( '/warranty' ) ); ?>">Warranty</a></li>
                        </ul>
                    </div>

                    <div class="footer-col">
                        <h3 class="footer-col-heading">FOLLOW US</h3>
                        <div class="footer-social">
                            <a href="https://www.facebook.com/carolinapanoramanewspaper/" class="footer-social-link" aria-label="Facebook" target="_blank" rel="noopener noreferrer">
                                <img src="https://stcdn.leadconnectorhq.com/funnel/icons/square/facebook-square.svg" alt="Facebook" width="36" height="36">
                            </a>
                            <a href="https://www.instagram.com/carolinapanorama/" class="footer-social-link" aria-label="Instagram" target="_blank" rel="noopener noreferrer">
                                <img src="https://stcdn.leadconnectorhq.com/funnel/icons/square/instagram-square.svg" alt="Instagram" width="36" height="36">
                            </a>
                            <a href="https://www.linkedin.com/company/carolina-panorama" class="footer-social-link" aria-label="LinkedIn" target="_blank" rel="noopener noreferrer">
                                <img src="https://stcdn.leadconnectorhq.com/funnel/icons/square/linkedin-square.svg" alt="LinkedIn" width="36" height="36">
                            </a>
                            <a href="https://www.youtube.com/@carolinapanoramanewspaper1760" class="footer-social-link" aria-label="YouTube" target="_blank" rel="noopener noreferrer">
                                <img src="https://stcdn.leadconnectorhq.com/funnel/icons/square/youtube-square.svg" alt="YouTube" width="36" height="36">
                            </a>
                        </div>
                    </div>

                </div>
            </div>

            <!-- ===== Row 3: Copyright ===== -->
            <div class="footer-bottom">
                <div class="footer-inner">
                    <hr class="footer-divider">
                    <p class="footer-copyright">Copyright <?php echo date( 'Y' ); ?> | MBD Media | All Rights Reserved.</p>
                </div>
            </div>

        </footer><!-- #colophon -->
    </div><!-- #page -->

    <?php wp_footer(); ?>
</body>
</html>
