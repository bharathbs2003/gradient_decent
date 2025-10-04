import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQuery } from 'react-query'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import { 
  CloudArrowUpIcon, 
  PlayIcon,
  DocumentIcon,
  GlobeAltIcon,
  Cog6ToothIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'
import { dubbingAPI } from '@/services/api'

interface DubbingForm {
  targetLanguages: string[]
  sourceLanguage?: string
  enableVoiceCloning: boolean
  enableEmotionPreservation: boolean
  qualityMode: 'structural' | 'end_to_end'
  requireHumanReview: boolean
}

const QUALITY_MODES = [
  {
    id: 'structural',
    name: 'High Quality (Structural)',
    description: 'Best quality with 3D face reconstruction and neural rendering',
    recommended: true,
  },
  {
    id: 'end_to_end',
    name: 'Fast Processing (End-to-End)',
    description: 'Faster processing with direct audio-to-video generation',
    recommended: false,
  },
]

export default function DubbingPage() {
  const navigate = useNavigate()
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [form, setForm] = useState<DubbingForm>({
    targetLanguages: [],
    sourceLanguage: '',
    enableVoiceCloning: true,
    enableEmotionPreservation: true,
    qualityMode: 'structural',
    requireHumanReview: false,
  })

  // Fetch supported languages
  const { data: languages } = useQuery(
    'supported-languages',
    dubbingAPI.getSupportedLanguages,
    {
      select: (response) => response.data,
    }
  )

  // Create dubbing job mutation
  const createJobMutation = useMutation(dubbingAPI.createJob, {
    onSuccess: (response) => {
      toast.success('Dubbing job created successfully!')
      navigate(`/projects/${response.data.project_id}`)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to create dubbing job')
    },
  })

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'video/*': ['.mp4', '.mov', '.avi', '.mkv'],
    },
    maxFiles: 1,
    maxSize: 500 * 1024 * 1024, // 500MB
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setSelectedFile(acceptedFiles[0])
      }
    },
    onDropRejected: (rejectedFiles) => {
      const error = rejectedFiles[0]?.errors[0]
      if (error?.code === 'file-too-large') {
        toast.error('File too large. Maximum size is 500MB.')
      } else {
        toast.error('Invalid file type. Please upload a video file.')
      }
    },
  })

  const handleLanguageToggle = (languageCode: string) => {
    setForm(prev => ({
      ...prev,
      targetLanguages: prev.targetLanguages.includes(languageCode)
        ? prev.targetLanguages.filter(lang => lang !== languageCode)
        : [...prev.targetLanguages, languageCode]
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!selectedFile) {
      toast.error('Please select a video file')
      return
    }

    if (form.targetLanguages.length === 0) {
      toast.error('Please select at least one target language')
      return
    }

    const formData = new FormData()
    formData.append('video_file', selectedFile)
    formData.append('target_languages', JSON.stringify(form.targetLanguages))
    
    if (form.sourceLanguage) {
      formData.append('source_language', form.sourceLanguage)
    }
    
    formData.append('enable_voice_cloning', form.enableVoiceCloning.toString())
    formData.append('enable_emotion_preservation', form.enableEmotionPreservation.toString())
    formData.append('quality_mode', form.qualityMode)
    formData.append('require_human_review', form.requireHumanReview.toString())

    createJobMutation.mutate(formData)
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Create New Dubbing Project
        </h1>
        <p className="text-gray-600">
          Upload your video and configure dubbing settings for multilingual content creation.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* File Upload */}
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <DocumentIcon className="w-5 h-5 mr-2" />
            Video Upload
          </h2>
          
          <div
            {...getRootProps()}
            className={`upload-area ${isDragActive ? 'dragover' : ''}`}
          >
            <input {...getInputProps()} />
            <CloudArrowUpIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            
            {selectedFile ? (
              <div className="text-center">
                <p className="text-lg font-medium text-gray-900 mb-2">
                  {selectedFile.name}
                </p>
                <p className="text-sm text-gray-500 mb-4">
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                </p>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    setSelectedFile(null)
                  }}
                  className="btn-secondary"
                >
                  Remove File
                </button>
              </div>
            ) : (
              <div className="text-center">
                <p className="text-lg font-medium text-gray-900 mb-2">
                  {isDragActive ? 'Drop your video here' : 'Upload your video file'}
                </p>
                <p className="text-sm text-gray-500 mb-4">
                  Drag and drop or click to browse. Supports MP4, MOV, AVI, MKV (max 500MB)
                </p>
                <button type="button" className="btn-primary">
                  Choose File
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Language Selection */}
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <GlobeAltIcon className="w-5 h-5 mr-2" />
            Language Settings
          </h2>

          {/* Source Language */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Source Language (optional)
            </label>
            <select
              value={form.sourceLanguage}
              onChange={(e) => setForm(prev => ({ ...prev, sourceLanguage: e.target.value }))}
              className="input max-w-xs"
            >
              <option value="">Auto-detect</option>
              {languages?.map((lang: any) => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">
              Leave empty for automatic language detection
            </p>
          </div>

          {/* Target Languages */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Target Languages ({form.targetLanguages.length} selected)
            </label>
            
            {languages && (
              <div className="language-grid">
                {languages.map((lang: any) => (
                  <div
                    key={lang.code}
                    onClick={() => handleLanguageToggle(lang.code)}
                    className={`language-card ${
                      form.targetLanguages.includes(lang.code) ? 'selected' : ''
                    }`}
                  >
                    <div className="text-sm font-medium text-gray-900">
                      {lang.name}
                    </div>
                    <div className="text-xs text-gray-500">
                      {lang.code.toUpperCase()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Quality & Processing Settings */}
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Cog6ToothIcon className="w-5 h-5 mr-2" />
            Processing Settings
          </h2>

          {/* Quality Mode */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Quality Mode
            </label>
            <div className="space-y-3">
              {QUALITY_MODES.map((mode) => (
                <label key={mode.id} className="flex items-start space-x-3 cursor-pointer">
                  <input
                    type="radio"
                    name="qualityMode"
                    value={mode.id}
                    checked={form.qualityMode === mode.id}
                    onChange={(e) => setForm(prev => ({ 
                      ...prev, 
                      qualityMode: e.target.value as 'structural' | 'end_to_end'
                    }))}
                    className="mt-1"
                  />
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-900">
                        {mode.name}
                      </span>
                      {mode.recommended && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-success-100 text-success-800">
                          Recommended
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {mode.description}
                    </p>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Advanced Options */}
          <div className="space-y-4">
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={form.enableVoiceCloning}
                onChange={(e) => setForm(prev => ({ 
                  ...prev, 
                  enableVoiceCloning: e.target.checked 
                }))}
              />
              <div>
                <span className="text-sm font-medium text-gray-900">
                  Enable Voice Cloning
                </span>
                <p className="text-xs text-gray-500">
                  Clone original speaker's voice for target languages
                </p>
              </div>
            </label>

            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={form.enableEmotionPreservation}
                onChange={(e) => setForm(prev => ({ 
                  ...prev, 
                  enableEmotionPreservation: e.target.checked 
                }))}
              />
              <div>
                <span className="text-sm font-medium text-gray-900">
                  Preserve Emotions & Gestures
                </span>
                <p className="text-xs text-gray-500">
                  Maintain original emotional expressions and facial gestures
                </p>
              </div>
            </label>

            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={form.requireHumanReview}
                onChange={(e) => setForm(prev => ({ 
                  ...prev, 
                  requireHumanReview: e.target.checked 
                }))}
              />
              <div>
                <span className="text-sm font-medium text-gray-900">
                  Require Human Review
                </span>
                <p className="text-xs text-gray-500">
                  Queue translations for human review before processing
                </p>
              </div>
            </label>
          </div>
        </div>

        {/* Submit */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => navigate('/dashboard')}
            className="btn-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={createJobMutation.isLoading || !selectedFile}
            className="btn-primary flex items-center space-x-2"
          >
            {createJobMutation.isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Creating...</span>
              </>
            ) : (
              <>
                <PlayIcon className="w-4 h-4" />
                <span>Start Dubbing</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}