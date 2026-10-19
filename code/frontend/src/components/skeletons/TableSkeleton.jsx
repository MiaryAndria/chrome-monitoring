import Skeleton from "../Skeleton";

function TableSkeleton({ rows = 6 }) {
    return (
        <div className="space-y-3">
            {Array.from({ length: rows }).map((_, index) => (
                <Skeleton key={index} className="h-12 w-full" />
            ))}
        </div>
    );
}

export default TableSkeleton;
