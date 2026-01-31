/**
 * RakshakAI - Call Monitor Screen
 * Real-time call monitoring with threat detection and AI handoff
 */

import React, { useEffect, useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
  ScrollView,
  SafeAreaView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useSelector, useDispatch } from 'react-redux';
import { RouteProp } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';

import { RootStackParamList } from '../App';
import { RootState } from '../store/store';
import { 
  updateThreatScore, 
  setCallStatus, 
  setAIHandoff,
  addTranscriptEntry 
} from '../store/callSlice';

import { WebSocketClient } from '../services/WebSocketClient';

type CallMonitorScreenNavigationProp = StackNavigationProp<RootStackParamList, 'CallMonitor'>;
type CallMonitorScreenRouteProp = RouteProp<RootStackParamList, 'CallMonitor'>;

interface Props {
  navigation: CallMonitorScreenNavigationProp;
  route: CallMonitorScreenRouteProp;
}

// Call Status Types
enum MonitorStatus {
  CONNECTING = 'connecting',
  MONITORING = 'monitoring',
  THREAT_DETECTED = 'threat_detected',
  AI_HANDOFF = 'ai_handoff',
  ENDED = 'ended',
}

export default function CallMonitorScreen({ navigation, route }: Props) {
  const { callId, phoneNumber } = route.params;
  const dispatch = useDispatch();
  
  // Local state
  const [status, setStatus] = useState<MonitorStatus>(MonitorStatus.CONNECTING);
  const [threatScore, setThreatScore] = useState(0);
  const [threatLevel, setThreatLevel] = useState<'safe' | 'low' | 'medium' | 'high' | 'critical'>('safe');
  const [transcript, setTranscript] = useState<string[]>([]);
  const [aiActive, setAiActive] = useState(false);
  const [callDuration, setCallDuration] = useState(0);
  const [intelligenceCount, setIntelligenceCount] = useState(0);
  
  // Animation refs
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const threatColorAnim = useRef(new Animated.Value(0)).current;
  
  // WebSocket ref
  const wsClient = useRef<WebSocketClient | null>(null);

  // Get state from Redux
  const { isAIHandoff } = useSelector((state: RootState) => state.call);

  // Start pulse animation
  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.2,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    ).start();
  }, []);

  // Connect WebSocket on mount
  useEffect(() => {
    connectWebSocket();
    
    // Start call duration timer
    const timer = setInterval(() => {
      setCallDuration(prev => prev + 1);
    }, 1000);
    
    return () => {
      clearInterval(timer);
      disconnectWebSocket();
    };
  }, []);

  // Update threat color animation
  useEffect(() => {
    let targetValue = 0;
    switch (threatLevel) {
      case 'safe': targetValue = 0; break;
      case 'low': targetValue = 0.25; break;
      case 'medium': targetValue = 0.5; break;
      case 'high': targetValue = 0.75; break;
      case 'critical': targetValue = 1; break;
    }
    
    Animated.timing(threatColorAnim, {
      toValue: targetValue,
      duration: 500,
      useNativeDriver: false,
    }).start();
  }, [threatLevel]);

  const connectWebSocket = async () => {
    try {
      wsClient.current = new WebSocketClient(callId);
      
      wsClient.current.onMessage((message) => {
        handleWebSocketMessage(message);
      });
      
      await wsClient.current.connect();
      setStatus(MonitorStatus.MONITORING);
      dispatch(setCallStatus('monitoring'));
    } catch (error) {
      console.error('WebSocket connection failed:', error);
    }
  };

  const disconnectWebSocket = () => {
    if (wsClient.current) {
      wsClient.current.disconnect();
      wsClient.current = null;
    }
  };

  const handleWebSocketMessage = (message: any) => {
    switch (message.type) {
      case 'threat_update':
        handleThreatUpdate(message.payload);
        break;
      case 'threat_alert':
        handleThreatAlert(message.payload);
        break;
      case 'ai_response':
        handleAIResponse(message.payload);
        break;
      case 'handoff_confirmed':
        handleHandoffConfirmed();
        break;
      case 'transcript':
        handleTranscriptUpdate(message.payload);
        break;
    }
  };

  const handleThreatUpdate = (payload: any) => {
    const { threat_score, threat_level, current_transcript } = payload;
    
    setThreatScore(threat_score);
    setThreatLevel(threat_level);
    dispatch(updateThreatScore(threat_score));
    
    if (current_transcript) {
      setTranscript(prev => [...prev, `Caller: ${current_transcript}`]);
    }
    
    // Update status based on threat level
    if (threat_level === 'high' || threat_level === 'critical') {
      setStatus(MonitorStatus.THREAT_DETECTED);
      dispatch(setCallStatus('threat_detected'));
    }
  };

  const handleThreatAlert = (payload: any) => {
    // Show high priority alert
    setStatus(MonitorStatus.THREAT_DETECTED);
    setThreatScore(payload.threat_score);
    setThreatLevel(payload.threat_level);
  };

  const handleAIResponse = (payload: any) => {
    if (payload.response_text) {
      setTranscript(prev => [...prev, `AI Agent: ${payload.response_text}`]);
    }
    if (payload.intelligence) {
      setIntelligenceCount(payload.intelligence.length);
    }
  };

  const handleHandoffConfirmed = () => {
    setAiActive(true);
    setStatus(MonitorStatus.AI_HANDOFF);
    dispatch(setAIHandoff(true));
  };

  const handleTranscriptUpdate = (payload: any) => {
    if (payload.text) {
      setTranscript(prev => [...prev, payload.text]);
    }
  };

  const handleHandoffToAI = async () => {
    if (wsClient.current) {
      wsClient.current.send({
        type: 'handoff_request',
        payload: {
          persona: 'confused_senior',
          extraction_enabled: true,
        },
      });
    }
  };

  const handleTerminateAI = async () => {
    if (wsClient.current) {
      wsClient.current.send({
        type: 'terminate_bait',
        payload: {},
      });
    }
    setAiActive(false);
    setStatus(MonitorStatus.MONITORING);
    dispatch(setAIHandoff(false));
  };

  const handleEndCall = () => {
    disconnectWebSocket();
    dispatch(setCallStatus('ended'));
    navigation.goBack();
  };

  // Format duration
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Get status color
  const getStatusColor = () => {
    switch (status) {
      case MonitorStatus.CONNECTING: return '#9e9e9e';
      case MonitorStatus.MONITORING: return '#388e3c';
      case MonitorStatus.THREAT_DETECTED: return '#f57c00';
      case MonitorStatus.AI_HANDOFF: return '#7b1fa2';
      case MonitorStatus.ENDED: return '#d32f2f';
      default: return '#9e9e9e';
    }
  };

  // Get status text
  const getStatusText = () => {
    switch (status) {
      case MonitorStatus.CONNECTING: return 'Connecting...';
      case MonitorStatus.MONITORING: return 'Monitoring Active';
      case MonitorStatus.THREAT_DETECTED: return 'THREAT DETECTED!';
      case MonitorStatus.AI_HANDOFF: return 'AI Agent Active';
      case MonitorStatus.ENDED: return 'Call Ended';
      default: return 'Unknown';
    }
  };

  // Interpolate threat color
  const threatColor = threatColorAnim.interpolate({
    inputRange: [0, 0.25, 0.5, 0.75, 1],
    outputRange: ['#388e3c', '#8bc34a', '#fbc02d', '#f57c00', '#d32f2f'],
  });

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerTop}>
          <TouchableOpacity onPress={handleEndCall}>
            <Ionicons name="close" size={28} color="#fff" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Call Monitor</Text>
          <View style={{ width: 28 }} />
        </View>
        
        <View style={styles.callInfo}>
          <Ionicons name="call" size={20} color="#fff" />
          <Text style={styles.phoneNumber}>{phoneNumber}</Text>
          <Text style={styles.duration}>{formatDuration(callDuration)}</Text>
        </View>
      </View>

      <ScrollView style={styles.content}>
        {/* Status Indicator */}
        <View style={styles.statusContainer}>
          <Animated.View 
            style={[
              styles.statusIndicator,
              { 
                backgroundColor: threatColor,
                transform: [{ scale: pulseAnim }],
              },
            ]} 
          />
          <Text style={[styles.statusText, { color: getStatusColor() }]}>
            {getStatusText()}
          </Text>
          
          {status === MonitorStatus.THREAT_DETECTED && (
            <View style={styles.threatBadge}>
              <Ionicons name="warning" size={16} color="#fff" />
              <Text style={styles.threatBadgeText}>
                Scam Likely ({Math.round(threatScore * 100)}%)
              </Text>
            </View>
          )}
        </View>

        {/* Threat Score Meter */}
        <View style={styles.meterContainer}>
          <Text style={styles.meterLabel}>Threat Score</Text>
          <View style={styles.meter}>
            <Animated.View 
              style={[
                styles.meterFill,
                { 
                  width: `${threatScore * 100}%`,
                  backgroundColor: threatColor,
                },
              ]} 
            />
          </View>
          <Text style={styles.meterValue}>{Math.round(threatScore * 100)}%</Text>
        </View>

        {/* AI Handoff Button */}
        {status === MonitorStatus.THREAT_DETECTED && !aiActive && (
          <TouchableOpacity 
            style={styles.handoffButton}
            onPress={handleHandoffToAI}
          >
            <Ionicons name="bot" size={32} color="#fff" />
            <View style={styles.handoffTextContainer}>
              <Text style={styles.handoffTitle}>Hand Off to AI Agent</Text>
              <Text style={styles.handoffSubtitle}>
                Let our AI waste the scammer's time
              </Text>
            </View>
            <Ionicons name="arrow-forward" size={24} color="#fff" />
          </TouchableOpacity>
        )}

        {/* AI Active Indicator */}
        {aiActive && (
          <View style={styles.aiActiveContainer}>
            <View style={styles.aiAvatar}>
              <Ionicons name="person-circle" size={48} color="#7b1fa2" />
              <View style={styles.aiPulse} />
            </View>
            <View style={styles.aiInfo}>
              <Text style={styles.aiName}>Ramesh Kumar (AI)</Text>
              <Text style={styles.aiStatus}>Engaging with caller...</Text>
              {intelligenceCount > 0 && (
                <Text style={styles.aiIntelligence}>
                  {intelligenceCount} entities extracted
                </Text>
              )}
            </View>
            <TouchableOpacity 
              style={styles.terminateButton}
              onPress={handleTerminateAI}
            >
              <Text style={styles.terminateText}>Take Over</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Live Transcript */}
        <View style={styles.transcriptContainer}>
          <Text style={styles.transcriptTitle}>Live Transcript</Text>
          <View style={styles.transcriptBox}>
            {transcript.length === 0 ? (
              <Text style={styles.emptyTranscript}>
                Waiting for speech...
              </Text>
            ) : (
              transcript.map((line, index) => (
                <Text 
                  key={index} 
                  style={[
                    styles.transcriptLine,
                    line.startsWith('AI Agent:') && styles.aiTranscriptLine,
                  ]}
                >
                  {line}
                </Text>
              ))
            )}
          </View>
        </View>

        {/* Intelligence Extracted */}
        {intelligenceCount > 0 && (
          <View style={styles.intelligenceContainer}>
            <Text style={styles.intelligenceTitle}>Intelligence Extracted</Text>
            <View style={styles.intelligenceBadge}>
              <Ionicons name="document-text" size={16} color="#7b1fa2" />
              <Text style={styles.intelligenceText}>
                {intelligenceCount} entities captured for evidence
              </Text>
            </View>
          </View>
        )}
      </ScrollView>

      {/* Bottom Actions */}
      <View style={styles.bottomActions}>
        <TouchableOpacity 
          style={[styles.actionButton, styles.endCallButton]}
          onPress={handleEndCall}
        >
          <Ionicons name="call" size={24} color="#fff" />
          <Text style={styles.actionButtonText}>End Call</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
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
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  callInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  phoneNumber: {
    fontSize: 16,
    color: '#fff',
    marginLeft: 8,
    flex: 1,
  },
  duration: {
    fontSize: 14,
    color: '#fff',
    opacity: 0.8,
  },
  content: {
    flex: 1,
    padding: 16,
  },
  statusContainer: {
    alignItems: 'center',
    marginBottom: 24,
  },
  statusIndicator: {
    width: 80,
    height: 80,
    borderRadius: 40,
    marginBottom: 12,
  },
  statusText: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  threatBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#d32f2f',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginTop: 8,
  },
  threatBadgeText: {
    color: '#fff',
    fontWeight: 'bold',
    marginLeft: 4,
  },
  meterContainer: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  meterLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  meter: {
    height: 12,
    backgroundColor: '#e0e0e0',
    borderRadius: 6,
    overflow: 'hidden',
  },
  meterFill: {
    height: '100%',
    borderRadius: 6,
  },
  meterValue: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 8,
    textAlign: 'right',
  },
  handoffButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#7b1fa2',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  handoffTextContainer: {
    flex: 1,
    marginLeft: 12,
  },
  handoffTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
  handoffSubtitle: {
    fontSize: 12,
    color: '#fff',
    opacity: 0.8,
  },
  aiActiveContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#7b1fa2',
  },
  aiAvatar: {
    position: 'relative',
  },
  aiPulse: {
    position: 'absolute',
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#7b1fa2',
    opacity: 0.3,
    transform: [{ scale: 1.3 }],
  },
  aiInfo: {
    flex: 1,
    marginLeft: 12,
  },
  aiName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  aiStatus: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  aiIntelligence: {
    fontSize: 12,
    color: '#7b1fa2',
    marginTop: 4,
  },
  terminateButton: {
    backgroundColor: '#f5f5f5',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
  },
  terminateText: {
    color: '#7b1fa2',
    fontWeight: '600',
  },
  transcriptContainer: {
    marginBottom: 16,
  },
  transcriptTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  transcriptBox: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    minHeight: 150,
    maxHeight: 250,
  },
  emptyTranscript: {
    color: '#999',
    fontStyle: 'italic',
    textAlign: 'center',
    marginTop: 50,
  },
  transcriptLine: {
    fontSize: 14,
    color: '#333',
    marginBottom: 8,
    lineHeight: 20,
  },
  aiTranscriptLine: {
    color: '#7b1fa2',
    fontStyle: 'italic',
  },
  intelligenceContainer: {
    marginBottom: 16,
  },
  intelligenceTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  intelligenceBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f3e5f5',
    padding: 12,
    borderRadius: 8,
  },
  intelligenceText: {
    marginLeft: 8,
    color: '#7b1fa2',
    fontSize: 14,
  },
  bottomActions: {
    padding: 16,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12,
  },
  endCallButton: {
    backgroundColor: '#d32f2f',
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
});
