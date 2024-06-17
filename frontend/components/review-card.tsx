import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardDescription,
  CardFooter
} from '@/components/ui/card'


interface ReviewCardProps {
  key: string
  title: string
  description: string
  content: string
  created_at: string | Date
}

export function ReviewCard({
  key,
  title,
  description,
  content,
  created_at
}: ReviewCardProps) {
  
  function splitDateOrString(input: string | Date): string {
    if (typeof input === 'string') {
      // input is a string, so we can safely call split
      return input.split('T')[0]
    } else {
      // input is a Date, so we need to convert it to a string first
      // For example, using toISOString() to get a string representation
      return input.toISOString().split('T')[0]
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <p>{content}</p>
      </CardContent>
      <CardFooter>
        <p>{splitDateOrString(created_at)}</p>
      </CardFooter>
    </Card>
  )
}
