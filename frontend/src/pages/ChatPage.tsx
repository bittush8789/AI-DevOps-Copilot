import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Send, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { chatApi, ChatMessage } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'
import ReactMarkdown from 'react-markdown'

export default function ChatPage() {
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const { toast } = useToast()

  const chatMutation = useMutation({
    mutationFn: chatApi.sendMessage,
    onSuccess: (response) => {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.data.response },
      ])
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to send message',
        variant: 'destructive',
      })
    },
  })

  const handleSend = () => {
    if (!message.trim()) return

    const userMessage: ChatMessage = { role: 'user', content: message }
    setMessages((prev) => [...prev, userMessage])

    chatMutation.mutate({
      message,
      context: messages.slice(-4),
      use_rag: true,
    })

    setMessage('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col">
      <Card className="mb-4">
        <CardHeader>
          <CardTitle>AI DevOps Assistant</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Ask questions about your infrastructure, troubleshoot issues, or get help with DevOps tasks.
          </p>
        </CardContent>
      </Card>

      <Card className="flex-1 flex flex-col overflow-hidden">
        <CardContent className="flex-1 overflow-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="flex h-full items-center justify-center">
              <div className="text-center">
                <h3 className="text-lg font-medium mb-2">Start a conversation</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Try asking:
                </p>
                <div className="space-y-2 text-sm text-left max-w-md">
                  <div className="p-3 bg-muted rounded-lg">
                    "Why is my pod crashing?"
                  </div>
                  <div className="p-3 bg-muted rounded-lg">
                    "Generate a Kubernetes deployment for a Node.js app"
                  </div>
                  <div className="p-3 bg-muted rounded-lg">
                    "How do I troubleshoot high memory usage?"
                  </div>
                </div>
              </div>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${
                  msg.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-4 ${
                    msg.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  }`}
                >
                  {msg.role === 'user' ? (
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  ) : (
                    <div className="prose prose-sm dark:prose-invert max-w-none">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          {chatMutation.isPending && (
            <div className="flex justify-start">
              <div className="bg-muted rounded-lg p-4">
                <Loader2 className="h-5 w-5 animate-spin" />
              </div>
            </div>
          )}
        </CardContent>

        <div className="border-t p-4">
          <div className="flex gap-2">
            <Textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question..."
              className="min-h-[60px]"
              disabled={chatMutation.isPending}
            />
            <Button
              onClick={handleSend}
              disabled={!message.trim() || chatMutation.isPending}
              size="icon"
              className="h-[60px] w-[60px]"
            >
              {chatMutation.isPending ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Send className="h-5 w-5" />
              )}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}
