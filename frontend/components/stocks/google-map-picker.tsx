import React, { useState, useEffect, useRef } from 'react'
import { createRoot } from 'react-dom/client'
import {
  APIProvider,
  ControlPosition,
  MapControl,
  AdvancedMarker,
  Map,
  useMap,
  useMapsLibrary,
  useAdvancedMarkerRef,
  AdvancedMarkerRef
} from '@vis.gl/react-google-maps'

const API_KEY = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY
  ? process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY
  : ''

export const GoogleMapPicker = ({ setPlaceState }) => {
  const [selectedPlace, setSelectedPlace] =
    useState<google.maps.places.PlaceResult | null>(null)
  const [markerRef, marker] = useAdvancedMarkerRef()

  useEffect(() => {
    if (selectedPlace) {
      setPlaceState(selectedPlace)
    }
  }, [selectedPlace])

  return (<div className="group flex flex-col items-middle w-full h-[400px] border-8 border-gray-100 rounded-md bg-white">
    <APIProvider
      apiKey={API_KEY}
      solutionChannel="GMP_devsite_samples_v3_rgmautocomplete"
    >
      <Map
        mapId={'3804f2650701a7e9'}
        defaultZoom={10}
        defaultCenter={{ lat: 45.385918147952474, lng: -75.74656436136979 }}
        gestureHandling={'greedy'}
        disableDefaultUI={true}
      >
        <AdvancedMarker ref={markerRef} position={null} />
      </Map>
      <MapControl position={ControlPosition.TOP}>
        <div className="mt-6 bg-white border-2 border-gray-700 rounded-sm">
          <PlaceAutocomplete onPlaceSelect={setSelectedPlace} />
        </div>
      </MapControl>
      <MapHandler place={selectedPlace} marker={marker} />
    </APIProvider>
  </div>)
}

interface MapHandlerProps {
  place: google.maps.places.PlaceResult | null
  marker: google.maps.marker.AdvancedMarkerElement | null
}

const MapHandler = ({ place, marker }: MapHandlerProps) => {
  const map = useMap()

  useEffect(() => {
    if (!map || !place || !marker) return

    if (place.geometry?.viewport) {
      map.fitBounds(place.geometry?.viewport)
    }
    marker.position = place.geometry?.location
  }, [map, place, marker])

  return null
}

interface PlaceAutocompleteProps {
  onPlaceSelect: (place: google.maps.places.PlaceResult | null) => void
}

const PlaceAutocomplete = ({ onPlaceSelect }: PlaceAutocompleteProps) => {
  const [placeAutocomplete, setPlaceAutocomplete] =
    useState<google.maps.places.Autocomplete | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const places = useMapsLibrary('places')

  useEffect(() => {
    if (!places || !inputRef.current) return

    const options = {
      fields: ['geometry', 'name', 'formatted_address']
    }

    setPlaceAutocomplete(new places.Autocomplete(inputRef.current, options))
  }, [places])

  useEffect(() => {
    if (!placeAutocomplete) return

    placeAutocomplete.addListener('place_changed', () => {
      onPlaceSelect(placeAutocomplete.getPlace())
    })
  }, [onPlaceSelect, placeAutocomplete])

  return (
    <div>
      <input ref={inputRef} className="w-32 " />
    </div>
  )
}
