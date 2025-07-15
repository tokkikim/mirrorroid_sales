import React from 'react';
import { Card, Typography, Button, Table, Space } from 'antd';
import { PlusOutlined } from '@ant-design/icons';

const { Title } = Typography;

const ReferenceAreas: React.FC = () => {
  const columns = [
    { title: '상권명', dataIndex: 'name', key: 'name' },
    { title: '주소', dataIndex: 'address', key: 'address' },
    { title: '월 매출', dataIndex: 'sales', key: 'sales' },
    { title: '상권 유형', dataIndex: 'type', key: 'type' },
    { title: '상태', dataIndex: 'status', key: 'status' },
    {
      title: '액션',
      key: 'action',
      render: () => (
        <Space size="middle">
          <Button type="link">수정</Button>
          <Button type="link">삭제</Button>
        </Space>
      ),
    },
  ];

  const data = [
    {
      key: '1',
      name: '용리단길점',
      address: '서울특별시 용산구 용리단길',
      sales: '15,000,000원',
      type: '번화가',
      status: '활성'
    },
    {
      key: '2',
      name: '평택 번화가점',
      address: '경기도 평택시 중앙로',
      sales: '12,000,000원',
      type: '번화가',
      status: '활성'
    }
  ];

  return (
    <div>
      <Title level={2}>기준 상권 관리</Title>
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Button type="primary" icon={<PlusOutlined />}>
            새 기준 상권 추가
          </Button>
        </div>
        <Table columns={columns} dataSource={data} />
      </Card>
    </div>
  );
};

export default ReferenceAreas;