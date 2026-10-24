import { getStatusColor } from '../utils/helpers';

export default function StatusBadge({ status }) {
  const colors = getStatusColor(status);
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '3px 10px',
        borderRadius: '4px',
        fontSize: '12px',
        fontWeight: 600,
        letterSpacing: '0.02em',
        background: colors.bg,
        color: colors.text,
        border: `1px solid ${colors.border}`,
        whiteSpace: 'nowrap',
      }}
    >
      {status}
    </span>
  );
}
