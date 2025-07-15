import React from 'react';
import { Card, Typography, Button, Form, Select, Slider, Row, Col } from 'antd';
import { PlayCircleOutlined } from '@ant-design/icons';

const { Title } = Typography;
const { Option } = Select;

const Analysis: React.FC = () => {
  const [form] = Form.useForm();

  const onFinish = (values: any) => {
    console.log('분석 요청:', values);
  };

  return (
    <div>
      <Title level={2}>분석 실행</Title>
      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Card title="분석 조건 설정">
            <Form form={form} onFinish={onFinish} layout="vertical">
              <Form.Item
                name="referenceArea"
                label="기준 상권"
                rules={[{ required: true, message: '기준 상권을 선택해주세요' }]}
              >
                <Select placeholder="기준 상권을 선택하세요">
                  <Option value="yongri">용리단길점</Option>
                  <Option value="pyeongtaek">평택 번화가점</Option>
                </Select>
              </Form.Item>

              <Form.Item name="maxResults" label="최대 추천 수" initialValue={10}>
                <Slider min={5} max={50} />
              </Form.Item>

              <Form.Item name="populationWeight" label="인구 가중치" initialValue={0.25}>
                <Slider min={0} max={1} step={0.05} />
              </Form.Item>

              <Form.Item name="businessWeight" label="업종 밀도 가중치" initialValue={0.25}>
                <Slider min={0} max={1} step={0.05} />
              </Form.Item>

              <Form.Item name="rentWeight" label="임대료 가중치" initialValue={0.20}>
                <Slider min={0} max={1} step={0.05} />
              </Form.Item>

              <Form.Item name="competitionWeight" label="경쟁 가중치" initialValue={0.15}>
                <Slider min={0} max={1} step={0.05} />
              </Form.Item>

              <Form.Item name="transportWeight" label="교통 가중치" initialValue={0.15}>
                <Slider min={0} max={1} step={0.05} />
              </Form.Item>

              <Form.Item>
                <Button type="primary" htmlType="submit" icon={<PlayCircleOutlined />}>
                  분석 시작
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="분석 결과">
            <p>분석을 실행하면 결과가 여기에 표시됩니다.</p>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Analysis;