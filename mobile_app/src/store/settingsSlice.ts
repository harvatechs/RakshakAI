/**
 * RakshakAI - Settings Slice
 * Redux slice for managing user preferences and settings
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface SettingsState {
  // Alert settings
  alertSounds: boolean;
  vibrationAlerts: boolean;
  pushNotifications: boolean;
  
  // AI settings
  autoHandoffThreshold: number;
  enableAIBaiting: boolean;
  aiPersona: string;
  
  // Privacy settings
  privacyLevel: 'strict' | 'standard' | 'permissive';
  enableAudioEncryption: boolean;
  audioRetentionDays: number;
  
  // Auto-report settings
  autoReportToAuthorities: boolean;
  autoReportThreshold: number;
  
  // On-device ML
  enableOnDeviceML: boolean;
  
  // Language
  language: string;
}

const initialState: SettingsState = {
  alertSounds: true,
  vibrationAlerts: true,
  pushNotifications: true,
  
  autoHandoffThreshold: 0.85,
  enableAIBaiting: true,
  aiPersona: 'confused_senior',
  
  privacyLevel: 'standard',
  enableAudioEncryption: true,
  audioRetentionDays: 30,
  
  autoReportToAuthorities: false,
  autoReportThreshold: 0.95,
  
  enableOnDeviceML: true,
  
  language: 'en',
};

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    setAlertSounds: (state, action: PayloadAction<boolean>) => {
      state.alertSounds = action.payload;
    },
    
    setVibrationAlerts: (state, action: PayloadAction<boolean>) => {
      state.vibrationAlerts = action.payload;
    },
    
    setPushNotifications: (state, action: PayloadAction<boolean>) => {
      state.pushNotifications = action.payload;
    },
    
    setAutoHandoffThreshold: (state, action: PayloadAction<number>) => {
      state.autoHandoffThreshold = action.payload;
    },
    
    setEnableAIBaiting: (state, action: PayloadAction<boolean>) => {
      state.enableAIBaiting = action.payload;
    },
    
    setAIPersona: (state, action: PayloadAction<string>) => {
      state.aiPersona = action.payload;
    },
    
    setPrivacyLevel: (state, action: PayloadAction<SettingsState['privacyLevel']>) => {
      state.privacyLevel = action.payload;
    },
    
    setEnableAudioEncryption: (state, action: PayloadAction<boolean>) => {
      state.enableAudioEncryption = action.payload;
    },
    
    setAudioRetentionDays: (state, action: PayloadAction<number>) => {
      state.audioRetentionDays = action.payload;
    },
    
    setAutoReportToAuthorities: (state, action: PayloadAction<boolean>) => {
      state.autoReportToAuthorities = action.payload;
    },
    
    setAutoReportThreshold: (state, action: PayloadAction<number>) => {
      state.autoReportThreshold = action.payload;
    },
    
    setEnableOnDeviceML: (state, action: PayloadAction<boolean>) => {
      state.enableOnDeviceML = action.payload;
    },
    
    setLanguage: (state, action: PayloadAction<string>) => {
      state.language = action.payload;
    },
    
    // Reset all settings to default
    resetSettings: (state) => {
      return initialState;
    },
    
    // Load settings from storage
    loadSettings: (state, action: PayloadAction<Partial<SettingsState>>) => {
      return { ...state, ...action.payload };
    },
  },
});

export const {
  setAlertSounds,
  setVibrationAlerts,
  setPushNotifications,
  setAutoHandoffThreshold,
  setEnableAIBaiting,
  setAIPersona,
  setPrivacyLevel,
  setEnableAudioEncryption,
  setAudioRetentionDays,
  setAutoReportToAuthorities,
  setAutoReportThreshold,
  setEnableOnDeviceML,
  setLanguage,
  resetSettings,
  loadSettings,
} = settingsSlice.actions;

export default settingsSlice.reducer;
