import { Link } from 'react-router-dom'
import { 
  PlayIcon, 
  GlobeAltIcon, 
  SparklesIcon,
  ShieldCheckIcon,
  ClockIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'

const features = [
  {
    name: 'Automated Dubbing Pipeline',
    description: 'Reduce manual dubbing effort by ≥80% with our AI-powered automation',
    icon: PlayIcon,
  },
  {
    name: '50+ Language Support',
    description: 'Cover top spoken languages by internet users worldwide',
    icon: GlobeAltIcon,
  },
  {
    name: 'High-Quality Lip Sync',
    description: 'Achieve LSE-C ≥ 0.85 accuracy with advanced facial re-animation',
    icon: SparklesIcon,
  },
  {
    name: 'Real-time Preview',
    description: '<5 second latency for short clips with instant feedback',
    icon: ClockIcon,
  },
  {
    name: 'Ethical AI Safeguards',
    description: 'Embedded provenance tracking and consent management',
    icon: ShieldCheckIcon,
  },
  {
    name: 'Quality Metrics',
    description: 'Comprehensive quality assessment with industry-standard metrics',
    icon: ChartBarIcon,
  },
]

const stats = [
  { name: 'Languages Supported', value: '50+' },
  { name: 'Processing Speed', value: '<1 min/min' },
  { name: 'Lip Sync Accuracy', value: '≥85%' },
  { name: 'Quality Score', value: '90%+' },
]

export default function HomePage() {
  return (
    <div className="bg-white">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                <GlobeAltIcon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Multilingual AI Video Dubbing Platform
                </h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                to="/login"
                className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                Sign in
              </Link>
              <Link
                to="/register"
                className="btn-primary"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <div className="relative bg-gradient-to-br from-primary-50 to-secondary-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
              Create High-Fidelity
              <span className="text-primary-600 block">Multilingual Dubbing</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Enable seamless, high-fidelity, multilingual dubbing of video content by 
              automatically synchronizing translated speech with realistic, speaker-consistent 
              facial animations—eliminating the "uncanny valley" effect.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register"
                className="btn-primary text-lg px-8 py-3"
              >
                Start Dubbing Now
              </Link>
              <Link
                to="/demo"
                className="btn-secondary text-lg px-8 py-3"
              >
                Watch Demo
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="bg-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat) => (
              <div key={stat.name} className="text-center">
                <div className="text-3xl font-bold text-primary-600 mb-2">
                  {stat.value}
                </div>
                <div className="text-sm text-gray-600">{stat.name}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="bg-gray-50 py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Powerful Features for Professional Dubbing
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Our AI-powered platform delivers studio-quality multilingual video content 
              at scale with cutting-edge technology.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature) => (
              <div key={feature.name} className="card p-6">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-primary-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {feature.name}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-primary-600 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Transform Your Content?
          </h2>
          <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
            Join leading content creators and streaming platforms using our 
            AI dubbing technology to reach global audiences.
          </p>
          <Link
            to="/register"
            className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-lg font-medium rounded-lg text-primary-600 bg-white hover:bg-gray-50 transition-colors"
          >
            Get Started Today
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center text-gray-600">
            <p>&copy; 2024 Multilingual AI Video Dubbing Platform. All rights reserved.</p>
            <p className="mt-2">Built with ethical AI principles and industry-leading technology.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}