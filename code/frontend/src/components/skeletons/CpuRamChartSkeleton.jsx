import Skeleton from "../Skeleton";

function CpuRamChartSkeleton() {
    return (
        <div className="mt-4 space-y-5">
            <div className="telemetry-panel">
                <div className="flex items-center gap-2 mb-4">
                    <Skeleton className="w-4 h-4" />
                    <Skeleton className="h-4 w-40" />
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    {Array.from({ length: 4 }).map((_, index) => (
                        <div className="stat-card" key={index}>
                            <Skeleton className="h-3 w-20 mb-2" />
                            <Skeleton className="h-6 w-16" />
                        </div>
                    ))}
                </div>
                <Skeleton className="h-3 w-full mb-1" />
            </div>

            <div className="telemetry-panel">
                <div className="flex items-center justify-between mb-4">
                    <Skeleton className="h-4 w-48" />
                    <Skeleton className="h-3 w-16" />
                </div>
                <div className="h-64 w-full flex items-end gap-2">
                    {Array.from({ length: 12 }).map((_, index) => (
                        <Skeleton
                            key={index}
                            className="flex-1"
                            style={{ height: `${30 + (index % 5) * 12}%` }}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
}

export default CpuRamChartSkeleton;
