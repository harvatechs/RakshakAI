'use client';

import React, { useState } from 'react';
import {
  Shield,
  Phone,
  Bot,
  FileText,
  Users,
  AlertTriangle,
  MapPin,
  Search,
  Bell,
  Menu,
  X,
  LogOut,
  Database,
  TrendingUp,
  Clock
} from 'lucide-react';
import StatCard from './StatCard';
import IntelligenceFeed from './IntelligenceFeed';
import GeographicHeatmap from './GeographicHeatmap';
import EvidenceViewer from './EvidenceViewer';
import SearchPanel from './SearchPanel';

// Mock data for dashboard stats
const DASHBOARD_STATS = {
  totalCalls: 15234,
  threatsDetected: 3421,
  scamsPrevented: 2890,
  aiEngagements: 1876,
  intelligencePackages: 1243,
  activeScammers: 456,
  avgThreatScore: 0.67,
  timeSaved: 5624, // minutes
};

// Mock recent alerts
const RECENT_ALERTS = [
  {
    id: 1,
    type: 'critical',
    message: 'High-volume UPI fraud network detected',
    timestamp: '5 minutes ago',
    location: 'Mumbai, Maharashtra',
  },
  {
    id: 2,
    type: 'warning',
    message: 'New scammer profile linked to 15+ calls',
    timestamp: '12 minutes ago',
    location: 'Delhi NCR',
  },
  {
    id: 3,
    type: 'info',
    message: 'Evidence package submitted for case CC/2024/001245',
    timestamp: '28 minutes ago',
    location: 'Bangalore, Karnataka',
  },
];

export default function Dashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  const menuItems = [
    { id: 'overview', label: 'Overview', icon: Shield },
    { id: 'intelligence', label: 'Intelligence Feed', icon: Database },
    { id: 'heatmap', label: 'Geographic Map', icon: MapPin },
    { id: 'evidence', label: 'Evidence Viewer', icon: FileText },
    { id: 'search', label: 'Advanced Search', icon: Search },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard
                title="Total Calls Monitored"
                value={DASHBOARD_STATS.totalCalls.toLocaleString()}
                icon={Phone}
                trend="+12%"
                trendUp={true}
                color="blue"
              />
              <StatCard
                title="Threats Detected"
                value={DASHBOARD_STATS.threatsDetected.toLocaleString()}
                icon={AlertTriangle}
                trend="+8%"
                trendUp={true}
                color="orange"
              />
              <StatCard
                title="Scams Prevented"
                value={DASHBOARD_STATS.scamsPrevented.toLocaleString()}
                icon={Shield}
                trend="+15%"
                trendUp={true}
                color="green"
              />
              <StatCard
                title="AI Engagements"
                value={DASHBOARD_STATS.aiEngagements.toLocaleString()}
                icon={Bot}
                trend="+23%"
                trendUp={true}
                color="purple"
              />
            </div>

            {/* Secondary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <StatCard
                title="Intelligence Packages"
                value={DASHBOARD_STATS.intelligencePackages.toLocaleString()}
                icon={FileText}
                color="indigo"
              />
              <StatCard
                title="Active Scammer Profiles"
                value={DASHBOARD_STATS.activeScammers.toLocaleString()}
                icon={Users}
                color="red"
              />
              <StatCard
                title="Time Saved (minutes)"
                value={DASHBOARD_STATS.timeSaved.toLocaleString()}
                icon={Clock}
                color="teal"
              />
            </div>

            {/* Main Content Area */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Intelligence Feed */}
              <div className="lg:col-span-2">
                <IntelligenceFeed />
              </div>

              {/* Alerts Panel */}
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Recent Alerts</h3>
                  <Bell className="w-5 h-5 text-gray-400" />
                </div>
                <div className="space-y-4">
                  {RECENT_ALERTS.map((alert) => (
                    <div
                      key={alert.id}
                      className={`p-4 rounded-lg border-l-4 ${
                        alert.type === 'critical'
                          ? 'bg-red-50 border-red-500'
                          : alert.type === 'warning'
                          ? 'bg-yellow-50 border-yellow-500'
                          : 'bg-blue-50 border-blue-500'
                      }`}
                    >
                      <p className="text-sm font-medium text-gray-900">{alert.message}</p>
                      <div className="flex items-center mt-2 text-xs text-gray-500">
                        <Clock className="w-3 h-3 mr-1" />
                        {alert.timestamp}
                        <span className="mx-2">•</span>
                        <MapPin className="w-3 h-3 mr-1" />
                        {alert.location}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        );
      case 'intelligence':
        return <IntelligenceFeed fullWidth />;
      case 'heatmap':
        return <GeographicHeatmap />;
      case 'evidence':
        return <EvidenceViewer />;
      case 'search':
        return <SearchPanel />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-indigo-900 text-white shadow-lg">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-lg hover:bg-indigo-800 transition-colors"
            >
              {sidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
            <div className="flex items-center space-x-3">
              <Shield className="w-8 h-8 text-yellow-400" />
              <div>
                <h1 className="text-xl font-bold">RakshakAI</h1>
                <p className="text-xs text-indigo-200">Law Enforcement Portal</p>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Quick search..."
                className="pl-10 pr-4 py-2 rounded-lg bg-indigo-800 text-white placeholder-indigo-300 focus:outline-none focus:ring-2 focus:ring-yellow-400"
              />
            </div>
            <button className="relative p-2 rounded-lg hover:bg-indigo-800 transition-colors">
              <Bell className="w-6 h-6" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-full bg-yellow-400 flex items-center justify-center text-indigo-900 font-bold">
                SP
              </div>
              <span className="hidden md:inline text-sm">Sub-Inspector Patel</span>
            </div>
            <button className="p-2 rounded-lg hover:bg-indigo-800 transition-colors">
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        {sidebarOpen && (
          <aside className="w-64 bg-white shadow-lg min-h-screen">
            <nav className="p-4 space-y-1">
              {menuItems.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                      activeTab === item.id
                        ? 'bg-indigo-100 text-indigo-900'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </button>
                );
              })}
            </nav>

            <div className="p-4 border-t">
              <div className="bg-indigo-50 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-indigo-900 mb-2">System Status</h4>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-xs text-gray-600">All systems operational</span>
                </div>
                <div className="mt-2 text-xs text-gray-500">
                  Last sync: 2 minutes ago
                </div>
              </div>
            </div>
          </aside>
        )}

        {/* Main Content */}
        <main className="flex-1 p-6">
          {renderContent()}
        </main>
      </div>
    </div>
  );
}
