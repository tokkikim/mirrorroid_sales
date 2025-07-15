import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout, Menu, theme } from 'antd';
import { 
  DashboardOutlined, 
  ShopOutlined, 
  EnvironmentOutlined, 
  BarChartOutlined, 
  FileTextOutlined,
  SettingOutlined 
} from '@ant-design/icons';

import Dashboard from './pages/Dashboard';
import ReferenceAreas from './pages/ReferenceAreas';
import LocationData from './pages/LocationData';
import Analysis from './pages/Analysis';
import Reports from './pages/Reports';
import Settings from './pages/Settings';

import './App.css';

const { Header, Content, Sider } = Layout;

const App: React.FC = () => {
  const {
    token: { colorBgContainer },
  } = theme.useToken();

  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <Header style={{ display: 'flex', alignItems: 'center', background: '#001529' }}>
          <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
            미라트 스튜디오 가맹 추천 시스템
          </div>
        </Header>
        <Layout>
          <Sider 
            width={200} 
            style={{ background: colorBgContainer }}
            breakpoint="lg"
            collapsedWidth="0"
          >
            <Menu
              mode="inline"
              defaultSelectedKeys={['1']}
              style={{ height: '100%', borderRight: 0 }}
              items={[
                {
                  key: '1',
                  icon: <DashboardOutlined />,
                  label: '대시보드',
                  onClick: () => window.location.href = '/'
                },
                {
                  key: '2',
                  icon: <ShopOutlined />,
                  label: '기준 상권',
                  onClick: () => window.location.href = '/reference-areas'
                },
                {
                  key: '3',
                  icon: <EnvironmentOutlined />,
                  label: '지역 데이터',
                  onClick: () => window.location.href = '/location-data'
                },
                {
                  key: '4',
                  icon: <BarChartOutlined />,
                  label: '분석',
                  onClick: () => window.location.href = '/analysis'
                },
                {
                  key: '5',
                  icon: <FileTextOutlined />,
                  label: '보고서',
                  onClick: () => window.location.href = '/reports'
                },
                {
                  key: '6',
                  icon: <SettingOutlined />,
                  label: '설정',
                  onClick: () => window.location.href = '/settings'
                }
              ]}
            />
          </Sider>
          <Layout style={{ padding: '0 24px 24px' }}>
            <Content
              style={{
                padding: 24,
                margin: 0,
                minHeight: 280,
                background: colorBgContainer,
              }}
            >
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/reference-areas" element={<ReferenceAreas />} />
                <Route path="/location-data" element={<LocationData />} />
                <Route path="/analysis" element={<Analysis />} />
                <Route path="/reports" element={<Reports />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </Content>
          </Layout>
        </Layout>
      </Layout>
    </Router>
  );
};

export default App;
