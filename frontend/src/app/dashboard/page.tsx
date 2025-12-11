'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useGeneration } from '@/hooks/useGeneration';

export default function DashboardPage() {
  const router = useRouter();
  const { generate, isGenerating, status, error, logs, progress } = useGeneration();
  
  const [formData, setFormData] = useState({
    topic: '',
    length: 'medium' as 'short' | 'medium' | 'long',
    style: 'informative',
    tone: 'professional',
    categories: '',
    tags: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await generate({
        topic: formData.topic,
        length: formData.length,
        style: formData.style,
        tone: formData.tone,
        categories: formData.categories ? formData.categories.split(',').map(c => c.trim()) : [],
        tags: formData.tags ? formData.tags.split(',').map(t => t.trim()) : [],
      });
    } catch (err) {
      console.error('Generation error:', err);
    }
  };

  const handleViewPost = () => {
    if (status?.result?.slug) {
      router.push(`/blog/${status.result.slug}`);
    } else {
      console.error('No slug available:', status?.result);
      alert('Post slug not found. Please check the generation results.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-4xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Content Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Generate AI-powered blog posts with advanced SEO optimization
          </p>
        </div>

        {/* Generation Form */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Topic */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Blog Topic *
              </label>
              <input
                type="text"
                value={formData.topic}
                onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                placeholder="Enter your blog topic..."
                required
                disabled={isGenerating}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg
                         bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                         focus:ring-2 focus:ring-indigo-500 focus:border-transparent
                         disabled:opacity-50 disabled:cursor-not-allowed
                         transition-all"
              />
            </div>

            {/* Length and Style */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Length
                </label>
                <select
                  value={formData.length}
                  onChange={(e) => setFormData({ ...formData, length: e.target.value as any })}
                  disabled={isGenerating}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg
                           bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                           focus:ring-2 focus:ring-indigo-500 focus:border-transparent
                           disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <option value="short">Short (600-1000 words)</option>
                  <option value="medium">Medium (1000-1500 words)</option>
                  <option value="long">Long (1500-2500 words)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Style
                </label>
                <input
                  type="text"
                  value={formData.style}
                  onChange={(e) => setFormData({ ...formData, style: e.target.value as 'short' | 'medium' | 'long' })}
                  placeholder="e.g., informative, technical, casual"
                  disabled={isGenerating}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg
                           bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                           focus:ring-2 focus:ring-indigo-500 focus:border-transparent
                           disabled:opacity-50 disabled:cursor-not-allowed"
                />
              </div>
            </div>

            {/* Tone */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Tone
              </label>
              <input
                type="text"
                value={formData.tone}
                onChange={(e) => setFormData({ ...formData, tone: e.target.value })}
                placeholder="e.g., professional, friendly, authoritative"
                disabled={isGenerating}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg
                         bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                         focus:ring-2 focus:ring-indigo-500 focus:border-transparent
                         disabled:opacity-50 disabled:cursor-not-allowed"
              />
            </div>

            {/* Categories and Tags */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Categories (comma-separated)
                </label>
                <input
                  type="text"
                  value={formData.categories}
                  onChange={(e) => setFormData({ ...formData, categories: e.target.value })}
                  placeholder="technology, ai, development"
                  disabled={isGenerating}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg
                           bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                           focus:ring-2 focus:ring-indigo-500 focus:border-transparent
                           disabled:opacity-50 disabled:cursor-not-allowed"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Tags (comma-separated)
                </label>
                <input
                  type="text"
                  value={formData.tags}
                  onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                  placeholder="tutorial, guide, howto"
                  disabled={isGenerating}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg
                           bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                           focus:ring-2 focus:ring-indigo-500 focus:border-transparent
                           disabled:opacity-50 disabled:cursor-not-allowed"
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={!formData.topic || isGenerating}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold
                       py-4 px-6 rounded-lg transition-all duration-200
                       disabled:opacity-50 disabled:cursor-not-allowed
                       transform hover:scale-[1.02] active:scale-[0.98]
                       shadow-lg hover:shadow-xl"
            >
              {isGenerating ? (
                <span className="flex items-center justify-center gap-3">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Generating... {progress}%
                </span>
              ) : (
                '🚀 Generate Blog Post'
              )}
            </button>
          </form>
        </div>

        {/* Progress Status */}
        {isGenerating && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-8">
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Generation Progress
                </h3>
                <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium
                               bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
                  </span>
                  {status?.status || 'queued'}
                </span>
              </div>

              {/* Progress Bar */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                  <span>Progress</span>
                  <span className="font-semibold">{progress}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden shadow-inner">
                  <div
                    className="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 h-full transition-all duration-500 ease-out relative overflow-hidden"
                    style={{ width: `${progress}%` }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer"></div>
                  </div>
                </div>
              </div>

              {/* Activity Logs */}
              <div className="mt-6 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                <div className="bg-gradient-to-r from-indigo-500 to-purple-600 px-4 py-2">
                  <h4 className="text-sm font-semibold text-white flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Activity Log
                  </h4>
                </div>
                
                <div className="p-4 max-h-80 overflow-y-auto custom-scrollbar">
                  {logs.length > 0 ? (
                    <div className="space-y-2">
                      {logs.map((log, i) => (
                        <div 
                          key={i} 
                          className="flex items-start gap-3 p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors animate-fadeIn"
                          style={{ animationDelay: `${i * 50}ms` }}
                        >
                          <span className="flex-shrink-0 text-indigo-500 dark:text-indigo-400 font-bold mt-0.5">→</span>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm text-gray-700 dark:text-gray-300 break-words">
                              {log.message}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-500 mt-0.5">
                              {new Date(log.timestamp).toLocaleTimeString()}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                      <svg className="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                      </svg>
                      <p className="text-sm">Waiting for activity...</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Success Result */}
        {status?.status === 'completed' && status.result && (
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 
                        rounded-2xl shadow-xl p-8 border-2 border-green-200 dark:border-green-700">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
              
              <div className="flex-1">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                  ✨ Content Generated Successfully!
                </h3>
                <div className="space-y-2 text-gray-700 dark:text-gray-300">
                  <p><strong>Title:</strong> {status.result.title || 'N/A'}</p>
                  <p><strong>Slug:</strong> {status.result.slug || 'N/A'}</p>
                  <p><strong>Word Count:</strong> {status.result.word_count || 0} words</p>
                  {status.result.seo_score !== undefined && (
                    <p><strong>SEO Score:</strong> {status.result.seo_score}/100</p>
                  )}
                  <p><strong>Iterations:</strong> {status.result.iterations || 0}</p>
                </div>
                
                <div className="mt-4 flex gap-3">
                  <button
                    onClick={handleViewPost}
                    className="bg-green-600 hover:bg-green-700 text-white font-semibold
                             py-2 px-6 rounded-lg transition-all"
                  >
                    View Post
                  </button>
                  <button
                    onClick={() => window.location.reload()}
                    className="bg-gray-600 hover:bg-gray-700 text-white font-semibold
                             py-2 px-6 rounded-lg transition-all"
                  >
                    Generate Another
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 rounded-2xl shadow-xl p-6 border-2 border-red-200 dark:border-red-700">
            <div className="flex items-start gap-3">
              <svg className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h3 className="text-lg font-semibold text-red-800 dark:text-red-300 mb-1">
                  Generation Failed
                </h3>
                <p className="text-red-600 dark:text-red-400">{error}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
