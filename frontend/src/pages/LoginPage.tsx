import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation } from 'react-query'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { GlobeAltIcon } from '@heroicons/react/24/outline'
import { authAPI } from '@/services/api'
import { useAuthStore } from '@/store/authStore'

interface LoginForm {
  username: string
  password: string
}

export default function LoginPage() {
  const navigate = useNavigate()
  const { login } = useAuthStore()
  
  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>()

  const loginMutation = useMutation(authAPI.login, {
    onSuccess: (response) => {
      const { access_token } = response.data
      // In a real app, you'd decode the JWT to get user info
      const mockUser = {
        id: '1',
        email: 'user@example.com',
        username: 'user',
        full_name: 'Demo User',
        role: 'creator',
        is_active: true,
      }
      
      login(access_token, mockUser)
      toast.success('Login successful!')
      navigate('/dashboard')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Login failed')
    },
  })

  const onSubmit = (data: LoginForm) => {
    loginMutation.mutate(data)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="flex justify-center">
            <div className="w-16 h-16 bg-primary-600 rounded-lg flex items-center justify-center">
              <GlobeAltIcon className="w-10 h-10 text-white" />
            </div>
          </div>
          <h2 className="mt-6 text-center text-3xl font-bold text-gray-900">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{' '}
            <Link
              to="/register"
              className="font-medium text-primary-600 hover:text-primary-500"
            >
              create a new account
            </Link>
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                Email or Username
              </label>
              <input
                {...register('username', { required: 'Email or username is required' })}
                type="text"
                className="input mt-1"
                placeholder="Enter your email or username"
              />
              {errors.username && (
                <p className="mt-1 text-sm text-error-600">{errors.username.message}</p>
              )}
            </div>
            
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                {...register('password', { required: 'Password is required' })}
                type="password"
                className="input mt-1"
                placeholder="Enter your password"
              />
              {errors.password && (
                <p className="mt-1 text-sm text-error-600">{errors.password.message}</p>
              )}
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900">
                Remember me
              </label>
            </div>

            <div className="text-sm">
              <a href="#" className="font-medium text-primary-600 hover:text-primary-500">
                Forgot your password?
              </a>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loginMutation.isLoading}
              className="w-full btn-primary"
            >
              {loginMutation.isLoading ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Signing in...</span>
                </div>
              ) : (
                'Sign in'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}