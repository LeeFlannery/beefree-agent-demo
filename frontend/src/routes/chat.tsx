import { createFileRoute } from '@tanstack/react-router'
import Layout from '../components/Layout'

export const Route = createFileRoute('/chat')({
  component: ChatPage,
})

function ChatPage() {
  return <Layout />
}
