import { Source } from "@/lib/api";

export default function SourceList({ sources }: { sources: Source[] }) {
  if (sources.length === 0) return null;

  return (
    <section className="mt-6">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
        Sources
      </h2>
      <ol className="mt-2 space-y-2">
        {sources.map((s, i) => (
          <li
            key={s.url}
            id={`source-${i + 1}`}
            className="flex scroll-mt-6 items-start gap-3 rounded-lg border border-slate-200 bg-white px-4 py-3 target:border-teal-600 target:ring-2 target:ring-teal-600/30"          >
            <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-teal-50 text-sm font-medium text-teal-800">
              {i + 1}
            </span>
            <div className="min-w-0">
              <a
                href={s.url}
                target="_blank"
                rel="noopener noreferrer"
                className="break-words font-medium text-teal-800 hover:underline"
              >
                {s.title}
              </a>
              <span
                className={
                  s.origin === "Knowledge base"
                    ? "mt-1 inline-block rounded-full bg-teal-50 px-2 py-0.5 text-xs font-medium text-teal-800"
                    : "mt-1 inline-block rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600"
                }
              >
                {s.origin === "Knowledge base"
                  ? "Verified knowledge base"
                  : "Trusted website"}
              </span>            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}