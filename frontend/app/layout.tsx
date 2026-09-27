import "./globals.css";

export const metadata = {
  title: "Personal Finance",
  description: "Local-first personal finance",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

