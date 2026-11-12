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
    const [firstLoadDone, setFirstLoadDone] = useState(false);

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
            setFirstLoadDone(true);
        } else {
            setLoading(true);
            fetcher({ page, page_size: pageSize, ...params })
                .then((data) => {
                    if (annule) return;
                    const pagesTotal = data?.total_pages || 0;
                    setItems(data?.items || []);
                    setTotal(data?.total || 0);
                    setTotalPages(pagesTotal);
                    setError(null);
                    setFirstLoadDone(true);

                    // Ne precharge la page suivante qu'apres la premiere page :
                    // evite un second scan complet a l'ouverture.
                    const cleSuivante = buildKey(page + 1, pageSize, paramsKey);
                    if (page > 1 && page + 1 <= pagesTotal && !prefetched.current.has(cleSuivante)) {
                        fetcher({ page: page + 1, page_size: pageSize, ...params })
                            .then((d) => {
                                if (d) prefetched.current.set(cleSuivante, d);
                            })
                            .catch(() => {});
                    }
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

        return () => {
            annule = true;
        };
    }, [fetcher, page, pageSize, paramsKey]);

    return { items, total, totalPages, loading, error, firstLoadDone };
}
