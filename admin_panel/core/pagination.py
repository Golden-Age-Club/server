import math

class MongoPaginator:
    def __init__(self, collection, query, page_number=1, page_size=25, sort=None):
        self.collection = collection
        self.query = query
        self.page_number = int(page_number) if int(page_number) > 0 else 1
        self.page_size = int(page_size)
        self.sort = sort

    def get_context(self):
        # Count total documents
        total_count = self.collection.count_documents(self.query)
        total_pages = math.ceil(total_count / self.page_size)

        # Calculate skip
        skip = (self.page_number - 1) * self.page_size

        # Fetch data
        cursor = self.collection.find(self.query)
        if self.sort:
            cursor = cursor.sort(self.sort)
        
        cursor = cursor.skip(skip).limit(self.page_size)
        data = []
        for doc in cursor:
            # Map _id to id string for Django templates
            if "_id" in doc:
                doc["id"] = str(doc["_id"])
            data.append(doc)

        # Pagination range logic (like Django admin)
        page_range = []
        if total_pages <= 10:
            page_range = range(1, total_pages + 1)
        else:
            # Simple window: current +/- 2
            start = max(1, self.page_number - 2)
            end = min(total_pages, self.page_number + 2)
            page_range = range(start, end + 1)

        return {
            "items": data,
            "total_count": total_count,
            "total_pages": total_pages,
            "current_page": self.page_number,
            "page_size": self.page_size,
            "has_next": self.page_number < total_pages,
            "has_previous": self.page_number > 1,
            "next_page": self.page_number + 1,
            "previous_page": self.page_number - 1,
            "page_range": list(page_range),
        }
