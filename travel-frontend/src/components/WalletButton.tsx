'use client';
import { useWallet } from '@/context/WalletContext';

export default function WalletButton() {
  const { address, isConnected, isConnecting, connect, disconnect } = useWallet();

  if (isConnected && address) {
    return (
      <div className="flex items-center space-x-3">
        <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
          {address.slice(0, 6)}...{address.slice(-4)}
        </div>
        <button
          onClick={disconnect}
          className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
        >
          Disconnect
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={connect}
      disabled={isConnecting}
      className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-semibold"
    >
      {isConnecting ? (
        <div className="flex items-center space-x-2">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          <span>Connecting...</span>
        </div>
      ) : (
        <div className="flex items-center space-x-2">
          <span>🔗</span>
          <span>Connect Wallet</span>
        </div>
      )}
    </button>
  );
}