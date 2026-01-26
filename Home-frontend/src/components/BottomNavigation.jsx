import React from 'react';
import { Home, MessageCircle } from 'lucide-react';

const BottomNavigation = ({ activeTab = 'home', onTabChange }) => {
    const navItems = [
        {
            id: 'home',
            label: '首页',
            icon: Home
        },
        {
            id: 'messages',
            label: '消息',
            icon: MessageCircle
        }
    ];

    return (
        <div className="fixed bottom-0 left-0 right-0 flex justify-center z-50">
            <div className="w-full max-w-md">
                {/* 底部导航栏 */}
                <nav className="bg-white/95 backdrop-blur-xl border-t border-black/10">
                    <div className="flex items-center justify-around py-2">
                        {navItems.map((item) => {
                            const isActive = activeTab === item.id;
                            const IconComponent = item.icon;

                            return (
                                <button
                                    key={item.id}
                                    onClick={() => onTabChange?.(item.id)}
                                    className="flex flex-col items-center gap-0.5 transition-all duration-200 px-6 py-1"
                                >
                                    {/* 图标 */}
                                    <IconComponent
                                        className={`w-5 h-5 transition-colors duration-200 ${
                                            isActive ? 'text-[#007AFF]' : 'text-[#94A3B8]'
                                        }`}
                                        strokeWidth={2.5}
                                    />

                                    {/* 文字标签 */}
                                    <span className={`
                                        text-[10px] font-medium transition-all duration-200
                                        ${isActive
                                            ? 'text-[#007AFF]'
                                            : 'text-[#94A3B8]'
                                        }
                                    `}>
                                        {item.label}
                                    </span>
                                </button>
                            );
                        })}
                    </div>
                </nav>
            </div>
        </div>
    );
};

export default BottomNavigation;
