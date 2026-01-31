/**
 * RakshakAI - Report Screen
 * Displays evidence reports and law enforcement submissions
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

// Mock evidence reports
const MOCK_REPORTS = [
  {
    id: 'RAK-1705312800-a1b2c3d4',
    callId: 'call_001',
    phoneNumber: '+91 98765 43210',
    createdAt: '2024-01-15T14:30:00Z',
    threatLevel: 'high',
    entities: [
      { type: 'upi_id', value: 'scammer@paytm', confidence: 0.95 },
      { type: 'phone_number', value: '+91 99999 88888', confidence: 0.88 },
    ],
    status: 'submitted',
    caseId: 'CC/2024/001234',
  },
  {
    id: 'RAK-1705226400-e5f6g7h8',
    callId: 'call_002',
    phoneNumber: '+91 87654 32109',
    createdAt: '2024-01-14T10:30:00Z',
    threatLevel: 'critical',
    entities: [
      { type: 'upi_id', value: 'fraud@okaxis', confidence: 0.92 },
      { type: 'bank_account', value: 'XXXXXX1234', confidence: 0.85 },
      { type: 'ifsc_code', value: 'AXIS0000123', confidence: 0.90 },
    ],
    status: 'under_review',
    caseId: 'CC/2024/001235',
  },
];

interface EvidenceReport {
  id: string;
  callId: string;
  phoneNumber: string;
  createdAt: string;
  threatLevel: string;
  entities: Array<{
    type: string;
    value: string;
    confidence: number;
  }>;
  status: string;
  caseId: string;
}

const getStatusColor = (status: string): string => {
  switch (status) {
    case 'submitted': return '#2196f3';
    case 'under_review': return '#ff9800';
    case 'resolved': return '#4caf50';
    case 'rejected': return '#f44336';
    default: return '#9e9e9e';
  }
};

const getThreatColor = (level: string): string => {
  switch (level) {
    case 'safe': return '#4caf50';
    case 'low': return '#8bc34a';
    case 'medium': return '#ffc107';
    case 'high': return '#ff9800';
    case 'critical': return '#f44336';
    default: return '#9e9e9e';
  }
};

const formatDate = (timestamp: string): string => {
  const date = new Date(timestamp);
  return date.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
};

const ReportItem: React.FC<{ item: EvidenceReport }> = ({ item }) => (
  <TouchableOpacity style={styles.reportItem}>
    <View style={styles.itemHeader}>
      <View style={styles.packageInfo}>
        <Ionicons name="document-text" size={20} color="#1a237e" />
        <View style={styles.packageTextContainer}>
          <Text style={styles.packageId}>{item.id}</Text>
          <Text style={styles.caseId}>Case: {item.caseId}</Text>
        </View>
      </View>
      <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) + '20' }]}>
        <Text style={[styles.statusText, { color: getStatusColor(item.status) }]}>
          {item.status.replace('_', ' ').toUpperCase()}
        </Text>
      </View>
    </View>
    
    <View style={styles.itemDetails}>
      <View style={styles.detailRow}>
        <Ionicons name="call-outline" size={14} color="#999" />
        <Text style={styles.detailText}>{item.phoneNumber}</Text>
      </View>
      
      <View style={styles.detailRow}>
        <Ionicons name="calendar-outline" size={14} color="#999" />
        <Text style={styles.detailText}>{formatDate(item.createdAt)}</Text>
      </View>
      
      <View style={styles.detailRow}>
        <Ionicons name="warning-outline" size={14} color={getThreatColor(item.threatLevel)} />
        <Text style={[styles.detailText, { color: getThreatColor(item.threatLevel) }]}>
          Threat Level: {item.threatLevel.toUpperCase()}
        </Text>
      </View>
    </View>
    
    <View style={styles.entitiesContainer}>
      <Text style={styles.entitiesTitle}>Extracted Intelligence:</Text>
      <View style={styles.entitiesList}>
        {item.entities.map((entity, index) => (
          <View key={index} style={styles.entityTag}>
            <Ionicons 
              name={getEntityIcon(entity.type) as any} 
              size={12} 
              color="#7b1fa2" 
            />
            <Text style={styles.entityText}>
              {entity.type.replace('_', ' ').toUpperCase()}
            </Text>
            <Text style={styles.confidenceText}>
              {Math.round(entity.confidence * 100)}%
            </Text>
          </View>
        ))}
      </View>
    </View>
  </TouchableOpacity>
);

const getEntityIcon = (type: string): string => {
  switch (type) {
    case 'upi_id': return 'wallet';
    case 'phone_number': return 'call';
    case 'bank_account': return 'card';
    case 'ifsc_code': return 'business';
    case 'email': return 'mail';
    case 'aadhaar': return 'id-card';
    default: return 'document';
  }
};

export default function ReportScreen() {
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Evidence Reports</Text>
        <Text style={styles.headerSubtitle}>
          Submitted to law enforcement
        </Text>
      </View>
      
      <FlatList
        data={MOCK_REPORTS}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <ReportItem item={item} />}
        contentContainerStyle={styles.listContainer}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="document-text-outline" size={64} color="#ccc" />
            <Text style={styles.emptyText}>No reports yet</Text>
            <Text style={styles.emptySubtext}>
              Evidence packages will appear here when submitted to authorities
            </Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#1a237e',
    padding: 16,
    paddingTop: 8,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#fff',
    opacity: 0.8,
    marginTop: 4,
  },
  listContainer: {
    padding: 16,
  },
  reportItem: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  itemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  packageInfo: {
    flexDirection: 'row',
    flex: 1,
  },
  packageTextContainer: {
    marginLeft: 12,
    flex: 1,
  },
  packageId: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  caseId: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  statusText: {
    fontSize: 10,
    fontWeight: 'bold',
  },
  itemDetails: {
    marginBottom: 12,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  detailText: {
    fontSize: 12,
    color: '#666',
    marginLeft: 6,
  },
  entitiesContainer: {
    borderTopWidth: 1,
    borderTopColor: '#eee',
    paddingTop: 12,
  },
  entitiesTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
    marginBottom: 8,
  },
  entitiesList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  entityTag: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f3e5f5',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
    marginRight: 8,
    marginBottom: 4,
  },
  entityText: {
    fontSize: 10,
    fontWeight: '600',
    color: '#7b1fa2',
    marginLeft: 4,
  },
  confidenceText: {
    fontSize: 9,
    color: '#999',
    marginLeft: 4,
  },
  emptyContainer: {
    alignItems: 'center',
    padding: 48,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#666',
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#999',
    marginTop: 8,
    textAlign: 'center',
  },
});
