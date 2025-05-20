// src/UploadForm.jsx
import React, { useState } from 'react';

function UploadForm() {
  const [file, setFile] = useState(null);
  const [msg, setMsg] = useState('');

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("http://localhost:8000/upload/", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    setMsg(data.message || data.error);
  };

  return (
    <>
      <input type="file" accept="application/pdf" onChange={e => setFile(e.target.files[0])} />
      <button onClick={handleUpload}>Upload</button>
      <p>{msg}</p>
    </>
  );
}

export default UploadForm;
