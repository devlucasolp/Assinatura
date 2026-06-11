import { LoginForm } from './LoginForm'
import { Suspense } from 'react'

export default async function LoginPage() {
  return (
    <Suspense fallback={<div className="flex justify-center p-8"><div className="w-6 h-6 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" /></div>}>
      <LoginForm />
    </Suspense>
  )
}
