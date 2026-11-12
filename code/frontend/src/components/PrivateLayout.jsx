import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";
import MouseSpotlight from "./MouseSpotlight";

function PrivateLayout() {
    return (
        <div className="device-layout" data-theme="dark">
            <MouseSpotlight />

            <div className="flex-1 flex flex-col h-screen overflow-hidden relative z-10">
                <div className="bg-glow-cyan"></div>
                <div className="bg-glow-purple"></div>
                <Navbar />

                <div className="flex-1 overflow-y-auto p-6 lg:p-8 z-10">
                    <Outlet />
                </div>
            </div>
        </div>
    );
}

export default PrivateLayout;
