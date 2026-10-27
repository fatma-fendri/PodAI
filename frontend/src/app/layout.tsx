import "./globals.css";

export const metadata = {
  title: "PodAI",
    description:
    "Educational information about foot and ankle conditions, based on verified medical sources.",
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