"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Paperclip, Send } from "lucide-react";

interface Message {
  id: number;
  role: "user" | "assistant";
  content: string;
  file?: File | null;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      role: "assistant",
      content: "Hello! How can I help you today? 😊",
    },
  ]);
  const [input, setInput] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  // Auto-scroll on new messages
  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  const sendMessage = () => {
    if (!input.trim() && !file) return;

    const newMessage: Message = {
      id: Date.now(),
      role: "user",
      content: input,
      file: file || null,
    };

    setMessages((prev) => [...prev, newMessage]);
    setInput("");
    setFile(null);

    // In real app, send API request here.

    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "assistant",
          content: "I received your message! 🤖",
        },
      ]);
    }, 800);
  };

  return (
    <div
      className="flex flex-col h-full w-full"
      style={{
        backgroundColor: "var(--background)",
        color: "var(--foreground)",
      }}
    >
      {/* Header */}
      <div className="p-4 border-b border-[var(--border)] text-lg font-semibold">
        Chat Interface
      </div>

      {/* Messages Container */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 space-y-4 max-h-[520px] min-h-[520px] "
      >
        {messages.map((msg) => (
          <ChatMessage key={msg.id} {...msg} />
        ))}
      </div>

      {/* Input Bar (sticky bottom) */}
      <div className="border-t border-[var(--border)] p-4 bg-[var(--card)]/40 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          {/* Hidden file input */}
          <input
            type="file"
            className="hidden"
            ref={fileInputRef}
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />

          {/* File Upload Button */}
          <Button
            variant="outline"
            className="bg-[var(--card)] border-[var(--border)] text-[var(--foreground)]"
            onClick={() => fileInputRef.current?.click()}
          >
            <Paperclip size={16} />
          </Button>

          {/* Input box */}
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Send a message"
            className="
              flex-1 bg-[var(--muted)] 
              border-[var(--border)] 
              text-[var(--foreground)]
              placeholder:text-[var(--muted-foreground)]
            "
          />

          {/* Send button */}
          <Button
            onClick={sendMessage}
            className="
              bg-[var(--primary)]
              text-[var(--primary-foreground)]
              hover:bg-[color-mix(in_oklch,var(--primary)_85%,var(--secondary))]
            "
          >
            <Send size={16} />
          </Button>
        </div>

        {/* File Selected Preview */}
        {file && (
          <div className="mt-3 text-sm text-[var(--muted-foreground)]">
            Attached: <span className="font-medium">{file.name}</span>
          </div>
        )}
      </div>
    </div>
  );
}

function ChatMessage({
  role,
  content,
  file,
}: {
  role: "user" | "assistant";
  content: string;
  file?: File | null;
}) {
  const isUser = role === "user";

  return (
    <div className={`flex w-full ${isUser ? "justify-end" : "justify-start"}`}>
      <Card
        className={`
          max-w-[80%] py-2 px-4 rounded-2xl text-sm whitespace-pre-wrap 
          ${
            isUser
              ? "bg-[var(--primary)] text-[var(--primary-foreground)] rounded-br-sm"
              : "bg-[var(--card)] text-[var(--card-foreground)] border border-[var(--border)] rounded-bl-sm"
          }
        `}
      >
        {/* Message Text */}
        {content}

        {/* Attachment Preview */}
        {file && (
          <div className="mt-2 text-xs opacity-80">
            📎 Attached: {file.name}
          </div>
        )}
      </Card>
    </div>
  );
}
