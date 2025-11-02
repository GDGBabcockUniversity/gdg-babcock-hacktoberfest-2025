import { useState } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import './BulkCertificateForm.css';

const BulkCertificateForm = () => {
  const [form, setForm] = useState({
    event_name: '',
    date_issued: '',
    certificate_type: 'participation',
  });
  const [csvFile, setCsvFile] = useState(null);
  const [manualParticipants, setManualParticipants] = useState([
    { participant_name: '', email: '' }
  ]);
  const [mode, setMode] = useState('csv'); // 'csv' or 'manual'
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const API_BASE_URL = 'https://gdg-wrapped-backend-hacktoberfest.vercel.app';

  const handleFormChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'text/csv') {
      setCsvFile(file);
    } else {
      toast.error('Please select a valid CSV file');
      e.target.value = '';
    }
  };

  const handleParticipantChange = (index, field, value) => {
    const updated = [...manualParticipants];
    updated[index][field] = value;
    setManualParticipants(updated);
  };

  const addParticipant = () => {
    setManualParticipants([...manualParticipants, { participant_name: '', email: '' }]);
  };

  const removeParticipant = (index) => {
    if (manualParticipants.length > 1) {
      const updated = manualParticipants.filter((_, i) => i !== index);
      setManualParticipants(updated);
    }
  };

  const handleCSVSubmit = async (e) => {
    e.preventDefault();
    if (!csvFile || !form.event_name || !form.date_issued) {
      toast.error('Please fill all required fields and select a CSV file');
      return;
    }

    setLoading(true);
    const toastId = toast.loading('Processing CSV and generating certificates...');

    try {
      const formData = new FormData();
      formData.append('csv_file', csvFile);
      formData.append('event_name', form.event_name);
      formData.append('date_issued', form.date_issued);
      formData.append('certificate_type', form.certificate_type);

      const response = await axios.post(
        `${API_BASE_URL}/certificates/bulk/csv`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setResult(response.data);
      toast.success(
        `Successfully generated ${response.data.success_count} certificates!`,
        { id: toastId }
      );

      // Reset form
      setForm({ event_name: '', date_issued: '', certificate_type: 'participation' });
      setCsvFile(null);
      document.querySelector('input[type="file"]').value = '';

    } catch (error) {
      console.error('Error:', error);
      toast.error(
        error.response?.data?.detail || 'Failed to generate certificates',
        { id: toastId }
      );
    } finally {
      setLoading(false);
    }
  };

  const handleManualSubmit = async (e) => {
    e.preventDefault();
    
    const validParticipants = manualParticipants.filter(p => p.participant_name.trim());
    if (!form.event_name || !form.date_issued || validParticipants.length === 0) {
      toast.error('Please fill all required fields and add at least one participant');
      return;
    }

    setLoading(true);
    const toastId = toast.loading('Generating certificates...');

    try {
      const response = await axios.post(`${API_BASE_URL}/certificates/bulk`, {
        event_name: form.event_name,
        date_issued: form.date_issued,
        participants: validParticipants,
        certificate_type: form.certificate_type
      });

      setResult(response.data);
      toast.success(
        `Successfully generated ${response.data.success_count} certificates!`,
        { id: toastId }
      );

      // Reset form
      setForm({ event_name: '', date_issued: '', certificate_type: 'participation' });
      setManualParticipants([{ participant_name: '', email: '' }]);

    } catch (error) {
      console.error('Error:', error);
      toast.error(
        error.response?.data?.detail || 'Failed to generate certificates',
        { id: toastId }
      );
    } finally {
      setLoading(false);
    }
  };

  const downloadBulkCertificates = () => {
    if (result?.download_url) {
      const link = document.createElement('a');
      link.href = `${API_BASE_URL}${result.download_url}`;
      link.download = 'certificates.zip';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="bulk-certificate-container">
      <div className="bulk-certificate-form">
        <h2>🎓 Bulk Certificate Generator</h2>
        <p>Generate certificates for multiple participants at once</p>

        {/* Mode Selection */}
        <div className="mode-selection">
          <button
            type="button"
            className={`mode-btn ${mode === 'csv' ? 'active' : ''}`}
            onClick={() => setMode('csv')}
          >
            📄 Upload CSV
          </button>
          <button
            type="button"
            className={`mode-btn ${mode === 'manual' ? 'active' : ''}`}
            onClick={() => setMode('manual')}
          >
            ✍️ Manual Entry
          </button>
        </div>

        {/* Common form fields */}
        <form onSubmit={mode === 'csv' ? handleCSVSubmit : handleManualSubmit}>
          <div className="form-group">
            <label htmlFor="event_name">Event Name *</label>
            <input
              type="text"
              id="event_name"
              name="event_name"
              value={form.event_name}
              onChange={handleFormChange}
              placeholder="e.g., Hacktoberfest 2025"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="date_issued">Date Issued *</label>
            <input
              type="date"
              id="date_issued"
              name="date_issued"
              value={form.date_issued}
              onChange={handleFormChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="certificate_type">Certificate Type *</label>
            <select
              id="certificate_type"
              name="certificate_type"
              value={form.certificate_type}
              onChange={handleFormChange}
              required
            >
              <option value="participation">Certificate of Participation</option>
              <option value="completion">Certificate of Completion</option>
            </select>
          </div>

          {/* CSV Upload Mode */}
          {mode === 'csv' && (
            <div className="csv-upload-section">
              <div className="form-group">
                <label htmlFor="csv_file">Upload CSV File *</label>
                <input
                  type="file"
                  id="csv_file"
                  accept=".csv"
                  onChange={handleFileChange}
                  required
                />
                <small className="file-hint">
                  CSV should have columns: <code>participant_name</code>, <code>email</code> (optional)
                </small>
              </div>
              
              <div className="csv-example">
                <h4>📋 CSV Format Example:</h4>
                <pre>
{`participant_name,email
John Doe,john@example.com
Jane Smith,jane@example.com
Mike Johnson,mike@example.com`}
                </pre>
              </div>
            </div>
          )}

          {/* Manual Entry Mode */}
          {mode === 'manual' && (
            <div className="manual-entry-section">
              <h4>👥 Participants</h4>
              {manualParticipants.map((participant, index) => (
                <div key={index} className="participant-row">
                  <input
                    type="text"
                    placeholder="Participant Name *"
                    value={participant.participant_name}
                    onChange={(e) => handleParticipantChange(index, 'participant_name', e.target.value)}
                    required
                  />
                  <input
                    type="email"
                    placeholder="Email (optional)"
                    value={participant.email}
                    onChange={(e) => handleParticipantChange(index, 'email', e.target.value)}
                  />
                  {manualParticipants.length > 1 && (
                    <button
                      type="button"
                      className="remove-btn"
                      onClick={() => removeParticipant(index)}
                    >
                      ❌
                    </button>
                  )}
                </div>
              ))}
              <button
                type="button"
                className="add-participant-btn"
                onClick={addParticipant}
              >
                ➕ Add Participant
              </button>
            </div>
          )}

          <button
            type="submit"
            className="generate-btn"
            disabled={loading}
          >
            {loading ? '⏳ Generating...' : '🎓 Generate Certificates'}
          </button>
        </form>

        {/* Results Section */}
        {result && (
          <div className="results-section">
            <h3>📊 Generation Results</h3>
            <div className="result-stats">
              <div className="stat success">
                <span className="stat-number">{result.success_count}</span>
                <span className="stat-label">Successful</span>
              </div>
              <div className="stat failed">
                <span className="stat-number">{result.failed_count}</span>
                <span className="stat-label">Failed</span>
              </div>
              <div className="stat total">
                <span className="stat-number">{result.total_count}</span>
                <span className="stat-label">Total</span>
              </div>
            </div>

            {result.download_url && (
              <button
                className="download-btn"
                onClick={downloadBulkCertificates}
              >
                📥 Download All Certificates (ZIP)
              </button>
            )}

            {result.failed_count > 0 && (
              <div className="failed-list">
                <h4>❌ Failed Certificates:</h4>
                <ul>
                  {result.failed_certificates.map((failed, index) => (
                    <li key={index}>
                      <strong>{failed.participant_name}</strong>: {failed.error}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default BulkCertificateForm;
