import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Search, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { logsApi } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'

export default function LogsPage() {
  const [namespace, setNamespace] = useState('')
  const [podName, setPodName] = useState('')
  const [analysis, setAnalysis] = useState<any>(null)
  const { toast } = useToast()

  const analyzeMutation = useMutation({
    mutationFn: logsApi.analyze,
    onSuccess: (response) => {
      setAnalysis(response.data)
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to analyze logs',
        variant: 'destructive',
      })
    },
  })

  const handleAnalyze = () => {
    if (!namespace || !podName) {
      toast({
        title: 'Missing Information',
        description: 'Please provide both namespace and pod name',
        variant: 'destructive',
      })
      return
    }

    analyzeMutation.mutate({
      source: 'kubernetes',
      namespace,
      pod_name: podName,
      tail_lines: 100,
    })
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Log Analysis</CardTitle>
          <CardDescription>
            Analyze logs from Kubernetes pods, CloudWatch, or Loki
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Namespace</label>
              <Input
                value={namespace}
                onChange={(e) => setNamespace(e.target.value)}
                placeholder="default"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Pod Name</label>
              <Input
                value={podName}
                onChange={(e) => setPodName(e.target.value)}
                placeholder="my-app-pod-123"
              />
            </div>
          </div>

          <Button
            onClick={handleAnalyze}
            disabled={analyzeMutation.isPending}
            className="w-full"
          >
            {analyzeMutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Search className="mr-2 h-4 w-4" />
                Analyze Logs
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {analysis && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <p className="whitespace-pre-wrap">{analysis.analysis}</p>
              </div>
            </CardContent>
          </Card>

          {analysis.issues_found && analysis.issues_found.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Issues Found</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {analysis.issues_found.map((issue: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-destructive">•</span>
                      <span className="text-sm">{issue}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {analysis.recommendations && analysis.recommendations.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Recommendations</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {analysis.recommendations.map((rec: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-primary">✓</span>
                      <span className="text-sm">{rec}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Raw Logs</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="bg-muted p-4 rounded-lg overflow-auto text-xs">
                {analysis.logs}
              </pre>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
