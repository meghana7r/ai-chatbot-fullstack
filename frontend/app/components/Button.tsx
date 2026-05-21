type ButtonProps = {
  label: string;
  onClick?: () => void;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
};

export default function Button({ label, onClick, variant = 'primary', disabled = false }: ButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`px-6 py-3 rounded-full font-semibold text-sm transition-all duration-200
        ${variant === 'primary'
          ? 'bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50'
          : 'border border-indigo-600 text-indigo-400 hover:bg-indigo-600 hover:text-white disabled:opacity-50'
        }`}
    >
      {label}
    </button>
  );
}
