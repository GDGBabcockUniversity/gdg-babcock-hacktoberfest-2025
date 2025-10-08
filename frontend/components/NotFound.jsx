import { Link } from 'react-router-dom';

// Simple 404 Page Component
const NotFound = () => (
  <div style={{
    minHeight: '60vh', // take most of the screen
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    textAlign: 'center',
    padding: '2rem' // some breathing space
  }}>
    {/* Main error code */}
    <h1 style={{ fontSize: '4rem', marginBottom: '1rem' }}>404</h1>
    
    {/* Secondary message */}
    <h2 style={{ marginBottom: '1rem' }}>Page Not Found</h2>
    
    {/* Small info text */}
    <p style={{ marginBottom: '1.5rem' }}>

      The page you're looking for doesn't exist or has been moved.
    
    </p>
    
    {/* Button to go back home */}
    <Link to="/" style={{
      textDecoration: 'none', // remove underline
      padding: '0.5rem 1rem',
      backgroundColor: '#4f46e5',
      color: '#fff',
      borderRadius: '8px' // small rounded corners
    }}>
      Go back Home
    </Link>
  </div>
);

export default NotFound;
