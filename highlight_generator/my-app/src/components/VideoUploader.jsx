import React, { useState } from 'react';
import axios from 'axios';

function VideoUploader() {
  const [videoFile, setVideoFile] = useState(null);
  const [status, setStatus] = useState('');
  const [previewUrl, setPreviewUrl] = useState('');
  const [progress, setProgress] = useState(0);

  const handleFileChange = (e) => {
    setVideoFile(e.target.files[0]);
    setStatus('');
    setPreviewUrl('');
    setProgress(0);
  };

  const steps = [
    '📂 Breaking down your video...',
    '🔊 Listening for excitement...',
    '🎞️ Finding exciting scenes...',
    '✨ Polishing your highlight...',
    '🎬 Wrapping up the final cut...',
  ];

  const simulateProgressSteps = async () => {
    for (let i = 0; i < steps.length; i++) {
      setStatus(steps[i]);
      setProgress(Math.round(((i + 1) / steps.length) * 100));
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
  };

  const handleUpload = async () => {
    if (!videoFile) {
      setStatus('📎 Please choose a video file.');
      return;
    }

    const formData = new FormData();
    formData.append('video', videoFile);

    try {
      setStatus('🚀 Uploading video...');
      setProgress(0);

      const response = await axios.post(
        `${import.meta.env.VITE_BACKEND_URL}/upload`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
          responseType: 'blob',
        }
      );

      await simulateProgressSteps();

      const blob = new Blob([response.data], { type: 'video/mp4' });
      const url = URL.createObjectURL(blob);

      setPreviewUrl(url);
      setStatus('✅ Done! Here is your highlight.');
      setProgress(100);
    } catch (err) {
      console.error(err);
      setStatus('❌ Something went wrong. Please try again.');
      setProgress(0);
    }
  };

  return (
    <div style={{ padding: '1rem', textAlign: 'center' }}>
      <input type="file" accept="video/mp4" onChange={handleFileChange} />
      <br />
      <button onClick={handleUpload} style={{ marginTop: '1rem' }}>
        Upload
      </button>

      {status && <p style={{ marginTop: '1rem' }}>{status}</p>}

      {progress > 0 && (
        <div style={{ marginTop: '0.5rem', width: '100%', maxWidth: 400, margin: 'auto' }}>
          <div style={{
            height: '10px',
            width: '100%',
            backgroundColor: '#eee',
            borderRadius: '5px',
            overflow: 'hidden',
          }}>
            <div style={{
              height: '10px',
              width: `${progress}%`,
              backgroundColor: '#4caf50',
              transition: 'width 0.3s ease-in-out',
            }} />
          </div>
          <small>{progress}%</small>
        </div>
      )}

      {previewUrl && (
        <div style={{ marginTop: '1.5rem' }}>
          <video controls src={previewUrl} style={{ maxWidth: '100%' }} />
          <br />
          <a href={previewUrl} download="highlight.mp4">
            <button style={{ marginTop: '0.75rem' }}>📥 Download Highlight</button>
          </a>
        </div>
      )}
    </div>
  );
}

export default VideoUploader;
