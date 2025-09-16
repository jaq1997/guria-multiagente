"use client"

import React, { useState, useRef, useEffect } from "react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Send, Smile, Paperclip, Mic, MoreVertical, Phone, Video } from "lucide-react"

interface Message {
  id: string
  text: string
  time: string
  sent: boolean
}

// Componente simples para renderizar markdown básico
const SimpleMarkdown = ({ children }: { children: string }) => {
  const renderText = (text: string) => {
    // Converte **texto** para <strong>texto</strong>
    let rendered = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Converte *texto* para <em>texto</em>  
    rendered = rendered.replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Converte quebras de linha
    rendered = rendered.replace(/\n/g, '<br />')
    
    return <div dangerouslySetInnerHTML={{ __html: rendered }} />
  }
  
  return renderText(children)
}

export default function WhatsappInterface() {
  const [message, setMessage] = useState("")
  const [messages, setMessages] = useState<Message[]>([])
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  // Auto scroll para a última mensagem
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages, isLoading])

  const handleSendMessage = async () => {
    if (message.trim() && !isLoading) {
      const userMessage: Message = {
        id: Date.now().toString(),
        text: message,
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        sent: true,
      }
      
      setMessages(prev => [...prev, userMessage])
      const currentMessage = message
      setMessage("")
      setIsLoading(true)

      try {
        const response = await fetch("http://localhost:8000/chat", {
          method: "POST",
          headers: { 
            "Content-Type": "application/json",
            "Accept": "application/json"
          },
          body: JSON.stringify({
            message: currentMessage,
            session_id: sessionId,
          }),
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        
        // Sempre atualiza o session_id se retornado
        if (data.session_id) {
          setSessionId(data.session_id)
        }

        // Cria a mensagem de resposta do bot
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: data.reply || "Desculpe, não recebi uma resposta válida.",
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          sent: false,
        }
        
        setMessages(prev => [...prev, botMessage])
      } catch (error) {
        console.error("Erro ao chamar backend:", error)
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: "Desculpe, não consegui me conectar ao servidor. Verifique se o backend está rodando.",
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          sent: false,
        }
        setMessages(prev => [...prev, errorMessage])
      } finally {
        // Garante que o loading sempre será desativado
        setIsLoading(false)
      }
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handlePaperclipClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    
    if (!file) return

    setIsLoading(true)

    // Se não tiver sessionId, cria uma mensagem primeiro
    if (!sessionId) {
      const initialMessage = "Olá! Vou enviar um arquivo."
      const userMessage: Message = {
        id: Date.now().toString(),
        text: initialMessage,
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        sent: true,
      }
      setMessages(prev => [...prev, userMessage])

      try {
        const response = await fetch("http://localhost:8000/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: initialMessage,
            session_id: sessionId,
          }),
        })
        const data = await response.json()
        setSessionId(data.session_id)
        
        // Adiciona resposta do bot se houver
        if (data.reply) {
          const botMessage: Message = {
            id: (Date.now() + 1).toString(),
            text: data.reply,
            time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
            sent: false,
          }
          setMessages(prev => [...prev, botMessage])
        }
      } catch (error) {
        console.error("Erro ao criar sessão:", error)
        setIsLoading(false)
        return
      }
    }

    // Agora envia o arquivo
    const formData = new FormData()
    formData.append("file", file)
    formData.append("session_id", sessionId || "")

    try {
      const response = await fetch("http://localhost:8000/upload-document", {
        method: "POST",
        body: formData,
      })
      
      const data = await response.json()
      
      const feedbackMessage: Message = {
        id: Date.now().toString(),
        text: data.status === "sucesso"
          ? `Arquivo "${data.filename}" enviado com sucesso!`
          : `Falha no envio do arquivo: ${data.message || "Erro desconhecido"}`,
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        sent: false,
      }
      
      setMessages(prev => [...prev, feedbackMessage])
    } catch (error) {
      console.error("Erro ao enviar arquivo:", error)
      const errorMessage: Message = {
        id: Date.now().toString(),
        text: "Erro ao enviar arquivo. Verifique sua conexão.",
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        sent: false,
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }

    // Limpa o input de arquivo
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  return (
    <div className="flex h-screen flex-col bg-gray-100 dark:bg-gray-900 w-full">
      <div className="flex-1 flex flex-col w-full">
        {/* Chat Header */}
        <div className="px-3 py-2 sm:px-4 sm:py-3 border-b border-gray-200 dark:border-gray-700 bg-green-600 flex items-center gap-2 sm:gap-3">
          <Avatar className="h-8 w-8 sm:h-10 sm:w-10">
            <AvatarImage src="/guria-avatar.png" alt="GurIA" />
            <AvatarFallback className="bg-yellow-400 text-black text-xs sm:text-sm">GA</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <h2 className="font-medium text-white truncate text-sm sm:text-base">GurIA - Assistente Virtual</h2>
            <p className="text-xs sm:text-sm text-green-100">
              {isLoading ? "Digitando..." : "Online"}
            </p>
          </div>
          <div className="flex items-center gap-1 sm:gap-2">
            <Button variant="ghost" size="icon" className="text-white hover:bg-green-700 h-8 w-8 sm:h-10 sm:w-10">
              <Video className="h-4 w-4 sm:h-5 sm:w-5" />
            </Button>
            <Button variant="ghost" size="icon" className="text-white hover:bg-green-700 h-8 w-8 sm:h-10 sm:w-10">
              <Phone className="h-4 w-4 sm:h-5 sm:w-5" />
            </Button>
            <Button variant="ghost" size="icon" className="text-white hover:bg-green-700 h-8 w-8 sm:h-10 sm:w-10">
              <MoreVertical className="h-4 w-4 sm:h-5 sm:w-5" />
            </Button>
          </div>
        </div>

        {/* Messages */}
        <ScrollArea className="flex-1 px-3 py-2 sm:px-4 sm:py-2 bg-gray-50 dark:bg-gray-800" ref={scrollAreaRef}>
          {messages.length === 0 && !isLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-gray-500 dark:text-gray-400">
                <Avatar className="h-12 w-12 sm:h-16 sm:w-16 mx-auto mb-3 sm:mb-4">
                  <AvatarImage src="/guria-avatar.png" alt="GurIA" />
                  <AvatarFallback className="bg-yellow-400 text-black text-sm sm:text-lg">GA</AvatarFallback>
                </Avatar>
                <p className="text-xs sm:text-sm">Olá! Sou a GurIA, sua assistente virtual.</p>
                <p className="text-xs mt-1">Como posso te ajudar hoje?</p>
              </div>
            </div>
          ) : (
            <div className="space-y-2 sm:space-y-3">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex items-end gap-2 ${msg.sent ? "justify-end" : "justify-start"}`}>
                  {!msg.sent && (
                    <Avatar className="h-6 w-6 sm:h-8 sm:w-8 mr-1 sm:mr-2 mt-1 flex-shrink-0">
                      <AvatarImage src="/guria-avatar.png" alt="GurIA" />
                      <AvatarFallback className="bg-yellow-400 text-black text-xs">GA</AvatarFallback>
                    </Avatar>
                  )}
                  <div className={`max-w-[80%] rounded-2xl px-2 py-1 sm:px-3 sm:py-2 ${
                    msg.sent 
                      ? "bg-green-600 text-white rounded-br-md" 
                      : "bg-white dark:bg-gray-700 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-600 rounded-bl-md"
                  }`}>
                    <div className="text-xs sm:text-sm leading-relaxed" style={{ wordWrap: "break-word" }}>
                      <SimpleMarkdown>{msg.text}</SimpleMarkdown>
                    </div>
                    <p className={`text-xs text-right mt-1 ${
                      msg.sent ? "text-green-100" : "text-gray-500 dark:text-gray-400"
                    }`}>
                      {msg.time}
                    </p>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex items-end gap-2 justify-start">
                  <Avatar className="h-6 w-6 sm:h-8 sm:w-8 mr-1 sm:mr-2 mt-1 flex-shrink-0">
                    <AvatarImage src="/guria-avatar.png" alt="GurIA" />
                    <AvatarFallback className="bg-yellow-400 text-black text-xs">GA</AvatarFallback>
                  </Avatar>
                  <div className="bg-white dark:bg-gray-700 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-600 rounded-2xl rounded-bl-md px-2 py-1 sm:px-3 sm:py-2">
                    <div className="text-xs sm:text-sm flex items-center gap-1">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0ms'}}></div>
                        <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
                        <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </ScrollArea>

        {/* Message Input */}
        <div className="p-2 sm:p-3 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-1 sm:gap-2">
            <Button variant="ghost" size="icon" className="text-gray-600 dark:text-gray-400 flex-shrink-0 h-8 w-8 sm:h-10 sm:w-10">
              <Smile className="h-4 w-4 sm:h-5 sm:w-5" />
            </Button>
            <div className="flex-1 relative">
              <Input 
                value={message}  
                onChange={(e) => setMessage(e.target.value)} 
                onKeyDown={handleKeyPress}
                placeholder="Mensagem" 
                className="pr-10 sm:pr-12 bg-gray-100 dark:bg-gray-700 border-0 rounded-full text-xs sm:text-sm h-8 sm:h-10 placeholder:text-[#b3b3b3]"
                disabled={isLoading}
              />
              {message.trim() ? (
                <Button 
                  onClick={handleSendMessage} 
                  size="icon" 
                  className="absolute right-1 top-1/2 transform -translate-y-1/2 h-6 w-6 sm:h-8 sm:w-8 bg-green-600 hover:bg-green-700 rounded-full"
                  disabled={isLoading}
                >
                  <Send className="h-3 w-3 sm:h-4 sm:w-4" />
                </Button>
              ) : (
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="absolute right-1 top-1/2 transform -translate-y-1/2 h-6 w-6 sm:h-8 sm:w-8 text-gray-600 dark:text-gray-400"
                >
                  <Mic className="h-3 w-3 sm:h-4 sm:w-4" />
                </Button>
              )}
            </div>
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileSelect} 
              style={{ display: 'none' }} 
              accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
            />
            <Button 
              onClick={handlePaperclipClick} 
              variant="ghost" 
              size="icon" 
              className="text-gray-600 dark:text-gray-400 flex-shrink-0 h-8 w-8 sm:h-10 sm:w-10"
              disabled={isLoading}
            >
              <Paperclip className="h-4 w-4 sm:h-5 sm:w-5" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}