import React from 'react';
import { ConfigProvider, App as AntApp } from 'antd';
import EnterpriseVideoComposer from './components/EnterpriseVideoComposer';
import './App.css';

function App() {
  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 6,
        },
      }}
    >
      <AntApp>
        <EnterpriseVideoComposer />
      </AntApp>
    </ConfigProvider>
  );
}

export default App;
