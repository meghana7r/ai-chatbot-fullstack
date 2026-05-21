type AvatarProps = {
  role: 'user' | 'bot';
};

export default function Avatar({ role }: AvatarProps) {
  return (
    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0
      ${role === 'user' ? 'bg-indigo-600 text-white' : 'bg-slate-700 text-indigo-300'}`}>
      {role === 'user' ? 'U' : 'AI'}
    </div>
  );
}
