import React from 'react';
import { Search, Bell, User } from 'lucide-react';

export default function Navbar() {
    return (
        <div className="header-container glass-panel">
            <div className="flex items-center gap-4">
                <h1 className="text-xl font-semibold text-zinc-100 hidden sm:block">Dashboard</h1>
            </div>

            <div className="flex items-center gap-6">
                <div className="relative hidden md:block">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
                    <input
                        type="text"
                        placeholder="Search resources..."
                        className="input input-sm input-bordered bg-zinc-900/50 border-zinc-800 text-zinc-300 w-64 pl-9 focus:border-cyan-500/50 focus:outline-none transition-all"
                    />
                </div>

                <div className="flex items-center gap-4">
                    <button className="relative p-2 text-zinc-400 hover:text-zinc-100 transition-colors">
                        <Bell className="w-5 h-5" />
                        <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-purple-500 rounded-full"></span>
                    </button>

                    <div className="avatar">
                        <div className="w-8 h-8 rounded-full ring ring-cyan-500/30 ring-offset-base-100 ring-offset-2 bg-zinc-800 flex items-center justify-center cursor-pointer">
                            <User className="w-4 h-4 text-zinc-400" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
