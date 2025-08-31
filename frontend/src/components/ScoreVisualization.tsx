import React from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import type { ScoringResult } from '../types';

interface ScoreVisualizationProps {
  result: ScoringResult;
}

const ScoreVisualization: React.FC<ScoreVisualizationProps> = ({ result }) => {
  const { feedback } = result;
  const breakdown = feedback.score_breakdown;

  const barData = [
    { name: 'Skills', score: breakdown.skills_score, color: '#0ea5e9' },
    { name: 'Experience', score: breakdown.experience_score, color: '#3b82f6' },
    { name: 'Education', score: breakdown.education_score, color: '#6366f1' },
    { name: 'Domain', score: breakdown.domain_score, color: '#8b5cf6' },
  ];

  const pieData = barData.map(item => ({
    name: item.name,
    value: item.score,
    color: item.color
  }));

  const COLORS = ['#0ea5e9', '#3b82f6', '#6366f1', '#8b5cf6'];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="glass-card rounded-2xl p-6"
    >
      <h3 className="text-lg font-semibold text-gray-800 mb-6">Score Breakdown</h3>
      
      <div className="grid lg:grid-cols-2 gap-8">
        {/* Bar Chart */}
        <div>
          <h4 className="text-md font-medium text-gray-700 mb-4">Component Scores</h4>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={barData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis 
                dataKey="name" 
                tick={{ fontSize: 12, fill: '#64748b' }}
                axisLine={{ stroke: '#cbd5e1' }}
              />
              <YAxis 
                domain={[0, 100]}
                tick={{ fontSize: 12, fill: '#64748b' }}
                axisLine={{ stroke: '#cbd5e1' }}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Bar 
                dataKey="score" 
                fill="#0ea5e9"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pie Chart */}
        <div>
          <h4 className="text-md font-medium text-gray-700 mb-4">Score Distribution</h4>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={2}
                dataKey="value"
              >
                {pieData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Score Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
        {barData.map((item, index) => (
          <motion.div
            key={item.name}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 * index }}
            className="p-4 bg-white rounded-xl border border-gray-200 text-center"
          >
            <div 
              className="w-12 h-12 rounded-full mx-auto mb-2 flex items-center justify-center text-white font-bold"
              style={{ backgroundColor: item.color }}
            >
              {item.score}
            </div>
            <p className="text-sm font-medium text-gray-700">{item.name}</p>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

export default ScoreVisualization;