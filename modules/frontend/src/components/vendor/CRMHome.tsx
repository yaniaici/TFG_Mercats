import React from 'react';

const CRMHome: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-sea-50 via-white to-olive-50">
      <div className="max-w-5xl mx-auto p-6">
        <div className="bg-white rounded-2xl shadow p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">CRM - Inici</h1>
          <p className="text-gray-600">Espai reservat per a funcionalitats CRM (llistat de clients, campanyes, etc.).</p>
        </div>
      </div>
    </div>
  );
};

export default CRMHome;


