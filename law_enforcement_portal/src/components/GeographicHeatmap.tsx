'use client';

import React from 'react';
import { MapPin, AlertTriangle, Phone, TrendingUp } from 'lucide-react';

// Mock geographic data
const GEOGRAPHIC_DATA = [
  { city: 'Mumbai', state: 'Maharashtra', lat: 19.0760, lng: 72.8777, incidents: 456, threatLevel: 'critical' },
  { city: 'Delhi', state: 'Delhi NCR', lat: 28.6139, lng: 77.2090, incidents: 389, threatLevel: 'high' },
  { city: 'Bangalore', state: 'Karnataka', lat: 12.9716, lng: 77.5946, incidents: 234, threatLevel: 'high' },
  { city: 'Chennai', state: 'Tamil Nadu', lat: 13.0827, lng: 80.2707, incidents: 187, threatLevel: 'medium' },
  { city: 'Kolkata', state: 'West Bengal', lat: 22.5726, lng: 88.3639, incidents: 156, threatLevel: 'medium' },
  { city: 'Hyderabad', state: 'Telangana', lat: 17.3850, lng: 78.4867, incidents: 198, threatLevel: 'high' },
  { city: 'Pune', state: 'Maharashtra', lat: 18.5204, lng: 73.8567, incidents: 145, threatLevel: 'medium' },
  { city: 'Ahmedabad', state: 'Gujarat', lat: 23.0225, lng: 72.5714, incidents: 123, threatLevel: 'medium' },
];

const getThreatColor = (level: string) => {
  switch (level) {
    case 'critical': return 'text-red-600 bg-red-100';
    case 'high': return 'text-orange-600 bg-orange-100';
    case 'medium': return 'text-yellow-600 bg-yellow-100';
    default: return 'text-green-600 bg-green-100';
  }
};

export default function GeographicHeatmap() {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <MapPin className="w-6 h-6 text-indigo-600" />
            <h3 className="text-lg font-semibold text-gray-900">Geographic Distribution</h3>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <span className="text-sm text-gray-600">Critical</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-orange-500"></div>
              <span className="text-sm text-gray-600">High</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <span className="text-sm text-gray-600">Medium</span>
            </div>
          </div>
        </div>

        {/* Map Placeholder */}
        <div className="relative h-96 bg-gray-100 rounded-lg overflow-hidden">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <MapPin className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">Interactive Map View</p>
              <p className="text-sm text-gray-400">Mapbox integration required</p>
            </div>
          </div>
          
          {/* Mock map markers */}
          {GEOGRAPHIC_DATA.slice(0, 4).map((city, idx) => (
            <div
              key={city.city}
              className="absolute"
              style={{
                left: `${20 + idx * 20}%`,
                top: `${30 + (idx % 2) * 30}%`,
              }}
            >
              <div className={`relative group cursor-pointer`}>
                <div className={`w-4 h-4 rounded-full ${getThreatColor(city.threatLevel)} animate-pulse`}></div>
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block z-10">
                  <div className="bg-gray-900 text-white text-xs rounded-lg py-2 px-3 whitespace-nowrap">
                    <p className="font-semibold">{city.city}</p>
                    <p>{city.incidents} incidents</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Hotspots Table */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">Top Hotspots</h3>
            <AlertTriangle className="w-5 h-5 text-orange-500" />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  City
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  State
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Incidents
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Threat Level
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Trend
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {GEOGRAPHIC_DATA.sort((a, b) => b.incidents - a.incidents).map((city) => (
                <tr key={city.city} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <MapPin className="w-4 h-4 text-gray-400 mr-2" />
                      <span className="text-sm font-medium text-gray-900">{city.city}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {city.state}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <Phone className="w-4 h-4 text-gray-400 mr-2" />
                      <span className="text-sm text-gray-900">{city.incidents}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getThreatColor(city.threatLevel)}`}>
                      {city.threatLevel.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center text-green-600">
                      <TrendingUp className="w-4 h-4 mr-1" />
                      <span className="text-sm">+12%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
