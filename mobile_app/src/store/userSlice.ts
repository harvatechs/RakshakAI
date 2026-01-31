/**
 * RakshakAI - User Slice
 * Redux slice for managing user data and statistics
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UserStats {
  totalCalls: number;
  threatsBlocked: number;
  aiEngagements: number;
  intelligenceExtracted: number;
  scamsReported: number;
  timeSaved: number; // in minutes
}

interface UserState {
  // User info
  userId: string | null;
  phoneNumber: string | null;
  email: string | null;
  name: string | null;
  
  // Device info
  deviceId: string | null;
  deviceType: 'android' | 'ios' | null;
  
  // Statistics
  stats: UserStats;
  
  // Achievement badges
  badges: string[];
  
  // Subscription
  isPremium: boolean;
  subscriptionExpiry: string | null;
  
  // Onboarding
  hasCompletedOnboarding: boolean;
  
  // Loading states
  isLoading: boolean;
  error: string | null;
}

const initialState: UserState = {
  userId: null,
  phoneNumber: null,
  email: null,
  name: null,
  
  deviceId: null,
  deviceType: null,
  
  stats: {
    totalCalls: 0,
    threatsBlocked: 0,
    aiEngagements: 0,
    intelligenceExtracted: 0,
    scamsReported: 0,
    timeSaved: 0,
  },
  
  badges: [],
  
  isPremium: false,
  subscriptionExpiry: null,
  
  hasCompletedOnboarding: false,
  
  isLoading: false,
  error: null,
};

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    // User info
    setUserInfo: (state, action: PayloadAction<{
      userId?: string;
      phoneNumber?: string;
      email?: string;
      name?: string;
    }>) => {
      Object.assign(state, action.payload);
    },
    
    // Device info
    setDeviceInfo: (state, action: PayloadAction<{
      deviceId: string;
      deviceType: 'android' | 'ios';
    }>) => {
      state.deviceId = action.payload.deviceId;
      state.deviceType = action.payload.deviceType;
    },
    
    // Statistics
    incrementStat: (state, action: PayloadAction<keyof UserStats>) => {
      state.stats[action.payload]++;
    },
    
    updateStats: (state, action: PayloadAction<Partial<UserStats>>) => {
      state.stats = { ...state.stats, ...action.payload };
    },
    
    // Call monitored
    recordCallMonitored: (state) => {
      state.stats.totalCalls++;
    },
    
    // Threat blocked
    recordThreatBlocked: (state) => {
      state.stats.threatsBlocked++;
    },
    
    // AI engagement
    recordAIEngagement: (state, durationMinutes: number) => {
      state.stats.aiEngagements++;
      state.stats.timeSaved += durationMinutes;
    },
    
    // Intelligence extracted
    recordIntelligenceExtracted: (state, count: number) => {
      state.stats.intelligenceExtracted += count;
    },
    
    // Scam reported
    recordScamReported: (state) => {
      state.stats.scamsReported++;
    },
    
    // Badges
    addBadge: (state, action: PayloadAction<string>) => {
      if (!state.badges.includes(action.payload)) {
        state.badges.push(action.payload);
      }
    },
    
    // Subscription
    setPremiumStatus: (state, action: PayloadAction<{ isPremium: boolean; expiry?: string }>) => {
      state.isPremium = action.payload.isPremium;
      if (action.payload.expiry) {
        state.subscriptionExpiry = action.payload.expiry;
      }
    },
    
    // Onboarding
    completeOnboarding: (state) => {
      state.hasCompletedOnboarding = true;
    },
    
    // Loading states
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    
    // Reset user state
    resetUserState: (state) => {
      return initialState;
    },
    
    // Load user data from storage
    loadUserData: (state, action: PayloadAction<Partial<UserState>>) => {
      return { ...state, ...action.payload };
    },
  },
});

export const {
  setUserInfo,
  setDeviceInfo,
  incrementStat,
  updateStats,
  recordCallMonitored,
  recordThreatBlocked,
  recordAIEngagement,
  recordIntelligenceExtracted,
  recordScamReported,
  addBadge,
  setPremiumStatus,
  completeOnboarding,
  setLoading,
  setError,
  resetUserState,
  loadUserData,
} = userSlice.actions;

export default userSlice.reducer;
