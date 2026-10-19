import Skeleton from "../Skeleton";

function PrinterCardSkeleton() {
    return (
        <div className="device-card">
            <div className="flex justify-between items-start mb-4">
                <Skeleton className="w-10 h-10" />
                <Skeleton className="w-12 h-4" />
            </div>
            <Skeleton className="h-5 w-2/3 mb-2" />
            <Skeleton className="h-3 w-1/2 mb-4" />
            <Skeleton className="h-3 w-5/6" />
        </div>
    );
}

function PrinterListSkeleton({ viewMode = "grid", count = 10 }) {
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
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
            {Array.from({ length: count }).map((_, index) => (
                <PrinterCardSkeleton key={index} />
            ))}
        </div>
    );
}

export default PrinterListSkeleton;
