'use client';

import React, { useState } from 'react';
import {
  Search,
  Filter,
  Phone,
  Wallet,
  CreditCard,
  Mail,
  User,
  MapPin,
  Calendar,
  AlertTriangle,
  ExternalLink,
  Database
} from 'lucide-react';

// Mock search results
const MOCK_SEARCH_RESULTS = [
  {
    id: 'SCAM-001',
    type: 'scammer_profile',
    title: 'Scammer Profile: SCAM-001',
    description: 'Linked to 45+ calls, UPI fraud network',
    phoneNumbers: ['+91 98765 43210', '+91 99999 88888'],
    upiIds: ['scammer@paytm', 'fraud@okaxis'],
    riskLevel: 'critical',
    lastSeen: '2024-01-15T14:30:00Z',
  },
  {
    id: 'call_001',
    type: 'call_record',
    title: 'Call Record: call_001',
    description: 'KYC fraud attempt, AI engaged for 12 minutes',
    phoneNumber: '+91 98765 43210',
    threatLevel: 'high',
    timestamp: '2024-01-15T14:30:00Z',
  },
  {
    id: 'RAK-1705312800-a1b2c3d4',
    type: 'evidence_package',
    title: 'Evidence Package: RAK-1705312800',
    description: '2 entities extracted, submitted to authorities',
    caseId: 'CC/2024/001234',
    threatLevel: 'high',
    timestamp: '2024-01-15T14:35:00Z',
  },
];

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'scammer_profile': return User;
    case 'call_record': return Phone;
    case 'evidence_package': return Database;
    default: return Search;
  }
};

const getThreatColor = (level: string) => {
  switch (level) {
    case 'safe': return 'bg-green-100 text-green-800';
    case 'low': return 'bg-green-100 text-green-800';
    case 'medium': return 'bg-yellow-100 text-yellow-800';
    case 'high': return 'bg-orange-100 text-orange-800';
    case 'critical': return 'bg-red-100 text-red-800';
    default: return 'bg-gray-100 text-gray-800';
  }
};

export default function SearchPanel() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState('all');
  const [dateRange, setDateRange] = useState('all');
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = () => {
    setHasSearched(true);
    // In production, this would call the API
  };

  return (
    <div className="space-y-6">
      {/* Search Form */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Search className="w-6 h-6 text-indigo-600" />
          <h3 className="text-lg font-semibold text-gray-900">Advanced Search</h3>
        </div>

        <div className="space-y-4">
          {/* Search Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Query
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Enter phone number, UPI ID, case ID, or keyword..."
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Entity Type
              </label>
              <select
                value={searchType}
                onChange={(e) => setSearchType(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              >
                <option value="all">All Types</option>
                <option value="phone_number">Phone Number</option>
                <option value="upi_id">UPI ID</option>
                <option value="bank_account">Bank Account</option>
                <option value="scammer_profile">Scammer Profile</option>
                <option value="call_record">Call Record</option>
                <option value="evidence_package">Evidence Package</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Date Range
              </label>
              <select
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              >
                <option value="all">All Time</option>
                <option value="today">Today</option>
                <option value="week">Last 7 Days</option>
                <option value="month">Last 30 Days</option>
                <option value="quarter">Last 3 Months</option>
              </select>
            </div>
          </div>

          {/* Quick Filters */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quick Filters
            </label>
            <div className="flex flex-wrap gap-2">
              <button className="flex items-center px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors">
                <Phone className="w-3 h-3 mr-1" />
                Phone Numbers
              </button>
              <button className="flex items-center px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors">
                <Wallet className="w-3 h-3 mr-1" />
                UPI IDs
              </button>
              <button className="flex items-center px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors">
                <CreditCard className="w-3 h-3 mr-1" />
                Bank Accounts
              </button>
              <button className="flex items-center px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors">
                <Mail className="w-3 h-3 mr-1" />
                Emails
              </button>
              <button className="flex items-center px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors">
                <AlertTriangle className="w-3 h-3 mr-1" />
                High Risk Only
              </button>
            </div>
          </div>

          {/* Search Button */}
          <button
            onClick={handleSearch}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-3 rounded-lg transition-colors"
          >
            Search
          </button>
        </div>
      </div>

      {/* Search Results */}
      {hasSearched && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">
                Search Results
              </h3>
              <span className="text-sm text-gray-500">
                {MOCK_SEARCH_RESULTS.length} results found
              </span>
            </div>
          </div>

          <div className="divide-y divide-gray-200">
            {MOCK_SEARCH_RESULTS.map((result) => {
              const Icon = getTypeIcon(result.type);
              return (
                <div
                  key={result.id}
                  className="p-6 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <Icon className="w-5 h-5 text-indigo-600" />
                        <span className="text-sm font-medium text-gray-900">
                          {result.title}
                        </span>
                        {'riskLevel' in result && (
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getThreatColor(result.riskLevel)}`}>
                            {result.riskLevel.toUpperCase()}
                          </span>
                        )}
                      </div>

                      <p className="text-sm text-gray-600 mb-3">
                        {result.description}
                      </p>

                      {/* Type-specific details */}
                      {result.type === 'scammer_profile' && (
                        <div className="space-y-2">
                          <div className="flex items-center text-sm">
                            <Phone className="w-4 h-4 text-gray-400 mr-2" />
                            <span className="text-gray-600">
                              {result.phoneNumbers?.join(', ')}
                            </span>
                          </div>
                          <div className="flex items-center text-sm">
                            <Wallet className="w-4 h-4 text-gray-400 mr-2" />
                            <span className="text-gray-600">
                              {result.upiIds?.join(', ')}
                            </span>
                          </div>
                        </div>
                      )}

                      {result.type === 'call_record' && (
                        <div className="flex items-center text-sm">
                          <Phone className="w-4 h-4 text-gray-400 mr-2" />
                          <span className="text-gray-600">{result.phoneNumber}</span>
                          <span className="mx-2">•</span>
                          <Calendar className="w-4 h-4 text-gray-400 mr-1" />
                          <span className="text-gray-600">
                            {new Date(result.timestamp).toLocaleString('en-IN')}
                          </span>
                        </div>
                      )}

                      {result.type === 'evidence_package' && (
                        <div className="flex items-center text-sm">
                          <Database className="w-4 h-4 text-gray-400 mr-2" />
                          <span className="text-gray-600">Case: {result.caseId}</span>
                          <span className="mx-2">•</span>
                          <Calendar className="w-4 h-4 text-gray-400 mr-1" />
                          <span className="text-gray-600">
                            {new Date(result.timestamp).toLocaleString('en-IN')}
                          </span>
                        </div>
                      )}
                    </div>

                    <button className="p-2 rounded-lg hover:bg-gray-200 transition-colors">
                      <ExternalLink className="w-4 h-4 text-gray-600" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
