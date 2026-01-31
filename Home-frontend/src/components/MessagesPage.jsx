import React, { useState, useEffect } from 'react';
import {
    Bell,
    Info,
    AlertCircle,
    Clock,
    CheckCircle2,
    X
} from 'lucide-react';
import { fetchNotifications, markAllAsRead, markAsRead } from '../api/notifications';

const MessagesPage = () => {
    const [messages, setMessages] = useState([]);
    const [activeFilter, setActiveFilter] = useState('all');
    const [loading, setLoading] = useState(false);
    // 假设当前用户ID为101 (匹配后端测试数据)
    const userId = 101;

    // 样式配置的方法
    const getMessageStyle = (type) => {
        switch (type) {
            case 'system':
                return {
                    icon: Info,
                    iconColor: 'text-[#007AFF]',
                    bgColor: 'bg-[#E1F2FF]'
                };
            case 'alert': // 安全提醒
                return {
                    icon: AlertCircle,
                    iconColor: 'text-[#FF6D00]',
                    bgColor: 'bg-[#FFF0EB]'
                };
            case 'reminder': // 日常提醒 (饮水等)
                return {
                    icon: Clock,
                    iconColor: 'text-[#FFB800]',
                    bgColor: 'bg-[#FFF9E6]'
                };
            default:
                return {
                    icon: Bell,
                    iconColor: 'text-[#4CAF50]',
                    bgColor: 'bg-[#E8F5E9]'
                };
        }
    };

    // 加载数据
    const loadMessages = async () => {
        setLoading(true);
        try {
            const data = await fetchNotifications(userId);
            // 这里后端返回的数据字段需要处理一下以匹配 UI
            // 后端: category, title, content, created_at
            // 前端: type, title, content, time

            const formatted = data.map(item => ({
                id: item.id,
                type: item.category, // system, reminder, alert
                title: item.title,
                content: item.content,
                time: formatTime(item.created_at),
                is_read: item.is_read
            }));
            setMessages(formatted);
        } catch (error) {
            console.error("Failed to load notifications:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        // 初始加载
        loadMessages();

        // 每10秒轮询一次
        const interval = setInterval(() => {
            loadMessages();
        }, 10000);

        // 清理函数
        return () => {
            clearInterval(interval);
        };
    }, []); // 空依赖数组 = 仅在挂载时运行一次

    const handleMarkAllRead = async () => {
        try {
            await markAllAsRead(userId);
            setMessages(prev => prev.map(msg => ({ ...msg, is_read: true })));
        } catch (error) {
            console.error("Mark all read failed:", error);
        }
    };

    const handleRead = async (id, isRead) => {
        if (isRead) return;
        try {
            await markAsRead(id, userId);
            setMessages(prev => prev.map(msg => msg.id === id ? { ...msg, is_read: true } : msg));
        } catch (error) {
            console.error("Mark read failed:", error);
        }
    };

    const formatTime = (isoString) => {
        if (!isoString) return '';
        const date = new Date(isoString);
        const now = new Date();
        const diff = now - date;
        const oneDay = 24 * 60 * 60 * 1000;

        if (diff < oneDay && now.getDate() === date.getDate()) {
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } else if (diff < 2 * oneDay) {
            return '昨天';
        } else {
            return date.toLocaleDateString([], { month: '2-digit', day: '2-digit' });
        }
    };

    // Filter Logic matching original
    const filteredMessages = activeFilter === 'all'
        ? messages
        : messages.filter(msg => {
            if (activeFilter === 'system') return msg.type === 'system';
            if (activeFilter === 'alert') return msg.type === 'alert' || msg.type === 'reminder';
            return false;
        });

    const filterButtons = [
        { id: 'all', label: '全部' },
        { id: 'system', label: '系统' },
        { id: 'alert', label: '提醒' }
    ];

    return (
        <div className="flex justify-center bg-[#f0f2f5] min-h-screen">
            <div className="w-full max-w-md bg-[#F8F9FA] text-slate-900 font-sans min-h-screen flex flex-col">

                {/* Header Section */}
                <div className="px-6 pt-12 pb-6">
                    <div className="flex items-center justify-between mb-6">
                        <h1 className="text-2xl font-bold text-slate-800 tracking-tight">消息中心</h1>
                        <button
                            onClick={handleMarkAllRead}
                            className="text-slate-400 hover:text-slate-600 transition-colors"
                            title="全部标为已读"
                        >
                            <CheckCircle2 className="w-5 h-5" />
                        </button>
                    </div>

                    {/* Filter Tabs - Original Style */}
                    <div className="flex gap-0 bg-slate-100/80 rounded-full p-1">
                        {filterButtons.map((button) => (
                            <button
                                key={button.id}
                                onClick={() => setActiveFilter(button.id)}
                                className={`
                                    flex-1 py-2 px-4 rounded-full text-sm font-medium
                                    transition-all duration-300 ease-out
                                    hover:scale-105 active:scale-95
                                    ${activeFilter === button.id
                                        ? 'bg-white text-slate-900 shadow-sm'
                                        : 'text-slate-500 hover:text-slate-700'
                                    }
                                `}
                            >
                                {button.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Messages List - Original Style */}
                <div className="flex-1 bg-white rounded-t-[40px] px-6 pt-8 pb-24 shadow-[0_-10px_40px_-15px_rgba(0,0,0,0.05)]">
                    {loading ? (
                        <div className="flex justify-center py-10 text-slate-400">加载中...</div>
                    ) : filteredMessages.length > 0 ? (
                        <div className="space-y-4">
                            {filteredMessages.map((message, index) => {
                                const style = getMessageStyle(message.type);
                                const Icon = style.icon;

                                return (
                                    <div
                                        key={message.id}
                                        className={`group flex gap-4 p-5 rounded-2xl transition-all duration-300 hover:bg-slate-50 ${!message.is_read ? 'bg-slate-50/50' : ''}`}
                                        style={{
                                            animation: `fade-in 0.3s ease-out ${index * 0.1}s both`
                                        }}
                                        onClick={() => handleRead(message.id, message.is_read)}
                                    >
                                        {/* Icon */}
                                        <div className={`w-12 h-12 rounded-2xl ${style.bgColor} flex items-center justify-center shrink-0`}>
                                            <Icon className={`w-6 h-6 ${style.iconColor}`} strokeWidth={2} />
                                        </div>

                                        {/* Content */}
                                        <div className="flex-1 min-w-0">
                                            <div className="flex justify-between items-start mb-1">
                                                <h3 className={`font-bold text-slate-800 text-sm ${!message.is_read ? 'text-blue-600' : ''}`}>
                                                    {message.title}
                                                </h3>
                                                <span className="text-[10px] text-slate-300 font-medium shrink-0 ml-2">{message.time}</span>
                                            </div>
                                            <p className="text-xs text-slate-500 leading-relaxed line-clamp-2">
                                                {message.content}
                                            </p>
                                        </div>

                                        {/* Delete/Action Button Placeholder (Original had logic for delete visual, keeping structure) */}
                                        <button className="shrink-0 text-slate-300 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100">
                                            <X className="w-4 h-4" />
                                        </button>
                                    </div>
                                );
                            })}
                        </div>
                    ) : (
                        /* Empty State */
                        <div className="flex flex-col items-center justify-center py-20">
                            <div className="w-20 h-20 rounded-3xl bg-[#F5F5F5] flex items-center justify-center mb-4">
                                <Bell className="w-10 h-10 text-slate-300" strokeWidth={2} />
                            </div>
                            <p className="text-slate-400 text-sm font-medium">暂无消息</p>
                            <p className="text-slate-300 text-xs mt-1">当有新消息时会显示在这里</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default MessagesPage;
