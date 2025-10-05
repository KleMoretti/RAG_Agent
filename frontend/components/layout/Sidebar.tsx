"use client";
import * as React from "react";
import { useRouter, usePathname } from "next/navigation";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/components/ui/sidebar";
import {
  Home,
  Database,
  Workflow,
  Settings,
  Bot,
  FlaskConical,
  Wrench,
  LineChart,
  ShieldCheck,
  Zap,
  CheckCircle2,
  LogOut,
  ChevronsUpDown,
  Plus,
  MessageSquare,
  Trash2,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useChatStore } from "@/store/chatStore";
import { usePromptStore } from "@/store/promptStore";
import { useAuthStore } from "@/store/authStore";
import { AgentTooltip } from "@/components/shared/AgentTooltip";
import { ROUTES } from "@/lib/constants";
import { cn } from "@/lib/utils";
import type { AgentWithMetadata } from "@/lib/types/prompt";

// 默认图标映射（用于向后兼容）
const defaultIcons: Record<string, any> = {
  general: Bot,
  process: FlaskConical,
  equipment: Wrench,
  market: LineChart,
  quality: ShieldCheck,
  environment: Zap,
};

// 获取Agent图标
const getAgentIcon = (agent: AgentWithMetadata) => {
  if (agent.iconComponent) {
    return agent.iconComponent;
  }
  return defaultIcons[agent.name] || Bot;
};

const menu = [
  { key: ROUTES.DASHBOARD, icon: Home, label: "AI 对话" },
  { key: ROUTES.KNOWLEDGE, icon: Database, label: "知识库" },
  { key: ROUTES.WORKFLOW, icon: Workflow, label: "工艺流程" },
  { key: ROUTES.ADMIN, icon: Settings, label: "系统管理" },
];

