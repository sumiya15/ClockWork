def page(db, scope, filters, limit, offset):
    query = {'$and': [scope, filters]}
    rows = list(db.obligations.find(query).sort([('active_due_at', 1), ('_id', 1)]).skip(offset).limit(limit))
    return rows, db.obligations.count_documents(query)


def get(db, scope, identifier):
    return db.obligations.find_one({'$and': [scope, {'_id': identifier}]})
