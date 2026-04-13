import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Activity, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { analyzeApi } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'

export default function AnalyzePage() {
  const [incidentDescription, setIncidentDescription] = useState('')
  const [namespace, setNamespace] = useState('')
  const [podName, setPodName] = useState('')
  const [result, setResult] = useState<any>(null)
  const { toast } = useToast()

  const rcaMutation = useMutation({
    mutationFn: analyzeApi.rca,
    onSuccess: (response) => {
      setResult(response.data)
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to perform RCA',
        variant: 'destructive',
      })
    },
  })

  const handleAnalyze = () => {
    if (!incidentDescription.trim()) {
      toast({
        title: 'Missing Description',
        description: 'Please describe the incident',
        variant: 'destructive',
      })
      return
    }

    rcaMutation.mutate({
      incident_description: incidentDescription,
      namespace: namespace || undefined,
      pod_name: podName || undefined,
    })
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Root Cause Analysis</CardTitle>
          <CardDescription>
            Get AI-powered root cause analysis and recommendations for incidents
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Incident Description</label>
            <Textarea
              value={incidentDescription}
              onChange={(e) => setIncidentDescription(e.target.value)}
              placeholder="Describe the incident... e.g., 'Application is returning 500 errors and pods are restarting'"
              className="min-h-[120px]"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Namespace (optional)</label>
              <Input
                value={namespace}
                onChange={(e) => setNamespace(e.target.value)}
                placeholder="default"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Pod Name (optional)</label>
              <Input
                value={podName}
                onChange={(e) => setPodName(e.target.value)}
                placeholder="my-app-pod-123"
              />
            </div>
          </div>

          <Button
            onClick={handleAnalyze}
            disabled={rcaMutation.isPending}
            className="w-full"
          >
            {rcaMutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Activity className="mr-2 h-4 w-4" />
                Perform RCA
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {result && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Root Cause</CardTitle>
              <CardDescription>
                Confidence: {(result.confidence_score * 100).toFixed(0)}%
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-lg font-medium">{result.root_cause}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Detailed Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <p className="whitespace-pre-wrap">{result.analysis}</p>
              </div>
            </CardContent>
          </Card>

          {result.contributing_factors && result.contributing_factors.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Contributing Factors</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {result.contributing_factors.map((factor: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-muted-foreground">•</span>
                      <span className="text-sm">{factor}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {result.recommendations && result.recommendations.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Recommendations</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {result.recommendations.map((rec: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-primary">✓</span>
                      <span className="text-sm">{rec}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {result.action_items && result.action_items.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Action Items</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {result.action_items.map((item: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-primary">→</span>
                      <span className="text-sm">{item}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  )
}
