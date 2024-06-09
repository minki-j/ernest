import React, { useState, useRef } from 'react'
import ReactDOM from 'react-dom/client'
import {
  AdvancedMarker,
  Map,
  Pin,
  APIProvider
} from '@vis.gl/react-google-maps'
import {
  PlaceReviews,
  PlaceDataProvider,
  PlaceDirectionsButton,
  IconButton,
  PlaceOverview,
  SplitLayout,
  OverlayLayout,
  PlacePicker
} from '@googlemaps/extended-component-library/react'

import { OverlayLayout as TOverlayLayout } from '@googlemaps/extended-component-library/overlay_layout.js'
import { PlacePicker as TPlacePicker } from '@googlemaps/extended-component-library/place_picker.js'

const API_KEY = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY
  ? process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY
  : ''


const DEFAULT_CENTER = { lat: 38, lng: -98 }
const DEFAULT_ZOOM = 4
const DEFAULT_ZOOM_WITH_LOCATION = 16

export const VendorPicker = () => {
  console.log('VendorPicker rendered');
  
  const overlayLayoutRef = useRef<TOverlayLayout>(null)
  const pickerRef = useRef<TPlacePicker>(null)
  const [college, setCollege] = useState<google.maps.places.Place | undefined>(
    undefined
  )

  return (
    <div className="group relative flex items-middle md:-ml-12 w-80vw h-30">
      <APIProvider
        solutionChannel="GMP_devsite_samples_v3_rgmcollegepicker"
        apiKey={API_KEY}
        version="beta"
      >
        <Map
          id="gmap"
          mapId="8c732c82e4ec29d9"
          center={college?.location ?? DEFAULT_CENTER}
          zoom={college?.location ? DEFAULT_ZOOM_WITH_LOCATION : DEFAULT_ZOOM}
          gestureHandling="none"
          fullscreenControl={false}
          zoomControl={false}
        ></Map>
        {/* <SplitLayout rowReverse rowLayoutMinWidth={100}>
          <p> SplitLayout </p>
          <div className="SlotDiv" slot="fixed">
            <OverlayLayout ref={overlayLayoutRef}>
              <div className="SlotDiv" slot="main">
                <PlacePicker
                  className="CollegePicker"
                  ref={pickerRef}
                  forMap="gmap"
                  country={['us', 'ca']}
                  type="university"
                  placeholder="Enter a college in the US or Canada"
                  onPlaceChange={() => {
                    if (!pickerRef.current?.value) {
                      setCollege(undefined)
                    } else {
                      setCollege(pickerRef.current?.value)
                    }
                  }}
                />
                <PlaceOverview
                  size="large"
                  place={college}
                  googleLogoAlreadyDisplayed
                >
                  <div slot="action" className="SlotDiv">
                    <IconButton
                      slot="action"
                      variant="filled"
                      onClick={() => overlayLayoutRef.current?.showOverlay()}
                    >
                      See Reviews
                    </IconButton>
                  </div>
                  <div slot="action" className="SlotDiv">
                    <PlaceDirectionsButton slot="action" variant="filled">
                      Directions
                    </PlaceDirectionsButton>
                  </div>
                </PlaceOverview>
              </div>
              <div slot="overlay" className="SlotDiv">
                <IconButton
                  className="CloseButton"
                  onClick={() => overlayLayoutRef.current?.hideOverlay()}
                >
                  Close
                </IconButton>
                <PlaceDataProvider place={college}>
                  <PlaceReviews />
                </PlaceDataProvider>
              </div>
            </OverlayLayout>
          </div>
          <div className="SplitLayoutContainer" slot="main">
            <Map
              id="gmap"
              mapId="8c732c82e4ec29d9"
              center={college?.location ?? DEFAULT_CENTER}
              zoom={
                college?.location ? DEFAULT_ZOOM_WITH_LOCATION : DEFAULT_ZOOM
              }
              gestureHandling="none"
              fullscreenControl={false}
              zoomControl={false}
            >
              {college?.location && (
                <AdvancedMarker position={college?.location}>
                  <Pin
                    background={'#FBBC04'}
                    glyphColor={'#000'}
                    borderColor={'#000'}
                  />
                </AdvancedMarker>
              )}
            </Map>
          </div>
        </SplitLayout> */}
      </APIProvider>
    </div>
  )
}