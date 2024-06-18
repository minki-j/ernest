import React, { useState, useEffect, useRef } from 'react';
import { createRoot } from 'react-dom/client';
import {
  APIProvider,
  ControlPosition,
  MapControl,
  AdvancedMarker,
  Map,
  useMap,
  useMapsLibrary,
  useAdvancedMarkerRef,
  AdvancedMarkerRef,
} from '@vis.gl/react-google-maps';

const API_KEY =
  process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY ||
  process.env['GOOGLE_MAPS_API_KEY'] ||
  '';

if (!API_KEY) {
  throw new Error('No GOOGLE_MAPS_API_KEY provided')
}

interface GoogleMapPickerProps {
  setPlaceState: (place: google.maps.places.PlaceResult) => void;
}

export const GoogleMapPicker: React.FC<GoogleMapPickerProps> = ({ setPlaceState }) => {
  const [selectedPlace, setSelectedPlace] = useState<google.maps.places.PlaceResult | null>(null);
  const [markerRef, marker] = useAdvancedMarkerRef();

  useEffect(() => {
    if (selectedPlace) {
      setPlaceState(selectedPlace);
    }
  }, [selectedPlace, setPlaceState]);

  return (
    <div className="group flex flex-col items-middle w-full h-[400px] border-8 border-gray-100 rounded-md bg-white">
      <APIProvider apiKey={API_KEY} solutionChannel="GMP_devsite_samples_v3_rgmautocomplete">
        <Map
          mapId={'3804f2650701a7e9'}
          defaultZoom={10}
          defaultCenter={{ lat: 45.385918147952474, lng: -75.74656436136979 }}
          gestureHandling={'greedy'}
          disableDefaultUI={true}
          onClick={(e) => handleMapClick(e, setSelectedPlace)}
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
    </div>
  );
};

// interface MapClickEvent {
//   detail: {
//     latLng: google.maps.LatLng
//     placeId: string
//   }
// }

const handleMapClick = (
  e: any,
  setSelectedPlace: React.Dispatch<
    React.SetStateAction<google.maps.places.PlaceResult | null>
  >
) => {
  const latLng = e.detail.latLng
  const placeId = e.detail.placeId
  if (!latLng || !placeId) return

  const placesService = new google.maps.places.PlacesService(
    document.createElement('div')
  )

  placesService.getDetails({ placeId }, (placeDetails, statusDetails) => {
    if (
      statusDetails === google.maps.places.PlacesServiceStatus.OK &&
      placeDetails
    ) {
      const place = {
        geometry: {
          location: placeDetails.geometry?.location,
          viewport: placeDetails.geometry?.viewport
        },
        formatted_address: placeDetails.formatted_address,
        name: placeDetails.name
      }
      setSelectedPlace(place)
    } else {
      console.error('Place details request failed: ' + statusDetails)
    }
  })
}

interface MapHandlerProps {
  place: google.maps.places.PlaceResult | null;
  marker: google.maps.marker.AdvancedMarkerElement | null;
}

const MapHandler: React.FC<MapHandlerProps> = ({ place, marker }) => {
  const map = useMap();

  useEffect(() => {
    if (!map || !place || !marker) return;

    if (place.geometry?.viewport) {
      map.fitBounds(place.geometry.viewport);
    } else {
      map.setCenter(place.geometry?.location!);
      map.setZoom(14); // Adjust the zoom level as needed
    }

    marker.position = place.geometry?.location!;
  }, [map, place, marker]);

  return null;
};

interface PlaceAutocompleteProps {
  onPlaceSelect: (place: google.maps.places.PlaceResult | null) => void;
}

const PlaceAutocomplete: React.FC<PlaceAutocompleteProps> = ({ onPlaceSelect }) => {
  const [placeAutocomplete, setPlaceAutocomplete] = useState<google.maps.places.Autocomplete | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const places = useMapsLibrary('places');

  useEffect(() => {
    if (!places || !inputRef.current) return;

    const options = {
      fields: ['geometry', 'name', 'formatted_address'],
    };

    const autocomplete = new places.Autocomplete(inputRef.current, options);
    setPlaceAutocomplete(autocomplete);
  }, [places]);

  useEffect(() => {
    if (!placeAutocomplete) return;

    placeAutocomplete.addListener('place_changed', () => {
      onPlaceSelect(placeAutocomplete.getPlace());
    });
  }, [onPlaceSelect, placeAutocomplete]);

  return (
    <div>
      <input ref={inputRef} className="w-32 p-2 border rounded" placeholder="Enter a place" />
    </div>
  );
};
