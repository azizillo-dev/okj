import type { Metadata } from "next";
import { Fraunces, Inter } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/components/providers/QueryProvider";
import { ClientLayoutShell } from "@/components/navigation/ClientLayoutShell";

const fraunces = Fraunces({
  variable: "--font-display",
  subsets: ["latin"],
  display: "swap",
});

const inter = Inter({
  variable: "--font-body",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "OKJ — O'zbekiston Kitobxonlari Jamiyati",
  description: "O'zbekistonning eng katta va zamonaviy intellektual kitobxonlik platformasi. Elektron pasport, qidiruv, lenta va gamifikatsiya.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="uz" className={`${fraunces.variable} ${inter.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col bg-okj-bg-deep text-okj-text-primary">
        <QueryProvider>
          <ClientLayoutShell>{children}</ClientLayoutShell>
        </QueryProvider>
      </body>
    </html>
  );
}
