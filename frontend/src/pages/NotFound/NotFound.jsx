import { Link } from 'react-router-dom';
import "../../App.css";

const NotFound = () => (
  <section className="not-found">
    <h1 className="not-found__heading">Page Not Found</h1>
    <p className="not-found__message">
      We couldn&apos;t find the page you were looking for. Let&apos;s get you back on track.
    </p>
    <Link to="/" className="not-found__link">
      Back to Home
    </Link>
  </section>
);

export default NotFound;
