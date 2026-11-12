function PageLayout({
    children,
    title,
    subtitle,
    titleIcon: TitleIcon,
    headerRight,
    contentClassName = "",
}) {
    return (
        <>
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
        </>
    );
}

export default PageLayout;
