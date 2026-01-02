import type { Metadata } from "next";
import "./globals.css";
import { ReactQueryClientProvider } from "@/components/providers";
import { DM_Sans, Crimson_Pro } from "next/font/google"
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { Toaster } from "react-hot-toast";
import { ThemeProvider } from "next-themes";


const dmSans = DM_Sans({
  subsets: ['latin'],
  display: 'swap',
  fallback: ['swap', 'sans-serif'],
  variable: '--font-dm-sans',
  weight: ['100', '200', '300', '400', '500', '600', '700', '800', '900'],
});

const crimsonPro = Crimson_Pro({
  subsets: ['latin'],
  display: 'swap',
  fallback: ['swap', 'erif'],
  variable: '--font-crimson-pro',
  weight: ['200', '300', '400', '500', '600', '700', '800', '900'],
});


export const metadata: Metadata = {
  title: {
    template: "%s | TaskFlow",
    default: "TaskFlow - Your AI-powered productivity companion",
  },
  description: "Your AI-powered productivity companion",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      cz-shortcut-listen="true"
      suppressHydrationWarning
    >
      <body
        className={`${dmSans.variable} ${crimsonPro.variable} antialiased`}
        data-qb-installed="true"
        cz-shortcut-listen="true"
      >
        <script
          src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
          async
        />
        <ReactQueryClientProvider>
          <ThemeProvider>
            <Navbar />
            {children}
            <Toaster
              position="top-right"
              reverseOrder={false}
            />
            <Footer />
          </ThemeProvider>
        </ReactQueryClientProvider>
      </body>
    </html>
  );
}
