'use client';

import React, { useState } from 'react';
import {
  FileText,
  Download,
  Share2,
  CheckCircle,
  Clock,
  AlertTriangle,
  Shield,
  Hash,
  User,
  Calendar,
  Phone,
  Bot,
  Database
} from 'lucide-react';

// Mock evidence packages
const MOCK_EVIDENCE = [
  {
    id: 'RAK-1705312800-a1b2c3d4',
    callId: 'call_001',
    phoneNumber: '+91 98765 43210',
    createdAt: '2024-01-15T14:30:00Z',
    threatLevel: 'high',
    includesAudio: true,
    includesTranscript: true,
    includesIntelligence: true,
    audioHash: 'a1b2c3d4e5f6...',
    signatureHash: 'sha256:7g8h9i0j1k2...',
    caseId: 'CC/2024/001234',
    reportStatus: 'submitted',
    chainOfCustody: [
      { action: 'package_created', actor: 'rakshak_system', timestamp: '2024-01-15T14:35:00Z' },
      { action: 'submitted_to_authorities', actor: 'system', timestamp: '2024-01-15T14:40:00Z' },
    ],
    entities: [
      { type: 'upi_id', value: 'scammer@paytm', confidence: 0.95 },
      { type: 'phone_number', value: '+91 99999 88888', confidence: 0.88 },
    ],
  },
  {
    id: 'RAK-1705226400-e5f6g7h8',
    callId: 'call_002',
    phoneNumber: '+91 87654 32109',
    createdAt: '2024-01-14T10:30:00Z',
    threatLevel: 'critical',
    includesAudio: true,
    includesTranscript: true,
    includesIntelligence: true,
    audioHash: 'e5f6g7h8i9j0...',
    signatureHash: 'sha256:k1l2m3n4o5...',
    caseId: 'CC/2024/001235',
    reportStatus: 'under_review',
    chainOfCustody: [
      { action: 'package_created', actor: 'rakshak_system', timestamp: '2024-01-14T10:35:00Z' },
      { action: 'submitted_to_authorities', actor: 'system', timestamp: '2024-01-14T10:40:00Z' },
      { action: 'acknowledged', actor: 'cyber_crime_cell', timestamp: '2024-01-14T11:00:00Z' },
    ],
    entities: [
      { type: 'upi_id', value: 'fraud@okaxis', confidence: 0.92 },
      { type: 'bank_account', value: 'XXXXXX5678', confidence: 0.85 },
      { type: 'ifsc_code', value: 'AXIS0000123', confidence: 0.90 },
    ],
  },
];

