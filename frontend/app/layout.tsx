import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ComplyAU — AI Compliance for Australian Businesses",
  description: "Upload your compliance documents and ask questions. ComplyAU analyses your policies against Australian law and identifies gaps instantly.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} min-h-full flex flex-col bg-white text-[#1A1A2E]`}>
        {children}
      </body>
    </html>
  );
}