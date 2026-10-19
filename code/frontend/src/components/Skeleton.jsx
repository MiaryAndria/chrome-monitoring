function Skeleton({ className = "", style }) {
    return (
        <div
            aria-hidden="true"
            style={style}
            className={`animate-pulse rounded-xl bg-white/5 ${className}`}
        />
    );
}

export default Skeleton;
