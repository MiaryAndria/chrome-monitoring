import Skeleton from "../Skeleton";

function StatCardSkeleton() {
    return (
        <div className="bg-white/5 rounded-xl p-4 border border-white/5">
            <Skeleton className="w-8 h-8 mb-3" />
            <Skeleton className="h-3 w-2/3 mb-2" />
            <Skeleton className="h-6 w-1/2" />
        </div>
    );
}

function DashboardSkeleton() {
    return (
        <div className="space-y-8">
            <div>
                <Skeleton className="h-5 w-48 mb-4" />
                <div className="device-card">
                    <Skeleton className="h-8 w-24 mb-3" />
                    <Skeleton className="h-3 w-56 mb-6" />
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                        {Array.from({ length: 4 }).map((_, index) => (
                            <StatCardSkeleton key={index} />
                        ))}
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="device-card">
                    <Skeleton className="w-10 h-10 mb-4" />
                    <Skeleton className="h-8 w-20 mb-3" />
                    <Skeleton className="h-3 w-48 mb-6" />
                    <div className="grid grid-cols-4 gap-2">
                        {Array.from({ length: 4 }).map((_, index) => (
                            <Skeleton key={index} className="h-16 w-full" />
                        ))}
                    </div>
                </div>
                <div className="device-card">
                    <Skeleton className="w-10 h-10 mb-4" />
                    <Skeleton className="h-8 w-20 mb-3" />
                    <Skeleton className="h-3 w-56 mb-6" />
                </div>
            </div>
        </div>
    );
}

export default DashboardSkeleton;
