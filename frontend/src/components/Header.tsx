import { Menu, Transition } from '@headlessui/react'
import { Fragment } from 'react'
import { 
  BellIcon, 
  UserCircleIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline'
import { useAuthStore } from '@/store/authStore'
import { useNavigate } from 'react-router-dom'

export default function Header() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-2xl font-bold text-gray-900">
            AI Dubbing Platform
          </h1>
        </div>

        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
            <BellIcon className="w-6 h-6" />
          </button>

          {/* User menu */}
          <Menu as="div" className="relative">
            <Menu.Button className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-100">
              <UserCircleIcon className="w-8 h-8 text-gray-400" />
              <div className="text-left">
                <p className="text-sm font-medium text-gray-900">
                  {user?.full_name}
                </p>
                <p className="text-xs text-gray-500 capitalize">
                  {user?.role}
                </p>
              </div>
            </Menu.Button>

            <Transition
              as={Fragment}
              enter="transition ease-out duration-100"
              enterFrom="transform opacity-0 scale-95"
              enterTo="transform opacity-100 scale-100"
              leave="transition ease-in duration-75"
              leaveFrom="transform opacity-100 scale-100"
              leaveTo="transform opacity-0 scale-95"
            >
              <Menu.Items className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
                <div className="p-1">
                  <Menu.Item>
                    {({ active }) => (
                      <button
                        onClick={() => navigate('/settings')}
                        className={`${
                          active ? 'bg-gray-100' : ''
                        } flex items-center space-x-2 w-full px-3 py-2 text-sm text-gray-700 rounded-md`}
                      >
                        <Cog6ToothIcon className="w-4 h-4" />
                        <span>Settings</span>
                      </button>
                    )}
                  </Menu.Item>
                  <Menu.Item>
                    {({ active }) => (
                      <button
                        onClick={handleLogout}
                        className={`${
                          active ? 'bg-gray-100' : ''
                        } flex items-center space-x-2 w-full px-3 py-2 text-sm text-gray-700 rounded-md`}
                      >
                        <ArrowRightOnRectangleIcon className="w-4 h-4" />
                        <span>Sign out</span>
                      </button>
                    )}
                  </Menu.Item>
                </div>
              </Menu.Items>
            </Transition>
          </Menu>
        </div>
      </div>
    </header>
  )
}