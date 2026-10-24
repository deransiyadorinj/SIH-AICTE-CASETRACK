import { Inbox } from 'lucide-react';

export default function EmptyState({ title = 'No data found', message = 'There are no records to display.' }) {
  return (
    <div className="empty-state">
      <Inbox size={48} strokeWidth={1} />
      <h3>{title}</h3>
      <p>{message}</p>
    </div>
  );
}