const getStatusColor = (status: string) => {
  switch (status) {
    case 'submitted': return 'bg-blue-100 text-blue-800';
    case 'under_review': return 'bg-yellow-100 text-yellow-800';
    case 'acknowledged': return 'bg-green-100 text-green-800';
    case 'resolved': return 'bg-green-100 text-green-800';
    case 'rejected': return 'bg-red-100 text-red-800';
    default: return 'bg-gray-100 text-gray-800';
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

export default function EvidenceViewer() {
  const [selectedEvidence, setSelectedEvidence] = useState<string | null>(null);

  return (
    <div className="space-y-6">
      {/* Evidence List */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <FileText className="w-6 h-6 text-indigo-600" />
              <h3 className="text-lg font-semibold text-gray-900">Evidence Packages</h3>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">
                {MOCK_EVIDENCE.length} packages
              </span>
            </div>
          </div>
        </div>

        <div className="divide-y divide-gray-200">
          {MOCK_EVIDENCE.map((evidence) => (
            <div
              key={evidence.id}
              className={`p-6 cursor-pointer transition-colors ${
                selectedEvidence === evidence.id ? 'bg-indigo-50' : 'hover:bg-gray-50'
              }`}
              onClick={() => setSelectedEvidence(
                selectedEvidence === evidence.id ? null : evidence.id
              )}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <Shield className="w-5 h-5 text-indigo-600" />
                    <span className="text-sm font-mono text-gray-600">{evidence.id}</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getThreatColor(evidence.threatLevel)}`}>
                      {evidence.threatLevel.toUpperCase()}
                    </span>
                  </div>

                  <div className="flex items-center text-sm text-gray-600 mb-3">
                    <Phone className="w-4 h-4 mr-1" />
                    {evidence.phoneNumber}
                    <span className="mx-2">•</span>
                    <Calendar className="w-4 h-4 mr-1" />
                    {new Date(evidence.createdAt).toLocaleString('en-IN')}
                  </div>

                  <div className="flex items-center space-x-4 mb-3">
                    {evidence.includesAudio && (
                      <span className="flex items-center text-xs text-gray-500">
                        <Database className="w-3 h-3 mr-1" />
                        Audio
                      </span>
                    )}
                    {evidence.includesTranscript && (
                      <span className="flex items-center text-xs text-gray-500">
                        <FileText className="w-3 h-3 mr-1" />
                        Transcript
                      </span>
                    )}
                    {evidence.includesIntelligence && (
                      <span className="flex items-center text-xs text-gray-500">
                        <Bot className="w-3 h-3 mr-1" />
                        Intelligence
                      </span>
                    )}
                  </div>

                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(evidence.reportStatus)}`}>
                      {evidence.reportStatus.replace('_', ' ').toUpperCase()}
                    </span>
                    {evidence.caseId && (
                      <span className="text-xs text-indigo-600 font-medium">
                        Case: {evidence.caseId}
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <button className="p-2 rounded-lg hover:bg-gray-200 transition-colors">
                    <Download className="w-4 h-4 text-gray-600" />
                  </button>
                  <button className="p-2 rounded-lg hover:bg-gray-200 transition-colors">
                    <Share2 className="w-4 h-4 text-gray-600" />
                  </button>
                </div>
              </div>

              {/* Expanded Details */}
              {selectedEvidence === evidence.id && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Integrity Verification */}
                    <div>
                      <h4 className="text-sm font-semibold text-gray-900 mb-3">
                        Integrity Verification
                      </h4>
                      <div className="space-y-2">
                        <div className="flex items-center text-sm">
                          <Hash className="w-4 h-4 text-gray-400 mr-2" />
                          <span className="text-gray-600">Audio Hash:</span>
                          <span className="ml-2 font-mono text-gray-800">{evidence.audioHash}</span>
                        </div>
                        <div className="flex items-center text-sm">
                          <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                          <span className="text-gray-600">Signature:</span>
                          <span className="ml-2 font-mono text-gray-800">{evidence.signatureHash}</span>
                        </div>
                      </div>
                    </div>

                    {/* Chain of Custody */}
                    <div>
                      <h4 className="text-sm font-semibold text-gray-900 mb-3">
                        Chain of Custody
                      </h4>
                      <div className="space-y-2">
                        {evidence.chainOfCustody.map((entry, idx) => (
                          <div key={idx} className="flex items-center text-sm">
                            <Clock className="w-4 h-4 text-gray-400 mr-2" />
                            <span className="text-gray-600">{entry.action.replace('_', ' ')}</span>
                            <span className="mx-2">•</span>
                            <User className="w-3 h-3 text-gray-400 mr-1" />
                            <span className="text-gray-500">{entry.actor}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Extracted Entities */}
                  <div className="mt-6">
                    <h4 className="text-sm font-semibold text-gray-900 mb-3">
                      Extracted Entities
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {evidence.entities.map((entity, idx) => (
                        <div
                          key={idx}
                          className="flex items-center space-x-1 px-3 py-1 bg-gray-100 rounded-full text-xs"
                        >
                          <span className="font-medium uppercase">{entity.type.replace('_', ' ')}</span>
                          <span className="text-gray-500">{entity.value}</span>
                          <span className="text-gray-400">({Math.round(entity.confidence * 100)}%)</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
