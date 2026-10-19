import { Source } from "@/lib/api";

export default function SourceList({ sources }: { sources: Source[] }) {
  if (sources.length === 0) return null;

  return (
    <div className="mt-4">
      <h2 className="font-semibold">Sources</h2>
      <ol className="list-decimal pl-6">
        {sources.map((s) => (
          <li key={s.url}>
            <a href={s.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">
              {s.title}
            </a>
            <span className="ml-2 text-sm text-gray-500">({s.origin})</span>
          </li>
        ))}
      </ol>
    </div>
  );
}