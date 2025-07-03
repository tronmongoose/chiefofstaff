'use client';
import { createContext, useContext } from 'react';
import { useAccount, useConnect, useDisconnect } from 'wagmi';
import { coinbaseWallet } from 'wagmi/connectors';

interface WalletContextType {
  address?: string;
  isConnected: boolean;
  isConnecting: boolean;
  connect: () => void;
  disconnect: () => void;
}

const WalletContext = createContext<WalletContextType | undefined>(undefined);

export function WalletProvider({ children }: { children: React.ReactNode }) {
  const { address, isConnected } = useAccount();
  const { connect, isPending } = useConnect();
  const { disconnect } = useDisconnect();

  const handleConnect = () => {
    connect({ connector: coinbaseWallet() });
  };

  return (
    <WalletContext.Provider value={{
      address,
      isConnected,
      isConnecting: isPending,
      connect: handleConnect,
      disconnect,
    }}>
      {children}
    </WalletContext.Provider>
  );
}

export const useWallet = () => {
  const context = useContext(WalletContext);
  if (!context) throw new Error('useWallet must be used within WalletProvider');
  return context;
};