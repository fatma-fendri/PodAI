"use client"

import { useState } from 'react';

export default function Home() {
  const [input, setInput] = useState(''); 
  const [reponse, setReponse] = useState(''); 

  const handleSubmit = async() => {
    const response = await fetch('http://localhost:8000/echo', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: input }),  
    });
    const data = await response.json();
    setReponse(data.message);
  }
  
  

  return (
  <div className="flex flex-col items-center justify-center min-h-screen">
    <h1 className="text-4xl font-bold">PodAI</h1>
    <p className="text-lg text-gray-600 mt-4">AI assistant for clinical podiatry</p>
    <input
    className="border rounded px-3 py-2 mt-4"
    value={input}
    onChange={(e) => setInput(e.target.value)}
    />
    <button
    className="bg-blue-600 text-white px-4 py-2 rounded mt-2"
    onClick={handleSubmit}
    >
      Send
    </button>
    {reponse && <p className="mt-4">{reponse}</p>}
  </div>
  )
}