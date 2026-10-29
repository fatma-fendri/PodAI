"use client";

import { useState } from "react";
import { askQuestion, AskResponse } from "@/lib/api";
import SourceList from "@/components/SourceList";
import ReactMarkdown from "react-markdown";
import Disclaimer from "@/components/Disclaimer";

const EXAMPLES = [
  "Pain under my heel with the first steps in the morning",
  "A painful bump at the base of my big toe",
  "Burning pain in the ball of my foot when I walk",
];

function linkCitations(text: string) {
  return text.replace(/\[(\d+)\]/g, "[\\[$1\\]](#source-$1)");
}

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
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <div className="mx-auto max-w-2xl px-4 py-12">
        <header className="mb-8">
          <h1 className="text-3xl font-semibold tracking-tight">PodAI</h1>
          <p className="mt-2 text-slate-600">
            Educational information about foot and ankle conditions, based on
            verified medical sources.
          </p>
        </header>
        <details className="mb-6 rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700">
          <summary className="cursor-pointer font-medium text-slate-800">
            How does it work?
          </summary>
          <p className="mt-2">
            PodAI first searches a knowledge base of foot and ankle
            conditions and, when needed, trusted medical websites (MedlinePlus,
            NHS, NCBI, Mayo Clinic). Every answer cites the sources it used, so
            you can check them yourself.
          </p>
        </details>
        <form
          className="flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            handleAsk();
          }}
        >
          <input
            className="flex-1 rounded-lg border border-slate-300 bg-white px-4 py-3 shadow-sm focus:border-teal-600 focus:outline-none focus:ring-2 focus:ring-teal-600/30"
            placeholder="Describe your symptoms or ask a question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <button
            type="submit"
            className="rounded-lg bg-teal-700 px-5 py-3 font-medium text-white hover:bg-teal-800 disabled:opacity-50"
            disabled={loading || question.trim() === ""}
          >
            {loading ? "Searching..." : "Ask"}
          </button>
        </form>

        {!result && !loading && (
          <div className="mt-4 flex flex-wrap gap-2">
            {EXAMPLES.map((example) => (
              <button
                key={example}
                type="button"
                className="rounded-full border border-slate-300 bg-white px-3 py-1 text-sm text-slate-700 hover:border-teal-600 hover:text-teal-800"
                onClick={() => setQuestion(example)}
              >
                {example}
              </button>
            ))}
          </div>
        )}
        {loading && (
          <div
            role="status"
            className="mt-8 animate-pulse rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <p className="text-slate-600">
              Searching the knowledge base and trusted medical websites. This can
              take up to a minute.
            </p>
            <div className="mt-4 space-y-2">
              <div className="h-3 w-5/6 rounded bg-slate-200" />
              <div className="h-3 w-4/6 rounded bg-slate-200" />
              <div className="h-3 w-3/6 rounded bg-slate-200" />
            </div>
          </div>
        )}
        {error && (
          <div
            role="alert"
            className="mt-6 flex items-center justify-between gap-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-red-700"
          >
            <span>{error}</span>
            <button
              type="button"
              className="shrink-0 rounded-md border border-red-300 bg-white px-3 py-1 text-sm font-medium text-red-700 hover:bg-red-100"
              onClick={handleAsk}
            >
              Try again
            </button>
          </div>
        )}

        {result && (
          <>
            <div className="mt-8 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="leading-relaxed [&_p]:mb-3 [&_ul]:mb-3 [&_ul]:list-disc [&_ul]:pl-5 [&_ol]:mb-3 [&_ol]:list-decimal [&_ol]:pl-5 [&_li]:mb-1 [&_strong]:font-semibold">
                <ReactMarkdown
                  components={{
                    a: ({ href, children }) => (
                      <a href={href} className="font-medium text-teal-700 hover:underline">
                        {children}
                      </a>
                    ),
                  }}
                >
                  {linkCitations(result.answer)}
                </ReactMarkdown>
              </div>
            </div>
            <SourceList sources={result.sources} />
          </>
        )}

        <Disclaimer />
        <footer className="mt-6 text-center text-xs text-slate-500">
          A portfolio project by Fatma Fendri ·{" "}
          <a
            href="https://github.com/fatma-fendri/PodAI"
            target="_blank"
            rel="noopener noreferrer"
            className="underline hover:text-teal-800"
          >
            Source code
          </a>
        </footer>
      </div>
    </main>
  );
}