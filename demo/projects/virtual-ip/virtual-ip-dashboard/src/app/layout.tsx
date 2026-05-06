import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

const plusJakarta = Plus_Jakarta_Sans({
  variable: "--font-plus-jakarta",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: "虚拟IP孵化与运营 | 周报数据平台",
  description: "虚拟IP孵化与运营项目周报数据分析平台 - 虚拟IP矩阵运营",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN" className={plusJakarta.variable}>
      <body className="min-h-full antialiased">
        {children}
      </body>
    </html>
  );
}
