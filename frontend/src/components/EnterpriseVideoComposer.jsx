import React, { useState, useEffect, useRef } from 'react';
import { 
  Card, 
  Button, 
  Typography,
  Space,
  Select,
  Divider,
  Alert,
  Spin,
  Upload,
  List,
  Tag,
  App,
  Steps,
  Row,
  Col,
  Statistic,
  Progress,
  Table,
  Tooltip,
  Badge,
  Timeline
} from 'antd';
import {
  PlayCircleOutlined,
  DownloadOutlined,
  ReloadOutlined,
  InboxOutlined,
  DeleteOutlined,
  VideoCameraOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  SettingOutlined,
  EyeOutlined,
  ArrowUpOutlined
} from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { Dragger } = Upload;
const { Step } = Steps;

const EnterpriseVideoComposer = () => {
  const { message } = App.useApp();
  const [currentStep, setCurrentStep] = useState(0);
  const [uploadedVideos, setUploadedVideos] = useState([]);
  const [transitionType, setTransitionType] = useState('fade');
  const [transitionDuration, setTransitionDuration] = useState(1.0);
  const [composing, setComposing] = useState(false);
  const [result, setResult] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [processingProgress, setProcessingProgress] = useState(0);
  const [showBackTop, setShowBackTop] = useState(false);
  const [headerHeight, setHeaderHeight] = useState(0);
  const headerRef = useRef(null);

  // 监听滚动事件
  useEffect(() => {
    const handleScroll = () => {
      setShowBackTop(window.scrollY > 300);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // 动态计算头部高度
  useEffect(() => {
    const updateHeaderHeight = () => {
      if (headerRef.current) {
        // 使用getBoundingClientRect获取更准确的高度
        const rect = headerRef.current.getBoundingClientRect();
        const height = rect.height;
        setHeaderHeight(height);
        console.log('头部高度更新:', height, 'px, 视频数量:', uploadedVideos.length, '当前步骤:', currentStep);

        // 添加调试信息
        console.log('头部元素详情:', {
          offsetHeight: headerRef.current.offsetHeight,
          clientHeight: headerRef.current.clientHeight,
          scrollHeight: headerRef.current.scrollHeight,
          boundingHeight: rect.height
        });
      }
    };

    // 多次延迟计算，确保DOM完全渲染
    const timeouts = [
      setTimeout(updateHeaderHeight, 50),
      setTimeout(updateHeaderHeight, 200),
      setTimeout(updateHeaderHeight, 500)
    ];

    // 监听窗口大小变化
    window.addEventListener('resize', updateHeaderHeight);

    // 使用MutationObserver监听头部内容变化
    const observer = new MutationObserver(() => {
      // 延迟执行，避免频繁更新
      setTimeout(updateHeaderHeight, 100);
    });

    if (headerRef.current) {
      observer.observe(headerRef.current, {
        childList: true,
        subtree: true,
        attributes: true,
        characterData: true
      });
    }

    return () => {
      timeouts.forEach(clearTimeout);
      window.removeEventListener('resize', updateHeaderHeight);
      observer.disconnect();
    };
  }, [uploadedVideos.length, currentStep, result]); // 依赖于可能影响头部高度的状态

  const transitions = [
    { value: 'fade', label: '🌅 淡入淡出', description: '平滑的透明度过渡效果，经典且优雅' },
    { value: 'slide_left', label: '⬅️ 左滑转场', description: '从右向左滑动切换，动感十足' },
    { value: 'slide_right', label: '➡️ 右滑转场', description: '从左向右滑动切换，流畅自然' },
    { value: 'slide_up', label: '⬆️ 上滑转场', description: '从下向上滑动切换，向上提升' },
    { value: 'slide_down', label: '⬇️ 下滑转场', description: '从上向下滑动切换，向下展开' },
    { value: 'zoom_in', label: '🔍 放大转场', description: '缩放放大过渡效果，聚焦突出' },
    { value: 'zoom_out', label: '🔎 缩小转场', description: '缩放缩小过渡效果，视野扩展' }
  ];

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const uploadProps = {
    name: 'files',
    multiple: true,
    action: 'http://localhost:5000/api/upload',
    accept: '.mp4,.avi,.mov,.mkv,.wmv,.flv,.webm',
    showUploadList: false,

    beforeUpload: (file) => {
      const isVideo = file.type.startsWith('video/') ||
        ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'].some(ext =>
          file.name.toLowerCase().endsWith(ext)
        );

      if (!isVideo) {
        message.error(`${file.name} 不是支持的视频格式`);
        return false;
      }

      const isLt500M = file.size / 1024 / 1024 < 500;
      if (!isLt500M) {
        message.error('视频文件大小不能超过 500MB');
        return false;
      }

      return true;
    },

    onChange: (info) => {
      console.log('Upload onChange:', info);
      const { status, response } = info.file;

      if (status === 'uploading') {
        setUploading(true);
      } else if (status === 'done') {
        console.log('Upload done:', response);

        if (response && response.status === 'success') {
          message.success(`${info.file.name} 上传成功`);

          // 修复：正确处理单个文件上传的响应
          const newFiles = response.files || [];
          console.log('新上传的文件:', newFiles);

          setUploadedVideos(prev => {
            const updated = [...prev, ...newFiles];
            console.log('更新后的视频列表:', updated);

            // 检查是否可以进入下一步
            if (updated.length >= 2) {
              setTimeout(() => setCurrentStep(1), 500);
            }

            return updated;
          });
        } else {
          console.error('上传失败:', response);
          message.error(`${info.file.name} 上传失败: ${response?.error || '未知错误'}`);
        }

        setUploading(false);
      } else if (status === 'error') {
        console.error('上传错误:', info.file.error);
        setUploading(false);
        message.error(`${info.file.name} 上传失败`);
      }
    },
  };

  const handleRemoveVideo = (index) => {
    const newVideos = uploadedVideos.filter((_, i) => i !== index);
    setUploadedVideos(newVideos);
    message.success('视频已移除');
    if (newVideos.length < 2) {
      setCurrentStep(0);
    }
  };

  const handleCompose = async () => {
    if (uploadedVideos.length < 2) {
      message.error('至少需要2个视频文件才能合成');
      return;
    }

    setComposing(true);
    setCurrentStep(2);
    setProcessingProgress(0);

    // 模拟进度更新
    const progressInterval = setInterval(() => {
      setProcessingProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return prev;
        }
        return prev + Math.random() * 10;
      });
    }, 1000);

    try {
      const transitions = uploadedVideos.slice(0, -1).map(() => ({
        type: transitionType,
        duration: transitionDuration
      }));

      console.log('发送合成请求:', {
        video_files: uploadedVideos.map(video => video.path),
        transitions: transitions
      });

      const response = await fetch('http://localhost:5000/api/compose', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          video_files: uploadedVideos.map(video => video.path),
          transitions: transitions,
          output_filename: `enterprise_composed_${Date.now()}.mp4`
        }),
      });

      const data = await response.json();
      console.log('合成响应:', data);
      
      clearInterval(progressInterval);
      setProcessingProgress(100);
      
      if (data.status === 'success') {
        setResult(data.result);
        setCurrentStep(3);
        message.success('视频合成完成！');
      } else {
        throw new Error(data.error || '合成失败');
      }
    } catch (error) {
      clearInterval(progressInterval);
      console.error('合成错误:', error);
      message.error(`合成失败: ${error.message}`);
      setCurrentStep(1);
    } finally {
      setComposing(false);
    }
  };

  const handleDownload = () => {
    if (!result?.output_filename) {
      message.error('没有可下载的文件');
      return;
    }

    const link = document.createElement('a');
    link.href = `http://localhost:5000/api/download/${result.output_filename}`;
    link.download = result.output_filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    message.success('开始下载视频文件');
  };

  const handleReset = () => {
    setUploadedVideos([]);
    setResult(null);
    setTransitionType('fade');
    setTransitionDuration(1.0);
    setCurrentStep(0);
    setProcessingProgress(0);
  };

  const handlePreviewVideo = (video) => {
    // 构建预览URL
    const previewUrl = `http://localhost:5000/api/preview/${video.filename}`;
    // 在新标签页中打开预览
    window.open(previewUrl, '_blank');
    message.info(`正在预览：${video.original_name}`);
  };

  const videoTableColumns = [
    {
      title: '序号',
      dataIndex: 'index',
      key: 'index',
      width: 60,
      render: (_, __, index) => index + 1,
    },
    {
      title: '文件名',
      dataIndex: 'original_name',
      key: 'original_name',
      ellipsis: true,
    },
    {
      title: '大小',
      dataIndex: 'size',
      key: 'size',
      width: 100,
      render: (size) => formatFileSize(size),
    },
    {
      title: '时长',
      dataIndex: 'info',
      key: 'duration',
      width: 80,
      render: (info) => info?.duration ? formatDuration(info.duration) : '-',
    },
    {
      title: '分辨率',
      dataIndex: 'info',
      key: 'resolution',
      width: 120,
      render: (info) => info?.size ? `${info.size[0]}×${info.size[1]}` : '-',
    },
    {
      title: '状态',
      key: 'status',
      width: 80,
      render: () => <Badge status="success" text="就绪" />,
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_, record, index) => (
        <Space>
          <Tooltip title="预览">
            <Button
              type="text"
              icon={<EyeOutlined />}
              size="small"
              onClick={() => handlePreviewVideo(record)}
            />
          </Tooltip>
          <Tooltip title="删除">
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              size="small"
              onClick={() => handleRemoveVideo(index)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  const steps = [
    {
      title: '上传视频',
      description: '选择并上传视频文件',
      icon: <InboxOutlined />,
    },
    {
      title: '配置参数',
      description: '设置转场效果和参数',
      icon: <SettingOutlined />,
    },
    {
      title: '处理中',
      description: '正在合成视频',
      icon: <ClockCircleOutlined />,
    },
    {
      title: '完成',
      description: '合成完成，可以下载',
      icon: <CheckCircleOutlined />,
    },
  ];

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleStepClick = (step) => {
    // 允许跳转的条件：
    // 1. 当前步骤或之前的步骤
    // 2. 如果有足够的视频文件，可以跳转到配置步骤
    // 3. 如果已经完成合成，可以跳转到结果步骤
    const canJump =
      step <= currentStep ||
      (step === 1 && uploadedVideos.length >= 2) ||
      (step === 3 && result);

    if (canJump) {
      setCurrentStep(step);
      scrollToTop();

      // 显示步骤切换提示
      const stepNames = ['上传视频', '配置参数', '处理中', '完成'];
      message.info(`已切换到：${stepNames[step]}`);
    } else {
      message.warning('请先完成当前步骤');
    }
  };

  // 渲染不同步骤的内容
  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return renderUploadStep();
      case 1:
        return renderConfigStep();
      case 2:
        return renderProcessingStep();
      case 3:
        return renderResultStep();
      default:
        return renderUploadStep();
    }
  };

  // 步骤1：上传视频
  const renderUploadStep = () => (
    <div className="step-content-wrapper">
      <Row gutter={[24, 24]}>
      <Col xs={24} lg={16}>
        <Card
          title="视频文件管理"
          style={{ minHeight: 500 }}
          extra={
            <Badge
              count={uploadedVideos.length}
              style={{ backgroundColor: '#52c41a' }}
            />
          }
        >
          <Dragger {...uploadProps} disabled={uploading} style={{ marginBottom: 16 }}>
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">
              点击或拖拽视频文件到此区域上传
            </p>
            <p className="ant-upload-hint">
              支持 MP4, AVI, MOV, MKV, WMV, FLV, WebM 格式，单文件最大 500MB
            </p>
          </Dragger>

          {uploadedVideos.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <Table
                dataSource={uploadedVideos.map((video, index) => ({ ...video, key: index }))}
                columns={videoTableColumns}
                pagination={false}
                size="small"
                rowKey="key"
                scroll={{ x: 800 }}
                style={{
                  background: 'white',
                  borderRadius: 6,
                  overflow: 'hidden'
                }}
              />
            </div>
          )}

          {uploadedVideos.length >= 2 && (
            <div style={{ marginTop: 24, textAlign: 'center' }}>
              <Alert
                message="可以开始配置转场效果了！"
                description={`已上传 ${uploadedVideos.length} 个视频文件，可以进行下一步配置`}
                type="success"
                showIcon
                style={{ marginBottom: 16 }}
              />
              <Button
                type="primary"
                size="large"
                icon={<SettingOutlined />}
                onClick={() => {
                  setCurrentStep(1);
                  scrollToTop();
                }}
              >
                下一步：配置转场效果
              </Button>
            </div>
          )}

          {uploadedVideos.length === 1 && (
            <div style={{ marginTop: 24, textAlign: 'center' }}>
              <Alert
                message="请再上传至少一个视频文件"
                description="需要至少2个视频文件才能进行合成"
                type="info"
                showIcon
              />
            </div>
          )}
        </Card>
      </Col>
      <Col xs={24} lg={8}>
        {renderStatisticsPanel()}
        {renderGuidePanel()}
      </Col>
    </Row>
    </div>
  );

  // 步骤2：配置参数
  const renderConfigStep = () => (
    <div className="step-content-wrapper">
      <Row gutter={[24, 24]}>
      <Col xs={24} lg={16}>
        <Card title="转场效果配置" style={{ minHeight: 500 }}>
          <Row gutter={[16, 16]}>
            <Col xs={24} md={12}>
              <div style={{ marginBottom: 16 }}>
                <Text strong>转场类型</Text>
                <Select
                  value={transitionType}
                  style={{ width: '100%', marginTop: 8 }}
                  onChange={setTransitionType}
                  optionLabelProp="label"
                  popupMatchSelectWidth={false}
                >
                  {transitions.map(t => (
                    <Option
                      key={t.value}
                      value={t.value}
                      label={t.label}
                    >
                      <div style={{ padding: '4px 0' }}>
                        <div style={{
                          fontWeight: 500,
                          marginBottom: 2,
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis'
                        }}>
                          {t.label}
                        </div>
                        <Text
                          type="secondary"
                          style={{
                            fontSize: 12,
                            lineHeight: '16px',
                            display: 'block',
                            whiteSpace: 'normal',
                            wordBreak: 'break-all'
                          }}
                        >
                          {t.description}
                        </Text>
                      </div>
                    </Option>
                  ))}
                </Select>
              </div>
            </Col>
            <Col xs={24} md={12}>
              <div style={{ marginBottom: 16 }}>
                <Text strong>转场时长（秒）</Text>
                <Select
                  value={transitionDuration}
                  style={{ width: '100%', marginTop: 8 }}
                  onChange={setTransitionDuration}
                >
                  <Option value={0.5}>0.5秒</Option>
                  <Option value={1.0}>1.0秒</Option>
                  <Option value={1.5}>1.5秒</Option>
                  <Option value={2.0}>2.0秒</Option>
                  <Option value={3.0}>3.0秒</Option>
                </Select>
              </div>
            </Col>
          </Row>

          <div style={{ marginBottom: 16 }}>
            <Alert
              message="转场效果预览"
              description={
                <div>
                  <p>将在 {uploadedVideos.length - 1} 个视频片段间添加 <strong>{transitions.find(t => t.value === transitionType)?.label}</strong> 效果</p>
                  <p>每个转场持续 <strong>{transitionDuration} 秒</strong></p>
                  <p style={{ margin: 0, fontSize: 12, color: '#666' }}>
                    {transitions.find(t => t.value === transitionType)?.description}
                  </p>
                </div>
              }
              type="info"
              showIcon
            />
          </div>

          <div style={{ textAlign: 'center', marginTop: 24 }}>
            <Space size="large">
              <Button
                size="large"
                icon={<InboxOutlined />}
                onClick={() => {
                  setCurrentStep(0);
                  scrollToTop();
                }}
              >
                上一步：重新上传
              </Button>
              <Button
                type="primary"
                size="large"
                icon={<PlayCircleOutlined />}
                loading={composing}
                onClick={handleCompose}
                disabled={uploadedVideos.length < 2}
              >
                开始合成视频
              </Button>
            </Space>
          </div>
        </Card>
      </Col>
      <Col xs={24} lg={8}>
        {renderStatisticsPanel()}
        {renderVideoListPanel()}
      </Col>
    </Row>
    </div>
  );

  // 步骤3：处理进度
  const renderProcessingStep = () => (
    <div className="step-content-wrapper">
      <Row gutter={[24, 24]} justify="center">
      <Col xs={24} lg={16}>
        <Card title="处理进度" style={{ minHeight: 500, textAlign: 'center' }}>
          <div style={{ padding: '80px 0' }}>
            <Spin size="large" />
            <div style={{ marginTop: 32 }}>
              <Title level={3}>正在处理视频，请稍候...</Title>
              <Progress
                percent={Math.round(processingProgress)}
                status="active"
                style={{ marginBottom: 24, maxWidth: 400, margin: '0 auto 24px' }}
              />
              <Text type="secondary" style={{ fontSize: 16 }}>
                正在应用 <strong>{transitions.find(t => t.value === transitionType)?.label}</strong> 转场效果
              </Text>
              <div style={{ marginTop: 16 }}>
                <Text type="secondary" style={{ fontSize: 14 }}>
                  预计剩余时间：{Math.max(0, Math.round((100 - processingProgress) / 10))} 秒
                </Text>
              </div>
            </div>
          </div>
        </Card>
      </Col>
      <Col xs={24} lg={8}>
        {renderStatisticsPanel()}
        {renderProcessingStatusPanel()}
      </Col>
    </Row>
    </div>
  );

  // 步骤4：完成结果
  const renderResultStep = () => (
    <div className="step-content-wrapper">
      <Row gutter={[24, 24]}>
      <Col xs={24} lg={16}>
        <Card title="合成完成" style={{ minHeight: 500 }}>
          <Alert
            message="🎉 视频合成成功！"
            description={`输出文件：${result?.output_filename || ''}`}
            type="success"
            showIcon
            style={{ marginBottom: 32 }}
          />

          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Space size="large" direction="vertical">
              <div>
                <VideoCameraOutlined style={{ fontSize: 64, color: '#52c41a', marginBottom: 24 }} />
                <Title level={2}>视频合成完成！</Title>
                <Text type="secondary" style={{ fontSize: 16 }}>
                  您的视频已成功合成，包含 {uploadedVideos.length - 1} 个转场效果
                </Text>
              </div>

              <Space size="large" wrap>
                <Button
                  type="primary"
                  size="large"
                  icon={<DownloadOutlined />}
                  onClick={handleDownload}
                >
                  下载视频
                </Button>
                <Button
                  size="large"
                  icon={<EyeOutlined />}
                  onClick={() => {
                    window.open(`http://localhost:5000/api/preview/${result.output_filename}`, '_blank');
                  }}
                >
                  在线预览
                </Button>
              </Space>

              <Button
                size="large"
                icon={<ReloadOutlined />}
                onClick={handleReset}
                style={{ marginTop: 24 }}
              >
                重新开始
              </Button>
            </Space>
          </div>
        </Card>
      </Col>
      <Col xs={24} lg={8}>
        {renderStatisticsPanel()}
        {renderVideoListPanel()}
      </Col>
    </Row>
    </div>
  );

  // 统计面板组件
  const renderStatisticsPanel = () => (
    <Card title="项目统计" style={{ marginBottom: 24 }}>
      <Row gutter={16}>
        <Col span={12}>
          <Statistic
            title="视频文件"
            value={uploadedVideos.length}
            suffix="个"
            valueStyle={{ color: '#1890ff' }}
          />
        </Col>
        <Col span={12}>
          <Statistic
            title="转场数量"
            value={Math.max(0, uploadedVideos.length - 1)}
            suffix="个"
            valueStyle={{ color: '#52c41a' }}
          />
        </Col>
      </Row>
      <Divider />
      <Row gutter={16}>
        <Col span={12}>
          <Statistic
            title="总大小"
            value={formatFileSize(uploadedVideos.reduce((sum, v) => sum + v.size, 0))}
            valueStyle={{ color: '#722ed1' }}
          />
        </Col>
        <Col span={12}>
          <Statistic
            title="总时长"
            value={uploadedVideos.reduce((sum, v) => sum + (v.info?.duration || 0), 0).toFixed(1)}
            suffix="秒"
            valueStyle={{ color: '#fa8c16' }}
          />
        </Col>
      </Row>
    </Card>
  );

  // 视频列表面板组件
  const renderVideoListPanel = () => (
    <Card title="视频列表" style={{ marginBottom: 24 }}>
      <List
        dataSource={uploadedVideos}
        renderItem={(video, index) => (
          <List.Item>
            <List.Item.Meta
              avatar={<Badge count={index + 1} style={{ backgroundColor: '#1890ff' }} />}
              title={<Text ellipsis style={{ width: 150 }}>{video.original_name}</Text>}
              description={
                <div>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {formatFileSize(video.size)} • {formatDuration(video.info?.duration || 0)}
                  </Text>
                </div>
              }
            />
          </List.Item>
        )}
      />
    </Card>
  );

  // 操作指南面板
  const renderGuidePanel = () => (
    <Card title="操作指南" size="small">
      <Timeline
        size="small"
        items={[
          {
            color: uploadedVideos.length > 0 ? 'green' : 'gray',
            children: '上传至少2个视频文件',
          },
          {
            color: currentStep >= 1 ? 'green' : 'gray',
            children: '选择转场效果和时长',
          },
          {
            color: currentStep >= 2 ? 'green' : 'gray',
            children: '开始视频合成处理',
          },
          {
            color: currentStep >= 3 ? 'green' : 'gray',
            children: '下载或预览结果',
          },
        ]}
      />
    </Card>
  );

  // 处理状态面板
  const renderProcessingStatusPanel = () => (
    <Card title="处理状态" style={{ marginBottom: 24 }}>
      <Timeline
        items={[
          {
            color: 'green',
            children: '视频文件加载完成',
          },
          {
            color: 'green',
            children: '转场效果配置完成',
          },
          {
            color: processingProgress > 50 ? 'green' : 'blue',
            children: '正在应用转场效果...',
          },
          {
            color: processingProgress > 90 ? 'blue' : 'gray',
            children: '生成最终视频文件',
          },
        ]}
      />
    </Card>
  );

  return (
    <div className="video-composer-container">
      {/* 固定的头部区域 */}
      <div
        ref={headerRef}
        className="video-composer-header"
        style={{
          padding: '16px 24px'
        }}>
        <div style={{
          maxWidth: 1400,
          margin: '0 auto',
          width: '100%'
        }}>
          {/* 页面标题 */}
          <div style={{ marginBottom: 16 }}>
            <Title level={2} style={{ margin: 0, fontSize: 24 }}>
              🎬 视频合成
            </Title>
            <Paragraph type="secondary" style={{ margin: 0, fontSize: 14 }}>
              视频合成简单方案，支持批量处理和多种转场效果
            </Paragraph>
          </div>

          {/* 可点击的步骤指示器 */}
          <Steps
            current={currentStep}
            items={steps.map((step, index) => {
              const canJump =
                index <= currentStep ||
                (index === 1 && uploadedVideos.length >= 2) ||
                (index === 3 && result);

              return {
                ...step,
                className: canJump ? 'clickable-step' : '',
                style: {
                  cursor: canJump ? 'pointer' : 'default',
                  opacity: canJump ? 1 : 0.7
                }
              };
            })}
            onChange={handleStepClick}
            style={{
              background: 'white',
              padding: '16px',
              borderRadius: 8,
              boxShadow: '0 2px 4px rgba(0,0,0,0.06)'
            }}
          />

          {/* 快速导航提示 */}
          <div style={{
            marginTop: 8,
            padding: '8px 16px',
            background: 'rgba(24, 144, 255, 0.1)',
            borderRadius: 6,
            fontSize: 12,
            color: '#1890ff',
            textAlign: 'center'
          }}>
            💡 提示：点击上方步骤可快速跳转到已完成的步骤
          </div>
        </div>
      </div>

      {/* 可滚动的内容区域 */}
      <div
        className="video-composer-content"
        style={{
          marginTop: Math.max(headerHeight + 60, 300), // 增加额外的60px间距，最小300px
          padding: '24px'
        }}>
        <div style={{
          maxWidth: 1400,
          margin: '0 auto',
          width: '100%'
        }}>
          {/* 调试信息 - 开发环境显示 */}
          {process.env.NODE_ENV === 'development' && (
            <div style={{
              background: 'rgba(24, 144, 255, 0.1)',
              padding: '8px 16px',
              borderRadius: '4px',
              marginBottom: '16px',
              fontSize: '12px',
              color: '#1890ff',
              border: '1px dashed #1890ff'
            }}>
              🔧 调试信息: 头部高度 {headerHeight}px, 内容区域顶部间距 {Math.max(headerHeight + 60, 300)}px
            </div>
          )}
          {renderStepContent()}
        </div>
      </div>

      {/* 返回顶部按钮 */}
      {showBackTop && (
        <Button
          type="primary"
          shape="circle"
          size="large"
          icon={<ArrowUpOutlined />}
          onClick={scrollToTop}
          className="back-top-btn"
          style={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            zIndex: 1000,
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
          }}
          title="返回顶部"
        />
      )}
    </div>
  );
};

export default EnterpriseVideoComposer;
