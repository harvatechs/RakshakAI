/**
 * RakshakAI - Threat Meter Component
 * Visual indicator of current threat level
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

interface ThreatMeterProps {
  score: number; // 0 to 1
  level: string; // 'safe', 'low', 'medium', 'high', 'critical'
}

export default function ThreatMeter({ score, level }: ThreatMeterProps) {
  // Get color based on threat level
  const getColors = (): [string, string] => {
    switch (level) {
      case 'safe':
        return ['#4caf50', '#81c784'];
      case 'low':
        return ['#8bc34a', '#aed581'];
      case 'medium':
        return ['#ffc107', '#ffd54f'];
      case 'high':
        return ['#ff9800', '#ffb74d'];
      case 'critical':
        return ['#f44336', '#e57373'];
      default:
        return ['#9e9e9e', '#bdbdbd'];
    }
  };

  // Get label text
  const getLabel = (): string => {
    switch (level) {
      case 'safe':
        return 'Safe';
      case 'low':
        return 'Low Risk';
      case 'medium':
        return 'Medium Risk';
      case 'high':
        return 'High Risk';
      case 'critical':
        return 'CRITICAL!';
      default:
        return 'Unknown';
    }
  };

  // Get description
  const getDescription = (): string => {
    switch (level) {
      case 'safe':
        return 'No suspicious activity detected';
      case 'low':
        return 'Minor anomalies detected';
      case 'medium':
        return 'Some suspicious patterns found';
      case 'high':
        return 'Likely scam - Stay alert!';
      case 'critical':
        return 'SCAM CONFIRMED - Take action!';
      default:
        return 'Analyzing...';
    }
  };

  const percentage = Math.round(score * 100);
  const colors = getColors();

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Threat Level</Text>
        <Text style={[styles.score, { color: colors[0] }]}>{percentage}%</Text>
      </View>

      {/* Progress Bar */}
      <View style={styles.meterContainer}>
        <LinearGradient
          colors={['#4caf50', '#ffc107', '#f44336']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
          style={styles.meterBackground}
        />
        <View 
          style={[
            styles.meterFill,
            { width: `${percentage}%` },
          ]} 
        />
        <View 
          style={[
            styles.indicator,
            { left: `${percentage}%`, backgroundColor: colors[0] },
          ]} 
        />
      </View>

      {/* Labels */}
      <View style={styles.labelsContainer}>
        <Text style={styles.label}>Safe</Text>
        <Text style={styles.label}>Critical</Text>
      </View>

      {/* Status Card */}
      <View style={[styles.statusCard, { borderLeftColor: colors[0] }]}>
        <Text style={[styles.statusLabel, { color: colors[0] }]}>
          {getLabel()}
        </Text>
        <Text style={styles.statusDescription}>
          {getDescription()}
        </Text>
      </View>

      {/* Indicators */}
      {level !== 'safe' && (
        <View style={styles.indicatorsContainer}>
          <Text style={styles.indicatorsTitle}>Detected Indicators:</Text>
          <View style={styles.indicatorsList}>
            {score > 0.3 && (
              <View style={styles.indicatorTag}>
                <Text style={styles.indicatorText}>Suspicious Keywords</Text>
              </View>
            )}
            {score > 0.5 && (
              <View style={styles.indicatorTag}>
                <Text style={styles.indicatorText}>Pressure Tactics</Text>
              </View>
            )}
            {score > 0.7 && (
              <View style={styles.indicatorTag}>
                <Text style={styles.indicatorText}>Financial Requests</Text>
              </View>
            )}
            {score > 0.85 && (
              <View style={styles.indicatorTag}>
                <Text style={styles.indicatorText}>Impersonation</Text>
              </View>
            )}
          </View>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  score: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  meterContainer: {
    height: 12,
    borderRadius: 6,
    overflow: 'hidden',
    position: 'relative',
  },
  meterBackground: {
    ...StyleSheet.absoluteFillObject,
  },
  meterFill: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
  },
  indicator: {
    position: 'absolute',
    width: 16,
    height: 16,
    borderRadius: 8,
    top: -2,
    marginLeft: -8,
    borderWidth: 2,
    borderColor: '#fff',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 2,
    elevation: 4,
  },
  labelsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 4,
  },
  label: {
    fontSize: 10,
    color: '#666',
  },
  statusCard: {
    marginTop: 16,
    padding: 12,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    borderLeftWidth: 4,
  },
  statusLabel: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  statusDescription: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  indicatorsContainer: {
    marginTop: 16,
  },
  indicatorsTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
    marginBottom: 8,
  },
  indicatorsList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  indicatorTag: {
    backgroundColor: '#ffebee',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 8,
    marginBottom: 8,
  },
  indicatorText: {
    fontSize: 11,
    color: '#c62828',
  },
});
