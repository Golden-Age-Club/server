import React from 'react';

const TopChannels = () => {
  // Mock data for the table
  const tableData = [
    { channel: 'Direct', visitors: '19,012', percentage: 45 },
    { channel: 'Social Media', visitors: '12,054', percentage: 30 },
    { channel: 'Google Search', visitors: '8,934', percentage: 20 },
    { channel: 'Email Marketing', visitors: '3,421', percentage: 5 },
  ];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 col-span-12">
      <div className="mb-6">
        <h3 className="text-lg font-bold text-gray-800 dark:text-white">Top Channels</h3>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead>
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Channel</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Visitors</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Growth</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {tableData.map((row, index) => (
              <tr key={index}>
                <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-800 dark:text-white">{row.channel}</td>
                <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-300">{row.visitors}</td>
                <td className="px-4 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-orange-500 h-2 rounded-full" 
                        style={{ width: `${row.percentage}%` }}
                      ></div>
                    </div>
                    <span className="ml-2 text-sm text-gray-600 dark:text-gray-300">{row.percentage}%</span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TopChannels;