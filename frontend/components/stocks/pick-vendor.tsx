'use client'

import { useState, useRef, useEffect, useId } from 'react'
import { scaleLinear } from 'd3-scale'
import { subMonths, format } from 'date-fns'
import { useResizeObserver } from 'usehooks-ts'
import { useAIState } from 'ai/rsc'

import { BellIcon, CheckIcon } from '@radix-ui/react-icons'

import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle
} from '@/components/ui/card'

import { VendorPicker } from '@/components/stocks/vendor-picker'

export function PickVendor() {
  return (

    //   <Card>
    //     <CardHeader>
    //       <CardTitle>Pick a vendor</CardTitle>
    //       {/* <CardDescription>Card Description</CardDescription> */}
    //     </CardHeader>
    //     <CardContent></CardContent>
    //     <CardFooter>
    //       <Button className="w-full">
    //         <CheckIcon className="mr-2 size-4" /> Select
    //       </Button>
    //     </CardFooter>
    //   </Card>
      <VendorPicker />

  )
}
