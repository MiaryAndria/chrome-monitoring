import Skeleton from "../Skeleton";

function CardGridSkeleton({ count = 8 }) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {Array.from({ length: count }).map((_, index) => (
                <div className="device-card" key={index}>
                    <Skeleton className="w-10 h-10 mb-4" />
                    <Skeleton className="h-5 w-2/3 mb-2" />
                    <Skeleton className="h-3 w-1/2 mb-4" />
                    <Skeleton className="h-3 w-full" />
                </div>
            ))}
        </div>
    );
}

export default CardGridSkeleton;
