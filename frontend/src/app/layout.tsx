import type { Metadata } from "next";
import { ReactQueryClientProvider } from "../components/ReactQueryClientProvider";
import Watermark from "../components/Watermark";

import "./globals.css";

// PROJECT IMPORTS
import ProviderWrapper from "./ProviderWrapper";

export const metadata: Metadata = {
  title: "D3P BEM Reports",
  description: "D3P BEM Reports",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const environmentName = process.env.NEXT_PUBLIC_ENV || "";

  return (
    <ReactQueryClientProvider>

      <html lang="en">
        <body>
          {(environmentName === "STAGING" || environmentName === "LOCAL") && (
            <Watermark environmentName={environmentName} />
          )}
          <ProviderWrapper>{children}</ProviderWrapper>
        </body>
      </html>

    </ReactQueryClientProvider>
  );
}
