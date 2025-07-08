# 🤝 贡献指南

感谢您对视频合成系统项目的关注！我们欢迎所有形式的贡献。

## 📋 贡献方式

### 🐛 报告Bug
- 使用 [GitHub Issues](https://github.com/your-username/video-synthesis/issues) 报告bug
- 请提供详细的复现步骤和环境信息
- 如果可能，请提供错误日志和截图

### 💡 功能建议
- 通过 [GitHub Issues](https://github.com/your-username/video-synthesis/issues) 提交功能建议
- 详细描述功能需求和使用场景
- 说明该功能的价值和重要性

### 🔧 代码贡献
1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📝 开发规范

### Python 代码规范
- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范
- 使用有意义的变量和函数名
- 添加必要的注释和文档字符串
- 保持函数简洁，单一职责

### JavaScript 代码规范
- 使用 ES6+ 语法
- 遵循 [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- 使用 ESLint 进行代码检查
- 组件名使用 PascalCase

### 提交信息规范
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型:**
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

**示例:**
```
feat(upload): add drag and drop file upload

- Add drag and drop functionality to file upload component
- Improve user experience with visual feedback
- Support multiple file selection

Closes #123
```

## 🧪 测试

### 运行测试
```bash
# 后端测试
cd backend
python -m pytest

# 前端测试
cd frontend
npm test
```

### 测试覆盖率
- 新功能必须包含相应的测试用例
- 保持测试覆盖率在 80% 以上
- 测试用例应该覆盖正常流程和异常情况

## 📚 文档

### 代码文档
- Python 函数使用 docstring
- JavaScript 函数使用 JSDoc
- 复杂逻辑添加行内注释

### API 文档
- 新增 API 需要更新 README.md 中的 API 文档
- 提供请求和响应示例
- 说明参数类型和约束

## 🔍 代码审查

### Pull Request 要求
- 提供清晰的 PR 描述
- 关联相关的 Issue
- 确保所有测试通过
- 代码符合项目规范

### 审查流程
1. 自动化测试检查
2. 代码质量检查
3. 功能测试
4. 代码审查
5. 合并到主分支

## 🆘 获取帮助

如果您在贡献过程中遇到问题，可以通过以下方式获取帮助：

- 📧 发送邮件到 [your-email@example.com]
- 💬 在 [GitHub Discussions](https://github.com/your-username/video-synthesis/discussions) 中提问
- 🐛 在 [GitHub Issues](https://github.com/your-username/video-synthesis/issues) 中报告问题

## 📄 许可证

通过贡献代码，您同意您的贡献将在 [MIT License](LICENSE) 下授权。

---

再次感谢您的贡献！🎉
