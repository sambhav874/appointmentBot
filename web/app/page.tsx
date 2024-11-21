import { ChatInterface } from "@/components/ChatInterface";
import Image from "next/image";

export default function Home() {
  return (
    
      <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Insurance Chatbot Service</h1>
      <ChatInterface />
    </div>
    
  );
}
