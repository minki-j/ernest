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

import { GoogleMapPicker } from '@/components/stocks/google-map-picker'

import { add_vendor } from '@/app/actions'

export function PickVendor() {
  const [placeState, setPlaceState] =
    useState<google.maps.places.PlaceResult | null>(null)
  const [isVendorSelected, setIsVendorSelected] = useState(false)

  const url = new URL(window.location.href)
  const pathnameParts = url.pathname.split('/')
  const reviewID =
    pathnameParts[pathnameParts.length - 1]

  const btnHandler = async () => {

    if (placeState && placeState.name && placeState.formatted_address) {
      setIsVendorSelected(true)

      const vendor_id = await add_vendor(placeState.name, placeState.formatted_address, reviewID)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          {isVendorSelected ? 'Selected Vendor' : 'Which place did you go?'}
        </CardTitle>
        {/* <CardDescription>Card Description</CardDescription> */}
      </CardHeader>
      <CardContent>
        {isVendorSelected ? (
          <div>
            <p>Name: {placeState?.name}</p>
            <p>Address: {placeState?.formatted_address}</p>
          </div>
        ) : (
          <GoogleMapPicker setPlaceState={setPlaceState} />
        )}
      </CardContent>
      <CardFooter>
        {isVendorSelected ? (
          <div></div>
        ) : (
          <Button className="w-full" onClick={btnHandler}>
            <CheckIcon className="mr-2 size-4" /> Select
          </Button>
        )}
      </CardFooter>
    </Card>
  )
}
