import { useState } from 'react'

interface MessageInputProps {
  onSend: (content: string) => void
  disabled: boolean
}

const MAX_LENGTH = 5000

export default function MessageInput({ onSend, disabled }: MessageInputProps) {
  const [content, setContent] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!content.trim() || content.length > MAX_LENGTH || disabled) return
    onSend(content)
    setContent('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const remaining = MAX_LENGTH - content.length
  const isOverLimit = remaining < 0
  const isNearLimit = remaining <= 500

  return (
    <form onSubmit={handleSubmit} className="border-t-2 border-white p-4 bg-black">
      <div className="flex gap-3 items-end">
        <textarea
          value={content}
          onChange={e => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={disabled ? 'Reconectando...' : 'Digite sua mensagem...'}
          disabled={disabled}
          rows={2}
          maxLength={MAX_LENGTH + 100} // Permite overflow visual mas bloqueia no submit
          className="input-42 flex-1 resize-none h-12"
        />
        <button
          type="submit"
          disabled={disabled || !content.trim() || isOverLimit}
          className="btn-42 h-12 px-4 text-sm"
        >
          Enviar
        </button>
      </div>

      {/* Char counter */}
      <div className="flex justify-between mt-2">
        <span className="text-xs text-gray-600">
          Shift+Enter para nova linha
        </span>
        <span
          className={`text-xs font-mono ${
            isOverLimit
              ? 'text-magenta'
              : isNearLimit
              ? 'text-yellow-500'
              : 'text-gray-500'
          }`}
        >
          {remaining}/{MAX_LENGTH}
        </span>
      </div>
    </form>
  )
}
