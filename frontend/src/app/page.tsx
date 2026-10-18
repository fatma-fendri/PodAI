"use client";

import { useState } from "react";
import { askQuestion, AskResponse } from "@/lib/api";
import SourceList from "@/components/SourceList";
import ReactMarkdown from "react-markdown";
import Disclaimer from "@/components/Disclaimer";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<AskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAsk() {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await askQuestion(question);
      setResult(data);
    } catch {
      setError("The assistant is unavailable right now. Please try again in a moment.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="p-8">
      <input
        className="border p-2 mr-2"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />
      <button
        className="border p-2 disabled:opacity-50"
        onClick={handleAsk}
        disabled={loading || question.trim() === ""}
      >
        {loading ? "Searching..." : "Ask"}
      </button>

      {error && <p className="mt-4 text-red-600">{error}</p>}

      {result && (
        <>
            <div className="mt-4">
                <ReactMarkdown>{result.answer}</ReactMarkdown>
            </div>
            <SourceList sources={result.sources} />
        </>
      )}
    <Disclaimer />
    </main>
  );
}