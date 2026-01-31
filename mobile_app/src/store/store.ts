/**
 * RakshakAI - Redux Store Configuration
 * Global state management for the application
 */

import { configureStore } from '@reduxjs/toolkit';
import callReducer from './callSlice';
import settingsReducer from './settingsSlice';
import userReducer from './userSlice';

export const store = configureStore({
  reducer: {
    call: callReducer,
    settings: settingsReducer,
    user: userReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types
        ignoredActions: ['call/setWebSocketClient'],
      },
    }),
});

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
