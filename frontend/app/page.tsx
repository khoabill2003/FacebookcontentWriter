"use client";

import { FormEvent, useState } from "react";

type Post = {
  title: string; body: string; slogan: string; cta: string;
  contact: string; warning: string; hashtags: string[]; caption: string;
};
type Result = {
  product: Record<string, string | null>;
  validation_issues: Record<string, string[]>;
  posts: Post[]; markdown: string; html: string;
};

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function download(name: string, text: string, type: string) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([text], { type }));
  a.download = name;
  a.click();
  URL.revokeObjectURL(a.href);
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [num, setNum] = useState(3);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<Result | null>(null);

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!file) return;
    setLoading(true); setError(""); setResult(null);
    const form = new FormData();
    form.append("image", file);
    form.append("num_posts", String(num));
    try {
      const res = await fetch(`${API}/api/content/generate`, { method: "POST", body: form });
      if (!res.ok) throw new Error((await res.json()).detail ?? res.statusText);
      setResult(await res.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>AI Content Factory – Rượu Thời Đại</h1>
      <form onSubmit={submit}>
        <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />{" "}
        <label>
          Số bài:{" "}
          <select value={num} onChange={(e) => setNum(Number(e.target.value))}>
            {[3, 4, 5].map((n) => <option key={n}>{n}</option>)}
          </select>
        </label>{" "}
        <button disabled={!file || loading}>{loading ? "Đang tạo..." : "Tạo nội dung"}</button>
      </form>
      {error && <p style={{ color: "crimson" }}>Lỗi: {error}</p>}
      {result && (
        <section>
          <h2>Sản phẩm</h2>
          <pre>{JSON.stringify(result.product, null, 2)}</pre>
          {Object.keys(result.validation_issues).length > 0 && (
            <p style={{ color: "darkorange" }}>
              Còn lỗi validate: {JSON.stringify(result.validation_issues)}
            </p>
          )}
          <button onClick={() => download("posts.md", result.markdown, "text/markdown")}>Tải Markdown</button>{" "}
          <button onClick={() => download("posts.html", result.html, "text/html")}>Tải HTML</button>
          {result.posts.map((p, i) => (
            <article key={i} style={{ border: "1px solid #ccc", padding: 12, margin: "1rem 0" }}>
              <h3>{p.title}</h3>
              <pre style={{ whiteSpace: "pre-wrap" }}>{p.caption}</pre>
              <button onClick={() => navigator.clipboard.writeText(p.caption)}>Copy</button>
            </article>
          ))}
        </section>
      )}
    </main>
  );
}
