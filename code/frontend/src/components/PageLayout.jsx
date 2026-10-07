import Sidebar from "./Sidebar";
import Navbar from "./Navbar";
import MouseSpotlight from "./MouseSpotlight";

function PageLayout({
    children,
    title,
    subtitle,
    titleIcon: TitleIcon,
    headerRight,
    className = "",
    contentClassName = "",
}) {
    return (
        <div className="device-layout" data-theme="dark">
            <MouseSpotlight />
            <Sidebar />

            <div className="flex-1 flex flex-col h-screen overflow-hidden relative z-10">
                <div className="bg-glow-cyan"></div>
                <div className="bg-glow-purple"></div>
                <Navbar />

                <div className={`flex-1 overflow-y-auto p-6 lg:p-8 z-10 ${className}`}>
                    {title && (
                        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
                            <div>
                                <h1 className="text-3xl font-bold tracking-tight text-zinc-100 flex items-center gap-3">
                                    {TitleIcon && <TitleIcon className="w-8 h-8 text-cyan-400" />}
                                    {title}
                                </h1>
                                {subtitle && (
                                    <p className="text-zinc-400 mt-2 font-medium tracking-wide">
                                        {subtitle}
                                    </p>
                                )}
                            </div>
                            {headerRight}
                        </div>
                    )}

                    <div className={contentClassName}>{children}</div>
                </div>
            </div>
        </div>
    );
}

export default PageLayout;
