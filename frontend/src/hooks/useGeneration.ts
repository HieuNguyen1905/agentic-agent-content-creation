/**
 * Hook for content generation with real-time updates
 */

import { useState, useEffect, useCallback } from 'react';
import { api, GenerateRequest, JobStatus } from '@/lib/api';

export function useGeneration() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<JobStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [logs, setLogs] = useState<Array<{ message: string; timestamp: string }>>([]);

  // Start generation
  const generate = useCallback(async (request: GenerateRequest): Promise<void> => {
    setIsGenerating(true);
    setError(null);
    setLogs([]);

    try {
      const response = await api.generatePost(request);
      setJobId(response.job_id);
    } catch (err: any) {
      setError(err.message || 'Failed to start generation');
      setIsGenerating(false);
      throw err;
    }
  }, []);

  // Poll for status updates
  useEffect(() => {
    if (!jobId || !isGenerating) return;

    const interval = setInterval(async () => {
      try {
        const jobStatus = await api.getJobStatus(jobId);
        setStatus(jobStatus);

        if (jobStatus.status === 'completed' || jobStatus.status === 'failed') {
          setIsGenerating(false);
          clearInterval(interval);
          
          if (jobStatus.status === 'failed') {
            setError(jobStatus.error || 'Generation failed');
          }
        }
      } catch (err: any) {
        console.error('Error polling status:', err);
        setError(err.message);
        setIsGenerating(false);
        clearInterval(interval);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [jobId, isGenerating]);

  // WebSocket connection for real-time updates
  useEffect(() => {
    if (!jobId) return;

    let ws: WebSocket | null = null;

    try {
      ws = api.createWebSocket(jobId);

      ws.onopen = () => {
        console.log('WebSocket connected');
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data) as { message: string; timestamp: string; status?: 'queued' | 'processing' | 'completed' | 'failed'; progress?: number };
        
        if (data.message) {
          // Store the full log entry with timestamp
          setLogs(prev => [...prev, { message: data.message, timestamp: data.timestamp }]);
        }

        if (data.status && data.status) {
          setStatus(prev => prev ? ({
            ...prev,
            status: data.status as 'queued' | 'processing' | 'completed' | 'failed',
            progress: data.progress || prev.progress || 0,
          }) : null);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
      };

      // Send keepalive
      const keepalive = setInterval(() => {
        if (ws?.readyState === WebSocket.OPEN) {
          ws.send('ping');
        }
      }, 25000);

      return () => {
        clearInterval(keepalive);
        ws?.close();
      };
    } catch (err) {
      console.error('WebSocket connection failed:', err);
    }
  }, [jobId]);

  const reset = useCallback(() => {
    setIsGenerating(false);
    setJobId(null);
    setStatus(null);
    setError(null);
    setLogs([]);
  }, []);

  return {
    generate,
    reset,
    isGenerating,
    jobId,
    status,
    error,
    logs,
    progress: status?.progress || 0,
  };
}
