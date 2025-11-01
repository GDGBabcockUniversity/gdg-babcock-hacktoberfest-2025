import "./Footer.css";
import { FaInstagram, FaXTwitter, FaLinkedin } from "react-icons/fa6";

const Footer = () => (
  <footer className="footer">
    <div className="footer-content">
      <span className="footer-text">
        &copy; GDG Babcock — Hacktoberfest 2025
      </span>

      <div className="social-icons">
        <a
          href="https://www.instagram.com/gdgbabcock"
          target="_blank"
          rel="noopener noreferrer"
          className="social-link instagram"
          aria-label="GDG Babcock Instagram"
        >
          <FaInstagram />
        </a>

        <a
          href="https://x.com/GDGBabcock"
          target="_blank"
          rel="noopener noreferrer"
          className="social-link twitter"
          aria-label="GDG Babcock Twitter / X"
        >
          <FaXTwitter />
        </a>

        <a
          href="https://www.linkedin.com/company/gdgbabcock/"
          target="_blank"
          rel="noopener noreferrer"
          className="social-link linkedin"
          aria-label="GDG Babcock LinkedIn"
        >
          <FaLinkedin />
        </a>
      </div>
    </div>
  </footer>
);

export default Footer;
