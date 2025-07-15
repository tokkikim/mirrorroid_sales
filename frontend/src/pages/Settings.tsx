import React from 'react';
import { Card, Typography, Form, Input, Button, Switch, Divider } from 'antd';

const { Title } = Typography;

const Settings: React.FC = () => {
  const [form] = Form.useForm();

  const onFinish = (values: any) => {
    console.log('설정 저장:', values);
  };

  return (
    <div>
      <Title level={2}>시스템 설정</Title>
      <Card>
        <Form form={form} onFinish={onFinish} layout="vertical">
          <Title level={4}>API 설정</Title>
          <Form.Item name="googleMapsApiKey" label="Google Maps API 키">
            <Input.Password placeholder="API 키를 입력하세요" />
          </Form.Item>
          <Form.Item name="naverMapApiKey" label="네이버 지도 API 키">
            <Input.Password placeholder="API 키를 입력하세요" />
          </Form.Item>
          <Form.Item name="dataGoKrApiKey" label="공공데이터 API 키">
            <Input.Password placeholder="API 키를 입력하세요" />
          </Form.Item>

          <Divider />

          <Title level={4}>시스템 설정</Title>
          <Form.Item name="autoDataCollection" label="자동 데이터 수집" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item name="emailNotification" label="이메일 알림" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item name="maxApiRequests" label="최대 API 요청 수">
            <Input type="number" />
          </Form.Item>

          <Divider />

          <Form.Item>
            <Button type="primary" htmlType="submit">
              설정 저장
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Settings;