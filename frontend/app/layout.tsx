import type { ReactNode } from "react";

export const metadata = { title: "AI Content Factory - Rượu Thời Đại" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="vi">
      <body style={{ fontFamily: "sans-serif", maxWidth: 800, margin: "2rem auto", padding: "0 1rem" }}>
        {children}
      </body>
    </html>
  );
}
