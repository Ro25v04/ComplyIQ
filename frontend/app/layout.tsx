import type { Metadata } from "next";
import { Public_Sans } from "next/font/google";
import "./globals.css";

const publicSans = Public_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-public-sans",
});

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
      <body className={`${publicSans.variable} ${publicSans.className} min-h-full flex flex-col bg-[#F8F9FF] text-[#0B1C30]`}>
        {children}
      </body>
    </html>
  );
}