import { useState } from "react";
import { Link } from "react-router-dom";
import "./Home.css";

export default function Home() {
  const [count, setCount] = useState(0);

  return (
    <main className="home-main">
      <h1>🎓 GDG Babcock Certificate Generator</h1>
      <p className="home-subtitle">
        Generate beautiful certificates for your events and participants
      </p>
      
      <div className="features-grid">
        <div className="feature-card">
          <h3>🏆 Single Certificate</h3>
          <p>Generate a certificate for one participant</p>
          <Link to="/completion" className="feature-btn">
            Create Certificate
          </Link>
        </div>
        
        <div className="feature-card featured">
          <h3>📋 Bulk Certificates</h3>
          <p>Generate certificates for multiple participants via CSV upload or manual entry</p>
          <Link to="/bulk-certificate" className="feature-btn">
            Bulk Generate
          </Link>
          <span className="new-badge">NEW!</span>
        </div>
        
        <div className="feature-card">
          <h3>🎯 View Certificates</h3>
          <p>View and manage generated certificates</p>
          <Link to="/participation" className="feature-btn">
            View Certificates
          </Link>
        </div>
      </div>

      <div className="stats-section">
        <h2>📊 Quick Stats</h2>
        <div className="stats-grid">
          <div className="stat-item">
            <span className="stat-number">{count}</span>
            <span className="stat-label">Test Counter</span>
            <button 
              className="count-btn" 
              onClick={() => setCount((c) => c + 1)}
            >
              Increment
            </button>
          </div>
        </div>
      </div>
      
      <div className="tech-info">
        <p>
          🛠️ Built with <strong>React + FastAPI</strong> for Hacktoberfest 2025
        </p>
        <p>
          Edit <code>src/pages/Home/Home.jsx</code> and save to test HMR
        </p>
      </div>
    </main>
  );
}
