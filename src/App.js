import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

const App = () => {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [videoPreview, setVideoPreview] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);

    if (selectedFile) {
      const fileReader = new FileReader();
      fileReader.onload = () => {
        setVideoPreview(fileReader.result);
      };
      fileReader.readAsDataURL(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (file) {
      setLoading(true);

      const formData = new FormData();
      formData.append('video', file);

      try {
        const response = await fetch('http://localhost:8000/upload_video/', {
          method: 'POST',
          body: formData,
        });
        const data = await response.json();
        setResult(data.message || 'No response from server');
      } catch (error) {
        setResult('Error uploading file');
      } finally {
        setLoading(false);
      }
    } else {
      setResult('Please select a file');
    }
  };

  return (
    <div className="container mt-5">
      <h1>Deepfake Detection</h1>
      <div className="mb-3">
        <input type="file" onChange={handleFileChange} />
      </div>
      {videoPreview && (
        <div className="mb-3">
          <video width="320" height="240" controls>
            <source src={videoPreview} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        </div>
      )}
      <div className="mb-3">
        <button className="btn btn-primary" onClick={handleUpload}>
          Upload Video
        </button>
      </div>
      {loading ? (
        <div className="d-flex align-items-center">
          <strong>Loading...</strong>
          <div className="spinner-border ms-auto" role="status" aria-hidden="true"></div>
        </div>
      ) : (
        <div className="mt-3">
          {result && <p>Result: {result}</p>}
        </div>
      )}
    </div>
  );
};

export default App;
