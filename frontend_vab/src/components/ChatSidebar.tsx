import { useState } from 'react'

interface ChatPreview {
  id: string
  name: string
  lastMessage: string
  timestamp: Date
  unread: number
}

interface ChatSidebarProps {
  isCollapsed: boolean
  onToggle: () => void
  activeChat: string
  onChatSelect: (chatId: string) => void
}

function ChatSidebar({ isCollapsed, onToggle, activeChat, onChatSelect }: ChatSidebarProps) {
  const [chats] = useState<ChatPreview[]>([
    {
      id: '1',
      name: 'General Support',
      lastMessage: 'How can I help you today?',
      timestamp: new Date(),
      unread: 0,
    },
    {
      id: '2',
      name: 'Technical Support',
      lastMessage: 'Have you tried clearing your cache?',
      timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000),
      unread: 2,
    },
  ])

  return (
    <div 
      className={`border-r border-gray-200 h-screen bg-white transition-all duration-300 flex flex-col
        ${isCollapsed ? 'w-16' : 'w-80'}`}
    >
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        {!isCollapsed && <h2 className="text-xl font-semibold">Chats</h2>}
        <button
          onClick={onToggle}
          className="p-2 hover:bg-gray-100 rounded-full"
        >
          {isCollapsed ? '→' : '←'}
        </button>
      </div>
      <div className="divide-y divide-gray-200 flex-1 overflow-y-auto">
        {chats.map((chat) => (
          <div
            key={chat.id}
            onClick={() => onChatSelect(chat.id)}
            className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors duration-150
              ${activeChat === chat.id ? 'bg-primary-50' : ''}`}
          >
            {isCollapsed ? (
              <div className="flex justify-center">
                <span className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                  {chat.name[0]}
                </span>
              </div>
            ) : (
              <>
                <div className="flex justify-between items-start">
                  <h3 className="font-medium">{chat.name}</h3>
                  <span className="text-xs text-gray-500">
                    {chat.timestamp.toLocaleDateString()}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mt-1 truncate">{chat.lastMessage}</p>
                {chat.unread > 0 && (
                  <span className="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-primary-600 rounded-full mt-2">
                    {chat.unread}
                  </span>
                )}
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default ChatSidebar 