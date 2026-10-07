function EmptyState({ icon: Icon, title, subtitle, iconClassName = "" }) {
    return (
        <div className="empty-state">
            {Icon && <Icon className={`empty-state-icon ${iconClassName}`} />}
            <p className="empty-state-title">{title}</p>
            {subtitle && <p className="empty-state-subtitle">{subtitle}</p>}
        </div>
    );
}

export default EmptyState;
