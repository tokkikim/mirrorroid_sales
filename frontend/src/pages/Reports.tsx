import React from 'react';
import { Card, Typography, Button, Table, Space, Select } from 'antd';
import { FileExcelOutlined, FilePdfOutlined, DownloadOutlined } from '@ant-design/icons';

const { Title } = Typography;
const { Option } = Select;

const Reports: React.FC = () => {
  const columns = [
    { title: '보고서명', dataIndex: 'name', key: 'name' },
    { title: '기준 상권', dataIndex: 'referenceArea', key: 'referenceArea' },
    { title: '생성일', dataIndex: 'createdAt', key: 'createdAt' },
    { title: '형식', dataIndex: 'format', key: 'format' },
    { title: '크기', dataIndex: 'size', key: 'size' },
    {
      title: '액션',
      key: 'action',
      render: () => (
        <Space size="middle">
          <Button type="link" icon={<DownloadOutlined />}>다운로드</Button>
          <Button type="link" danger>삭제</Button>
        </Space>
      ),
    },
  ];

  const data = [
    // 샘플 데이터 - 실제로는 API에서 가져옴
  ];

  return (
    <div>
      <Title level={2}>보고서 관리</Title>
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Space>
            <Select placeholder="기준 상권 선택" style={{ width: 200 }}>
              <Option value="yongri">용리단길점</Option>
              <Option value="pyeongtaek">평택 번화가점</Option>
            </Select>
            <Button type="primary" icon={<FileExcelOutlined />}>
              Excel 보고서 생성
            </Button>
            <Button icon={<FilePdfOutlined />}>
              PDF 보고서 생성
            </Button>
          </Space>
        </div>
        <Table columns={columns} dataSource={data} />
      </Card>
    </div>
  );
};

export default Reports;