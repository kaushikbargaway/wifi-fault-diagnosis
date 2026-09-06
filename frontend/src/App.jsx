import React from 'react';
import { Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';

// Pages — lazy-loaded to keep the initial bundle small
import Dashboard from './pages/Dashboard';
import FaultDiagnosis from './pages/FaultDiagnosis';
import DigitalTwin from './pages/DigitalTwin';
import RecoveryRecommendation from './pages/RecoveryRecommendation';
import Explanation from './pages/Explanation';
import Monitoring from './pages/Monitoring';

function App() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index                    element={<Dashboard />} />
        <Route path="diagnosis"         element={<FaultDiagnosis />} />
        <Route path="digital-twin"      element={<DigitalTwin />} />
        <Route path="recovery"          element={<RecoveryRecommendation />} />
        <Route path="explanation"       element={<Explanation />} />
        <Route path="monitoring"        element={<Monitoring />} />
      </Route>
    </Routes>
  );
}

export default App;
