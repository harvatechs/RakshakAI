/**
 * RakshakAI - Settings Screen
 * User preferences and app configuration
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store/store';
import {
  setAlertSounds,
  setVibrationAlerts,
  setPushNotifications,
  setAutoHandoffThreshold,
  setEnableAIBaiting,
  setAIPersona,
  setPrivacyLevel,
  setAutoReportToAuthorities,
  setEnableOnDeviceML,
} from '../store/settingsSlice';

interface SettingItemProps {
  icon: keyof typeof Ionicons.glyphMap;
  title: string;
  subtitle?: string;
  value?: boolean;
  onValueChange?: (value: boolean) => void;
  onPress?: () => void;
  showArrow?: boolean;
}

const SettingItem: React.FC<SettingItemProps> = ({
  icon,
  title,
  subtitle,
  value,
  onValueChange,
  onPress,
  showArrow = false,
}) => (
  <TouchableOpacity 
    style={styles.settingItem}
    onPress={onPress}
    disabled={!onPress && !onValueChange}
  >
    <View style={styles.settingIconContainer}>
      <Ionicons name={icon} size={22} color="#1a237e" />
    </View>
    <View style={styles.settingTextContainer}>
      <Text style={styles.settingTitle}>{title}</Text>
      {subtitle && <Text style={styles.settingSubtitle}>{subtitle}</Text>}
    </View>
    {onValueChange !== undefined && (
      <Switch
        value={value}
        onValueChange={onValueChange}
        trackColor={{ false: '#ddd', true: '#1a237e' }}
        thumbColor="#fff"
      />
    )}
    {showArrow && (
      <Ionicons name="chevron-forward" size={20} color="#999" />
    )}
  </TouchableOpacity>
);

export default function SettingsScreen() {
  const dispatch = useDispatch();
  const settings = useSelector((state: RootState) => state.settings);
  
  const [showPersonaSelector, setShowPersonaSelector] = useState(false);

  const personas = [
    { key: 'confused_senior', label: 'Confused Senior (Ramesh Kumar)', description: 'Elderly person not tech-savvy' },
    { key: 'cautious_professional', label: 'Cautious Professional (Suresh Patel)', description: 'Business owner, asks questions' },
    { key: 'trusting_homemaker', label: 'Trusting Homemaker (Lakshmi Devi)', description: 'Family-oriented, respectful' },
  ];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Settings</Text>
      </View>

      {/* Alert Settings */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Alerts</Text>
        <View style={styles.sectionContent}>
          <SettingItem
            icon="volume-high"
            title="Alert Sounds"
            subtitle="Play sound when threat detected"
            value={settings.alertSounds}
            onValueChange={(value) => dispatch(setAlertSounds(value))}
          />
          <SettingItem
            icon="phone-portrait"
            title="Vibration"
            subtitle="Vibrate on high-priority alerts"
            value={settings.vibrationAlerts}
            onValueChange={(value) => dispatch(setVibrationAlerts(value))}
          />
          <SettingItem
            icon="notifications"
            title="Push Notifications"
            subtitle="Receive alerts even when app is closed"
            value={settings.pushNotifications}
            onValueChange={(value) => dispatch(setPushNotifications(value))}
          />
        </View>
      </View>

      {/* AI Agent Settings */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>AI Agent</Text>
        <View style={styles.sectionContent}>
          <SettingItem
            icon="bot"
            title="Enable AI Baiting"
            subtitle="Allow AI to engage with scammers"
            value={settings.enableAIBaiting}
            onValueChange={(value) => dispatch(setEnableAIBaiting(value))}
          />
          
          {settings.enableAIBaiting && (
            <>
              <TouchableOpacity 
                style={styles.personaSelector}
                onPress={() => setShowPersonaSelector(!showPersonaSelector)}
              >
                <View style={styles.settingIconContainer}>
                  <Ionicons name="person" size={22} color="#1a237e" />
                </View>
                <View style={styles.settingTextContainer}>
                  <Text style={styles.settingTitle}>AI Persona</Text>
                  <Text style={styles.settingSubtitle}>
                    {personas.find(p => p.key === settings.aiPersona)?.label}
                  </Text>
                </View>
                <Ionicons 
                  name={showPersonaSelector ? 'chevron-up' : 'chevron-down'} 
                  size={20} 
                  color="#999" 
                />
              </TouchableOpacity>
              
              {showPersonaSelector && (
                <View style={styles.personaOptions}>
                  {personas.map((persona) => (
                    <TouchableOpacity
                      key={persona.key}
                      style={[
                        styles.personaOption,
                        settings.aiPersona === persona.key && styles.personaOptionActive
                      ]}
                      onPress={() => {
                        dispatch(setAIPersona(persona.key));
                        setShowPersonaSelector(false);
                      }}
                    >
                      <Text style={[
                        styles.personaOptionLabel,
                        settings.aiPersona === persona.key && styles.personaOptionLabelActive
                      ]}>
                        {persona.label}
                      </Text>
                      <Text style={styles.personaOptionDescription}>
                        {persona.description}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              )}
            </>
          )}
        </View>
      </View>

      {/* Privacy Settings */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Privacy & Security</Text>
        <View style={styles.sectionContent}>
          <SettingItem
            icon="shield-checkmark"
            title="On-Device ML"
            subtitle="Process audio locally for privacy"
            value={settings.enableOnDeviceML}
            onValueChange={(value) => dispatch(setEnableOnDeviceML(value))}
          />
          <SettingItem
            icon="lock-closed"
            title="Audio Encryption"
            subtitle="Encrypt stored audio recordings"
            value={settings.enableAudioEncryption}
            onValueChange={(value) => {}}
          />
        </View>
      </View>

      {/* Law Enforcement */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Law Enforcement</Text>
        <View style={styles.sectionContent}>
          <SettingItem
            icon="flag"
            title="Auto-Report to Authorities"
            subtitle="Automatically report confirmed scams"
            value={settings.autoReportToAuthorities}
            onValueChange={(value) => dispatch(setAutoReportToAuthorities(value))}
          />
        </View>
      </View>

      {/* About */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        <View style={styles.sectionContent}>
          <SettingItem
            icon="information-circle"
            title="About RakshakAI"
            showArrow
          />
          <SettingItem
            icon="document-text"
            title="Privacy Policy"
            showArrow
          />
          <SettingItem
            icon="help-circle"
            title="Help & Support"
            showArrow
          />
          <View style={styles.versionContainer}>
            <Text style={styles.versionText}>Version 1.0.0</Text>
          </View>
        </View>
      </View>
    </ScrollView>
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
  section: {
    marginTop: 16,
    paddingHorizontal: 16,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    marginBottom: 8,
    textTransform: 'uppercase',
  },
  sectionContent: {
    backgroundColor: '#fff',
    borderRadius: 12,
    overflow: 'hidden',
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  settingIconContainer: {
    width: 36,
    height: 36,
    borderRadius: 8,
    backgroundColor: '#f5f5f5',
    justifyContent: 'center',
    alignItems: 'center',
  },
  settingTextContainer: {
    flex: 1,
    marginLeft: 12,
  },
  settingTitle: {
    fontSize: 16,
    color: '#333',
  },
  settingSubtitle: {
    fontSize: 12,
    color: '#999',
    marginTop: 2,
  },
  personaSelector: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  personaOptions: {
    backgroundColor: '#f9f9f9',
    paddingVertical: 8,
  },
  personaOption: {
    padding: 12,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  personaOptionActive: {
    backgroundColor: '#e8eaf6',
  },
  personaOptionLabel: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  personaOptionLabelActive: {
    color: '#1a237e',
  },
  personaOptionDescription: {
    fontSize: 12,
    color: '#999',
    marginTop: 2,
  },
  versionContainer: {
    padding: 16,
    alignItems: 'center',
  },
  versionText: {
    fontSize: 12,
    color: '#999',
  },
});
