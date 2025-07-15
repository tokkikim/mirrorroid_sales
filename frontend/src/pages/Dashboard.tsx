import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Table, Button, Typography, Alert } from 'antd';
import { 
  ShopOutlined, 
  EnvironmentOutlined, 
  BarChartOutlined, 
  FileTextOutlined,
  PlayCircleOutlined
} from '@ant-design/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const { Title, Text } = Typography;

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState({
    totalReferenceAreas: 2,
    totalLocationData: 0,
    totalRecommendations: 0,
    totalReports: 0
  });

  const [recentAnalyses, setRecentAnalyses] = useState([
    {
      key: '1',
      date: '2024-01-15',
      referenceArea: '용리단길점',
      recommendationsCount: 10,
      avgSimilarity: 0.85,
      status: '완료'
    },
    {
      key: '2',
      date: '2024-01-14',
      referenceArea: '평택 번화가점',
      recommendationsCount: 8,
      avgSimilarity: 0.78,
      status: '완료'
    }
  ]);

  const chartData = [
    { month: '1월', analyses: 15, recommendations: 120 },
    { month: '2월', analyses: 18, recommendations: 140 },
    { month: '3월', analyses: 22, recommendations: 180 },
    { month: '4월', analyses: 25, recommendations: 200 },
  ];

  const columns = [
    {
      title: '분석 일자',
      dataIndex: 'date',
      key: 'date',
    },
    {
      title: '기준 상권',
      dataIndex: 'referenceArea',
      key: 'referenceArea',
    },
    {
      title: '추천 수',
      dataIndex: 'recommendationsCount',
      key: 'recommendationsCount',
    },
    {
      title: '평균 유사도',
      dataIndex: 'avgSimilarity',
      key: 'avgSimilarity',
      render: (value: number) => `${(value * 100).toFixed(1)}%`
    },
    {
      title: '상태',
      dataIndex: 'status',
      key: 'status',
    },
  ];

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Title level={2}>대시보드</Title>
          <Alert
            message="시스템 상태"
            description="미라트 스튜디오 가맹 추천 시스템이 정상적으로 운영 중입니다."
            type="success"
            showIcon
            style={{ marginBottom: 16 }}
          />
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="기준 상권"
              value={stats.totalReferenceAreas}
              prefix={<ShopOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="지역 데이터"
              value={stats.totalLocationData}
              prefix={<EnvironmentOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="추천 결과"
              value={stats.totalRecommendations}
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="생성된 보고서"
              value={stats.totalReports}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={16}>
          <Card title="분석 트렌드">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="analyses" stroke="#1890ff" name="분석 수" />
                <Line type="monotone" dataKey="recommendations" stroke="#52c41a" name="추천 수" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="빠른 실행" style={{ marginBottom: 16 }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <Button 
                type="primary" 
                icon={<PlayCircleOutlined />}
                onClick={() => window.location.href = '/analysis'}
              >
                새 분석 시작
              </Button>
              <Button 
                icon={<FileTextOutlined />}
                onClick={() => window.location.href = '/reports'}
              >
                보고서 생성
              </Button>
              <Button 
                icon={<ShopOutlined />}
                onClick={() => window.location.href = '/reference-areas'}
              >
                기준 상권 관리
              </Button>
            </div>
          </Card>
          <Card title="시스템 정보">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <Text><strong>버전:</strong> 1.0.0</Text>
              <Text><strong>마지막 데이터 수집:</strong> 2024-01-15</Text>
              <Text><strong>데이터베이스 상태:</strong> 정상</Text>
              <Text><strong>API 상태:</strong> 정상</Text>
            </div>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title="최근 분석 결과">
            <Table columns={columns} dataSource={recentAnalyses} pagination={false} />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;