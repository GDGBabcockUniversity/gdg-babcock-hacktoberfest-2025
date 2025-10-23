import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar/Navbar.jsx";
import Footer from "./components/Footer/Footer.jsx";
import NotFound from "./pages/NotFound/NotFound.jsx";
import CertCompletion from "./pages/CertificationForm/CertCompletion.jsx";
import CertParticipation from "./pages/CertParticipation/CertParticipation.jsx";
import BulkCertificateForm from "./pages/BulkCertificateForm/BulkCertificateForm.jsx";
import Home from "./pages/Home/Home.jsx";
import { Toaster } from "react-hot-toast";

function App() {
  return (
    <Router>
      <Navbar />
      <Toaster
        position="top-center"
        gutter={16}
        toastOptions={{
          duration: 5000,
          success: { duration: 5000 },
          error: { duration: 6000 },
          loading: { duration: Infinity },
        }}
      />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/completion" element={<CertCompletion />} />
        <Route path="/bulk-certificate" element={<BulkCertificateForm />} />
        <Route path="/participation" element={<CertParticipation />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
      <Footer />
    </Router>
  );
}

export default App;
