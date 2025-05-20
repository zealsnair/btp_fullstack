// src/AskQuestion.jsx
import React, { useState } from 'react';

function AskQuestion() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const handleAsk = async () => {
    const formData = new FormData();
    formData.append("question", question);

    const res = await fetch("http://localhost:8000/ask/", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    setAnswer(data.answer);
  };

  return (
    <>
      <input
        type="text"
        value={question}
        onChange={e => setQuestion(e.target.value)}
        placeholder="Ask a question"
      />
      <button onClick={handleAsk}>Ask</button>
      <p>{answer}</p>
    </>
  );
}

export default AskQuestion;
