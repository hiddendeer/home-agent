import { useState } from 'react'
import H5Dashboard from './components/H5Dashboard'
import MessagesPage from './components/MessagesPage'
import BottomNavigation from './components/BottomNavigation'

function App() {
    const [activeTab, setActiveTab] = useState('home')

    return (
        <div className="w-full relative max-w-md mx-auto">
            {activeTab === 'home' && <H5Dashboard />}
            {activeTab === 'messages' && <MessagesPage />}
            <BottomNavigation
                activeTab={activeTab}
                onTabChange={setActiveTab}
            />
        </div>
    )
}

export default App
