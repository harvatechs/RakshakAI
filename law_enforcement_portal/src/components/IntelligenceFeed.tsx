'use client';

import React from 'react';
import {
  Database,
  Phone,
  Wallet,
  CreditCard,
  Mail,
  User,
  MapPin,
  FileText,
  AlertTriangle,
  CheckCircle,
  Clock,
  ExternalLink
} from 'lucide-react';

// Mock intelligence data
const MOCK_INTELLIGENCE = [
  {
    id: 'RAK-1705312800-a1b2c3d4',
    callId: 'call_001',
    phoneNumber: '+91 98765 43210',
    timestamp: '2024-01-15T14:30:00Z',
    threatLevel: 'high',
    entities: [
      { type: 'upi_id', value: 'scammer@paytm', confidence: 0.95, verified: true },
      { type: 'phone_number', value: '+91 99999 88888', confidence: 0.88, verified: false },
      { type: 'bank_account', value: 'XXXXXX1234', confidence: 0.82, verified: false },
    ],
    status: 'submitted',
    caseId: 'CC/2024/001234',
  },
  {
    id: 'RAK-1705226400-e5f6g7h8',
    callId: 'call_002',
    phoneNumber: '+91 87654 32109',
    timestamp: '2024-01-14T10:30:00Z',
    threatLevel: 'critical',
    entities: [
      { type: 'upi_id', value: 'fraud@okaxis', confidence: 0.92, verified: true },
      { type: 'bank_account', value: 'XXXXXX5678', confidence: 0.85, verified: true },
      { type: 'ifsc_code', value: 'AXIS0000123', confidence: 0.90, verified: true },
      { type: 'email', value: 'scam@fakebank.com', confidence: 0.78, verified: false },
    ],
    status: 'under_review',
    caseId: 'CC/2024/001235',
  },
  {
    id: 'RAK-1705140000-i9j0k1l2',
    callId: 'call_003',
    phoneNumber: '+91 76543 21098',
    timestamp: '2024-01-13T16:45:00Z',
    threatLevel: 'medium',
    entities: [
      { type: 'phone_number', value: '+91 88888 77777', confidence: 0.75, verified: false },
      { type: 'location', value: 'Mumbai, Maharashtra', confidence: 0.65, verified: false },
    ],
    status: 'pending',
    caseId: null,
  },
];

const getEntityIcon = (type: string) => {
  switch (type) {
    case 'upi_id': return Wallet;
    case 'phone_number': return Phone;
    case 'bank_account': return CreditCard;
    case 'ifsc_code': return FileText;
    case 'email': return Mail;
    case 'aadhaar': return User;
    case 'pan': return FileText;
    case 'location': return MapPin;
    default: return Database;
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

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'submitted': return CheckCircle;
    case 'under_review': return Clock;
    case 'pending': return AlertTriangle;
    default: return Database;
  }
};

interface IntelligenceFeedProps {
  fullWidth?: boolean;
}

export default function IntelligenceFeed({ fullWidth = false }: IntelligenceFeedProps) {
  return (
    <div className={`bg-white rounded-lg shadow ${fullWidth ? '' : ''}`}>
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Database className="w-6 h-6 text-indigo-600" />
            <h3 className="text-lg font-semibold text-gray-900">Intelligence Feed</h3>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">Live updates</span>
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          </div>
        </div>
      </div>

      <div className="divide-y divide-gray-200">
        {MOCK_INTELLIGENCE.map((item) => (
          <div key={item.id} className="p-6 hover:bg-gray-50 transition-colors">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <span className="text-sm font-mono text-gray-500">{item.id}</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getThreatColor(item.threatLevel)}`}>
                    {item.threatLevel.toUpperCase()}
                  </span>
                  {item.caseId && (
                    <span className="text-xs text-indigo-600 font-medium">
                      Case: {item.caseId}
                    </span>
                  )}
                </div>

                <div className="flex items-center text-sm text-gray-600 mb-3">
                  <Phone className="w-4 h-4 mr-1" />
                  {item.phoneNumber}
                  <span className="mx-2">•</span>
                  <Clock className="w-4 h-4 mr-1" />
                  {new Date(item.timestamp).toLocaleString('en-IN')}
                </div>

                <div className="flex flex-wrap gap-2">
                  {item.entities.map((entity, idx) => {
                    const Icon = getEntityIcon(entity.type);
                    return (
                      <div
                        key={idx}
                        className={`flex items-center space-x-1 px-3 py-1 rounded-full text-xs ${
                          entity.verified
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        <Icon className="w-3 h-3" />
                        <span className="font-medium uppercase">{entity.type.replace('_', ' ')}</span>
                        <span className="text-gray-500">{entity.value}</span>
                        <span className="text-gray-400">({Math.round(entity.confidence * 100)}%)</span>
                        {entity.verified && <CheckCircle className="w-3 h-3 text-green-600" />}
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="flex items-center space-x-2 ml-4">
                {React.createElement(getStatusIcon(item.status), {
                  className: `w-5 h-5 ${
                    item.status === 'submitted'
                      ? 'text-green-500'
                      : item.status === 'under_review'
                      ? 'text-yellow-500'
                      : 'text-gray-400'
                  }`,
                })}
                <button className="p-2 rounded-lg hover:bg-gray-200 transition-colors">
                  <ExternalLink className="w-4 h-4 text-gray-400" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="p-4 border-t border-gray-200 text-center">
        <button className="text-indigo-600 hover:text-indigo-800 text-sm font-medium">
          View All Intelligence →
        </button>
      </div>
    </div>
  );
}
