import { useState } from "react";
import axios from "axios";
import "./CertCompletion.css";
import { toast } from "react-hot-toast";

const CertCompletion = () => {
  const [form, setForm] = useState({
    participant_name: "",
    event_name: "",
    certificate_type: "completion",
    date_issued: "",
  });
  const [loading, setLoading] = useState(false);
  const [certificateUrl, setCertificateUrl] = useState(null);
  const [imageLoading, setImageLoading] = useState(false);
  const [imageError, setImageError] = useState(null);

  const API_BASE_URL = "https://gdg-wrapped-backend-hacktoberfest.vercel.app";

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setCertificateUrl(null);
    setImageError(null);
    const toastId = toast.loading("Generating certificate...");

    try {
      const res = await axios.post(`${API_BASE_URL}/certificates/`, {
        participant_name: form.participant_name,
        event_name: form.event_name,
        date_issued: form.date_issued,
        certificate_type: form.certificate_type,
      });

      setForm({
        participant_name: "",
        event_name: "",
        certificate_type: "completion",
        date_issued: "",
      });

      if (res.data.download_url) {
        setImageLoading(true);
        const url = `${API_BASE_URL}${res.data.download_url}`;
        try {
          await axios.get(url);
          setCertificateUrl(url);
        } catch (imgErr) {
          setImageError("Could not load certificate image.");
          toast.error("Could not load certificate image.");
        } finally {
          setImageLoading(false);
        }
      }
      toast.success("Certificate generated successfully!", { id: toastId });
    } catch (err) {
      const message =
        err.response?.data?.message ||
        err.message ||
        "An error occurred, please try again.";
      toast.error(message, { id: toastId });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="cert-completion-main">
      <form className="cert-form" onSubmit={handleSubmit}>
        <h2>Certificate Generator</h2>
        <label>
          Name
          <input
            type="text"
            name="participant_name"
            value={form.participant_name}
            onChange={handleChange}
            required
            minLength={2}
            maxLength={100}
            placeholder="Enter full name"
          />
        </label>
        <label>
          Event
          <input
            type="text"
            name="event_name"
            value={form.event_name}
            onChange={handleChange}
            required
            minLength={3}
            maxLength={200}
            placeholder="Event name"
          />
        </label>
        <label>
          Certificate Type
          <select
            name="certificate_type"
            value={form.certificate_type}
            onChange={handleChange}
            required>
            <option value="participation">Certificate of Participation</option>
            <option value="completion">Certificate of Completion</option>
          </select>
        </label>
        <label>
          Date
          <input
            type="date"
            name="date_issued"
            value={form.date_issued}
            onChange={handleChange}
            required
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "Generating..." : "Generate"}
        </button>
      </form>

      {certificateUrl && (
        <div className="cert-preview-container">
          <h3>Certificate Preview</h3>
          {imageLoading ? (
            <p>Loading certificate...</p>
          ) : (
            <img src={certificateUrl} alt="Certificate Preview" />
          )}
          <div>
            <a href={certificateUrl} download>
              <button type="button">Download Certificate</button>
            </a>
          </div>
        </div>
      )}
      {imageError && <p className="cert-error">{imageError}</p>}
    </main>
  );
};

export default CertCompletion;
