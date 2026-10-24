import { Loader2 } from 'lucide-react';

export default function LoadingSpinner({ message = 'Loading…' }) {
  return (
    <div className="loading-state">
      <Loader2 size={32} className="spin-icon" />
      <p>{message}</p>
    </div>
  );
}
