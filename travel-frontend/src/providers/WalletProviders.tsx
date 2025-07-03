'use client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { WagmiProvider } from 'wagmi';
import { coinbaseWallet } from 'wagmi/connectors';
import { createConfig, http } from 'wagmi';
import { base, baseSepolia } from 'wagmi/chains';

const config = createConfig({
  chains: [base, baseSepolia],
  connectors: [
    coinbaseWallet({
      appName: 'x402 Travel Planner',
      appLogoUrl: 'https://your-app-logo.png',
    }),
  ],
  transports: {
    [base.id]: http(),
    [baseSepolia.id]: http(),
  },
});

const queryClient = new QueryClient();

export function WalletProviders({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <WagmiProvider config={config}>
        {children}
      </WagmiProvider>
    </QueryClientProvider>
  );
}