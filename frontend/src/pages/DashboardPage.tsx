import { useQuery } from 'react-query'
import { Link } from 'react-router-dom'
import { 
  PlayIcon,
  FolderIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  PlusIcon
} from '@heroicons/react/24/outline'
import { dubbingAPI, projectsAPI } from '@/services/api'

const stats = [
  { name: 'Total Projects', value: '12', icon: FolderIcon, color: 'text-blue-600' },
  { name: 'In Progress', value: '3', icon: ClockIcon, color: 'text-yellow-600' },
  { name: 'Completed', value: '8', icon: CheckCircleIcon, color: 'text-green-600' },
  { name: 'Failed', value: '1', icon: ExclamationTriangleIcon, color: 'text-red-600' },
]

export default function DashboardPage() {
  // Fetch recent jobs
  const { data: recentJobs, isLoading: jobsLoading } = useQuery(
    'recent-jobs',
    () => dubbingAPI.listJobs({ limit: 5 }),
    {
      select: (response) => response.data,
    }
  )

  // Fetch recent projects
  const { data: recentProjects, isLoading: projectsLoading } = useQuery(
    'recent-projects',
    () => projectsAPI.list({ limit: 5 }),
    {
      select: (response) => response.data,
    }
  )

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Welcome back! Here's what's happening with your dubbing projects.
          </p>
        </div>
        <Link to="/dubbing" className="btn-primary flex items-center space-x-2">
          <PlusIcon className="w-4 h-4" />
          <span>New Project</span>
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <div key={stat.name} className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <stat.icon className={`w-8 h-8 ${stat.color}`} />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Jobs */}
        <div className="card">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Recent Jobs</h2>
              <Link to="/jobs" className="text-sm text-primary-600 hover:text-primary-700">
                View all
              </Link>
            </div>
          </div>
          
          <div className="p-6">
            {jobsLoading ? (
              <div className="space-y-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </div>
                ))}
              </div>
            ) : recentJobs && recentJobs.length > 0 ? (
              <div className="space-y-4">
                {recentJobs.map((job: any) => (
                  <div key={job.id} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`w-2 h-2 rounded-full ${
                        job.status === 'completed' ? 'bg-green-500' :
                        job.status === 'running' ? 'bg-yellow-500' :
                        job.status === 'failed' ? 'bg-red-500' : 'bg-gray-400'
                      }`}></div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {job.target_languages?.join(', ') || 'Multiple Languages'}
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(job.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        job.status === 'completed' ? 'bg-green-100 text-green-800' :
                        job.status === 'running' ? 'bg-yellow-100 text-yellow-800' :
                        job.status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {job.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <PlayIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No jobs yet</p>
                <Link to="/dubbing" className="text-primary-600 hover:text-primary-700 text-sm">
                  Create your first dubbing job
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Recent Projects */}
        <div className="card">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Recent Projects</h2>
              <Link to="/projects" className="text-sm text-primary-600 hover:text-primary-700">
                View all
              </Link>
            </div>
          </div>
          
          <div className="p-6">
            {projectsLoading ? (
              <div className="space-y-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </div>
                ))}
              </div>
            ) : recentProjects && recentProjects.length > 0 ? (
              <div className="space-y-4">
                {recentProjects.map((project: any) => (
                  <Link
                    key={project.id}
                    to={`/projects/${project.id}`}
                    className="block hover:bg-gray-50 rounded-lg p-2 -m-2"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {project.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {project.target_languages?.length || 0} languages • 
                          {new Date(project.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="progress-bar w-20">
                        <div 
                          className="progress-fill" 
                          style={{ width: `${(project.progress || 0) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <FolderIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No projects yet</p>
                <Link to="/dubbing" className="text-primary-600 hover:text-primary-700 text-sm">
                  Create your first project
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            to="/dubbing"
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors"
          >
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <PlayIcon className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <p className="font-medium text-gray-900">New Dubbing</p>
              <p className="text-sm text-gray-500">Start a new project</p>
            </div>
          </Link>
          
          <Link
            to="/projects"
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors"
          >
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <FolderIcon className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <p className="font-medium text-gray-900">View Projects</p>
              <p className="text-sm text-gray-500">Manage your work</p>
            </div>
          </Link>
          
          <Link
            to="/settings"
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors"
          >
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <Cog6ToothIcon className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <p className="font-medium text-gray-900">Settings</p>
              <p className="text-sm text-gray-500">Configure preferences</p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  )
}