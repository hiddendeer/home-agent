import React, { useState } from 'react';
import {
    Bell,
    Info,
    AlertCircle,
    Clock,
    CheckCircle2,
    X
} from 'lucide-react';

// 模拟消息数据
const mockMessages = [
    {
        id: 1,
        type: 'system',
        title: '系统通知',
        content: '您的设备已成功连接到家庭网络',
        time: '10:30',
        icon: Info,
        iconColor: 'text-[#007AFF]',
        bgColor: 'bg-[#E1F2FF]'
    },
    {
        id: 2,
        type: 'alert',
        title: '安全提醒',
        content: '检测到入户门异常开启，请注意安全',
        time: '09:15',
        icon: AlertCircle,
        iconColor: 'text-[#FF6D00]',
        bgColor: 'bg-[#FFF0EB]'
    },
    {
        id: 3,
        type: 'system',
        title: '设备更新',
        content: '客厅固件已更新至最新版本',
        time: '昨天',
        icon: Bell,
        iconColor: 'text-[#4CAF50]',
        bgColor: 'bg-[#E8F5E9]'
    },
    {
        id: 4,
        type: 'reminder',
        title: '饮水提醒',
        content: '今日饮水量未达标，记得多喝水哦',
        time: '昨天',
        icon: Clock,
        iconColor: 'text-[#FFB800]',
        bgColor: 'bg-[#FFF9E6]'
    }
];

const MessagesPage = () => {
    const [activeFilter, setActiveFilter] = useState('all');
    const [messages] = useState(mockMessages);

    const filterButtons = [
        { id: 'all', label: '全部' },
        { id: 'system', label: '系统' },
        { id: 'alert', label: '提醒' }
    ];

    const filteredMessages = activeFilter === 'all'
        ? messages
        : messages.filter(msg => msg.type === activeFilter || (activeFilter === 'alert' && msg.type === 'reminder'));

    return (
        <div className="flex justify-center bg-[#f0f2f5] min-h-screen">
            <div className="w-full max-w-md bg-[#F8F9FA] text-slate-900 font-sans min-h-screen flex flex-col">

                {/* Header Section */}
                <div className="px-6 pt-12 pb-6">
                    <div className="flex items-center justify-between mb-6">
                        <h1 className="text-2xl font-bold text-slate-800 tracking-tight">消息中心</h1>
                        <button className="text-slate-400 hover:text-slate-600 transition-colors">
                            <CheckCircle2 className="w-5 h-5" />
                        </button>
                    </div>

                    {/* Filter Tabs */}
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

                {/* Messages List */}
                <div className="flex-1 bg-white rounded-t-[40px] px-6 pt-8 pb-24 shadow-[0_-10px_40px_-15px_rgba(0,0,0,0.05)]">
                    {filteredMessages.length > 0 ? (
                        <div className="space-y-4">
                            {filteredMessages.map((message, index) => (
                                <div
                                    key={message.id}
                                    className="group flex gap-4 p-5 rounded-2xl transition-all duration-300 hover:bg-slate-50"
                                    style={{
                                        animation: `fade-in 0.3s ease-out ${index * 0.1}s both`
                                    }}
                                >
                                    {/* Icon */}
                                    <div className={`w-12 h-12 rounded-2xl ${message.bgColor} flex items-center justify-center shrink-0`}>
                                        <message.icon className={`w-6 h-6 ${message.iconColor}`} strokeWidth={2} />
                                    </div>

                                    {/* Content */}
                                    <div className="flex-1 min-w-0">
                                        <div className="flex justify-between items-start mb-1">
                                            <h3 className="font-bold text-slate-800 text-sm">{message.title}</h3>
                                            <span className="text-[10px] text-slate-300 font-medium shrink-0 ml-2">{message.time}</span>
                                        </div>
                                        <p className="text-xs text-slate-500 leading-relaxed line-clamp-2">
                                            {message.content}
                                        </p>
                                    </div>

                                    {/* Delete Button */}
                                    <button className="shrink-0 text-slate-300 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100">
                                        <X className="w-4 h-4" />
                                    </button>
                                </div>
                            ))}
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
