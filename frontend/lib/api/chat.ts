import apiClient from './client';
import { API_ENDPOINTS } from '../constants';
import { ChatRequest, ChatResponse } from '../types/api';

/**
 * Chat API methods
 */
export const chatApi = {
  /**
   * Send a chat message
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>(
      API_ENDPOINTS.CHAT,
      request
    );
    return response.data;
  },

  /**
   * Get chat history for a session
   */
  async getChatHistory(sessionId: string): Promise<ChatResponse[]> {
    const response = await apiClient.get<ChatResponse[]>(
      `${API_ENDPOINTS.CHAT_HISTORY}/${sessionId}`
    );
    return response.data;
  },
};

/**
 * Helper function to send message (exported for direct use)
 */
export async function sendMessage(
  message: string,
  sessionId?: string,
  agentId?: string
): Promise<ChatResponse> {
  return chatApi.sendMessage({ message, sessionId, agentId });
}
