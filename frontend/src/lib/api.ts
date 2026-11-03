export type Source = { title: string; url: string; origin: string  };
export type AskResponse = { answer: string; sources: Source[] };

// An error returned by the backend: keeps the HTTP status and the message it sent
export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export async function askQuestion(question: string): Promise<AskResponse> {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: question }),
  });
  if (!res.ok) {
    let message = "";
    try {
      const body = await res.json();
      if (typeof body.detail === "string") message = body.detail;
    } catch {
      // the response had no JSON body
    }
    throw new ApiError(res.status, message);
  }
  return res.json();
}