/**
 * RakshakAI - Notification Service
 * Handles push notifications and local alerts for threat detection
 */

import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';

// Configure notification handler
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

/**
 * Initialize notifications
 */
export async function initializeNotifications(): Promise<boolean> {
  try {
    // Request permissions
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;
    
    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }
    
    if (finalStatus !== 'granted') {
      console.warn('Notification permissions not granted');
      return false;
    }

    // Get push token (for remote notifications)
    const token = await Notifications.getExpoPushTokenAsync({
      projectId: 'your-project-id', // Replace with your Expo project ID
    });
    
    console.log('Push token:', token.data);

    // Configure Android notification channel
    if (Platform.OS === 'android') {
      await Notifications.setNotificationChannelAsync('threat-alerts', {
        name: 'Threat Alerts',
        importance: Notifications.AndroidImportance.MAX,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: '#FF231F7C',
        sound: 'default',
      });

      await Notifications.setNotificationChannelAsync('call-monitoring', {
        name: 'Call Monitoring',
        importance: Notifications.AndroidImportance.HIGH,
        sound: 'default',
      });
    }

    console.log('Notifications initialized');
    return true;
  } catch (error) {
    console.error('Failed to initialize notifications:', error);
    return false;
  }
}

/**
 * Show a local threat alert notification
 */
export async function showThreatAlert(
  title: string,
  body: string,
  data?: Record<string, any>
): Promise<void> {
  try {
    await Notifications.scheduleNotificationAsync({
      content: {
        title,
        body,
        data: data || {},
        sound: 'default',
        priority: Notifications.AndroidImportance.MAX,
        vibrate: [0, 250, 250, 250],
      },
      trigger: null, // Show immediately
    });
  } catch (error) {
    console.error('Failed to show notification:', error);
  }
}

/**
 * Show high-priority scam alert
 */
export async function showScamAlert(
  phoneNumber: string,
  threatScore: number
): Promise<void> {
  const title = '🚨 SCAM CALL DETECTED!';
  const body = `Incoming call from ${phoneNumber} is likely a scam (${Math.round(threatScore * 100)}% confidence). Tap to view details.`;
  
  await showThreatAlert(title, body, {
    type: 'scam_alert',
    phoneNumber,
    threatScore,
  });
}

/**
 * Show AI handoff notification
 */
export async function showAIHandoffNotification(
  callId: string,
  duration: number
): Promise<void> {
  const title = '🤖 AI Agent Active';
  const body = `Our AI has been engaging the scammer for ${Math.floor(duration / 60)} minutes. Intelligence is being extracted.`;
  
  await showThreatAlert(title, body, {
    type: 'ai_handoff',
    callId,
    duration,
  });
}

/**
 * Show evidence package ready notification
 */
export async function showEvidenceReadyNotification(
  packageId: string,
  entitiesCount: number
): Promise<void> {
  const title = '📋 Evidence Package Ready';
  const body = `${entitiesCount} pieces of intelligence extracted and packaged for law enforcement.`;
  
  await showThreatAlert(title, body, {
    type: 'evidence_ready',
    packageId,
    entitiesCount,
  });
}

/**
 * Cancel all notifications
 */
export async function cancelAllNotifications(): Promise<void> {
  await Notifications.cancelAllScheduledNotificationsAsync();
}

/**
 * Add notification listener
 */
export function addNotificationListener(
  callback: (notification: Notifications.Notification) => void
): Notifications.Subscription {
  return Notifications.addNotificationReceivedListener(callback);
}

/**
 * Add notification response listener (when user taps notification)
 */
export function addNotificationResponseListener(
  callback: (response: Notifications.NotificationResponse) => void
): Notifications.Subscription {
  return Notifications.addNotificationResponseReceivedListener(callback);
}

/**
 * Remove notification listener
 */
export function removeNotificationListener(subscription: Notifications.Subscription): void {
  Notifications.removeNotificationSubscription(subscription);
}
