'use client';

import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string;
  icon: LucideIcon;
  trend?: string;
  trendUp?: boolean;
  color: 'blue' | 'green' | 'orange' | 'purple' | 'red' | 'indigo' | 'teal';
}

const colorClasses = {
  blue: 'bg-blue-50 text-blue-600 border-blue-200',
  green: 'bg-green-50 text-green-600 border-green-200',
  orange: 'bg-orange-50 text-orange-600 border-orange-200',
  purple: 'bg-purple-50 text-purple-600 border-purple-200',
  red: 'bg-red-50 text-red-600 border-red-200',
  indigo: 'bg-indigo-50 text-indigo-600 border-indigo-200',
  teal: 'bg-teal-50 text-teal-600 border-teal-200',
};

export default function StatCard({
  title,
  value,
  icon: Icon,
  trend,
  trendUp,
  color,
}: StatCardProps) {
  return (
    <div className={`bg-white rounded-lg shadow p-6 border ${colorClasses[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          {trend && (
            <div className={`flex items-center mt-2 text-sm ${trendUp ? 'text-green-600' : 'text-red-600'}`}>
              {trendUp ? (
                <TrendingUp className="w-4 h-4 mr-1" />
              ) : (
                <TrendingDown className="w-4 h-4 mr-1" />
              )}
              <span>{trend}</span>
            </div>
          )}
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color].split(' ')[0]}`}>
          <Icon className={`w-6 h-6 ${colorClasses[color].split(' ')[1]}`} />
        </div>
      </div>
    </div>
  );
}
