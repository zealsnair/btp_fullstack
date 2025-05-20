// src/App.jsx
import React from 'react';
import UploadForm from './UploadForm';
import AskQuestion from './AskQuestion';

function App() {
  return (
    <div>
      <h1>Chat with Your PDF 🤖📄</h1>
      <UploadForm />
      <AskQuestion />
    </div>
  );
}

export default App;
