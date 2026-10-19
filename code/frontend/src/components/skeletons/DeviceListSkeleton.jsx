import Skeleton from "../Skeleton";

function DeviceCardSkeleton() {
    return (
        <div className="device-card">
            <div className="flex justify-between items-start mb-4">
                <Skeleton className="w-10 h-10" />
                <Skeleton className="w-16 h-5" />
            </div>
            <Skeleton className="h-5 w-2/3 mb-2" />
            <Skeleton className="h-3 w-1/2 mb-4" />
            <div className="space-y-2.5">
                <Skeleton className="h-3 w-full" />
                <Skeleton className="h-3 w-5/6" />
                <Skeleton className="h-3 w-4/6" />
                <Skeleton className="h-3 w-3/4" />
                <Skeleton className="h-8 w-full mt-4" />
            </div>
        </div>
    );
}

function DeviceListSkeleton({ viewMode = "grid", count = 8 }) {
    if (viewMode === "table") {
        return (
            <div className="space-y-3">
                {Array.from({ length: count }).map((_, index) => (
                    <Skeleton key={index} className="h-12 w-full" />
                ))}
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {Array.from({ length: count }).map((_, index) => (
                <DeviceCardSkeleton key={index} />
            ))}
        </div>
    );
}

export default DeviceListSkeleton;
