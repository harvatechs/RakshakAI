/**
 * RakshakAI - Call Slice
 * Redux slice for managing call-related state
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface TranscriptEntry {
  speaker: 'caller' | 'user' | 'ai';
  text: string;
  timestamp: number;
}

interface ThreatAlert {
  id: string;
  threatScore: number;
  threatLevel: 'safe' | 'low' | 'medium' | 'high' | 'critical';
  message: string;
  recommendedAction: string;
  timestamp: number;
}

interface CallState {
  // Call status
  isMonitoring: boolean;
  callId: string | null;
  phoneNumber: string | null;
  callStatus: 'idle' | 'incoming' | 'connected' | 'monitoring' | 'threat_detected' | 'ai_handoff' | 'ended';
  
  // Threat detection
  threatScore: number;
  threatLevel: 'safe' | 'low' | 'medium' | 'high' | 'critical';
  lastThreatScore: number;
  
  // AI Handoff
  isAIHandoff: boolean;
  aiPersona: string | null;
  
  // Transcript
  transcript: TranscriptEntry[];
  
  // Alerts
  currentAlert: ThreatAlert | null;
  alertHistory: ThreatAlert[];
  
  // Intelligence
  extractedEntities: any[];
  
  // Connection
  isConnected: boolean;
  connectionError: string | null;
}

const initialState: CallState = {
  isMonitoring: false,
  callId: null,
  phoneNumber: null,
  callStatus: 'idle',
  threatScore: 0,
  threatLevel: 'safe',
  lastThreatScore: 0,
  isAIHandoff: false,
  aiPersona: null,
  transcript: [],
  currentAlert: null,
  alertHistory: [],
  extractedEntities: [],
  isConnected: false,
  connectionError: null,
};

const callSlice = createSlice({
  name: 'call',
  initialState,
  reducers: {
    // Call management
    startCall: (state, action: PayloadAction<{ callId: string; phoneNumber: string }>) => {
      state.isMonitoring = true;
      state.callId = action.payload.callId;
      state.phoneNumber = action.payload.phoneNumber;
      state.callStatus = 'connected';
      state.transcript = [];
      state.extractedEntities = [];
    },
    
    endCall: (state) => {
      state.isMonitoring = false;
      state.callStatus = 'ended';
      state.isAIHandoff = false;
    },
    
    setCallStatus: (state, action: PayloadAction<CallState['callStatus']>) => {
      state.callStatus = action.payload;
    },
    
    // Threat detection
    updateThreatScore: (state, action: PayloadAction<number>) => {
      state.lastThreatScore = state.threatScore;
      state.threatScore = action.payload;
      
      // Update threat level based on score
      if (action.payload >= 0.85) {
        state.threatLevel = 'critical';
      } else if (action.payload >= 0.6) {
        state.threatLevel = 'high';
      } else if (action.payload >= 0.3) {
        state.threatLevel = 'medium';
      } else if (action.payload > 0.1) {
        state.threatLevel = 'low';
      } else {
        state.threatLevel = 'safe';
      }
    },
    
    setThreatLevel: (state, action: PayloadAction<CallState['threatLevel']>) => {
      state.threatLevel = action.payload;
    },
    
    // AI Handoff
    setAIHandoff: (state, action: PayloadAction<boolean>) => {
      state.isAIHandoff = action.payload;
      if (action.payload) {
        state.callStatus = 'ai_handoff';
      }
    },
    
    setAIPersona: (state, action: PayloadAction<string>) => {
      state.aiPersona = action.payload;
    },
    
    // Transcript
    addTranscriptEntry: (state, action: PayloadAction<TranscriptEntry>) => {
      state.transcript.push(action.payload);
    },
    
    clearTranscript: (state) => {
      state.transcript = [];
    },
    
    // Alerts
    setAlert: (state, action: PayloadAction<ThreatAlert>) => {
      state.currentAlert = action.payload;
      state.alertHistory.push(action.payload);
    },
    
    clearAlert: (state) => {
      state.currentAlert = null;
    },
    
    // Intelligence
    addExtractedEntity: (state, action: PayloadAction<any>) => {
      state.extractedEntities.push(action.payload);
    },
    
    setExtractedEntities: (state, action: PayloadAction<any[]>) => {
      state.extractedEntities = action.payload;
    },
    
    // Connection
    setConnected: (state, action: PayloadAction<boolean>) => {
      state.isConnected = action.payload;
    },
    
    setConnectionError: (state, action: PayloadAction<string | null>) => {
      state.connectionError = action.payload;
    },
    
    // Reset
    resetCallState: (state) => {
      return initialState;
    },
  },
});

export const {
  startCall,
  endCall,
  setCallStatus,
  updateThreatScore,
  setThreatLevel,
  setAIHandoff,
  setAIPersona,
  addTranscriptEntry,
  clearTranscript,
  setAlert,
  clearAlert,
  addExtractedEntity,
  setExtractedEntities,
  setConnected,
  setConnectionError,
  resetCallState,
} = callSlice.actions;

export default callSlice.reducer;
