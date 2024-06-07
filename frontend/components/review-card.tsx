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
        <p>{created_at.split("T")[0]}</p>
      </CardFooter>
    </Card>
  )
}
