/**
 * 模块名称: API/Notifications
 * 主要功能: 封装消息中心相关的后端 API 调用
 * 关键逻辑: 使用 fetch 进行 HTTP 请求，处理 query params
 */

const API_BASE_URL = '/api/v1'; // 使用相对路径，自动指向当前域名

// Helper to handle response
async function handleResponse(response) {
    if (!response.ok) {
        const error = await response.text();
        throw new Error(error || response.statusText);
    }
    return response.json();
}

/**
 * 获取通知列表
 * @param {number} userId - 用户ID
 * @param {string} category - (可选) 分类: system, reminder, alert
 * @param {number} skip - 分页起始
 * @param {number} limit - 分页大小
 */
export async function fetchNotifications(userId, category = null, skip = 0, limit = 100) {
    const params = new URLSearchParams({
        user_id: userId,
        skip: skip,
        limit: limit
    });

    if (category) {
        params.append('category', category);
    }

    const response = await fetch(`${API_BASE_URL}/notifications/?${params.toString()}`);
    return handleResponse(response);
}

/**
 * 标记单个消息为已读
 * @param {number} notificationId - 消息ID
 * @param {number} userId - 用户ID
 */
export async function markAsRead(notificationId, userId) {
    const params = new URLSearchParams({ user_id: userId });
    const response = await fetch(`${API_BASE_URL}/notifications/${notificationId}/read?${params.toString()}`, {
        method: 'PUT'
    });
    return handleResponse(response);
}

/**
 * 标记所有消息为已读
 * @param {number} userId - 用户ID
 */
export async function markAllAsRead(userId) {
    const params = new URLSearchParams({ user_id: userId });
    const response = await fetch(`${API_BASE_URL}/notifications/read-all?${params.toString()}`, {
        method: 'PUT'
    });
    return handleResponse(response);
}

/**
 * 获取未读数量
 * @param {number} userId 
 */
export async function fetchUnreadCount(userId) {
    const params = new URLSearchParams({ user_id: userId });
    const response = await fetch(`${API_BASE_URL}/notifications/unread-count?${params.toString()}`);
    return handleResponse(response);
}
