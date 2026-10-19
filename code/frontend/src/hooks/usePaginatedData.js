import { useEffect, useRef, useState } from 'react';

function buildKey(page, pageSize, paramsKey) {
    return `${page}:${pageSize}:${paramsKey}`;
}

export default function usePaginatedData(fetcher, page, pageSize, params) {
    const prefetched = useRef(new Map());
    const dernierParams = useRef(null);
    const [items, setItems] = useState([]);
    const [total, setTotal] = useState(0);
    const [totalPages, setTotalPages] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const paramsKey = JSON.stringify(params);

    useEffect(() => {
        let annule = false;

        if (dernierParams.current !== paramsKey) {
            prefetched.current.clear();
            dernierParams.current = paramsKey;
        }

        const key = buildKey(page, pageSize, paramsKey);
        const dejaPrecharge = prefetched.current.get(key);

        if (dejaPrecharge) {
            prefetched.current.delete(key);
            setItems(dejaPrecharge.items || []);
            setTotal(dejaPrecharge.total || 0);
            setTotalPages(dejaPrecharge.total_pages || 0);
            setLoading(false);
            setError(null);
        } else {
            setLoading(true);
            fetcher({ page, page_size: pageSize, ...params })
                .then((data) => {
                    if (annule) return;
                    setItems(data?.items || []);
                    setTotal(data?.total || 0);
                    setTotalPages(data?.total_pages || 0);
                    setError(null);
                })
                .catch((e) => {
                    if (annule) return;
                    console.log(e);
                    setError(e);
                })
                .finally(() => {
                    if (!annule) setLoading(false);
                });
        }

        const cleSuivante = buildKey(page + 1, pageSize, paramsKey);
        const cleApres = buildKey(page + 2, pageSize, paramsKey);

        if (!prefetched.current.has(cleSuivante)) {
            fetcher({ page: page + 1, page_size: pageSize, ...params })
                .then((data) => {
                    if (data) prefetched.current.set(cleSuivante, data);
                })
                .catch(() => {});
        }

        if (!prefetched.current.has(cleApres)) {
            fetcher({ page: page + 2, page_size: pageSize, ...params })
                .then((data) => {
                    if (data) prefetched.current.set(cleApres, data);
                })
                .catch(() => {});
        }

        return () => {
            annule = true;
        };
    }, [fetcher, page, pageSize, paramsKey]);

    return { items, total, totalPages, loading, error };
}
