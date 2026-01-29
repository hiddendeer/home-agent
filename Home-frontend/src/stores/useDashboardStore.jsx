import { create } from 'zustand';
import {
    DoorOpen,
    Droplet,
    Lightbulb,
    Wind,
    Waves,
    Pocket
} from 'lucide-react';

// 初始控制项配置
const initialActions = [
    { id: 'water', name: '喝水', type: 'drink_water', icon: Droplet, active: false, color: 'bg-[#E1F2FF]', iconColor: 'text-[#007AFF]', subtitle: '2200ml / 3000ml' },
    { id: 'faucet', name: '纯净水', type: 'water_purifier', icon: Waves, active: false, color: 'bg-[#E1F2FF]', iconColor: 'text-[#007AFF]', subtitle: '水质优' },
    { id: 'light', name: '客厅灯', type: 'toggle_light', icon: Lightbulb, active: false, color: 'bg-[#FFF9E6]', iconColor: 'text-[#FFB800]', subtitle: '暖白光 · 80%' },
    { id: 'door', name: '入户门', type: 'unlock_door', icon: DoorOpen, active: false, color: 'bg-[#E8F5E9]', iconColor: 'text-[#4CAF50]', subtitle: '已锁止' },
    { id: 'ac', name: '全屋空调', type: 'toggle_ac', icon: Wind, active: false, color: 'bg-[#E1F2FF]', iconColor: 'text-[#007AFF]', subtitle: '24°C · 自动' },
    { id: 'heater', name: '热水器', type: 'toggle_heater', icon: Pocket, active: false, color: 'bg-[#FFF0EB]', iconColor: 'text-[#FF6D00]', subtitle: '恒温 45°C' },
];

const useDashboardStore = create((set, get) => ({
    // 快捷控制项状态
    actions: initialActions,

    // 更新控制项状态
    updateAction: (id, updates) => set((state) => ({
        actions: state.actions.map((action) =>
            action.id === id ? { ...action, ...updates } : action
        ),
    })),

    // 切换控制项激活状态
    toggleAction: (id) => {
        const { actions } = get();
        const action = actions.find(a => a.id === id);

        if (!action) return;

        // 切换状态
        const newActive = !action.active;

        set((state) => ({
            actions: state.actions.map((a) =>
                a.id === id ? { ...a, active: newActive } : a
            ),
        }));

        return newActive;
    },

    // 重置所有状态（可选）
    resetActions: () => set({ actions: initialActions }),
}));

export default useDashboardStore;
