/**
 * RakshakAI - Main Application Entry Point
 * React Native mobile app for real-time scam call defense
 */

import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Provider } from 'react-redux';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';

// Redux store
import { store } from './store/store';

// Screens
import HomeScreen from './screens/HomeScreen';
import CallMonitorScreen from './screens/CallMonitorScreen';
import HistoryScreen from './screens/HistoryScreen';
import ReportScreen from './screens/ReportScreen';
import SettingsScreen from './screens/SettingsScreen';

// Services
import { initializeNotifications } from './services/NotificationService';
import { initializeAudioCapture } from './services/AudioCapture';

// Types
export type RootStackParamList = {
  MainTabs: undefined;
  CallMonitor: { callId: string; phoneNumber: string };
  ReportDetail: { reportId: string };
};

export type MainTabParamList = {
  Home: undefined;
  History: undefined;
  Reports: undefined;
  Settings: undefined;
};

const Stack = createStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<MainTabParamList>();

/**
 * Main Tab Navigator
 * Bottom navigation for primary app sections
 */
function MainTabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap;

          switch (route.name) {
            case 'Home':
              iconName = focused ? 'home' : 'home-outline';
              break;
            case 'History':
              iconName = focused ? 'time' : 'time-outline';
              break;
            case 'Reports':
              iconName = focused ? 'shield-checkmark' : 'shield-checkmark-outline';
              break;
            case 'Settings':
              iconName = focused ? 'settings' : 'settings-outline';
              break;
            default:
              iconName = 'help-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#1a237e',
        tabBarInactiveTintColor: 'gray',
        tabBarStyle: {
          paddingBottom: 5,
          paddingTop: 5,
        },
        headerStyle: {
          backgroundColor: '#1a237e',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{ title: 'RakshakAI' }}
      />
      <Tab.Screen 
        name="History" 
        component={HistoryScreen}
        options={{ title: 'Call History' }}
      />
      <Tab.Screen 
        name="Reports" 
        component={ReportScreen}
        options={{ title: 'Evidence Reports' }}
      />
      <Tab.Screen 
        name="Settings" 
        component={SettingsScreen}
        options={{ title: 'Settings' }}
      />
    </Tab.Navigator>
  );
}

/**
 * Root Stack Navigator
 * Handles main navigation flow including modals
 */
function RootNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: '#1a237e',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      <Stack.Screen 
        name="MainTabs" 
        component={MainTabNavigator}
        options={{ headerShown: false }}
      />
      <Stack.Screen 
        name="CallMonitor" 
        component={CallMonitorScreen}
        options={{ 
          title: 'Call Monitor',
          presentation: 'fullScreenModal',
        }}
      />
    </Stack.Navigator>
  );
}

/**
 * Main App Component
 */
export default function App() {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // Initialize app services
    const initializeApp = async () => {
      try {
        // Initialize notifications
        await initializeNotifications();
        
        // Initialize audio capture (mock for now)
        await initializeAudioCapture();
        
        setIsReady(true);
      } catch (error) {
        console.error('Failed to initialize app:', error);
        // Still set ready to show error state
        setIsReady(true);
      }
    };

    initializeApp();
  }, []);

  if (!isReady) {
    // Could show a splash screen here
    return null;
  }

  return (
    <Provider store={store}>
      <NavigationContainer>
        <StatusBar style="light" />
        <RootNavigator />
      </NavigationContainer>
    </Provider>
  );
}
