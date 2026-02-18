'use client'

import Link from 'next/link'
import { BookOpen, Users, GraduationCap, Brain } from 'lucide-react'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <Brain className="h-8 w-8 text-primary-600" />
              <h1 className="text-2xl font-bold text-gray-900">Helix</h1>
            </div>
            <nav className="flex space-x-4">
              <Link href="/login" className="text-gray-600 hover:text-gray-900">
                Login
              </Link>
              <Link
                href="/register"
                className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
              >
                Get Started
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold text-gray-900 mb-4">
            Generative Teaching Infrastructure
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            Transform any curriculum into personalized, Socratic pedagogy. 
            Real-time, adaptive AI that generates infinite learning pathways.
          </p>
          <div className="flex justify-center space-x-4">
            <Link
              href="/register"
              className="bg-primary-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-primary-700"
            >
              Start Learning
            </Link>
            <Link
              href="/demo"
              className="bg-white text-primary-600 px-8 py-3 rounded-lg text-lg font-semibold border-2 border-primary-600 hover:bg-primary-50"
            >
              See Demo
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mt-16">
          <FeatureCard
            icon={<BookOpen className="h-8 w-8" />}
            title="Curriculum-Native"
            description="Aligned with official syllabi: IGCSE, KCSE, CBSE, Common Core"
          />
          <FeatureCard
            icon={<Brain className="h-8 w-8" />}
            title="Socratic Teaching"
            description="Guides understanding through questions, not direct answers"
          />
          <FeatureCard
            icon={<Users className="h-8 w-8" />}
            title="Personalized"
            description="Knowledge graphs adapt to each student's learning journey"
          />
          <FeatureCard
            icon={<GraduationCap className="h-8 w-8" />}
            title="Infinite Practice"
            description="Unlimited exam-style questions with instant feedback"
          />
        </div>

        {/* Use Cases */}
        <div className="mt-24">
          <h3 className="text-3xl font-bold text-center mb-12">Built for Everyone</h3>
          <div className="grid md:grid-cols-3 gap-8">
            <UseCaseCard
              title="Homeschool Families"
              description="Reclaim your time. One platform for all subjects, all learning styles."
              link="/homeschool"
            />
            <UseCaseCard
              title="Students"
              description="Personalized tutoring that adapts to your pace and learning style."
              link="/students"
            />
            <UseCaseCard
              title="Schools & Teachers"
              description="Force multiplication: 1 teacher + Helix = 1:1 tutoring for every student."
              link="/schools"
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-center text-gray-600">
            © 2024 Helix. Generative Teaching Infrastructure.
          </p>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="text-primary-600 mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}

function UseCaseCard({ title, description, link }: { title: string; description: string; link: string }) {
  return (
    <Link href={link} className="block bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition">
      <h4 className="text-xl font-semibold mb-2">{title}</h4>
      <p className="text-gray-600">{description}</p>
    </Link>
  )
}
