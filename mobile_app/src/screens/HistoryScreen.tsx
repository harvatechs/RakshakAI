/**
 * RakshakAI - History Screen
 * Displays call history and past threat detections
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

// Mock data for demonstration
const MOCK_CALL_HISTORY = [
  {
    id: '1',
    phoneNumber: '+91 98765 43210',
    timestamp: '2024-01-15T14:30:00Z',
    duration: 180,
    threatLevel: 'high',
    threatScore: 0.87,
    wasScam: true,
    aiEngaged: true,
    status: 'blocked',
  },
  {
    id: '2',
    phoneNumber: '+91 87654 32109',
    timestamp: '2024-01-14T09:15:00Z',
    duration: 45,
    threatLevel: 'medium',
    threatScore: 0.45,
    wasScam: false,
    aiEngaged: false,
    status: 'safe',
  },
  {
    id: '3',
    phoneNumber: '+91 76543 21098',
    timestamp: '2024-01-13T16:45:00Z',
    duration: 320,
    threatLevel: 'critical',
    threatScore: 0.95,
    wasScam: true,
    aiEngaged: true,
    status: 'reported',
  },
];

interface CallHistoryItem {
  id: string;
  phoneNumber: string;
  timestamp: string;
  duration: number;
  threatLevel: string;
  threatScore: number;
  wasScam: boolean;
  aiEngaged: boolean;
  status: string;
}

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

const getStatusIcon = (status: string): keyof typeof Ionicons.glyphMap => {
  switch (status) {
    case 'blocked': return 'shield-checkmark';
    case 'reported': return 'checkmark-circle';
    case 'safe': return 'checkmark';
    default: return 'help-circle';
  }
};

const formatDuration = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs}s`;
};

const formatDate = (timestamp: string): string => {
  const date = new Date(timestamp);
  return date.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
};

const formatTime = (timestamp: string): string => {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
  });
};

const HistoryItem: React.FC<{ item: CallHistoryItem }> = ({ item }) => (
  <TouchableOpacity style={styles.historyItem}>
    <View style={styles.itemHeader}>
      <View style={styles.phoneInfo}>
        <Ionicons name="call" size={16} color="#666" />
        <Text style={styles.phoneNumber}>{item.phoneNumber}</Text>
      </View>
      <View style={[styles.threatBadge, { backgroundColor: getThreatColor(item.threatLevel) }]}>
        <Text style={styles.threatText}>
          {Math.round(item.threatScore * 100)}%
        </Text>
      </View>
    </View>
    
    <View style={styles.itemDetails}>
      <View style={styles.detailRow}>
        <Ionicons name="time-outline" size={14} color="#999" />
        <Text style={styles.detailText}>
          {formatDate(item.timestamp)} at {formatTime(item.timestamp)}
        </Text>
      </View>
      
      <View style={styles.detailRow}>
        <Ionicons name="hourglass-outline" size={14} color="#999" />
        <Text style={styles.detailText}>Duration: {formatDuration(item.duration)}</Text>
      </View>
    </View>
    
    <View style={styles.itemFooter}>
      {item.aiEngaged && (
        <View style={styles.badge}>
          <Ionicons name="bot" size={12} color="#7b1fa2" />
          <Text style={[styles.badgeText, { color: '#7b1fa2' }]}>AI Engaged</Text>
        </View>
      )}
      
      {item.wasScam && (
        <View style={[styles.badge, { backgroundColor: '#ffebee' }]}>
          <Ionicons name="warning" size={12} color="#c62828" />
          <Text style={[styles.badgeText, { color: '#c62828' }]}>Scam Confirmed</Text>
        </View>
      )}
      
      <View style={[styles.statusBadge, { backgroundColor: getThreatColor(item.status === 'safe' ? 'safe' : 'critical') + '20' }]}>
        <Ionicons 
          name={getStatusIcon(item.status)} 
          size={14} 
          color={getThreatColor(item.status === 'safe' ? 'safe' : 'critical')} 
        />
        <Text style={[
          styles.statusText, 
          { color: getThreatColor(item.status === 'safe' ? 'safe' : 'critical') }
        ]}>
          {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
        </Text>
      </View>
    </View>
  </TouchableOpacity>
);

export default function HistoryScreen() {
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Call History</Text>
        <Text style={styles.headerSubtitle}>
          {MOCK_CALL_HISTORY.length} calls monitored
        </Text>
      </View>
      
      <FlatList
        data={MOCK_CALL_HISTORY}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <HistoryItem item={item} />}
        contentContainerStyle={styles.listContainer}
        showsVerticalScrollIndicator={false}
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
  historyItem: {
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
    alignItems: 'center',
    marginBottom: 12,
  },
  phoneInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  phoneNumber: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginLeft: 8,
  },
  threatBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  threatText: {
    color: '#fff',
    fontSize: 12,
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
  itemFooter: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f3e5f5',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
    marginRight: 8,
    marginBottom: 4,
  },
  badgeText: {
    fontSize: 11,
    fontWeight: '600',
    marginLeft: 4,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
    marginBottom: 4,
  },
  statusText: {
    fontSize: 11,
    fontWeight: '600',
    marginLeft: 4,
  },
});
