import { Database } from 'lucide-react';

function NoData({ title }) {
    return (
        <div className="telemetry-empty">
            <Database className="w-8 h-8 text-zinc-600 mb-2" />
            <span>Aucune donnée {title} disponible pour cet appareil.</span>
        </div>
    );
}

export default NoData;