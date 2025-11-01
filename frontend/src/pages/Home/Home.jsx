import { useState } from "react";
import { Link } from "react-router-dom";
import "./Home.css";

export default function Home() {
  const [count, setCount] = useState(0);

  return (
    <main className="home-main">
      <h1> GDG Babcock Certificate Generator 🎓</h1>
      <p className="home-subtitle"><strong>Generate beautiful certificates for your events and participants</strong></p>
      
      <div className="features-grid">
        <div className="feature-card">
          <h3>🥇 Certificate of Participation</h3>
          <p>Generate participation certificates for event attendees</p>
          <Link to="/participation" className="feature-btn">
            Generate Participation
          </Link>
        </div>
        
        <div className="feature-card">
          <h3>🏆 Certificate of Completion</h3>
          <p>Generate completion certificates for successful participants</p>
          <Link to="/completion" className="feature-btn">
            Generate Completion
          </Link>
        </div>
        
        <div className="feature-card featured">
          <h3>📋 Bulk Certificates</h3>
          <p>Generate multiple certificates (participation or completion) via CSV upload</p>
          <Link to="/bulk-certificate" className="feature-btn">
            Bulk Generate
          </Link>
          <span className="new-badge">NEW!</span>
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
