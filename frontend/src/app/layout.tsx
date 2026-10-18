import "./globals.css";

export const metadata = {
  title: "PodAI",
  description: "Clinical podiatry assistant",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}