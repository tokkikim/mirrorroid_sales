import React from 'react';
import { Card, Typography, Button, Table, Space } from 'antd';
import { UploadOutlined } from '@ant-design/icons';

const { Title } = Typography;

const LocationData: React.FC = () => {
  const columns = [
    { title: '지역명', dataIndex: 'name', key: 'name' },
    { title: '주소', dataIndex: 'address', key: 'address' },
    { title: '인구수', dataIndex: 'population', key: 'population' },
    { title: '임대료', dataIndex: 'rent', key: 'rent' },
    { title: '경쟁업체', dataIndex: 'competitors', key: 'competitors' },
    {
      title: '액션',
      key: 'action',
      render: () => (
        <Space size="middle">
          <Button type="link">상세보기</Button>
          <Button type="link">수정</Button>
        </Space>
      ),
    },
  ];

  const data = [
    // 샘플 데이터 - 실제로는 API에서 가져옴
  ];

  return (
    <div>
      <Title level={2}>지역 데이터 관리</Title>
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Button type="primary" icon={<UploadOutlined />}>
            CSV 파일 업로드
          </Button>
        </div>
        <Table columns={columns} dataSource={data} />
      </Card>
    </div>
  );
};

export default LocationData;