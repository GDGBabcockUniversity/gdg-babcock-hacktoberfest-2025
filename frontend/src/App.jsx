import { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './App.css';
import Navbar from './components/Navbar/Navbar.jsx';
import Footer from './components/Footer/Footer.jsx';
import NotFound from "./pages/NotFound/NotFound.jsx";
import CertificateForm from './pages/CertificateForm.jsx';

function Home() {
  const [count, setCount] = useState(0);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />
      <main style={{ flex: 1, textAlign: 'center' }}>
        <h1>HacktoberFest Demo by Favour!</h1>
        <div className="card">
          <button onClick={() => setCount((c) => c + 1)}>
            count is {count}
          </button>
          <p>
            Edit <code>src/App.jsx</code> and save to test HMR
          </p>
        </div>
      </main>
      <Footer />
    </div>
  );
}


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/certificate" element={<CertificateForm />} />
        <Route path="*" element={<NotFound   />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;