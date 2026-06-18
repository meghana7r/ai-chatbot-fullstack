// Avatar.tsx — Profile circle for user and bot messages
// Built by Meghana Ravi
// Bot shows "M" with rose/orange gradient, User shows "U" with rose color

type AvatarProps = {
  role: 'user' | 'bot';
};

export default function Avatar({ role }: AvatarProps) {
  return (
    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0
      ${role === 'user'
        ? 'bg-rose-500 text-white'
        : 'bg-gradient-to-br from-rose-500 to-orange-400 text-white shadow-sm'
      }`}>
      {role === 'user' ? 'U' : 'M'}
    </div>
  );
}
