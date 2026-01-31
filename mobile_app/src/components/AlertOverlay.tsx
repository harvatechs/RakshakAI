/**
 * RakshakAI - Alert Overlay Component
 * Displays threat alerts with "Hand Off to AI" option
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
  Modal,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store/store';
import { clearAlert } from '../store/callSlice';

export default function AlertOverlay() {
  const dispatch = useDispatch();
  const { currentAlert, isAIHandoff } = useSelector((state: RootState) => state.call);
  
  // Animation values
  const slideAnim = React.useRef(new Animated.Value(-300)).current;
  const pulseAnim = React.useRef(new Animated.Value(1)).current;
  
  React.useEffect(() => {
    if (currentAlert) {
      // Slide in
      Animated.spring(slideAnim, {
        toValue: 0,
        useNativeDriver: true,
      }).start();
      
      // Start pulse animation
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.1,
            duration: 500,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 500,
            useNativeDriver: true,
          }),
        ])
      ).start();
    } else {
      // Slide out
      Animated.timing(slideAnim, {
        toValue: -300,
        duration: 300,
        useNativeDriver: true,
      }).start();
    }
  }, [currentAlert]);
  
  const handleDismiss = () => {
    dispatch(clearAlert());
  };
  
  const handleHandoff = () => {
    // Trigger AI handoff
    dispatch(clearAlert());
    // Navigate to call monitor or trigger handoff
  };
  
  if (!currentAlert) {
    return null;
  }
  
  const getAlertColor = () => {
    switch (currentAlert.threatLevel) {
      case 'critical': return '#d32f2f';
      case 'high': return '#f57c00';
      case 'medium': return '#fbc02d';
      default: return '#388e3c';
    }
  };
  
  const getAlertIcon = () => {
    switch (currentAlert.threatLevel) {
      case 'critical': return 'warning';
      case 'high': return 'alert-circle';
      case 'medium': return 'alert';
      default: return 'information-circle';
    }
  };
  
  return (
    <Modal
      transparent
      visible={!!currentAlert}
      animationType="none"
    >
      <View style={styles.overlay}>
        <Animated.View 
          style={[
            styles.alertContainer,
            { 
              backgroundColor: getAlertColor(),
              transform: [{ translateY: slideAnim }],
            },
          ]}
        >
          <Animated.View 
            style={[
              styles.iconContainer,
              { transform: [{ scale: pulseAnim }] },
            ]}
          >
            <Ionicons 
              name={getAlertIcon() as any} 
              size={48} 
              color="#fff" 
            />
          </Animated.View>
          
          <Text style={styles.alertTitle}>
            {currentAlert.threatLevel === 'critical' 
              ? 'CRITICAL THREAT!' 
              : 'Threat Detected'}
          </Text>
          
          <Text style={styles.alertMessage}>
            {currentAlert.message}
          </Text>
          
          <View style={styles.threatInfo}>
            <Text style={styles.threatScore}>
              Risk Score: {Math.round(currentAlert.threatScore * 100)}%
            </Text>
          </View>
          
          {currentAlert.recommendedAction === 'handoff_to_ai' && !isAIHandoff && (
            <TouchableOpacity 
              style={styles.handoffButton}
              onPress={handleHandoff}
            >
              <Ionicons name="bot" size={24} color="#7b1fa2" />
              <Text style={styles.handoffText}>Hand Off to AI Agent</Text>
            </TouchableOpacity>
          )}
          
          <TouchableOpacity 
            style={styles.dismissButton}
            onPress={handleDismiss}
          >
            <Text style={styles.dismissText}>Dismiss</Text>
          </TouchableOpacity>
        </Animated.View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-start',
    paddingTop: 50,
  },
  alertContainer: {
    margin: 16,
    padding: 24,
    borderRadius: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  iconContainer: {
    marginBottom: 16,
  },
  alertTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 8,
  },
  alertMessage: {
    fontSize: 16,
    color: '#fff',
    textAlign: 'center',
    marginBottom: 16,
    opacity: 0.9,
  },
  threatInfo: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    marginBottom: 16,
  },
  threatScore: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#fff',
  },
  handoffButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
    marginBottom: 12,
  },
  handoffText: {
    color: '#7b1fa2',
    fontWeight: 'bold',
    fontSize: 16,
    marginLeft: 8,
  },
  dismissButton: {
    paddingVertical: 8,
  },
  dismissText: {
    color: '#fff',
    fontSize: 14,
    opacity: 0.8,
  },
});
