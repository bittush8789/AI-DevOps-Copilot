import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Code, Copy, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { generateApi } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'

const codeTypes = [
  { value: 'terraform', label: 'Terraform' },
  { value: 'kubernetes', label: 'Kubernetes YAML' },
  { value: 'github_actions', label: 'GitHub Actions' },
  { value: 'helm', label: 'Helm Chart' },
  { value: 'dockerfile', label: 'Dockerfile' },
]

export default function GeneratePage() {
  const [selectedType, setSelectedType] = useState('terraform')
  const [description, setDescription] = useState('')
  const [result, setResult] = useState<any>(null)
  const { toast } = useToast()

  const generateMutation = useMutation({
    mutationFn: generateApi.generate,
    onSuccess: (response) => {
      setResult(response.data)
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to generate code',
        variant: 'destructive',
      })
    },
  })

  const handleGenerate = () => {
    if (!description.trim()) {
      toast({
        title: 'Missing Description',
        description: 'Please provide a description of what to generate',
        variant: 'destructive',
      })
      return
    }

    generateMutation.mutate({
      type: selectedType as any,
      description,
    })
  }

  const copyToClipboard = () => {
    if (result?.code) {
      navigator.clipboard.writeText(result.code)
      toast({
        title: 'Copied!',
        description: 'Code copied to clipboard',
      })
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Code Generation</CardTitle>
          <CardDescription>
            Generate infrastructure code, Kubernetes manifests, and CI/CD pipelines
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Code Type</label>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
              {codeTypes.map((type) => (
                <Button
                  key={type.value}
                  variant={selectedType === type.value ? 'default' : 'outline'}
                  onClick={() => setSelectedType(type.value)}
                  className="w-full"
                >
                  {type.label}
                </Button>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Description</label>
            <Textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe what you want to generate... e.g., 'Create an EKS cluster with 3 nodes'"
              className="min-h-[120px]"
            />
          </div>

          <Button
            onClick={handleGenerate}
            disabled={generateMutation.isPending}
            className="w-full"
          >
            {generateMutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Code className="mr-2 h-4 w-4" />
                Generate Code
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {result && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Explanation</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm whitespace-pre-wrap">{result.explanation}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>{result.filename}</CardTitle>
                <CardDescription>Generated code</CardDescription>
              </div>
              <Button variant="outline" size="sm" onClick={copyToClipboard}>
                <Copy className="mr-2 h-4 w-4" />
                Copy
              </Button>
            </CardHeader>
            <CardContent>
              <pre className="bg-muted p-4 rounded-lg overflow-auto text-xs">
                <code>{result.code}</code>
              </pre>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
