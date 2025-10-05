/**
 * Language type
 */
export type Language = 'zh-CN' | 'en-US';

/**
 * Translation dictionary
 */
export const translations = {
  'zh-CN': {
    common: {
      login: '登录',
      logout: '退出',
      submit: '提交',
      cancel: '取消',
      save: '保存',
      delete: '删除',
      edit: '编辑',
      search: '搜索',
      loading: '加载中...',
      confirm: '确认',
      back: '返回',
    },
    auth: {
      username: '用户名',
      password: '密码',
      email: '邮箱',
      rememberMe: '记住我',
      forgotPassword: '忘记密码？',
      noAccount: '还没有账号？',
      registerNow: '立即注册',
      signIn: '登录',
      signInProgress: '登录中...',
      signUp: '注册',
      confirmPassword: '确认密码',
      loginTitle: '钢铁行业 AI 决策中心',
      loginSubtitle: '智能决策支持系统',
      demoCredentials: '演示账号：admin / admin123',
    },
    errors: {
      loginFailed: '登录失败',
      loginFailedMessage: '用户名或密码错误',
      networkError: '网络连接失败，请检查后端服务是否启动',
      requiredField: '此字段为必填项',
    },
    chat: {
      sendMessage: '发送',
      inputPlaceholder: '输入您的问题... (Shift + Enter 换行)',
      thinking: '正在思考...',
      aiDisclaimer: 'AI 可能会产生错误，请验证重要信息',
      newConversation: '新建对话',
      selectAgent: '选择 AI Agent',
    },
  },
  'en-US': {
    common: {
      login: 'Login',
      logout: 'Logout',
      submit: 'Submit',
      cancel: 'Cancel',
      save: 'Save',
      delete: 'Delete',
      edit: 'Edit',
      search: 'Search',
      loading: 'Loading...',
      confirm: 'Confirm',
      back: 'Back',
    },
    auth: {
      username: 'Username',
      password: 'Password',
      email: 'Email',
      rememberMe: 'Remember me',
      forgotPassword: 'Forgot password?',
      noAccount: "Don't have an account?",
      registerNow: 'Register now',
      signIn: 'Sign In',
      signInProgress: 'Signing in...',
      signUp: 'Sign Up',
      confirmPassword: 'Confirm Password',
      loginTitle: 'Steel Industry AI Decision Hub',
      loginSubtitle: 'Intelligent Decision Support System',
      demoCredentials: 'Demo: admin / admin123',
    },
    errors: {
      loginFailed: 'Login Failed',
      loginFailedMessage: 'Invalid username or password',
      networkError: 'Network error - please check backend service',
      requiredField: 'This field is required',
    },
    chat: {
      sendMessage: 'Send',
      inputPlaceholder: 'Enter your question... (Shift + Enter for new line)',
      thinking: 'Thinking...',
      aiDisclaimer: 'AI may make mistakes. Verify important information.',
      newConversation: 'New Conversation',
      selectAgent: 'Select AI Agent',
    },
  },
} as const;

export type TranslationKey = keyof typeof translations['zh-CN'];
