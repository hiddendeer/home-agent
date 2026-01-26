import React, { useState, useEffect } from 'react';
import * as Avatar from '@radix-ui/react-avatar';
import {
    DoorOpen,
    Droplet,
    Lightbulb,
    Wind,
    Waves,
    Pocket,
    MoreHorizontal
} from 'lucide-react';
import useDashboardStore from '../stores/useDashboardStore';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const H5Dashboard = () => {
    // 从 Zustand store 获取状态
    const actions = useDashboardStore((state) => state.actions);
    const updateAction = useDashboardStore((state) => state.updateAction);
    const toggleAction = useDashboardStore((state) => state.toggleAction);

    const [logs, setLogs] = useState([]);
    const [userInfo, setUserInfo] = useState({ full_name: '加载中...', id: 101 });

    // 获取用户信息
    const fetchUserInfo = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/users/101`);
            if (response.ok) {
                const data = await response.json();
                setUserInfo(data);
            }
        } catch (error) {
            console.error('Failed to fetch user info:', error);
        }
    };

    // 获取最近动态
    const fetchLogs = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/behavior/?user_id=101&limit=5`);
            if (response.ok) {
                const data = await response.json();
                const formattedLogs = data.map(item => ({
                    time: new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                    icon: getIconByActionType(item.action_type),
                    text: item.semantic_content || item.raw_content || item.action_type,
                    iconColor: getIconColorByActionType(item.action_type)
                }));
                setLogs(formattedLogs);
            }
        } catch (error) {
            console.error('Failed to fetch logs:', error);
        }
    };

    const getIconByActionType = (type) => {
        const mapping = {
            'drink_water': Droplet,
            'toggle_light': Lightbulb,
            'unlock_door': DoorOpen,
            'toggle_ac': Wind,
            'water_purifier': Waves,
            'toggle_heater': Pocket
        };
        return mapping[type] || MoreHorizontal;
    };

    const getIconColorByActionType = (type) => {
        const mapping = {
            'drink_water': 'text-[#007AFF]',
            'toggle_light': 'text-[#FFB800]',
            'unlock_door': 'text-[#4CAF50]',
            'toggle_ac': 'text-[#007AFF]',
            'water_purifier': 'text-[#9C27B0]',
            'toggle_heater': 'text-[#FF6D00]'
        };
        return mapping[type] || 'text-slate-400';
    };

    useEffect(() => {
        fetchUserInfo();
        fetchLogs();
        // 轮询更新动态
        const interval = setInterval(fetchLogs, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleActionClick = async (action) => {
        // 使用 Zustand store 切换状态
        const newActive = toggleAction(action.id);

        // 解析细节数据
        const details = { status: newActive ? 'on' : 'off' };

        // 尝试从 subtitle 中提取数值信息（如温度、水量等）
        if (action.subtitle) {
            const tempMatch = action.subtitle.match(/(\d+)°C/);
            if (tempMatch) details.temperature = parseInt(tempMatch[1]);

            const waterMatch = action.subtitle.match(/(\d+)ml/);
            if (waterMatch) details.amount = parseInt(waterMatch[1]);
        }

        // 发送行为到后端
        try {
            const response = await fetch(`${API_BASE_URL}/behavior/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: 101, // 模拟用户ID
                    device_id: action.id,
                    action_type: action.type,
                    details: details,
                    raw_content: `用户${newActive ? '开启' : '关闭'}了${action.name}${details.temperature ? `，设定的温度为 ${details.temperature}°C` : ''}`
                }),
            });

            if (response.ok) {
                // 立即刷新动态
                setTimeout(fetchLogs, 1000);
            }
        } catch (error) {
            console.error('Failed to record behavior:', error);
        }
    };

    return (
        <div className="flex justify-center bg-[#f0f2f5] min-h-screen">
            <div className="w-full max-w-md bg-[#F8F9FA] text-slate-900 font-sans min-h-screen flex flex-col">

                {/* Header Section */}
                <div className="px-6 pt-12 pb-8">
                    <div className="flex items-center justify-between mb-8">
                        <div>
                            <h1 className="text-2xl font-bold text-slate-800 tracking-tight">你好，{userInfo.full_name}</h1>
                            <p className="text-slate-400 text-sm mt-1 flex items-center gap-1.5">
                                <span className="w-2 h-2 rounded-full bg-green-500"></span>
                                当前位置：家中
                            </p>
                        </div>
                        <Avatar.Root className="w-14 h-14 rounded-2xl overflow-hidden bg-white shadow-sm border border-white">
                            <Avatar.Fallback className="w-full h-full flex items-center justify-center bg-slate-100 text-slate-400 font-bold">
                                {userInfo.full_name?.charAt(0) || '陈'}
                            </Avatar.Fallback>
                        </Avatar.Root>
                    </div>

                    {/* Quick Stats */}
                    <div className="flex gap-4">
                        {[
                            { label: '室内温度', value: '24', unit: '°C' },
                            { label: '环境光感', value: '暖光', unit: '' },
                            { label: '今日饮水', value: '2', unit: 'L' }
                        ].map((stat, i) => (
                            <div key={i} className="flex-1 bg-white/60 backdrop-blur-sm rounded-2xl p-3 border border-white/50">
                                <span className="block text-[10px] text-slate-400 uppercase font-bold tracking-wider mb-1">{stat.label}</span>
                                <div className="flex items-baseline gap-0.5">
                                    <span className="text-lg font-bold text-slate-700">{stat.value}</span>
                                    <span className="text-[10px] text-slate-400 font-bold">{stat.unit}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Main Content Area */}
                <div className="flex-1 bg-white rounded-t-[40px] px-6 pt-10 shadow-[0_-10px_40px_-15px_rgba(0,0,0,0.05)]">

                    {/* Actions Grid */}
                    <div className="flex items-center justify-between mb-6 px-1">
                        <h2 className="text-lg font-bold text-slate-800">快捷控制</h2>
                        <button className="text-slate-300"><MoreHorizontal className="w-5 h-5" /></button>
                    </div>

                    <div className="grid grid-cols-2 gap-4 mb-10">
                        {actions.map((action) => (
                            <button
                                key={action.id}
                                onClick={() => handleActionClick(action)}
                                className={`
                                    relative overflow-hidden group flex flex-col items-start p-5 rounded-[28px] transition-all duration-300 
                                    ${action.active
                                        ? `${action.color || 'bg-[#F2F2F2]'} ring-1 ring-black/5`
                                        : 'bg-[#F5F5F5] hover:bg-slate-100'}
                                `}
                            >
                                <div className={`
                                    p-2 rounded-xl mb-4 transition-colors
                                    ${action.active ? 'bg-white shadow-sm' : 'bg-white/50 text-slate-400'}
                                    ${action.iconColor || ''}
                                `}>
                                    <action.icon className="w-5 h-5" strokeWidth={2.5} />
                                </div>
                                <div className="text-left">
                                    <span className={`block font-bold text-sm ${action.active ? 'text-slate-800' : 'text-slate-500'}`}>
                                        {action.name}
                                    </span>
                                    <span className={`text-[10px] mt-0.5 font-medium ${action.active ? 'opacity-60 text-slate-600' : 'text-slate-400'}`}>
                                        {action.subtitle}
                                    </span>
                                </div>
                            </button>
                        ))}
                    </div>

                    {/* Recent Activity */}
                    <div className="mb-6 px-1 flex items-center justify-between">
                        <h2 className="text-lg font-bold text-slate-800">最近动态</h2>
                        <span className="text-[10px] text-slate-400">自动同步中</span>
                    </div>

                    <div className="space-y-4 pb-24">
                        {logs.length > 0 ? logs.map((log, index) => (
                            <div key={index} className="flex items-center gap-4 group animate-in fade-in slide-in-from-bottom-2 duration-500">
                                <div className={`w-10 h-10 rounded-full bg-[#F5F5F5] flex items-center justify-center shrink-0 ${log.iconColor}`}>
                                    <log.icon className="w-4 h-4" />
                                </div>
                                <div className="flex-1 border-b border-slate-50 pb-4 group-last:border-0">
                                    <div className="flex justify-between items-start">
                                        <p className="text-sm font-medium text-slate-600">{log.text}</p>
                                        <span className="text-[10px] text-slate-300 font-medium">{log.time}</span>
                                    </div>
                                </div>
                            </div>
                        )) : (
                            <div className="py-10 text-center text-slate-300 text-sm italic">
                                暂无动态
                            </div>
                        )}
                    </div>

                </div>
            </div>
        </div>
    );
};

export default H5Dashboard;
