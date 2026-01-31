/**
 * RakshakAI - Home Screen
 * Main dashboard showing protection status and quick actions
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useSelector } from 'react-redux';
import { RootState } from '../store/store';

// Components
import ThreatMeter from '../components/ThreatMeter';
import AlertOverlay from '../components/AlertOverlay';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: keyof typeof Ionicons.glyphMap;
  color: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color }) => (
  <View style={[styles.statCard, { borderLeftColor: color }]}>
    <Ionicons name={icon} size={24} color={color} />
    <Text style={styles.statValue}>{value}</Text>
    <Text style={styles.statTitle}>{title}</Text>
  </View>
);

export default function HomeScreen() {
  // Get state from Redux store
  const { isMonitoring, threatLevel, lastThreatScore } = useSelector(
    (state: RootState) => state.call
  );
  const { stats } = useSelector((state: RootState) => state.user);

  // Determine protection status
  const getProtectionStatus = () => {
    if (!isMonitoring) return { text: 'Not Active', color: '#9e9e9e', icon: 'shield-outline' };
    if (threatLevel === 'critical') return { text: 'Critical Threat!', color: '#d32f2f', icon: 'warning' };
    if (threatLevel === 'high') return { text: 'High Risk', color: '#f57c00', icon: 'alert' };
    if (threatLevel === 'medium') return { text: 'Monitoring', color: '#fbc02d', icon: 'shield-half' };
    return { text: 'Protected', color: '#388e3c', icon: 'shield-checkmark' };
  };

  const protectionStatus = getProtectionStatus();

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        {/* Protection Status Card */}
        <View style={styles.statusCard}>
          <View style={[styles.shieldContainer, { backgroundColor: protectionStatus.color + '20' }]}>
            <Ionicons 
              name={protectionStatus.icon as any} 
              size={64} 
              color={protectionStatus.color} 
            />
          </View>
          <Text style={[styles.statusText, { color: protectionStatus.color }]}>
            {protectionStatus.text}
          </Text>
          <Text style={styles.statusSubtext}>
            {isMonitoring 
              ? 'Real-time monitoring is active' 
              : 'Tap below to start protection'}
          </Text>
        </View>

        {/* Threat Meter */}
        {isMonitoring && (
          <View style={styles.threatMeterContainer}>
            <ThreatMeter score={lastThreatScore} level={threatLevel} />
          </View>
        )}

        {/* Quick Stats */}
        <View style={styles.statsContainer}>
          <Text style={styles.sectionTitle}>Protection Statistics</Text>
          <View style={styles.statsGrid}>
            <StatCard
              title="Calls Monitored"
              value={stats?.totalCalls || 0}
              icon="call-outline"
              color="#1a237e"
            />
            <StatCard
              title="Threats Blocked"
              value={stats?.threatsBlocked || 0}
              icon="shield-checkmark-outline"
              color="#388e3c"
            />
            <StatCard
              title="AI Engagements"
              value={stats?.aiEngagements || 0}
              icon="chatbubble-ellipses-outline"
              color="#f57c00"
            />
            <StatCard
              title="Intelligence"
              value={stats?.intelligenceExtracted || 0}
              icon="document-text-outline"
              color="#7b1fa2"
            />
          </View>
        </View>

        {/* Quick Actions */}
        <View style={styles.actionsContainer}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          
          <TouchableOpacity style={styles.actionButton}>
            <Ionicons name="call-outline" size={24} color="#1a237e" />
            <View style={styles.actionTextContainer}>
              <Text style={styles.actionTitle}>Simulate Test Call</Text>
              <Text style={styles.actionSubtitle}>Test the scam detection system</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color="#9e9e9e" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionButton}>
            <Ionicons name="school-outline" size={24} color="#1a237e" />
            <View style={styles.actionTextContainer}>
              <Text style={styles.actionTitle}>Scam Education</Text>
              <Text style={styles.actionSubtitle}>Learn about common scam tactics</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color="#9e9e9e" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionButton}>
            <Ionicons name="share-social-outline" size={24} color="#1a237e" />
            <View style={styles.actionTextContainer}>
              <Text style={styles.actionTitle}>Share with Family</Text>
              <Text style={styles.actionSubtitle}>Protect your loved ones</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color="#9e9e9e" />
          </TouchableOpacity>
        </View>

        {/* Recent Activity */}
        <View style={styles.activityContainer}>
          <Text style={styles.sectionTitle}>Recent Activity</Text>
          <View style={styles.emptyActivity}>
            <Ionicons name="time-outline" size={48} color="#9e9e9e" />
            <Text style={styles.emptyText}>No recent calls monitored</Text>
            <Text style={styles.emptySubtext}>
              RakshakAI will automatically monitor incoming calls
            </Text>
          </View>
        </View>
      </ScrollView>

      {/* Alert Overlay - Shows when threat detected */}
      <AlertOverlay />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollView: {
    flex: 1,
  },
  statusCard: {
    backgroundColor: '#fff',
    margin: 16,
    padding: 24,
    borderRadius: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  shieldContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  statusText: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  statusSubtext: {
    fontSize: 14,
    color: '#666',
  },
  threatMeterContainer: {
    marginHorizontal: 16,
    marginBottom: 16,
  },
  statsContainer: {
    marginHorizontal: 16,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
    color: '#333',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statCard: {
    backgroundColor: '#fff',
    width: '48%',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    marginVertical: 8,
    color: '#333',
  },
  statTitle: {
    fontSize: 12,
    color: '#666',
  },
  actionsContainer: {
    marginHorizontal: 16,
    marginBottom: 16,
  },
  actionButton: {
    backgroundColor: '#fff',
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  actionTextContainer: {
    flex: 1,
    marginLeft: 12,
  },
  actionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  actionSubtitle: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  activityContainer: {
    marginHorizontal: 16,
    marginBottom: 24,
  },
  emptyActivity: {
    backgroundColor: '#fff',
    padding: 32,
    borderRadius: 12,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#666',
    marginTop: 12,
  },
  emptySubtext: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
    textAlign: 'center',
  },
});
