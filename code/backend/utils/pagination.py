def build_page(items, total, page, page_size):
    if page_size is None or page_size <= 0:
        total_pages = 0
    else:
        total_pages = (total + page_size - 1) // page_size
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


__all__ = ["build_page"]
