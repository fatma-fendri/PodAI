export type Source = { title: string; url: string };
export type AskResponse = { answer: string; sources: Source[] };

export async function askQuestion(question: string): Promise<AskResponse> {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: question }),
  });
  if (!res.ok) {
    throw new Error(`API error ${res.status}`);
  }
  return res.json();
}