export function AppSidebar() {
  const router = useRouter();
  const pathname = usePathname();
  const { 
    selectedAgent, 
    setSelectedAgent,
    setSelectedAgentData,
    sessions, 
    currentSessionId, 
    createSession, 
    setCurrentSession, 
    deleteSession 
  } = useChatStore();
  const { 
    agents, 
    agentsLoading, 
    error, 
    initialized, 
    initialize, 
    setError,
    recordUsage,
    setSelectedAgent: setSelectedAgentWithPrompt // 重命名以避免冲突
  } = usePromptStore();
  const { user, logout } = useAuthStore();

  // 初始化Prompt Store
  React.useEffect(() => {
    if (!initialized) {
      initialize();
    }
  }, [initialized, initialize]);

  // 悬浮窗口状态管理
  const [hoveredAgent, setHoveredAgent] = React.useState<{
    id: string;
    name: string;
    icon: any;
    color: string;
    description: string;
  } | null>(null);
  const [tooltipPosition, setTooltipPosition] = React.useState({ x: 0, y: 0 });
  const [showTooltip, setShowTooltip] = React.useState(false);
  const hoverTimeoutRef = React.useRef<NodeJS.Timeout | null>(null);

  // 鼠标悬停事件处理
  const handleAgentMouseEnter = (agentId: string, event: React.MouseEvent) => {
    const agent = agents.find(a => a.id === agentId);
    if (!agent) return;

    // 清除之前的延时器
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current);
    }

    // 计算悬浮窗口位置
    const rect = event.currentTarget.getBoundingClientRect();
    const tooltipWidth = 320; // AgentTooltip 组件的宽度 (w-80 = 320px)
    const tooltipHeight = 400; // 预估高度
    
    let tooltipX = rect.right + 10; // 默认在按钮右侧显示
    let tooltipY = rect.top;

    // 检查右侧是否有足够空间，如果没有则显示在左侧
    if (tooltipX + tooltipWidth > window.innerWidth) {
      tooltipX = rect.left - tooltipWidth - 10;
    }

    // 检查垂直位置，确保不超出屏幕
    if (tooltipY + tooltipHeight > window.innerHeight) {
      tooltipY = window.innerHeight - tooltipHeight - 10;
    }
    
    // 确保不会超出屏幕顶部
    if (tooltipY < 10) {
      tooltipY = 10;
    }

    // 设置tooltip agent数据
    const tooltipAgent = {
      id: agent.id,
      name: agent.displayName || agent.name || '',
      icon: getAgentIcon(agent),
      color: agent.colorScheme?.primary || 'text-muted-foreground',
      description: agent.description
    };

    setHoveredAgent(tooltipAgent);
    setTooltipPosition({ x: tooltipX, y: tooltipY });
    
    // 延迟显示悬浮窗口，避免快速移动时频繁显示
    hoverTimeoutRef.current = setTimeout(() => {
      setShowTooltip(true);
    }, 100);
  };

  const handleAgentMouseLeave = () => {
    // 清除延时器
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current);
    }
    
    // 延迟隐藏悬浮窗口，给用户时间移动到悬浮窗口上
    hoverTimeoutRef.current = setTimeout(() => {
      setShowTooltip(false);
      setHoveredAgent(null);
    }, 150);
  };

  // 清理定时器
  React.useEffect(() => {
    return () => {
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current);
      }
    };
  }, []);

  const handleAgentSelect = (agentId: string) => {
    // 如果选择的是当前已选中的 Agent，不做任何操作
    if (selectedAgent === agentId) {
      return;
    }

    // 查找选中的Agent数据
    const selectedAgentInfo = agents.find(agent => agent.id === agentId);
    if (!selectedAgentInfo) {
      console.error(`Agent with id ${agentId} not found`);
      return;
    }

    // 检查当前会话是否有消息
    const currentSession = sessions.find(session => session.id === currentSessionId);
    const hasMessages = currentSession && currentSession.messages.length > 0;

    if (hasMessages) {
      // 如果当前会话有消息，创建新会话并设置新的 Agent
      const sessionTitle = `与${selectedAgentInfo.displayName}的对话`;
      const sessionId = createSession(sessionTitle, agentId);
      setCurrentSession(sessionId);
      // 使用promptStore的setSelectedAgent方法，它会自动处理prompt加载和缓存
      setSelectedAgentWithPrompt(selectedAgentInfo);
    } else {
      // 如果当前会话没有消息，直接切换 Agent
      // 使用promptStore的setSelectedAgent方法，它会自动处理prompt加载和缓存
      setSelectedAgentWithPrompt(selectedAgentInfo);
    }

    // 确保导航到对话页面
    if (pathname !== ROUTES.DASHBOARD) {
      router.push(ROUTES.DASHBOARD);
    }
  };

  const handleMenuClick = (key: string) => {
    router.push(key);
  };

  const handleLogout = () => {
    logout();
    document.cookie =
      "auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;";
    router.push(ROUTES.LOGIN);
  };

  const handleNewChat = () => {
    const sessionId = createSession();
    setCurrentSession(sessionId);
    if (pathname !== ROUTES.DASHBOARD) {
      router.push(ROUTES.DASHBOARD);
    }
  };

  const handleChatSelect = (sessionId: string) => {
    setCurrentSession(sessionId);
    if (pathname !== ROUTES.DASHBOARD) {
      router.push(ROUTES.DASHBOARD);
    }
  };

  const handleDeleteChat = (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    deleteSession(sessionId);
  };

  return (
    <>
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <a href="#" className="group-data-[collapsible=icon]:px-2">
                <div className="flex flex-col gap-0.5 leading-relaxed group-data-[collapsible=icon]:hidden">
                  <span className="text-lg tracking-tight leading-tight" style={{ fontFamily: 'Michroma, monospace' }}>CastIron</span>
                  <span className="text-xs text-sidebar-foreground/70 leading-relaxed">钢铁行业 AI 决策中心</span>
                </div>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        {/* AI Agents Section */}
        <SidebarGroup>
          <SidebarGroupLabel className="menu-label">🤖 选择 AI Agent</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {agentsLoading ? (
                <SidebarMenuItem>
                  <div className="flex items-center justify-center py-4">
                    <Loader2 className="size-4 animate-spin mr-2" />
                    <span className="text-sm text-muted-foreground">加载中...</span>
                  </div>
                </SidebarMenuItem>
              ) : error ? (
                <SidebarMenuItem>
                  <div className="flex items-center justify-center py-4 text-destructive">
                    <AlertCircle className="size-4 mr-2" />
                    <span className="text-sm">加载失败</span>
                  </div>
                </SidebarMenuItem>
              ) : !agents || agents.length === 0 ? (
                <SidebarMenuItem>
                  <div className="flex items-center justify-center py-4">
                    <span className="text-sm text-muted-foreground">暂无可用Agent</span>
                  </div>
                </SidebarMenuItem>
              ) : (
                agents.map((agent) => {
                  const Icon = getAgentIcon(agent);
                  const isSelected = selectedAgent === agent.id;
                  const colorScheme = agent.colorScheme;
                  
                  return (
                    <SidebarMenuItem key={agent.id}>
                      <SidebarMenuButton
                        onClick={() => handleAgentSelect(agent.id)}
                        onMouseEnter={(e) => handleAgentMouseEnter(agent.id, e)}
                        onMouseLeave={handleAgentMouseLeave}
                        isActive={isSelected}
                        tooltip={agent.displayName}
                        size="lg"
                        className={cn(
                          "group-data-[collapsible=icon]:px-2",
                          "transition-all duration-200",
                          "min-h-[3.5rem] py-2 px-4",
                          // 默认状态样式
                          !isSelected && [
                            colorScheme?.border || "border-border",
                            colorScheme?.hover || "hover:bg-muted",
                            "border",
                            "hover:shadow-md hover:scale-[1.02]",
                            "hover:border-border/80"
                          ],
                          // 选中状态样式 - 白色背景和主题色边框
                          isSelected && [
                            "!bg-white",
                            colorScheme?.selected || "border-primary",
                            "border-2",
                            "shadow-md scale-[1.02]"
                          ]
                        )}
                      >
                        <div className="flex items-center gap-3 w-full">
                          <Icon className={cn(
                            "size-5 flex-shrink-0",
                            colorScheme?.primary || "text-foreground"
                          )} />
                          <div className="flex flex-col items-start justify-center group-data-[collapsible=icon]:hidden flex-1 min-w-0">
                            <span className={cn(
                              "text-sm font-medium leading-tight",
                              colorScheme?.primary || "text-foreground"
                            )}>
                              {agent.displayName}
                            </span>
                            <span className={cn(
                              "text-xs truncate max-w-[200px]",
                              colorScheme?.secondary || "text-muted-foreground"
                            )}>
                              {agent.description}
                            </span>
                          </div>
                          {isSelected && (
                          <CheckCircle2 className={cn(
                            "ml-auto size-4 group-data-[collapsible=icon]:hidden",
                            colorScheme?.primary || "text-foreground"
                          )} />
                        )}
                        </div>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  );
                })
              )}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Chat History Section */}
        <SidebarGroup>
          <SidebarGroupLabel className="menu-label flex items-center justify-between">
            💬 对话历史
            <button
              onClick={handleNewChat}
              className="p-1 rounded hover:bg-accent transition-colors"
              title="新建对话"
            >
              <Plus className="size-3" />
            </button>
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {sessions.length === 0 ? (
                <SidebarMenuItem>
                  <div className="px-2 py-1 text-xs text-muted-foreground group-data-[collapsible=icon]:hidden">
                    暂无对话历史
                  </div>
                </SidebarMenuItem>
              ) : (
                sessions
                  .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
                  .map((session) => {
                    const isActive = currentSessionId === session.id;
                    return (
                      <SidebarMenuItem key={session.id}>
                        <SidebarMenuButton
                          onClick={() => handleChatSelect(session.id)}
                          isActive={isActive}
                          tooltip={session.title}
                          className={cn(
                            "group relative",
                            "hover:bg-accent transition-colors",
                            isActive && "bg-accent border-accent"
                          )}
                        >
                          <MessageSquare className="size-4 flex-shrink-0" />
                          <span className="truncate group-data-[collapsible=icon]:hidden">
                            {session.title}
                          </span>
                          {sessions.length > 1 && (
                            <div
                              onClick={(e) => handleDeleteChat(session.id, e)}
                              className="opacity-0 group-hover:opacity-100 absolute right-1 p-1 rounded hover:bg-destructive/10 transition-all group-data-[collapsible=icon]:hidden cursor-pointer"
                              title="删除对话"
                              role="button"
                              tabIndex={0}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                  e.preventDefault();
                                  e.stopPropagation();
                                  deleteSession(session.id);
                                }
                              }}
                            >
                              <Trash2 className="size-3 text-destructive" />
                            </div>
                          )}
                        </SidebarMenuButton>
                      </SidebarMenuItem>
                    );
                  })
              )}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Navigation Menu */}
        <SidebarGroup>
          <SidebarGroupLabel className="menu-label">导航</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {menu.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.key;
                return (
                  <SidebarMenuItem key={item.key}>
                    <SidebarMenuButton
                      onClick={() => handleMenuClick(item.key)}
                      isActive={isActive}
                      tooltip={item.label}
                    >
                      <Icon />
                      <span>{item.label}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <SidebarMenu>
          {/* User Menu */}
          <SidebarMenuItem>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <SidebarMenuButton
                  size="lg"
                  className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
                >
                  <Avatar className="h-8 w-8 rounded-lg">
                    <AvatarImage src="" alt="avatar" />
                    <AvatarFallback className="rounded-lg">
                      {user?.username?.[0] || "U"}
                    </AvatarFallback>
                  </Avatar>
                  <div className="grid flex-1 text-left leading-tight group-data-[collapsible=icon]:hidden">
                    <span className="text-sm font-medium truncate">
                      {user?.username || "用户"}
                    </span>
                    <span className="text-xs truncate text-muted-foreground">
                      钢铁行业专家
                    </span>
                  </div>
                  <ChevronsUpDown className="ml-auto size-4 group-data-[collapsible=icon]:hidden" />
                </SidebarMenuButton>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                className="w-56 rounded-lg bg-popover text-popover-foreground shadow-lg border border-border"
                side="right"
                align="end"
                sideOffset={4}
              >
                <DropdownMenuLabel className="p-0 font-normal">
                  <div className="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
                    <Avatar className="h-8 w-8 rounded-lg">
                      <AvatarImage src="" alt="avatar" />
                      <AvatarFallback className="rounded-lg">
                        {user?.username?.[0] || "U"}
                      </AvatarFallback>
                    </Avatar>
                    <div className="grid flex-1 text-left leading-tight">
                      <span className="text-sm font-medium truncate">
                        {user?.username || "用户"}
                      </span>
                      <span className="text-xs truncate text-muted-foreground">
                        钢铁行业专家
                      </span>
                    </div>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <Settings className="mr-2 size-4" />
                  个人设置
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Settings className="mr-2 size-4" />
                  系统设置
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout}>
                  <LogOut className="mr-2 size-4" />
                  退出登录
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>

      <SidebarRail />
    </Sidebar>
    
    {/* Agent 悬浮窗口 */}
    {hoveredAgent && (
      <AgentTooltip
        agent={hoveredAgent}
        isVisible={showTooltip}
        position={tooltipPosition}
      />
    )}
    </>
  );
}
