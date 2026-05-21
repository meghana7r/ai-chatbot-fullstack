import ChatBubble from './ChatBubble';

type Message = {
  id: string;
  role: 'user' | 'bot';
  message: string;
  timestamp: string;
};

type MessageListProps = {
  messages: Message[];
};

export default function MessageList({ messages }: MessageListProps) {
  return (
    <div className="flex flex-col px-4 py-4">
      {messages.map((msg) => (
        <ChatBubble
          key={msg.id}
          role={msg.role}
          message={msg.message}
          timestamp={msg.timestamp}
        />
      ))}
    </div>
  );
}
